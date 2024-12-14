# Таблица служебных слов (n = 1)
keywords_table = {
    "PROGRAM": 1,
    "VAR": 2,
    "BEGIN": 3,
    "END": 4,
    "INTEGER": 5,
    "REAL": 6,
    "BOOLEAN": 7,
    "TRUE": 8,
    "FALSE": 9,
    "IF": 10,
    "THEN": 11,
    "ELSE": 12,
    "FOR": 13,
    "TO": 14,
    "DO": 15,
    "WHILE": 16,
    "READ": 17,
    "WRITE": 18,
    "AND": 19,
    "OR": 20,
    "MULT": 21,
    "DIV": 22,
    "PLUS": 23,
    "MIN": 24,
    "NE": 25,
    "EQ": 26,
    "LT": 27,
    "LE": 28,
    "GT": 29,
    "GE": 30,
    "AS": 31,
}

# Таблица ограничителей (n = 2)
delimiters_table = {
    ";": 1,
    ",": 2,
    ":": 3,
    "(": 4,
    ")": 5,
    "[": 6,
    "]": 7,
    ".": 8,
    "~": 9,
    "=": 10,
    "<": 11,
    ">": 12
}

numbers_table = {}
identifiers_table = {}

tables = {
    1: keywords_table,
    2: delimiters_table,
    3: numbers_table,
    4: identifiers_table
}


class Token:
    def __init__(self, table_num, lexeme_num, line, column, value=None):
        self.table_num = table_num  # n
        self.lexeme_num = lexeme_num  # k
        self.line = line
        self.column = column
        self.value = value  # Добавлено для хранения значения, если нужно

    def __str__(self):
        return f"({self.table_num}, {self.lexeme_num})"
