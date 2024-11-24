from typing import List, Any


def flatten_list(lst: List) -> List:
    """
    Рекурсивно "выпрямляет" вложенный список, возвращая одноуровневый список.

    Если элемент списка является вложенным списком, функция вызывает 
    себя рекурсивно для обработки вложенных элементов. Все элементы 
    объединяются в один плоский список.
    """
    return [item
            for sublist in lst
            for item in (flatten_list(sublist)
                         if isinstance(sublist, list)
                         else [sublist])]


def print_few_lists(*lists: List[Any]) -> None:
    """
    Печатает несколько листов, где элементы на
    одинаковых индексах соотвествуют друг другу.
    """
    list_count = len(lists)
    min_len = min(len(lst) for lst in lists)
    for i in range(min_len):
        for j in range(list_count):
            print(f'{lists[j][i]}\t', end='')
        print('')
