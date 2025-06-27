# data/levels.py

# Этот файл содержит словарь со всеми игровыми уровнями.
# Изменение этого файла позволяет легко настраивать существующие уровни
# и добавлять новые без изменения кода.
#
# Структура данных для каждого уровня:
#   - ID уровня (int): Уникальный идентификатор. Уровень 0 - тестовый.
#   - 'name': Название уровня, отображаемое в UI (например, "Курс 1").
#   - 'start_coffee': Начальное количество кофе на уровне.
#   - 'neuro_slots': Количество доступных слотов для нейросетей.
#   - 'calamities': Список возможных "напастей" на этом уровне.
#   - 'enemies': Список кортежей, определяющий последовательность появления врагов.
#       - Каждый кортеж: ('тип_врага', номер_ряда), где ряд 0 - верхний.
#       - Враги появляются в том порядке, в котором они указаны в списке.

LEVELS = {
    0: {
        'name': "Тестовая площадка",
        'start_coffee': 5000,
        'neuro_slots': 4,
        'calamities': ['epidemic', 'big_party', 'colloquium', 'internet_down'],
        'enemies': [
            # --- ВОЛНА 1: Знакомство с каждым врагом ---
            ('alarm_clock', 0),   # Базовый
            ('calculus', 1),      # Дальнобойный
            ('math_teacher', 2),  # Прыгун
            ('addict', 3),        # Охотник за сильными
            ('thief', 4),         # Охотник за кофемашинами

            # # --- ВОЛНА 2: Проверка парных взаимодействий ---
            ('alarm_clock', 0),
            ('calculus', 0),      # Два врага на одной линии
            ('math_teacher', 3),
            ('thief', 3),         # Прыгун и вор на одной линии

            # --- ВОЛНА 3: Стресс-тест и хаос ---
            ('alarm_clock', 0),
            ('math_teacher', 3),
            ('addict', 4),
            ('thief', 0),
            ('addict', 3),
            ('math_teacher', 4),
            ('calculus', 3),
            ('thief', 2),
        ]
    },
    1: {
        'name': "Курс 1",
        'start_coffee': 150,
        'neuro_slots': 2,
        'calamities': ['epidemic'],
        'enemies': [
            ('alarm_clock', 2),
            ('alarm_clock', 2),
            ('calculus', 3),
            ('alarm_clock', 1),
            ('alarm_clock', 3),
            ('calculus', 2),
            ('alarm_clock', 2),
            ('alarm_clock', 2),
        ]
    },
    2: {
        'name': "Курс 2",
        'start_coffee': 150,
        'neuro_slots': 3,
        'calamities': ['epidemic', 'colloquium'],
        'enemies': [
            ('alarm_clock', 1),
            ('calculus', 3),
            ('math_teacher', 2),
            ('alarm_clock', 2),
            ('alarm_clock', 4),
            ('calculus', 1),
            ('math_teacher', 3),
            ('alarm_clock', 0),
            ('calculus', 4),
            ('alarm_clock', 1),
            ('alarm_clock', 3),
            ('math_teacher', 2),
        ]
    },
    3: {
        'name': "Курс 3",
        'start_coffee': 150,
        'neuro_slots': 3,
        'calamities': ['colloquium', 'internet_down'],
        'enemies': [
            ('calculus', 1),
            ('thief', 3),
            ('math_teacher', 2),
            ('alarm_clock', 4),
            ('calculus', 0),
            ('thief', 2),
            ('alarm_clock', 1),
            ('math_teacher', 0),
            ('alarm_clock', 3),
            ('calculus', 4),
            ('alarm_clock', 2),
            ('alarm_clock', 2),
            ('math_teacher', 3),
            ('thief', 1),
        ]
    },
    4: {
        'name': "Курс 4",
        'start_coffee': 150,
        'neuro_slots': 4,
        'calamities': ['internet_down', 'big_party'],
        'enemies': [
            ('math_teacher', 1),
            ('math_teacher', 3),
            ('addict', 2),
            ('thief', 4),
            ('calculus', 0),
            ('alarm_clock', 2),
            ('addict', 3),
            ('calculus', 1),
            ('thief', 0),
            ('math_teacher', 4),
            ('alarm_clock', 1),
            ('alarm_clock', 3),
            ('calculus', 2),
            ('addict', 4),
            ('thief', 2),
            ('math_teacher', 0),
        ]
    },
    5: {
        'name': "Защита Диплома",
        'start_coffee': 150,
        'neuro_slots': 4,
        'calamities': ['epidemic', 'big_party', 'colloquium', 'internet_down'],
        'enemies': [
            ('calculus', 0), ('calculus', 4), ('alarm_clock', 1), ('alarm_clock', 2), ('alarm_clock', 3),
            ('alarm_clock', 1), ('alarm_clock', 2), ('alarm_clock', 3),
            ('math_teacher', 2), ('thief', 1), ('addict', 2),
            ('thief', 0), ('addict', 4),
            ('alarm_clock', 0), ('alarm_clock', 4),
            ('calculus', 1), ('calculus', 3),
            ('math_teacher', 0), ('math_teacher', 4),
            ('thief', 1), ('addict', 3),
            ('alarm_clock', 2), ('alarm_clock', 2),
            ('calculus', 2),('thief', 3), ('thief', 0),
            ('thief', 3), ('math_teacher', 2), ('math_teacher', 3),
            ('addict', 1),
            ('math_teacher', 1), ('math_teacher', 3),
            ('alarm_clock', 0), ('alarm_clock', 1), ('alarm_clock', 2), ('alarm_clock', 3), ('alarm_clock', 4),
        ]
    }
}