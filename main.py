from enum import Enum
from dataclasses import dataclass


class TokenType(Enum):
    NULL = 0  # Пустой тип

    # КЛЮЧЕВЫЕ СЛОВА
    PROGRAM = 1  # Начало программы
    VAR = 2  # Объявление переменных
    BEGIN = 3  # Начало блока операторов
    END = 4  # Конец блока операторов
    INTEGER = 5  # Целочисленный тип данных
    REAL = 6  # Вещественный тип данных
    BOOLEAN = 7  # Булевский тип данных
    TRUE = 8  # Логическое значение "истина"
    FALSE = 9  # Логическое значение "ложь"
    IF = 10  # Условный оператор
    THEN = 11  # Ветвь then условного оператора
    ELSE = 12  # Ветвь else условного оператора
    FOR = 13  # Цикл for (с фиксированным числом повторений)
    TO = 14  # Ключевое слово to в цикле for
    DO = 15  # Ключевое слово do в циклах for и while
    WHILE = 16  # Цикл while
    READ = 17  # Оператор ввода
    WRITE = 18  # Оператор вывода

    # ОПЕРАТОРЫ
    AND = 19  # Логическое И (в группе умножения)
    OR = 20  # Логическое ИЛИ (в группе сложения)
    NOT = 21  # '~' логическое отрицание
    MULT = 22  # Умножение (в группе умножения)
    DIV = 23  # Деление (в группе умножения)
    PLUS = 24  # Сложение (в группе сложения)
    MIN = 25  # Вычитание (в группе сложения)
    NE = 26  # Не равно (в группе отношения)
    EQ = 27  # Равно (в группе отношения)
    LT = 28  # Меньше (в группе отношения)
    LE = 29  # Меньше или равно (в группе отношения)
    GT = 30  # Больше (в группе отношения)
    GE = 31  # Больше или равно (в группе отношения)

    # РАЗДЕЛИТЕЛИ
    SEMICOLON = 32  # Точка с запятой (;)
    COMMA = 33  # Запятая (,)
    COLON = 34  # Двоеточие (:)
    AS = 35  # Оператор присваивания (as)
    LPAREN = 36  # Открывающая круглая скобка (()
    RPAREN = 37  # Закрывающая круглая скобка ())
    LBRACKET = 38  # Открывающая квадратная скобка ([)
    RBRACKET = 39  # Закрывающая квадратная скобка (])
    DOT = 40  # Точка (.)
    TILDE = 41  # Тильда (~) - унарная операция

    # ЧИСЛОВЫЕ КОНСТАНТЫ
    BIN = 42  # Двоичное число
    OCT = 43  # Восьмеричное число
    DEC = 44  # Десятичное число
    HEX = 45  # Шестнадцатеричное число
    NUM_REAL = 46  # Вещественное число

    # ИДЕНТИФИКАТОР
    ID = 47  # Идентификатор (переменная)

    # МАРКЕР КОНЦА ТЕКСТА ПРОГРАММЫ
    FIN = 48  # Конец файла


@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"({self.type}, '{self.value}', {self.line}, {self.column})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0  # Текущая позиция в тексте
        self.line = 1  # Текущая строка
        self.column = 1  # Текущий столбец
        self.current_char = self.text[self.pos] if self.pos < len(
            self.text) else None

    def advance(self):
        """Перейти к следующему символу."""
        if self.current_char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def skip_whitespace(self):
        """Пропустить пробелы и переносы строк."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """Пропустить многострочный комментарий."""
        while self.current_char is not None and self.current_char != "*":
            self.advance()
        if self.current_char == "*":
            self.advance()
            if self.current_char == "/":
                self.advance()
            else:
                print(
                    f"SyntaxError: unterminated multiline comment (detected at line {self.line})")
                exit(1)
        else:
            print(
                f"SyntaxError: unterminated multiline comment (detected at line {self.line})")
            exit(1)

    def number(self):
        """Считать число (целое или вещественное)."""
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        current_type = TokenType.DEC

        if self.current_char == ".":
            current_type = TokenType.NUM_REAL
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        if self.current_char is not None and (self.current_char in "eE"):
            current_type = TokenType.NUM_REAL
            result += self.current_char
            self.advance()
            if self.current_char is not None and (self.current_char in "+-"):
                result += self.current_char
                self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        if current_type == TokenType.NUM_REAL:
            if self.current_char is not None and (self.current_char in "eE"):
                return Token(TokenType.NULL, result, self.line, self.column)
            if self.current_char is not None and (self.current_char.lower() in "bhdo"):
                return Token(TokenType.NULL, result, self.line, self.column)
            return Token(TokenType.NUM_REAL, result, self.line, self.column)

        # Проверяем окончание числа, только если result содержит цифры
        if len(result) > 0 and result[-1].isdigit() and self.current_char is not None:
            if self.current_char is not None and (self.current_char.lower() == "b"):
                current_type = TokenType.BIN
            elif self.current_char is not None and (self.current_char.lower() == "o"):
                current_type = TokenType.OCT
            elif self.current_char is not None and (self.current_char.lower() == "h"):
                current_type = TokenType.HEX
            elif self.current_char is not None and (self.current_char.lower() == "d"):
                current_type = TokenType.DEC
            if current_type != TokenType.DEC:
                result += self.current_char
                self.advance()

        # Если после числа идет буква, то это идентификатор
        if current_type == TokenType.DEC and self.current_char is not None and self.current_char.isalpha():
            while self.current_char is not None and self.current_char.isalnum():
                result += self.current_char
                self.advance()
            return Token(TokenType.ID, result, self.line, self.column)

        if current_type == TokenType.DEC:
            return Token(TokenType.DEC, result, self.line, self.column)
        if current_type == TokenType.HEX:
            return Token(TokenType.HEX, result, self.line, self.column)
        if current_type == TokenType.OCT:
            return Token(TokenType.OCT, result, self.line, self.column)
        if current_type == TokenType.BIN:
            return Token(TokenType.BIN, result, self.line, self.column)

    def _id(self):
        """Считать идентификатор или ключевое слово."""
        result = ""
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        token_type = TokenType.ID  # По умолчанию считаем, что это идентификатор
        # Проверяем, не является ли строка ключевым словом
        if result.upper() == "PROGRAM":
            token_type = TokenType.PROGRAM
        elif result.upper() == "VAR":
            token_type = TokenType.VAR
        elif result.upper() == "BEGIN":
            token_type = TokenType.BEGIN
        elif result.upper() == "END":
            token_type = TokenType.END
        elif result.upper() == "INTEGER":
            token_type = TokenType.INTEGER
        elif result.upper() == "REAL":
            token_type = TokenType.REAL
        elif result.upper() == "BOOLEAN":
            token_type = TokenType.BOOLEAN
        elif result.upper() == "TRUE":
            token_type = TokenType.TRUE
        elif result.upper() == "FALSE":
            token_type = TokenType.FALSE
        elif result.upper() == "IF":
            token_type = TokenType.IF
        elif result.upper() == "THEN":
            token_type = TokenType.THEN
        elif result.upper() == "ELSE":
            token_type = TokenType.ELSE
        elif result.upper() == "FOR":
            token_type = TokenType.FOR
        elif result.upper() == "TO":
            token_type = TokenType.TO
        elif result.upper() == "DO":
            token_type = TokenType.DO
        elif result.upper() == "WHILE":
            token_type = TokenType.WHILE
        elif result.upper() == "READ":
            token_type = TokenType.READ
        elif result.upper() == "WRITE":
            token_type = TokenType.WRITE
        elif result.upper() == "AND":
            token_type = TokenType.AND
        elif result.upper() == "OR":
            token_type = TokenType.OR
        elif result.upper() == "MULT":
            token_type = TokenType.MULT
        elif result.upper() == "DIV":
            token_type = TokenType.DIV
        elif result.upper() == "PLUS":
            token_type = TokenType.PLUS
        elif result.upper() == "MIN":
            token_type = TokenType.MIN
        elif result.upper() == "NE":
            token_type = TokenType.NE
        elif result.upper() == "EQ":
            token_type = TokenType.EQ
        elif result.upper() == "LT":
            token_type = TokenType.LT
        elif result.upper() == "LE":
            token_type = TokenType.LE
        elif result.upper() == "GT":
            token_type = TokenType.GT
        elif result.upper() == "GE":
            token_type = TokenType.GE
        elif result.upper() == "AS":
            token_type = TokenType.AS

        return Token(token_type, result, self.line, self.column)

    def get_next_token(self):
        """Получить следующий токен из текста."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == "/" and self.peek() == "*":
                self.advance()
                self.advance()
                self.skip_comment()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == ";":
                self.advance()
                return Token(TokenType.SEMICOLON, ";", self.line, self.column)

            if self.current_char == ",":
                self.advance()
                return Token(TokenType.COMMA, ",", self.line, self.column)

            if self.current_char == ":":
                self.advance()
                return Token(TokenType.COLON, ":", self.line, self.column)

            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN, "(", self.line, self.column)

            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN, ")", self.line, self.column)

            if self.current_char == "[":
                self.advance()
                return Token(TokenType.LBRACKET, "[", self.line, self.column)

            if self.current_char == "]":
                self.advance()
                return Token(TokenType.RBRACKET, "]", self.line, self.column)

            if self.current_char == ".":
                self.advance()
                return Token(TokenType.DOT, ".", self.line, self.column)

            if self.current_char == "~":
                self.advance()
                return Token(TokenType.TILDE, "~", self.line, self.column)

            # Если ничего не подошло, возвращаем токен ошибки
            token = Token(TokenType.NULL, self.current_char,
                          self.line, self.column)
            self.advance()
            return token

        # Конец текста
        return Token(TokenType.FIN, None, self.line, self.column)

    def peek(self):
        """Подсмотреть следующий символ, не сдвигаясь."""
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        else:
            return None

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
            f"Syntax error at line {self.current_token.line}, column {self.current_token.column}: {message}"
        )

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type.name}, found {self.current_token.type.name}")

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
            self.error(f"expected ';' or 'END', found '{self.current_token.type.name}'", context="operator_list")

    def description(self):
        """
        <описание> ::= {<идентификатор> {, <идентификатор>} : <тип> ;}
        """
        while self.current_token.type == TokenType.ID:
            if not self.current_token.value[0].isalpha():
                self.error(message=f"Invalid ID name: '{self.current_token.value}'")
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

def main():
    path = "example.txt"  # Путь к файлу с кодом
    with open(path, "r") as file:
        text = file.read()

    lexer = Lexer(text)

    # token = lexer.get_next_token()
    # while token.type != TokenType.FIN:
    #     print(token)
    #     token = lexer.get_next_token()

    parser = Parser(lexer)

    try:
        parser.parse()
        print("Yes")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
