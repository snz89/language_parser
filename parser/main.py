from lexer import Lexer
from parser import Parser

def main():
    path = "example.txt"
    with open(path, "r") as file:
        text = file.read()
    lexer = Lexer(text)
    parser = Parser(lexer)

    id_table = parser.id_table
    for id in id_table:
        print(id)


if __name__ == "__main__":
    main()
