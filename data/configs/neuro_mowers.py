# data/configs/neuro_mowers.py

NEURO_MOWERS_DATA = {
    'chat_gpt': {
        'cost': 25, 'display_name': 'ChatGPT', 'category': 'systems', 'fallback_color': (0, 168, 150),
        'description': 'Последний рубеж обороны. При контакте с врагом активируется, едет по всей линии и уничтожает всех на своем пути. Может быть не более двух.'
    },
    'deepseek': {
        'cost': 15, 'display_name': 'DeepSeek', 'category': 'systems', 'fallback_color': (20, 20, 40),
        'description': 'Тактическая нейросеть. Уничтожает 3 самых близких к вашей базе врага на всем поле.'
    },
    'gemini': {
        'cost': 40, 'display_name': 'Gemini', 'category': 'systems', 'fallback_color': (106, 90, 205),
        'description': 'Элитная нейросеть. Уничтожает 4 самых сильных (по текущему здоровью) врага на всем поле.'
    }
}