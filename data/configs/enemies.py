# data/configs/enemies.py

# Этот файл содержит словарь с данными для всех врагов в игре.
# Использование такого файла позволяет легко изменять баланс и добавлять
# новых врагов, не затрагивая основной код (принцип Data-Driven Design).
#
# Структура данных для каждого врага:
#   - 'health': Здоровье врага.
#   - 'speed': Скорость передвижения (пикселей за кадр).
#   - 'damage': Урон, наносимый за одну атаку.
#   - 'cooldown': Время между атаками в секундах.
#   - 'display_name': Имя, отображаемое в UI.
#   - 'category': Категория для поиска ассетов ('enemies').
#   - 'fallback_color': Цвет для резервной отрисовки, если ассет не найден.
#   - 'description': Текст с описанием для UI.
#   - 'animation_data': Словарь с настройками анимации.
#       - 'folder': Название папки с изображениями анимаций.
#       - 'speed': Скорость смены кадров.
#       - 'walk', 'attack', 'hit': Списки кадров для разных состояний (заполняются автоматически).

ENEMIES_DATA = {
    'alarm_clock': {
        'health': 100, 'speed': 0.8, 'damage': 50, 'cooldown': 1.0, 'display_name': "Первая пара", 'category': 'enemies',
        'fallback_color': (169, 169, 169),
        'description': "Обычный враг, который просто идет вперед и больно кусает первого встречного. Берет числом, а не умением.",
        'animation_data': {'folder': 'alarm_clock', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}
    },
    'calculus': {
        'health': 180, 'speed': 0.8, 'damage': 10, 'cooldown': 3.0, 'display_name': "Матанализ", 'category': 'enemies',
        'fallback_color': (70, 130, 180),
        'description': "Опасный дальнобойный противник. Останавливается и обстреливает защитников на своей линии с безопасного расстояния.",
        'animation_data': {'folder': 'calculus', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}
    },
    'math_teacher': {
        'health': 150, 'speed': 1.5, 'damage': 80, 'cooldown': 1.0, 'display_name': "Злая математичка", 'category': 'enemies',
        'fallback_color': (210, 105, 30),
        'description': "Быстрый враг. При столкновении с первым защитником на линии перепрыгивает его, чтобы прорваться в тыл. После прыжка ее скорость снижается.",
        'animation_data': {'folder': 'math_teacher', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}
    },
    'addict': {
        'health': 120, 'speed': 2.5, 'damage': 9999, 'cooldown': 0.5, 'display_name': "Наркоман", 'category': 'enemies',
        'fallback_color': (0, 100, 0),
        'description': "Враг-убийца. Игнорирует всех, кроме защитника с самым большим уроном на поле. Целенаправленно бежит к нему и уносит с экрана.",
        'animation_data': {'folder': 'addict', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}
    },
    'thief': {
        'health': 120, 'speed': 2.5, 'damage': 9999, 'cooldown': 0.5, 'display_name': "Вор", 'category': 'enemies',
        'fallback_color': (139, 0, 0),
        'description': "Главный враг экономики. Ищет Кофемашины, игнорируя героев. Украдет одну и вернется за следующей. Если Кофемашин нет, атакует как обычный враг.",
        'animation_data': {'folder': 'thief', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}
    }
}