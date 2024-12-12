from parser.tokens import TokenType


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
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.symbol_table = SymbolTable()

    def error(self, message, context=None):
        if context:
            message = f"In '{context}', " + message
        raise Exception(
            f"Syntax error at line {self.current_token.line}, column {
                self.current_token.column}: {message}"
        )

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type.name}, found {
                       self.current_token.type.name}")

    def program(self):
        """
        <программа> ::= program var <описание> begin <оператор> {; <оператор>} end.
        """
        self.eat(TokenType.PROGRAM)
        self.eat(TokenType.VAR)
        self.symbol_table.enter_scope()  # Входим в глобальную область видимости
        self.description()
        self.eat(TokenType.BEGIN)
        self.operator_list()
        self.eat(TokenType.END)
        self.eat(TokenType.DOT)
        self.symbol_table.exit_scope()  # Выходим из глобальной области видимости
        if self.current_token.type != TokenType.FIN:
            self.error("Expected end of program")

    def operator_list(self):
        """
        <оператор> {; <оператор>}
        """
        self.operator_()
        while self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            if self.current_token.type == TokenType.END:
                return  # Обрабатываем END
            self.operator_()
        if self.current_token.type != TokenType.END:
            self.error(f"expected ';' or 'END', found '{
                       self.current_token.type.name}'", context="operator_list")

    def description(self):
        """
        <описание> ::= {<идентификатор> {, <идентификатор>} : <тип> ;}
        """
        while self.current_token.type == TokenType.ID:
            # Проверяем валидность имени идентификатора
            if not self.current_token.value[0].isalpha():
                self.error(message=f"Invalid ID name: '{
                           self.current_token.value}'")

            ids = self.id_list()
            self.eat(TokenType.COLON)
            type = self.type()
            for id_token in ids:
                if not self.symbol_table.define(id_token.value, type):
                    self.error(f"Variable '{id_token.value}' already declared")
            self.eat(TokenType.SEMICOLON)

    def id_list(self):
        """
        <идентификатор> {, <идентификатор>}
        """
        id_tokens = [self.current_token]
        self.eat(TokenType.ID)
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            id_tokens.append(self.current_token)
            self.eat(TokenType.ID)
        return id_tokens

    def type(self):
        """
        <тип> ::= integer | real | boolean
        """
        if self.current_token.type == TokenType.INTEGER:
            type = self.current_token
            self.eat(TokenType.INTEGER)
            return type
        elif self.current_token.type == TokenType.REAL:
            type = self.current_token
            self.eat(TokenType.REAL)
            return type
        elif self.current_token.type == TokenType.BOOLEAN:
            type = self.current_token
            self.eat(TokenType.BOOLEAN)
            return type
        else:
            self.error("Expected type (integer, real, boolean)")

    def operator_(self):
        """
        <оператор> ::= <присваивания> | <условный> | <фиксированного_цикла> | <условного_цикла> | <составной> | <ввода> | <вывода>
        """
        if self.current_token.type == TokenType.ID:
            self.assignment()
        elif self.current_token.type == TokenType.IF:
            self.conditional()
        elif self.current_token.type == TokenType.FOR:
            self.fixed_loop()
        elif self.current_token.type == TokenType.WHILE:
            self.conditional_loop()
        elif self.current_token.type == TokenType.LBRACKET:
            self.compound()
        elif self.current_token.type == TokenType.READ:
            self.input_op()
        elif self.current_token.type == TokenType.WRITE:
            self.output_op()
        else:
            self.error("Expected operator")

    def assignment(self):
        """
        <присваивания> ::= <идентификатор> as <выражение>
        """
        id_token = self.current_token
        self.eat(TokenType.ID)
        if not self.symbol_table.lookup(id_token.value):
            self.error(f"Variable '{id_token.value}' not declared")
        self.eat(TokenType.AS)
        self.expression()

    def conditional(self):
        """
        <условный> ::= if <выражение> then <оператор> [ else <оператор>]
        """
        self.eat(TokenType.IF)
        self.expression()
        self.eat(TokenType.THEN)
        self.operator_()
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            self.operator_()

    def fixed_loop(self):
        """
        <фиксированного_цикла> ::= for <присваивания> to <выражение> do <оператор>
        """
        self.eat(TokenType.FOR)
        self.symbol_table.enter_scope()  # Входим в область видимости цикла
        self.assignment()
        self.eat(TokenType.TO)
        self.expression()
        self.eat(TokenType.DO)
        self.operator_()
        self.symbol_table.exit_scope()  # Выходим из области видимости цикла

    def conditional_loop(self):
        """
        <условного_цикла> ::= while <выражение> do <оператор>
        """
        self.eat(TokenType.WHILE)
        self.expression()
        self.eat(TokenType.DO)
        self.operator_()

    def compound(self):
        """
        <составной> ::= «[» <оператор> { ( : | \n) <оператор> } «]»
        """
        self.eat(TokenType.LBRACKET)
        self.symbol_table.enter_scope()  # Входим в область видимости составного оператора
        self.operator_()
        while self.current_token.type == TokenType.COLON or self.current_token.type == TokenType.SEMICOLON:
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            else:
                self.eat(TokenType.COLON)
            self.operator_()
        self.symbol_table.exit_scope()  # Выходим из области видимости составного оператора
        self.eat(TokenType.RBRACKET)

    def input_op(self):
        """
        <ввода> ::= read «(»<идентификатор> {, <идентификатор> } «)»
        """
        self.eat(TokenType.READ)
        self.eat(TokenType.LPAREN)
        id_token = self.current_token
        self.eat(TokenType.ID)
        if not self.symbol_table.lookup(id_token.value):
            self.error(f"Variable '{id_token.value}' not declared")
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            id_token = self.current_token
            self.eat(TokenType.ID)
            if not self.symbol_table.lookup(id_token.value):
                self.error(f"Variable '{id_token.value}' not declared")
        self.eat(TokenType.RPAREN)

    def output_op(self):
        """
        <вывода> ::= write «(»<выражение> {, <выражение> } «)»
        """
        self.eat(TokenType.WRITE)
        self.eat(TokenType.LPAREN)
        self.expression()
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            self.expression()
        self.eat(TokenType.RPAREN)

    def expression(self):
        """
        <выражение> ::= <сумма> | <выражение> (<>|=|<|<=|>|>=) <сумма>
        """
        self.sum()
        while self.current_token.type in (
            TokenType.NE,
            TokenType.EQ,
            TokenType.LT,
            TokenType.LE,
            TokenType.GT,
            TokenType.GE,
        ):
            if self.current_token.type == TokenType.NE:
                self.eat(TokenType.NE)
            elif self.current_token.type == TokenType.EQ:
                self.eat(TokenType.EQ)
            elif self.current_token.type == TokenType.LT:
                self.eat(TokenType.LT)
            elif self.current_token.type == TokenType.LE:
                self.eat(TokenType.LE)
            elif self.current_token.type == TokenType.GT:
                self.eat(TokenType.GT)
            elif self.current_token.type == TokenType.GE:
                self.eat(TokenType.GE)
            self.sum()

    def sum(self):
        """
        <сумма> ::= <произведение> { (+ | - | or) <произведение>}
        """
        self.product()
        while self.current_token.type in (
            TokenType.PLUS,
            TokenType.MIN,
            TokenType.OR,
        ):
            if self.current_token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif self.current_token.type == TokenType.MIN:
                self.eat(TokenType.MIN)
            elif self.current_token.type == TokenType.OR:
                self.eat(TokenType.OR)
            self.product()

    def product(self):
        """
        <произведение> ::= <множитель> { (* | / | and) <множитель>}
        """
        self.multiplier()
        while self.current_token.type in (
            TokenType.MULT,
            TokenType.DIV,
            TokenType.AND,
        ):
            if self.current_token.type == TokenType.MULT:
                self.eat(TokenType.MULT)
            elif self.current_token.type == TokenType.DIV:
                self.eat(TokenType.DIV)
            elif self.current_token.type == TokenType.AND:
                self.eat(TokenType.AND)
            self.multiplier()

    def multiplier(self):
        """
        <множитель> ::= <идентификатор> | <число> | <логическая_константа> | not <множитель> | «(»<выражение>«)»
        """
        if self.current_token.type == TokenType.ID:
            id_token = self.current_token
            self.eat(TokenType.ID)
            if not self.symbol_table.lookup(id_token.value):
                self.error(f"Variable '{id_token.value}' not declared")
        elif self.current_token.type in (
            TokenType.DEC,
            TokenType.HEX,
            TokenType.OCT,
            TokenType.BIN,
            TokenType.NUM_REAL,
        ):
            self.number()
        elif self.current_token.type in (TokenType.TRUE, TokenType.FALSE):
            self.logical_constant()
        elif self.current_token.type == TokenType.TILDE:
            self.eat(TokenType.TILDE)
            self.multiplier()
        elif self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            self.expression()
            self.eat(TokenType.RPAREN)
        else:
            self.error(
                "Expected identifier, number, logical constant, 'not', or '('"
            )

    def number(self):
        """
        <число> ::= <целое> | <действительное>
        """
        if self.current_token.type == TokenType.DEC:
            self.eat(TokenType.DEC)
        elif self.current_token.type == TokenType.HEX:
            self.eat(TokenType.HEX)
        elif self.current_token.type == TokenType.OCT:
            self.eat(TokenType.OCT)
        elif self.current_token.type == TokenType.BIN:
            self.eat(TokenType.BIN)
        elif self.current_token.type == TokenType.NUM_REAL:
            self.eat(TokenType.NUM_REAL)
        else:
            self.error("Expected number")

    def logical_constant(self):
        """
        <логическая_константа> ::= true | false
        """
        if self.current_token.type == TokenType.TRUE:
            self.eat(TokenType.TRUE)
        elif self.current_token.type == TokenType.FALSE:
            self.eat(TokenType.FALSE)
        else:
            self.error("Expected 'true' or 'false'")

    def parse(self):
        self.program()
        if self.current_token.type != TokenType.FIN:
            self.error("Expected end of program")
