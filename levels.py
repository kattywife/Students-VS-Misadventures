# levels.py

LEVELS = {
    1: {
        'name': "Курс 1: Введение",
        'start_coffee': 150,
        'neuro_slots': 2, # <-- ИЗМЕНЕНИЕ: Количество слотов для нейросетей
        'calamities': [], # На первом уровне без напастей
        'enemies': [
            ('alarm_clock', 2), ('alarm_clock', 1), ('alarm_clock', 3),
            ('alarm_clock', 2), ('alarm_clock', 0), ('alarm_clock', 4),
            ('alarm_clock', 1), ('alarm_clock', 3),
        ]
    },
    2: {
        'name': "Курс 2: Основы матана",
        'start_coffee': 200,
        'neuro_slots': 3,
        'calamities': ['colloquium'],
        'enemies': [
            ('alarm_clock', 2), ('calculus', 3), ('alarm_clock', 1),
            ('professor', 2), ('calculus', 2), ('alarm_clock', 0),
            ('alarm_clock', 4), ('calculus', 1), ('professor', 3),
            ('alarm_clock', 2), ('calculus', 0),
        ]
    },
    3: {
        'name': "Курс 3: Злые преподаватели",
        'start_coffee': 250,
        'neuro_slots': 3,
        'calamities': ['internet_down'],
        'enemies': [
            ('calculus', 1), ('math_teacher', 3), ('professor', 2),
            ('math_teacher', 0), ('math_teacher', 4), ('calculus', 2),
            ('professor', 1), ('professor', 3), ('alarm_clock', 1),
            ('alarm_clock', 2), ('alarm_clock', 3), ('professor', 0),
            ('math_teacher', 2),
        ]
    },
    4: {
        'name': "Курс 4: Сессия близко",
        'start_coffee': 300,
        'neuro_slots': 4,
        'calamities': ['epidemic', 'colloquium'],
        'enemies': [
            ('professor', 2), ('calculus', 1), ('calculus', 3),
            ('thief', 0), ('professor', 4), ('math_teacher', 1),
            ('math_teacher', 2), ('addict', 3), ('math_teacher', 4),
            ('calculus', 2), ('professor', 1), ('thief', 3),
            ('professor', 0), ('addict', 4),
        ]
    },
    5: {
        'name': "Защита Диплома",
        'start_coffee': 400,
        'neuro_slots': 4,
        'calamities': ['big_party', 'internet_down'],
        'enemies': [
            ('calculus', 0), ('calculus', 4), ('professor', 1),
            ('professor', 3), ('math_teacher', 2), ('thief', 0),
            ('addict', 4), ('thief', 1), ('addict', 3),
            ('calculus', 1), ('calculus', 3), ('professor', 2),
            ('math_teacher', 0), ('math_teacher', 4), ('professor', 0),
            ('professor', 4), ('thief', 2), ('addict', 2),
            ('calculus', 2), ('professor', 2),
        ]
    }
}