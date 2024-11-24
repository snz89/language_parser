KEYWORDS = {"program", "var", "begin", "end", "if", "then", "else",  "for",
            "to", "do", "while", "read", "write", "writeln", "integer", "real", "boolean"}
SYMBOL_OPERATORS = {"+", "-", "*", "/", "(", ")", "[", "]", ",", ";", ":", "."}
WORD_OPERATORS = {"as", "GT", "GE", "LT", "LE", "EQ", "NE", "and", "or", "not"}

KEYWORD_TOKENS = {
    "program": "PROGRAM",
    "var": "VAR",
    "begin": "BEGIN",
    "end": "END",
    "if": "IF",
    "then": "THEN",
    "else": "ELSE",
    "for": "FOR",
    "to": "TO",
    "do": "DO",
    "while": "WHILE",
    "read": "READ",
    "write": "WRITE",
    "writeln": "WRITELN",
    "integer": "INTEGER",
    "real": "REAL",
    "boolean": "BOOLEAN"
}

SYMBOL_OPERATOR_TOKENS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MULTIPLY",
    "/": "DIVIDE",
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ",": "COMMA",
    ";": "SEMICOLON",
    ":": "COLON",
    ".": "DOT",
}

WORD_OPERATOR_TOKENS = {
    "as": "AS",
    "GT": "GT",
    "GE": "GE",
    "LT": "LT",
    "LE": "LE",
    "EQ": "EQ",
    "NE": "NE",
    "and": "AND",
    "or": "OR",
    "not": "NOT"
}
