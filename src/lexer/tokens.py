from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str

KEYWORDS = {"program", "var", "begin", "end", "if", "then", "else",  "for",
            "to", "do", "while", "read", "write", "writeln", "integer", "real", "boolean"}
SYMBOL_OPERATORS = {"+", "-", "*", "/", "(", ")", "[", "]", ",", ";", ":", "."}
WORD_OPERATORS = {"as", "GT", "GE", "LT", "LE", "EQ", "NE", "and", "or", "not"}

KEYWORD_TOKENS = {kw: kw.upper() for kw in KEYWORDS}
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
WORD_OPERATOR_TOKENS = {op: op.upper() for op in WORD_OPERATORS}
