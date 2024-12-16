class Token:
    def __init__(self, table_num, lexeme_num, line, column, value=None):
        self.table_num = table_num  # n
        self.lexeme_num = lexeme_num  # k
        self.line = line
        self.column = column
        self.value = value

    def __str__(self):
        return f"'{self.value}': ({self.table_num}, {self.lexeme_num})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        self.tokens = []
        self.text_lines = self.text.split("\n")

        # Таблица служебных слов (n = 1)
        self.keywords_table = [
            "program",
            "var",
            "begin",
            "end",
            "if",
            "else",
            "while",
            "for",
            "to",
            "then",
            "do",
            "read",
            "write",
            "true",
            "false",
            "integer",
            "real",
            "boolean",
            "as",
        ]

        # Таблица операторов отношений (n = 2)
        self.rel_op_table = ["NE", "EQ", "LT", "LE", "GT", "GE"]

        # Таблица операций сложения (n = 3)
        self.add_ops_table = ["plus", "min", "or"]

        # Таблица операций умножения (n = 4)
        self.mul_ops_table = ["mult", "div", "and"]

        # Таблица унарных операций (n = 5)
        self.uops_table = ["~"]

        # Таблица разделителей (n = 6)
        self.delimiters_table = ["[", "]", "(", ")", ",", ":", ";", ".", "=", "<", ">"]

        # Таблица для чисел (n = 7)
        self.numbers_table = []

        # Таблица для идентификаторов (n = 8)
        self.identifiers_table = []

    def advance(self):
        """Переход к следующему символу."""
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

    def add_token(self, n, k, value=None):
        """Добавление токена в список токенов."""
        self.tokens.append(
            Token(n, k, self.line, self.column - (len(value) if value else 0), value)
        )

    def skip_whitespace(self):
        """Пропуск пробельных символов."""
        while self.current_char and self.current_char.isspace():
            self.advance()

    def parse_identifier_or_keyword(self):
        """Разбор идентификаторов и ключевых слов."""
        start = self.pos
        while self.current_char and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            self.advance()
        text = self.text[start : self.pos]

        # Проверяем, является ли текст служебным словом
        if text.lower() in self.keywords_table:
            self.add_token(1, self.keywords_table.index(text.lower()) + 1, value=text)
        # Проверяем, является ли текст оператором отношений
        elif text.upper() in self.rel_op_table:
            self.add_token(2, self.rel_op_table.index(text.upper()) + 1, value=text)
        # Проверяем, является ли текст операцией сложения
        elif text.lower() in self.add_ops_table:
            self.add_token(3, self.add_ops_table.index(text.lower()) + 1, value=text)
        # Проверяем, является ли текст операцией умножения
        elif text.lower() in self.mul_ops_table:
            self.add_token(4, self.mul_ops_table.index(text.lower()) + 1, value=text)
        else:
            # Иначе считаем текст идентификатором
            if text not in self.identifiers_table:
                self.identifiers_table.append(text)
            self.add_token(8, self.identifiers_table.index(text) + 1, value=text)

    def parse_number(self):
        """Разбор числовых литералов, включая поддержку суффиксов."""
        text = ""
        has_decimal_point = False
        is_float = False

        while self.current_char and (self.current_char.isdigit() or self.current_char.upper() in 'ABCDEF' or self.current_char == '.'):
            if self.current_char == '.':
                if has_decimal_point:
                    # Две десятичные точки - считаем за идентификатор
                    is_float = False
                    break
                has_decimal_point = True
                is_float = True
            text += self.current_char
            self.advance()

        if self.current_char and self.current_char.upper() == 'E':
            is_float = True
            text += self.current_char
            self.advance()
            if self.current_char in '+-':
                text += self.current_char
                self.advance()
            if self.current_char and self.current_char.isdigit():
                while self.current_char and self.current_char.isdigit():
                    text += self.current_char
                    self.advance()
            else:
                is_float = False

        suffix = ""
        if self.current_char and self.current_char.lower() in 'bohd':
            suffix = self.current_char.lower()
            text += self.current_char
            self.advance()

        # Если после числа идет буква, и это не суффикс системы счисления, то это идентификатор
        if self.current_char is not None and self.current_char.isalpha() and len(suffix) != 1:
            while self.current_char is not None and self.current_char.isalnum():
                text += self.current_char
                self.advance()
            if text not in self.identifiers_table:
                self.identifiers_table.append(text)
            self.add_token(8, self.identifiers_table.index(text) + 1, value=text)
            return
        
        if text not in self.numbers_table:
            self.numbers_table.append(text)
        self.add_token(7, self.numbers_table.index(text) + 1, value=text)

    def parse_comment(self):
        """Разбор комментариев вида /* ... */."""
        self.advance()  # Пропускаем '/'
        self.advance()  # Пропускаем '*'
        while self.current_char:
            if self.current_char == "*":
                self.advance()
                if self.current_char == "/":
                    self.advance()
                    return
                else:
                    raise Exception(
                        f"Syntax error at line {self.line}: An incomplete multi-line comment\n    {self.text_lines[self.line - 1].strip()}"
                    )
            else:
                self.advance()

    def parse_delimiter_or_operator(self):
        """Разбор разделителей и операторов."""
        char = self.current_char
        self.advance()
        text = char

        # Проверка на многосимвольные операторы
        if char == "<" and self.current_char == "=":
            text += self.current_char
            self.advance()
        elif char == ">" and self.current_char == "=":
            text += self.current_char
            self.advance()
        elif char == "a" and self.current_char == "s":
            text += self.current_char
            self.advance()

        # Определение типа токена
        if text.upper() in self.rel_op_table:
            self.add_token(2, self.rel_op_table.index(text.upper()) + 1, value=text)
        elif text.lower() in self.add_ops_table:
            self.add_token(3, self.add_ops_table.index(text.lower()) + 1, value=text)
        elif text.lower() in self.mul_ops_table:
            self.add_token(4, self.mul_ops_table.index(text.lower()) + 1, value=text)
        elif text in self.uops_table:
            self.add_token(5, self.uops_table.index(text) + 1, value=text)
        elif text in self.delimiters_table:
            self.add_token(6, self.delimiters_table.index(text) + 1, value=text)
        else:
            self.add_token(0, 0, value=text)  # Неизвестный токен

    def tokenize(self):
        """Основной метод лексического анализа."""
        while self.current_char:
            self.skip_whitespace()
            if not self.current_char:
                break

            if self.current_char == "/" and self.peek() == "*":
                self.parse_comment()
            elif self.current_char.isalpha() or self.current_char == "_":
                self.parse_identifier_or_keyword()
            elif self.current_char.isdigit():
                self.parse_number()
            elif self.current_char in self.delimiters_table or self.current_char in [
                "<",
                ">",
                ":",
                "!",
                "=",
                "~",
                "+",
                "-",
                "*",
                "/",
                "a",
            ]:
                self.parse_delimiter_or_operator()
            else:
                # Неизвестный символ, можно обработать как ошибку или пропустить
                self.add_token(0, 0, value=self.current_char)
                self.advance()

        self.add_token(0, 0, value="EOF")  # Добавляем токен конца файла
        return self.tokens

    def peek(self):
        """Вспомогательный метод для просмотра следующего символа без его извлечения."""
        if self.pos + 1 < len(self.text):
            return self.text[self.pos + 1]
        else:
            return None
