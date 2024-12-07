from parser.lexer.tokens import (
    Token,
    TokenType
)

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
        if self.current_char == '\n':
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
        while self.current_char is not None and self.current_char != '*':
            self.advance()
        if self.current_char == '*':
            self.advance()
            if self.current_char == '/':
                self.advance()

    def number(self):
        """Считать число (целое или вещественное)."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        current_type = TokenType.DEC

        if self.current_char == '.':
            current_type = TokenType.NUM_REAL
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        if self.current_char is not None and (self.current_char in 'eE'):
            current_type = TokenType.NUM_REAL
            result += self.current_char
            self.advance()
            if self.current_char is not None and (self.current_char in '+-'):
                result += self.current_char
                self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        if current_type == TokenType.NUM_REAL:
            if self.current_char is not None and (self.current_char in 'eE'):
                return Token(TokenType.NULL, result, self.line, self.column)
            if self.current_char is not None and (self.current_char.lower() in 'bhdo'):
                return Token(TokenType.NULL, result, self.line, self.column)
            return Token(TokenType.NUM_REAL, result, self.line, self.column)

        while self.current_char is not None and self.current_char.isalnum():
            if self.current_char is not None and (self.current_char.lower() == 'b'):
                current_type = TokenType.BIN
            elif self.current_char is not None and (self.current_char.lower() == 'o'):
                current_type = TokenType.OCT
            elif self.current_char is not None and (self.current_char.lower() == 'h'):
                current_type = TokenType.HEX
            elif self.current_char is not None and (self.current_char.lower() == 'd'):
                current_type = TokenType.DEC
            elif self.current_char is not None and self.current_char.isdigit():
                if current_type != TokenType.HEX:
                    return Token(TokenType.NULL, result, self.line, self.column)
            elif self.current_char is not None and self.current_char.isalpha():
                if current_type != TokenType.HEX or self.current_char.lower() not in 'abcdef':
                    return Token(TokenType.NULL, result, self.line, self.column)
            result += self.current_char
            self.advance()

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
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        token_type = TokenType.ID  # По умолчанию считаем, что это идентификатор
        # Проверяем, не является ли строка ключевым словом
        if result.upper() == 'PROGRAM':
            token_type = TokenType.PROGRAM
        elif result.upper() == 'VAR':
            token_type = TokenType.VAR
        elif result.upper() == 'BEGIN':
            token_type = TokenType.BEGIN
        elif result.upper() == 'END':
            token_type = TokenType.END
        elif result.upper() == 'INTEGER':
            token_type = TokenType.INTEGER
        elif result.upper() == 'REAL':
            token_type = TokenType.REAL
        elif result.upper() == 'BOOLEAN':
            token_type = TokenType.BOOLEAN
        elif result.upper() == 'TRUE':
            token_type = TokenType.TRUE
        elif result.upper() == 'FALSE':
            token_type = TokenType.FALSE
        elif result.upper() == 'IF':
            token_type = TokenType.IF
        elif result.upper() == 'THEN':
            token_type = TokenType.THEN
        elif result.upper() == 'ELSE':
            token_type = TokenType.ELSE
        elif result.upper() == 'FOR':
            token_type = TokenType.FOR
        elif result.upper() == 'TO':
            token_type = TokenType.TO
        elif result.upper() == 'DO':
            token_type = TokenType.DO
        elif result.upper() == 'WHILE':
            token_type = TokenType.WHILE
        elif result.upper() == 'READ':
            token_type = TokenType.READ
        elif result.upper() == 'WRITE':
            token_type = TokenType.WRITE
        elif result.upper() == 'AND':
            token_type = TokenType.AND
        elif result.upper() == 'OR':
            token_type = TokenType.OR
        elif result.upper() == 'MULT':
            token_type = TokenType.MULT
        elif result.upper() == 'DIV':
            token_type = TokenType.DIV
        elif result.upper() == 'PLUS':
            token_type = TokenType.PLUS
        elif result.upper() == 'MIN':
            token_type = TokenType.MIN
        elif result.upper() == 'NE':
            token_type = TokenType.NE
        elif result.upper() == 'EQ':
            token_type = TokenType.EQ
        elif result.upper() == 'LT':
            token_type = TokenType.LT
        elif result.upper() == 'LE':
            token_type = TokenType.LE
        elif result.upper() == 'GT':
            token_type = TokenType.GT
        elif result.upper() == 'GE':
            token_type = TokenType.GE
        elif result.upper() == 'AS':
            token_type = TokenType.AS
        elif result.upper() == 'B' and len(result) == 1:
            token_type = TokenType.BIN_END
        elif result.upper() == 'O' and len(result) == 1:
            token_type = TokenType.OCT_END
        elif result.upper() == 'D' and len(result) == 1:
            token_type = TokenType.DEC_END
        elif result.upper() == 'H' and len(result) == 1:
            token_type = TokenType.HEX_END
        elif result.upper() == 'E' and len(result) == 1:
            token_type = TokenType.EXP

        return Token(token_type, result, self.line, self.column)

    def get_next_token(self):
        """Получить следующий токен из текста."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and self.peek() == '*':
                self.advance()
                self.advance()
                self.skip_comment()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', self.line, self.column)

            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', self.line, self.column)

            if self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON, ':', self.line, self.column)

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line, self.column)

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line, self.column)

            if self.current_char == '[':
                self.advance()
                return Token(TokenType.LBRACKET, '[', self.line, self.column)

            if self.current_char == ']':
                self.advance()
                return Token(TokenType.RBRACKET, ']', self.line, self.column)

            if self.current_char == '.':
                self.advance()
                return Token(TokenType.DOT, '.', self.line, self.column)

            if self.current_char == '~':
                self.advance()
                return Token(TokenType.TILDE, '~', self.line, self.column)

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


text = """
program test; 
var x, y : integer;
begin
    x as 10;
    y as 20;
    /* 
    Это многострочный
    комментарий
    */
    write(x plus y)
end.
"""

with open('example.txt', 'r') as file:
    text = file.read()