from .lexer.lexer import tokenize_file


def main():
    filepath = 'example.txt'
    try:
        file = open(filepath, 'r')
    except FileNotFoundError:
        print("File not found")
        exit(1)

    tokens = tokenize_file(file)

    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
