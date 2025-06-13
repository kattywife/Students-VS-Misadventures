# levels.py

LEVELS = {
    1: {
        'name': "Курс 1: Введение в специальность",
        'start_coffee': 150,
        # (тип врага, ряд)
        'enemies': [
            ('alarm_clock', 2), ('alarm_clock', 1), ('alarm_clock', 3),
            ('alarm_clock', 2), ('professor', 2), ('alarm_clock', 0),
            ('alarm_clock', 4),
        ]
    },
    2: {
        'name': "Курс 2: Математический Ад",
        'start_coffee': 200,
        'enemies': [
            ('alarm_clock', 2), ('calculus', 3), ('alarm_clock', 1),
            ('professor', 2), ('calculus', 2), ('alarm_clock', 0),
            ('alarm_clock', 4), ('calculus', 1), ('professor', 3),
        ]
    },
    3: {
        'name': "Курс 3: Теория вероятностей",
        'start_coffee': 250,
        'enemies': [
            ('calculus', 1), ('calculus', 3), ('professor', 2),
            ('alarm_clock', 0), ('alarm_clock', 4), ('calculus', 2),
            ('professor', 1), ('professor', 3), ('alarm_clock', 1),
            ('alarm_clock', 2), ('alarm_clock', 3),
        ]
    },
    4: {
        'name': "Курс 4: Сессия",
        'start_coffee': 300,
        'enemies': [
            ('professor', 2), ('calculus', 1), ('calculus', 3),
            ('professor', 0), ('professor', 4), ('alarm_clock', 0),
            ('alarm_clock', 1), ('alarm_clock', 2), ('alarm_clock', 3),
            ('alarm_clock', 4), ('calculus', 2), ('professor', 1),
            ('professor', 3), ('professor', 2)
        ]
    },
    5: {
        'name': "Защита Диплома",
        'start_coffee': 500,
        'enemies': [
            ('calculus', 0), ('calculus', 1), ('calculus', 2),
            ('calculus', 3), ('calculus', 4), ('professor', 0),
            ('professor', 1), ('professor', 2), ('professor', 3),
            ('professor', 4), ('alarm_clock', 2), ('calculus', 1),
            ('calculus', 3), ('professor', 2), ('alarm_clock', 0),
            ('alarm_clock', 4), ('professor', 0), ('professor', 4),
        ]
    }
}