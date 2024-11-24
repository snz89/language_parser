from io import TextIOWrapper
from typing import List

from .tokens import *
from ..utils.utils import flatten_list


def split_lexems_with_operators(input: str) -> List[str]:
    """
    Разбивает строку на токены, учитывая символы-операторы,
    которые могут быть написаны слитно с идентификаторами.
    """
    return ''.join(f' {c} '
                   if c in SYMBOL_OPERATORS
                   else c for c in input).split()


def classify_token(raw_token: str) -> str:
    """
    Преобразует лексему в токен в зависимости от её содержания.

    Функция проверяет, является ли входная строка ключевым словом, оператором,
    числом или идентификатором. В зависимости от типа токен возвращается 
    соответствующее значение:
    """
    if raw_token.lower() in KEYWORDS:
        return KEYWORD_TOKENS[raw_token.lower()]
    if raw_token in WORD_OPERATORS:
        return WORD_OPERATOR_TOKENS[raw_token]
    if raw_token in SYMBOL_OPERATORS:
        return SYMBOL_OPERATOR_TOKENS[raw_token]
    if raw_token.isdigit():
        return 'NUMBER'
    if raw_token.isalpha():
        return 'IDENTIFIER'
    return 'UNKNOWN'


# TODO: Объединить эту функцию с lexems_to_tokens в tokenize_file
def split_file_to_lexems(file: TextIOWrapper) -> List[str]:
    """
    Разбивает файл на токены, учитывая символы-операторы,
    которые могут быть написаны слитно с идентификаторами.
    """
    lines = [line.strip() for line in file]
    lexems = flatten_list(
        split_lexems_with_operators(word)
        for line in lines
        for word in line.split()
    )
    return lexems


def lexems_to_tokens(lexems: List[str]) -> List[str]:
    return [classify_token(raw_token) for raw_token in lexems]
