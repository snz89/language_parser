from parser.tokens import (
    Token,
    keywords_table,
    delimiters_table,
    numbers_table,
    identifiers_table,
)


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0  # Текущая позиция в тексте
        self.line = 1  # Текущая строка
        self.column = 1  # Текущий столбец
        self.current_char = self.text[self.pos] if self.pos < len(
            self.text) else None
        self.text_lines = text.splitlines()

    def error(self, message) -> Exception:
        """Вызывает исключение с сообщением об ошибке."""
        line = self.text_lines[self.line - 1]
        stript_line = line.strip()
        spaces = len(line) - len(line.lstrip())
        pointer_shift = self.column - spaces
        raise Exception(
            f"Syntax error at line {self.line}: {
                message}\n    {stript_line}\n    {'^':>{pointer_shift}}"
        )

    def advance(self) -> None:
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

    def skip_whitespace(self) -> None:
        """Пропустить пробелы и переносы строк."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self) -> None:
        """Пропустить многострочный комментарий."""
        while self.current_char is not None and self.current_char != "*":
            self.advance()
        if self.current_char == "*":
            self.advance()
            if self.current_char == "/":
                self.advance()
            else:
                self.error("Unterminated multiline comment")
        else:
            self.error("Unterminated multiline comment")

    def number(self) -> Token:
        """Считать число."""
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == ".":
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        if self.current_char is not None and (self.current_char in "eE"):
            result += self.current_char
            self.advance()
            if self.current_char is not None and (self.current_char in "+-"):
                result += self.current_char
                self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        if self.current_char is not None and (self.current_char.lower() in "bhdo"):
            result += self.current_char
            self.advance()

        # Если после числа идет буква, то это идентификатор
        if self.current_char is not None and self.current_char.isalpha():
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isalnum():
                result += self.current_char
                self.advance()
            if result not in identifiers_table:
                identifiers_table[result] = len(identifiers_table) + 1
            return Token(4, identifiers_table[result], self.line, self.column - len(result), value=result)

        if result not in numbers_table:
            numbers_table[result] = len(numbers_table) + 1

        return Token(3, numbers_table[result], self.line, self.column - len(result), value=result)

    def _id(self) -> Token:
        """Считать идентификатор или ключевое слово."""
        result = ""
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        # Проверяем, является ли строка ключевым словом
        if result.upper() in keywords_table:
            return Token(1, keywords_table[result.upper()], self.line, self.column - len(result), value=result)
        else:
            if result not in identifiers_table:
                identifiers_table[result] = len(identifiers_table) + 1
            return Token(4, identifiers_table[result], self.line, self.column - len(result), value=result)

    def get_next_token(self) -> Token:
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

            # Проверяем ограничители
            for delim, delim_num in delimiters_table.items():
                if self.current_char == delim[0]:
                    if len(delim) > 1:
                        if self.peek() == delim[1]:
                            self.advance()
                            self.advance()
                            return Token(2, delim_num, self.line, self.column - 2, value=delim)
                    else:
                        self.advance()
                        return Token(2, delim_num, self.line, self.column - 1, value=delim)

            # Если ничего не подошло, возвращаем токен ошибки
            token = Token(0, 0, self.line, self.column,
                          value=self.current_char)
            self.advance()
            return token

        return Token(0, 0, self.line, self.column)  # Конец текста

    def peek(self):
        """Подсмотреть следующий символ, не сдвигаясь."""
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        else:
            return None
