from .lexer.lexer import (
    split_file_to_lexems,
    lexems_to_tokens
)
from .utils.utils import print_few_lists


def main():
    filepath = 'example.txt'
    try:
        file = open(filepath, 'r')
    except FileNotFoundError:
        print("File not found")
        exit(1)

    raw_tokens = split_file_to_lexems(file)
    tokens = lexems_to_tokens(raw_tokens)

    print_few_lists(raw_tokens, tokens)


if __name__ == "__main__":
    main()
