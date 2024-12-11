from typing import Any, List

from lexer import Lexer
from tokens import TokenType, Id


class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value: Any) -> None:
        """Добавляет элемент в стек."""
        self.stack.append(value)

    def pop(self) -> Any:
        """Удаляет элемент с вершины стека и возвращает его."""
        if len(self.stack) == 0:
            return None
        removed = self.stack.pop()
        return removed

    def peek(self) -> Any:
        """Возвращает элемент с вершины стека, не удаляя его."""
        length = len(self.stack)
        return self.stack[length - 1]

    def clear(self) -> None:
        self.stack.clear()

    def __len__(self) -> int:
        return len(self.stack)

    def __str__(self) -> str:
        return str(self.stack)


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = None
        self.stack = Stack()  # Для контроля за объявлением идентификаторов
        self.id_table = self.lexer.get_id_table()

    def get_token(self):
        self.current_token = self.lexer.get_next_token()

    def reset(self):
        self.stack.clear()
