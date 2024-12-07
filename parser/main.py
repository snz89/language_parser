from parser.lexer.lexer import Lexer
from parser.lexer.tokens import TokenType

def main():
    path = "example.txt"
    with open(path, 'r') as file:
        text = file.read()
    lexer = Lexer(text)
    token = lexer.get_next_token()
    while token.type != TokenType.FIN:
        print(token)
        token = lexer.get_next_token()


if __name__ == "__main__":
    main()
