# core/pathfinding.py

import heapq
from data.configs.game import UP, DOWN, LEFT, RIGHT

class Node:
    """Узел для алгоритма A*. Представляет собой одну клетку сетки."""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position  # (row, col)

        self.g = 0  # Расстояние от начального узла
        self.h = 0  # Эвристическое расстояние до конечного узла
        self.f = 0  # Общая стоимость (g + h)

    def __eq__(self, other):
        return self.position == other.position

    # Для использования в приоритетной очереди (heapq)
    def __lt__(self, other):
        return self.f < other.f


def find_path(grid, start, end):
    """
    Алгоритм поиска пути A*.
    Возвращает список кортежей (row, col), представляющих путь.
    """
    start_node = Node(None, start)
    end_node = Node(None, end)

    open_list = []
    closed_list = set()

    # heapq - это приоритетная очередь, которая позволит быстро получать узел с наименьшим f
    heapq.heappush(open_list, start_node)

    while len(open_list) > 0:
        current_node = heapq.heappop(open_list)
        closed_list.add(current_node.position)

        # Путь найден
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Возвращаем перевернутый путь

        # Генерируем дочерние узлы (соседей)
        for new_position in [UP, DOWN, LEFT, RIGHT]:  # Соседи по горизонтали и вертикали
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Проверяем, что узел в пределах сетки
            if not (0 <= node_position[0] < len(grid) and 0 <= node_position[1] < len(grid[0])):
                continue

            # Проверяем, что узел "проходим" (не препятствие)
            if grid[node_position[0]][node_position[1]] != 0:
                continue

            # Проверяем, не находится ли узел уже в рассмотренных
            if node_position in closed_list:
                continue

            child = Node(current_node, node_position)

            child.g = current_node.g + 1
            # Эвристика: Манхэттенское расстояние
            child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])
            child.f = child.g + child.h

            # Если сосед уже в списке на рассмотрение, проверяем, не короче ли новый путь
            if any(open_node for open_node in open_list if child == open_node and child.g > open_node.g):
                continue

            heapq.heappush(open_list, child)

    return None  # Путь не найден