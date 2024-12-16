from .lexer import Lexer
from .parser import Parser


def main():
    path = "example.txt"
    with open(path, "r", encoding="UTF-8") as file:
        text = file.read()

    try:
        lexer = Lexer(text)
        parser = Parser(lexer)
        parser.parse()
        print("yep")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
