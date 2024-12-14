from parser.lexer import Lexer
from parser.parser import Parser


def print_tokens(text):
    lexer = Lexer(text)
    token = lexer.get_next_token()
    while token.table_num != 0:
        print(f"{token}\t--> '{token.value}'")
        token = lexer.get_next_token()


def main():
    path = "example.txt"
    with open(path, "r", encoding="UTF-8") as file:
        text = file.read()

    try:
        lexer = Lexer(text)
        parser = Parser(lexer, text)
        parser.parse()
        print("Yeah!")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
