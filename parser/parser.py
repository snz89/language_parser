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
        self.tokens = lexer.tokenize()  # Получаем список токенов сразу
        self.current_token_index = 0
        self.current_token = (
            self.tokens[self.current_token_index] if self.tokens else None
        )
        self.symbol_table = SymbolTable()
        self.text_lines = lexer.text.split("\n")

        # Словари для быстрого доступа к номерам лексем по их именам
        self.keywords_dict = {
            name: i + 1 for i, name in enumerate(lexer.keywords_table)
        }
        self.rel_op_dict = {name: i + 1 for i, name in enumerate(lexer.rel_op_table)}
        self.add_ops_dict = {name: i + 1 for i, name in enumerate(lexer.add_ops_table)}
        self.mul_ops_dict = {name: i + 1 for i, name in enumerate(lexer.mul_ops_table)}
        self.uops_dict = {name: i + 1 for i, name in enumerate(lexer.uops_table)}
        self.delimiters_dict = {
            name: i + 1 for i, name in enumerate(lexer.delimiters_table)
        }

    def advance(self):
        """Переход к следующему токену."""
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None

    def error(self, message, context=None):
        line = self.text_lines[self.current_token.line - 1]
        stript_line = line.strip()
        if context:
            message = f"In rule '{context}', " + message
        raise Exception(
            f"Syntax error at line {self.current_token.line}: {
                message}\n    {stript_line}"
        )

    def get_token_name(self, token):
        """Вспомогательная функция для получения имени токена по его типу и значению."""
        if token.table_num == 0:
            return token.value
        if token.table_num == 1:
            try:
                return self.lexer.keywords_table[token.lexeme_num - 1]
            except IndexError:
                return "unknown keyword"
        elif token.table_num == 2:
            try:
                return self.lexer.rel_op_table[token.lexeme_num - 1]
            except IndexError:
                return "unknown rel_op"
        elif token.table_num == 3:
            try:
                return self.lexer.add_ops_table[token.lexeme_num - 1]
            except IndexError:
                return "unknown add_op"
        elif token.table_num == 4:
            try:
                return self.lexer.mul_ops_table[token.lexeme_num - 1]
            except IndexError:
                return "unknown mul_op"
        elif token.table_num == 5:
            try:
                return self.lexer.uops_table[token.lexeme_num - 1]
            except IndexError:
                return "unknown uop"
        elif token.table_num == 6:
            try:
                return self.lexer.delimiters_table[token.lexeme_num - 1]
            except IndexError:
                return "unknown delimiter"
        elif token.table_num in (7, 8):
            return token.value  # Для чисел и идентификаторов выводим их значение
        else:
            return f"({token.table_num}, {token.lexeme_num})"

    def eat(self, table_num, lexeme_num):
        if (
            self.current_token.table_num == table_num
            and self.current_token.lexeme_num == lexeme_num
        ):
            self.advance()
        else:
            # Поиск имени токена для вывода ошибки:
            if table_num == 1:
                expected_token_name = (
                    self.lexer.keywords_table[lexeme_num - 1]
                    if lexeme_num - 1 < len(self.lexer.keywords_table)
                    else "unknown keyword"
                )
            elif table_num == 2:
                expected_token_name = (
                    self.lexer.rel_op_table[lexeme_num - 1]
                    if lexeme_num - 1 < len(self.lexer.rel_op_table)
                    else "unknown rel_op"
                )
            elif table_num == 3:
                expected_token_name = (
                    self.lexer.add_ops_table[lexeme_num - 1]
                    if lexeme_num - 1 < len(self.lexer.add_ops_table)
                    else "unknown add_op"
                )
            elif table_num == 4:
                expected_token_name = (
                    self.lexer.mul_ops_table[lexeme_num - 1]
                    if lexeme_num - 1 < len(self.lexer.mul_ops_table)
                    else "unknown mul_op"
                )
            elif table_num == 5:
                expected_token_name = (
                    self.lexer.uops_table[lexeme_num - 1]
                    if lexeme_num - 1 < len(self.lexer.uops_table)
                    else "unknown uop"
                )
            elif table_num == 6:
                expected_token_name = (
                    self.lexer.delimiters_table[lexeme_num - 1]
                    if lexeme_num - 1 < len(self.lexer.delimiters_table)
                    else "unknown delimiter"
                )
            else:
                expected_token_name = f"({table_num}, {lexeme_num})"

            current_token_name = self.get_token_name(self.current_token)

            if (table_num, lexeme_num) == (
                6,
                self.delimiters_dict[";"],
            ):
                # Если ожидался конец составного оператора, но нашелся другой разделитель, указываем на него
                self.error(
                    f"Expected '{expected_token_name}', found '{current_token_name}'"
                )
            else:
                self.error(
                    f"Expected '{expected_token_name}', found '{current_token_name}'"
                )

    def program(self):
        """
        <программа> ::= program var <описание> begin <оператор> {; <оператор>} end.
        """
        self.eat(1, self.keywords_dict["program"])
        self.eat(1, self.keywords_dict["var"])
        self.symbol_table.enter_scope()  # Входим в глобальную область видимости
        self.description()
        self.eat(1, self.keywords_dict["begin"])
        self.operator_list()
        self.eat(1, self.keywords_dict["end"])
        self.eat(6, self.delimiters_dict["."])
        self.symbol_table.exit_scope()  # Выходим из глобальной области видимости
        if not (
            self.current_token.table_num == 0 and self.current_token.lexeme_num == 0
        ):
            self.error("Expected end of program")

    def operator_list(self):
        """
        <оператор> {; <оператор>}
        """
        self.operator_()
        while (
            self.current_token.table_num == 6
            and self.current_token.lexeme_num == self.delimiters_dict[";"]
        ):
            self.eat(6, self.delimiters_dict[";"])
            if (
                self.current_token.table_num == 1
                and self.current_token.lexeme_num == self.keywords_dict["end"]
            ):
                return  # Обрабатываем END
            self.operator_()

    def description(self):
        """
        <описание> ::= {<идентификатор> {, <идентификатор>} : <тип> ;}
        """
        while self.current_token.table_num == 8:
            ids = self.id_list()
            self.eat(6, self.delimiters_dict[":"])
            type_token = self.type()
            for id_token in ids:
                if not self.symbol_table.define(id_token.value, type_token):
                    self.error(f"Variable '{id_token.value}' already declared")
            self.eat(6, self.delimiters_dict[";"])

    def id_list(self):
        """
        <идентификатор> {, <идентификатор>}
        """
        id_tokens = [self.current_token]
        if not self.current_token.value[0].isalpha():
            self.error(
                f"Identifier '{self.current_token.value}' must start with a letter",
                context="id_list",
            )
        self.eat(8, self.current_token.lexeme_num)
        while (
            self.current_token.table_num == 6
            and self.current_token.lexeme_num == self.delimiters_dict[","]
        ):
            self.eat(6, self.delimiters_dict[","])
            id_tokens.append(self.current_token)
            if not self.current_token.value[0].isalpha():
                self.error(
                    f"Identifier '{self.current_token.value}' must start with a letter",
                    context="id_list",
                )
            self.eat(8, self.current_token.lexeme_num)
        return id_tokens

    def type(self):
        """
        <тип> ::= integer | real | boolean
        """
        if (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["integer"]
        ):
            type_token = self.current_token
            self.eat(1, self.keywords_dict["integer"])
            return type_token
        elif (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["real"]
        ):
            type_token = self.current_token
            self.eat(1, self.keywords_dict["real"])
            return type_token
        elif (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["boolean"]
        ):
            type_token = self.current_token
            self.eat(1, self.keywords_dict["boolean"])
            return type_token
        else:
            self.error("Expected type (integer, real, boolean)")

    def operator_(self):
        """
        <оператор> ::= <присваивания> | <условный> | <фиксированного_цикла> | <условного_цикла> | <составной> | <ввода> | <вывода>
        """
        if self.current_token.table_num == 8:
            self.assignment()
        elif (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["if"]
        ):
            self.conditional()
        elif (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["for"]
        ):
            self.fixed_loop()
        elif (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["while"]
        ):
            self.conditional_loop()
        elif (
            self.current_token.table_num == 6
            and self.current_token.lexeme_num == self.delimiters_dict["["]
        ):
            self.compound()
        elif (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["read"]
        ):
            self.input_op()
        elif (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["write"]
        ):
            self.output_op()
        else:
            self.error("Expected operator")

    def assignment(self):
        """
        <присваивания> ::= <идентификатор> as <выражение>
        """
        id_token = self.current_token
        self.eat(8, self.current_token.lexeme_num)
        if not self.symbol_table.lookup(id_token.value):
            self.error(f"Variable '{id_token.value}' not declared")
        self.eat(1, self.keywords_dict["as"])
        self.expression()

    def conditional(self):
        """
        <условный> ::= if <выражение> then <оператор> [ else <оператор>]
        """
        self.eat(1, self.keywords_dict["if"])
        self.expression()
        self.eat(1, self.keywords_dict["then"])
        self.operator_()
        if (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["else"]
        ):
            self.eat(1, self.keywords_dict["else"])
            self.operator_()

    def fixed_loop(self):
        """
        <фиксированного_цикла> ::= for <присваивания> to <выражение> do <оператор>
        """
        self.eat(1, self.keywords_dict["for"])
        self.symbol_table.enter_scope()  # Входим в область видимости цикла
        self.assignment()
        self.eat(1, self.keywords_dict["to"])
        self.expression()
        self.eat(1, self.keywords_dict["do"])
        self.operator_()
        self.symbol_table.exit_scope()  # Выходим из области видимости цикла

    def conditional_loop(self):
        """
        <условного_цикла> ::= while <выражение> do <оператор>
        """
        self.eat(1, self.keywords_dict["while"])
        self.expression()
        self.eat(1, self.keywords_dict["do"])
        self.operator_()

    def compound(self):
        """
        <составной> ::= «[» <оператор> { ( : | \n) <оператор> } «]»
        """
        self.eat(6, self.delimiters_dict["["])
        self.symbol_table.enter_scope()  # Входим в область видимости составного оператора
        self.operator_()
        while self.current_token.table_num == 6 and (
            self.current_token.lexeme_num == self.delimiters_dict[":"]
            or self.current_token.lexeme_num == self.delimiters_dict[";"]
        ):
            if self.current_token.lexeme_num == self.delimiters_dict[";"]:
                self.eat(6, self.delimiters_dict[";"])
            else:
                self.eat(6, self.delimiters_dict[":"])
            self.operator_()
        if (
            self.current_token.table_num != 6
            or self.current_token.lexeme_num != self.delimiters_dict["]"]
        ):
            self.error(
                f"Expected ']', found '{self.get_token_name(self.current_token)}'",
                context="compound",
            )
        self.symbol_table.exit_scope()  # Выходим из области видимости составного оператора
        self.eat(6, self.delimiters_dict["]"])

    def input_op(self):
        """
        <ввода> ::= read «(»<идентификатор> {, <идентификатор> } «)»
        """
        self.eat(1, self.keywords_dict["read"])
        self.eat(6, self.delimiters_dict["("])
        id_token = self.current_token
        self.eat(8, self.current_token.lexeme_num)
        if not self.symbol_table.lookup(id_token.value):
            self.error(f"Variable '{id_token.value}' not declared")
        while (
            self.current_token.table_num == 6
            and self.current_token.lexeme_num == self.delimiters_dict[","]
        ):
            self.eat(6, self.delimiters_dict[","])
            id_token = self.current_token
            self.eat(8, self.current_token.lexeme_num)
            if not self.symbol_table.lookup(id_token.value):
                self.error(f"Variable '{id_token.value}' not declared")
        self.eat(6, self.delimiters_dict[")"])

    def output_op(self):
        """
        <вывода> ::= write «(»<выражение> {, <выражение> } «)»
        """
        self.eat(1, self.keywords_dict["write"])
        self.eat(6, self.delimiters_dict["("])
        self.expression()
        while (
            self.current_token.table_num == 6
            and self.current_token.lexeme_num == self.delimiters_dict[","]
        ):
            self.eat(6, self.delimiters_dict[","])
            self.expression()
        self.eat(6, self.delimiters_dict[")"])

    def expression(self):
        """
        <выражение> ::= <сумма> | <выражение> (<>|=|<|<=|>|>=) <сумма>
        """
        self.sum()
        while self.current_token.table_num == 2:
            if self.current_token.lexeme_num == self.rel_op_dict["NE"]:
                self.eat(2, self.rel_op_dict["NE"])
            elif self.current_token.lexeme_num == self.rel_op_dict["EQ"]:
                self.eat(2, self.rel_op_dict["EQ"])
            elif self.current_token.lexeme_num == self.rel_op_dict["LT"]:
                self.eat(2, self.rel_op_dict["LT"])
            elif self.current_token.lexeme_num == self.rel_op_dict["LE"]:
                self.eat(2, self.rel_op_dict["LE"])
            elif self.current_token.lexeme_num == self.rel_op_dict["GT"]:
                self.eat(2, self.rel_op_dict["GT"])
            elif self.current_token.lexeme_num == self.rel_op_dict["GE"]:
                self.eat(2, self.rel_op_dict["GE"])
            else:
                break
            self.sum()

    def sum(self):
        """
        <сумма> ::= <произведение> { (+ | - | or) <произведение>}
        """
        self.product()
        while self.current_token.table_num == 3:
            if self.current_token.lexeme_num == self.add_ops_dict["plus"]:
                self.eat(3, self.add_ops_dict["plus"])
            elif self.current_token.lexeme_num == self.add_ops_dict["min"]:
                self.eat(3, self.add_ops_dict["min"])
            elif self.current_token.lexeme_num == self.add_ops_dict["or"]:
                self.eat(3, self.add_ops_dict["or"])
            else:
                break
            self.product()

    def product(self):
        """
        <произведение> ::= <множитель> { (* | / | and) <множитель>}
        """
        self.multiplier()
        while self.current_token.table_num == 4:
            if self.current_token.lexeme_num == self.mul_ops_dict["mult"]:
                self.eat(4, self.mul_ops_dict["mult"])
            elif self.current_token.lexeme_num == self.mul_ops_dict["div"]:
                self.eat(4, self.mul_ops_dict["div"])
            elif self.current_token.lexeme_num == self.mul_ops_dict["and"]:
                self.eat(4, self.mul_ops_dict["and"])
            else:
                break
            self.multiplier()

    def multiplier(self):
        """
        <множитель> ::= <идентификатор> | <число> | <логическая_константа> | not <множитель> | «(»<выражение>«)»
        """
        if self.current_token.table_num == 8:
            id_token = self.current_token
            self.eat(8, self.current_token.lexeme_num)
            if not self.symbol_table.lookup(id_token.value):
                self.error(f"Variable '{id_token.value}' not declared")
        elif self.current_token.table_num == 7:
            self.number()
        elif self.current_token.table_num == 1 and (
            self.current_token.lexeme_num == self.keywords_dict["true"]
            or self.current_token.lexeme_num == self.keywords_dict["false"]
        ):
            self.logical_constant()
        elif (
            self.current_token.table_num == 5
            and self.current_token.lexeme_num == self.uops_dict["~"]
        ):
            self.eat(5, self.uops_dict["~"])
            self.multiplier()
        elif (
            self.current_token.table_num == 6
            and self.current_token.lexeme_num == self.delimiters_dict["("]
        ):
            self.eat(6, self.delimiters_dict["("])
            self.expression()
            self.eat(6, self.delimiters_dict[")"])
        else:
            self.error("Expected identifier, number, logical constant, 'not', or '('")

    def number(self):
        """
        <число> ::= <целое> | <действительное>
        """
        if self.current_token.table_num == 7:
            number_token = self.current_token
            number_value = number_token.value
            self.eat(7, self.current_token.lexeme_num)

            if (
                number_value.endswith("b")
                and number_value.startswith("0")
                and len(number_value) > 2
            ):
                self.error(f"Invalid binary number '{number_value}'", context="number")
            elif (
                number_value.endswith("o")
                and number_value.startswith("0")
                and len(number_value) > 2
            ):
                self.error(f"Invalid octal number '{number_value}'", context="number")
            elif (
                number_value.endswith("h")
                and number_value.startswith("0")
                and len(number_value) > 2
            ):
                self.error(
                    f"Invalid hexadecimal number '{number_value}'", context="number"
                )
            elif (
                number_value.endswith("d")
                and number_value.startswith("0")
                and len(number_value) > 2
            ):
                self.error(f"Invalid decimal number '{number_value}'", context="number")
            elif any(
                c not in "01" for c in number_value[:-1]
            ) and number_value.endswith("b"):
                self.error(f"Invalid binary number '{number_value}'", context="number")
            elif any(
                c not in "01234567" for c in number_value[:-1]
            ) and number_value.endswith("o"):
                self.error(f"Invalid octal number '{number_value}'", context="number")
            elif any(
                c not in "0123456789abcdefABCDEF" for c in number_value[:-1]
            ) and number_value.endswith("h"):
                self.error(
                    f"Invalid hexadecimal number '{number_value}'", context="number"
                )
            elif any(
                c not in "0123456789" for c in number_value[:-1]
            ) and number_value.endswith("d"):
                self.error(f"Invalid decimal number '{number_value}'", context="number")
            elif any(c not in "0123456789.eE+-" for c in number_value) and (
                "e" in number_value or "E" in number_value or "." in number_value
            ):
                self.error(f"Invalid float number '{number_value}'", context="number")
            elif (
                any(c not in "0123456789" for c in number_value)
                and not (
                    "e" in number_value or "E" in number_value or "." in number_value
                )
                and (number_value[-1] not in "bohd")
            ):
                self.error(f"Invalid decimal number '{number_value}'", context="number")
        else:
            self.error("Expected number")

    def logical_constant(self):
        """
        <логическая_константа> ::= true | false
        """
        if (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["true"]
        ):
            self.eat(1, self.keywords_dict["true"])
        elif (
            self.current_token.table_num == 1
            and self.current_token.lexeme_num == self.keywords_dict["false"]
        ):
            self.eat(1, self.keywords_dict["false"])
        else:
            self.error("Expected 'true' or 'false'")

    def parse(self):
        """Запуск синтаксического анализа."""
        self.program()
        if not (
            self.current_token.table_num == 0 and self.current_token.lexeme_num == 0
        ):
            self.error("Expected end of program")
