from io import TextIOWrapper
from typing import List

from .tokens import *


def split_lexems_with_operators(input: str) -> List[str]:
    """
    Разбивает строку на токены, учитывая символы-операторы,
    которые могут быть написаны слитно с идентификаторами.
    """
    lexems = []
    i = 0
    while i < len(input):
        char = input[i]

        if char.isspace():
            i += 1
            continue

        if char.isdigit() or (char == '.' and i + 1 < len(input) and input[i + 1].isdigit()):
            num = char
            i += 1
            while i < len(input) and (input[i].isdigit() or input[i] == '.'):
                num += input[i]
                i += 1
            lexems.append(num)
            continue

        if char.isalpha():
            word = char
            i += 1
            while i < len(input) and (input[i].isalnum() or input[i] == '_'):
                word += input[i]
                i += 1
            lexems.append(word)
            continue

        if char in SYMBOL_OPERATORS:
            lexems.append(char)
            i += 1
            continue

        raise RuntimeError(f'Unexpected character: {char}')

    return lexems


def classify_token(raw_token: str) -> Token:
    """
    Преобразует лексему в токен в зависимости от её содержания.

    Функция проверяет, является ли входная строка ключевым словом, оператором,
    числом или идентификатором. В зависимости от типа токен возвращается 
    соответствующее значение:
    """
    if raw_token.lower() in KEYWORDS:
        return Token(KEYWORD_TOKENS[raw_token.lower()], raw_token)
    if raw_token in WORD_OPERATORS:
        return Token(WORD_OPERATOR_TOKENS[raw_token], raw_token)
    if raw_token in SYMBOL_OPERATORS:
        return Token(SYMBOL_OPERATOR_TOKENS[raw_token], raw_token)
    if raw_token.replace('.', '', 1).isdigit():
        return Token('NUMBER', raw_token)
    if raw_token.isalpha():
        return Token('IDENTIFIER', raw_token)
    return Token('UNKNOWN', raw_token)


def tokenize_file(file: TextIOWrapper) -> List[Token]:
    """
    Разбивает файл на токены, учитывая символы-операторы,
    которые могут быть написаны слитно с идентификаторами.
    """
    tokens = []
    for line in file:
        line = line.split('//')[0].strip()  # Удаление комментариев
        lexems = split_lexems_with_operators(line)
        tokens.extend(classify_token(lexem) for lexem in lexems)
    return tokens
