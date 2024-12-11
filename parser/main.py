from parser.lexer import Lexer
from parser.parser import Parser

def main():
    path = "example.txt"  # Путь к файлу с кодом
    with open(path, "r") as file:
        text = file.read()

    lexer = Lexer(text)
    parser = Parser(lexer)

    try:
        parser.parse()
        print("Yeah!")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
