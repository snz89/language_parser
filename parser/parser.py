from parser.tokens import (
    Token,
    keywords_table,
    delimiters_table,
    numbers_table,
    identifiers_table,
)


class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.scopes = []

    def enter_scope(self):
        """Вход в новую область видимости."""
        self.scopes.append({})

    def exit_scope(self):
        """Выход из текущей области видимости."""
        self.scopes.pop()

    def define(self, name, type):
        """Определить переменную в текущей области видимости."""
        current_scope = self.scopes[-1]
        if name in current_scope:
            return False  # Переменная уже определена в этой области видимости
        current_scope[name] = type
        return True

    def lookup(self, name):
        """Найти переменную в таблице символов."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None


class Parser:
    def __init__(self, lexer, text):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.symbol_table = SymbolTable()
        self.text_lines = text.splitlines()

    def error(self, message, additional_shift = 0):
        line = self.text_lines[self.current_token.line - 1]
        stript_line = line.strip()
        spaces = len(line) - len(line.lstrip())
        pointer_shift = self.current_token.column - spaces + additional_shift
        raise Exception(
            f"Syntax error at line {self.current_token.line}: {
                message}\n    {stript_line}\n    {'^':>{pointer_shift}}"
        )

    def eat(self, table_num, lexeme_num):
        if self.current_token.table_num == table_num and self.current_token.lexeme_num == lexeme_num:
            self.current_token = self.lexer.get_next_token()
        else:
            # Поиск имени токена для вывода ошибки:
            if table_num == 1:
                for name, num in keywords_table.items():
                    if num == lexeme_num:
                        expected_token_name = name
                        break
            elif table_num == 2:
                for name, num in delimiters_table.items():
                    if num == lexeme_num:
                        expected_token_name = name
                        break
            else:
                expected_token_name = f"({table_num}, {lexeme_num})"

            if self.current_token.table_num == 1:
                for name, num in keywords_table.items():
                    if num == self.current_token.lexeme_num:
                        current_token_name = name
                        break
            elif self.current_token.table_num == 2:
                for name, num in delimiters_table.items():
                    if num == self.current_token.lexeme_num:
                        current_token_name = name
                        break
            elif self.current_token.table_num == 3:
                current_token_name = self.current_token.value
            elif self.current_token.table_num == 4:
                current_token_name = self.current_token.value
            else:
                current_token_name = f"({self.current_token.table_num}, {
                    self.current_token.lexeme_num})"
            self.error(f"Expected {expected_token_name}, found {
                       current_token_name}")

    def program(self):
        """
        <программа> ::= program var <описание> begin <оператор> {; <оператор>} end.
        """
        self.eat(1, keywords_table["PROGRAM"])
        self.eat(1, keywords_table["VAR"])
        self.symbol_table.enter_scope()  # Входим в глобальную область видимости
        self.description()
        self.eat(1, keywords_table["BEGIN"])
        self.operator_list()
        self.eat(1, keywords_table["END"])
        self.eat(2, delimiters_table["."])
        self.symbol_table.exit_scope()  # Выходим из глобальной области видимости
        if not (self.current_token.table_num == 0 and self.current_token.lexeme_num == 0):
            self.error("Expected end of program")

    def operator_list(self):
        """
        <оператор> {; <оператор>}
        """
        self.operator_()
        while self.current_token.table_num == 2 and self.current_token.lexeme_num == delimiters_table[";"]:
            self.eat(2, delimiters_table[";"])
            if self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["END"]:
                return  # Обрабатываем END
            self.operator_()

    def description(self):
        """
        <описание> ::= {<идентификатор> {, <идентификатор>} : <тип> ;}
        """
        while self.current_token.table_num == 4:
            if not self.current_token.value.isalpha():
                self.error(f"Invalid ID name: '{self.current_token.value}'")

            ids = self.id_list()
            self.eat(2, delimiters_table[":"])
            type = self.type()
            for id_token in ids:
                if not self.symbol_table.define(id_token.value, type):
                    self.error(f"Variable '{id_token.value}' already declared")
            self.eat(2, delimiters_table[";"])

    def id_list(self):
        """
        <идентификатор> {, <идентификатор>}
        """
        id_tokens = [self.current_token]
        if not self.current_token.value[0].isalpha():
            self.error(f"Identifier '{
                       self.current_token.value}' must start with a letter")
        self.eat(4, self.current_token.lexeme_num)
        while self.current_token.table_num == 2 and self.current_token.lexeme_num == delimiters_table[","]:
            self.eat(2, delimiters_table[","])
            id_tokens.append(self.current_token)
            if not self.current_token.value[0].isalpha():
                self.error(f"Identifier '{
                           self.current_token.value}' must start with a letter")
            self.eat(4, self.current_token.lexeme_num)
        return id_tokens

    def type(self):
        """
        <тип> ::= integer | real | boolean
        """
        if self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["INTEGER"]:
            type = self.current_token
            self.eat(1, keywords_table["INTEGER"])
            return type
        elif self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["REAL"]:
            type = self.current_token
            self.eat(1, keywords_table["REAL"])
            return type
        elif self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["BOOLEAN"]:
            type = self.current_token
            self.eat(1, keywords_table["BOOLEAN"])
            return type
        else:
            self.error("Expected type (integer, real, boolean)")

    def operator_(self):
        """
        <оператор> ::= <присваивания> | <условный> | <фиксированного_цикла> | <условного_цикла> | <составной> | <ввода> | <вывода>
        """
        if self.current_token.table_num == 4:
            self.assignment()
        elif self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["IF"]:
            self.conditional()
        elif self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["FOR"]:
            self.fixed_loop()
        elif self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["WHILE"]:
            self.conditional_loop()
        elif self.current_token.table_num == 2 and self.current_token.lexeme_num == delimiters_table["["]:
            self.compound()
        elif self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["READ"]:
            self.input_op()
        elif self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["WRITE"]:
            self.output_op()
        else:
            self.error("Expected operator")

    def assignment(self):
        """
        <присваивания> ::= <идентификатор> as <выражение>
        """
        id_token = self.current_token
        self.eat(4, self.current_token.lexeme_num)
        if not self.symbol_table.lookup(id_token.value):
            self.error(f"Variable '{id_token.value}' not declared", -2)
        self.eat(1, keywords_table["AS"])
        self.expression()

    def conditional(self):
        """
        <условный> ::= if <выражение> then <оператор> [ else <оператор>]
        """
        self.eat(1, keywords_table["IF"])
        self.expression()
        self.eat(1, keywords_table["THEN"])
        self.operator_()
        if self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["ELSE"]:
            self.eat(1, keywords_table["ELSE"])
            self.operator_()

    def fixed_loop(self):
        """
        <фиксированного_цикла> ::= for <присваивания> to <выражение> do <оператор>
        """
        self.eat(1, keywords_table["FOR"])
        self.symbol_table.enter_scope()  # Входим в область видимости цикла
        self.assignment()
        self.eat(1, keywords_table["TO"])
        self.expression()
        self.eat(1, keywords_table["DO"])
        self.operator_()
        self.symbol_table.exit_scope()  # Выходим из области видимости цикла

    def conditional_loop(self):
        """
        <условного_цикла> ::= while <выражение> do <оператор>
        """
        self.eat(1, keywords_table["WHILE"])
        self.expression()
        self.eat(1, keywords_table["DO"])
        self.operator_()

    def compound(self):
        """
        <составной> ::= «[» <оператор> { ( : | \n) <оператор> } «]»
        """
        self.eat(2, delimiters_table["["])
        self.symbol_table.enter_scope()  # Входим в область видимости составного оператора
        self.operator_()
        while self.current_token.table_num == 2 and (self.current_token.lexeme_num == delimiters_table[":"] or self.current_token.lexeme_num == delimiters_table[";"]):
            if self.current_token.lexeme_num == delimiters_table[";"]:
                self.eat(2, delimiters_table[";"])
            else:
                self.eat(2, delimiters_table[":"])
            self.operator_()
        self.symbol_table.exit_scope()  # Выходим из области видимости составного оператора
        self.eat(2, delimiters_table["]"])

    def input_op(self):
        """
        <ввода> ::= read «(»<идентификатор> {, <идентификатор> } «)»
        """
        self.eat(1, keywords_table["READ"])
        self.eat(2, delimiters_table["("])
        id_token = self.current_token
        self.eat(4, self.current_token.lexeme_num)
        if not self.symbol_table.lookup(id_token.value):
            self.error(f"Variable '{id_token.value}' not declared", -2)
        while self.current_token.table_num == 2 and self.current_token.lexeme_num == delimiters_table[","]:
            self.eat(2, delimiters_table[","])
            id_token = self.current_token
            self.eat(4, self.current_token.lexeme_num)
            if not self.symbol_table.lookup(id_token.value):
                self.error(f"Variable '{id_token.value}' not declared", -2)
        self.eat(2, delimiters_table[")"])

    def output_op(self):
        """
        <вывода> ::= write «(»<выражение> {, <выражение> } «)»
        """
        self.eat(1, keywords_table["WRITE"])
        self.eat(2, delimiters_table["("])
        self.expression()
        while self.current_token.table_num == 2 and self.current_token.lexeme_num == delimiters_table[","]:
            self.eat(2, delimiters_table[","])
            self.expression()
        self.eat(2, delimiters_table[")"])

    def expression(self):
        """
        <выражение> ::= <сумма> | <выражение> (<>|=|<|<=|>|>=) <сумма>
        """
        self.sum()
        while self.current_token.table_num == 1 and self.current_token.lexeme_num in (keywords_table["NE"], keywords_table["EQ"], keywords_table["LT"], keywords_table["LE"], keywords_table["GT"], keywords_table["GE"]):
            if self.current_token.lexeme_num == keywords_table["NE"]:
                self.eat(1, keywords_table["NE"])
            elif self.current_token.lexeme_num == keywords_table["EQ"]:
                self.eat(1, keywords_table["EQ"])
            elif self.current_token.lexeme_num == keywords_table["LT"]:
                self.eat(1, keywords_table["LT"])
            elif self.current_token.lexeme_num == keywords_table["LE"]:
                self.eat(1, keywords_table["LE"])
            elif self.current_token.lexeme_num == keywords_table["GT"]:
                self.eat(1, keywords_table["GT"])
            elif self.current_token.lexeme_num == keywords_table["GE"]:
                self.eat(1, keywords_table["GE"])
            self.sum()

    def sum(self):
        """
        <сумма> ::= <произведение> { (+ | - | or) <произведение>}
        """
        self.product()
        while self.current_token.table_num == 1 and self.current_token.lexeme_num in (keywords_table["PLUS"], keywords_table["MIN"], keywords_table["OR"]):
            if self.current_token.lexeme_num == keywords_table["PLUS"]:
                self.eat(1, keywords_table["PLUS"])
            elif self.current_token.lexeme_num == keywords_table["MIN"]:
                self.eat(1, keywords_table["MIN"])
            elif self.current_token.lexeme_num == keywords_table["OR"]:
                self.eat(1, keywords_table["OR"])
            self.product()

    def product(self):
        """
        <произведение> ::= <множитель> { (* | / | and) <множитель>}
        """
        self.multiplier()
        while self.current_token.table_num == 1 and self.current_token.lexeme_num in (keywords_table["MULT"], keywords_table["DIV"], keywords_table["AND"]):
            if self.current_token.lexeme_num == keywords_table["MULT"]:
                self.eat(1, keywords_table["MULT"])
            elif self.current_token.lexeme_num == keywords_table["DIV"]:
                self.eat(1, keywords_table["DIV"])
            elif self.current_token.lexeme_num == keywords_table["AND"]:
                self.eat(1, keywords_table["AND"])
            self.multiplier()

    def multiplier(self):
        """
        <множитель> ::= <идентификатор> | <число> | <логическая_константа> | not <множитель> | «(»<выражение>«)»
        """
        if self.current_token.table_num == 4:
            id_token = self.current_token
            self.eat(4, self.current_token.lexeme_num)
            if not self.symbol_table.lookup(id_token.value):
                self.error(f"Variable '{id_token.value}' not declared", -2)
        elif self.current_token.table_num == 3:
            self.number()
        elif self.current_token.table_num == 1 and self.current_token.lexeme_num in (keywords_table["TRUE"], keywords_table["FALSE"]):
            self.logical_constant()
        elif self.current_token.table_num == 2 and self.current_token.lexeme_num == delimiters_table["~"]:
            self.eat(2, delimiters_table["~"])
            self.multiplier()
        elif self.current_token.table_num == 2 and self.current_token.lexeme_num == delimiters_table["("]:
            self.eat(2, delimiters_table["("])
            self.expression()
            self.eat(2, delimiters_table[")"])
        else:
            self.error(
                "Expected identifier, number, logical constant, 'not', or '('"
            )

    def number(self):
        """
        <число> ::= <целое> | <действительное>
        """
        if self.current_token.table_num == 3:
            self.eat(3, self.current_token.lexeme_num)
        else:
            self.error("Expected number")

    def logical_constant(self):
        """
        <логическая_константа> ::= true | false
        """
        if self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["TRUE"]:
            self.eat(1, keywords_table["TRUE"])
        elif self.current_token.table_num == 1 and self.current_token.lexeme_num == keywords_table["FALSE"]:
            self.eat(1, keywords_table["FALSE"])
        else:
            self.error("Expected 'true' or 'false'")

    def parse(self):
        self.program()
        if not (self.current_token.table_num == 0 and self.current_token.lexeme_num == 0):
            self.error("Expected end of program")
