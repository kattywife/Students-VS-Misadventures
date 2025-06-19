# data/settings.py

# Этот файл служит единой точкой входа для всех настроек проекта.
# Он импортирует константы из специализированных модулей в папке 'configs'.
# Это позволяет сохранять чистоту и порядок, разделяя настройки по категориям.
# Также здесь создаются объединенные словари для удобства доступа из других частей кода.

import pygame

# --- ИМПОРТ ВСЕХ КОНФИГУРАЦИОННЫХ ФАЙЛОВ ---
# Используются абсолютные импорты от корня проекта, что обеспечивается
# добавлением пути к проекту в sys.path в main.py.
from data.configs.game import *
from data.configs.audio import *
from data.configs.colors import *
from data.configs.fonts import *
from data.configs.ui import *
from data.configs.mechanics import *

# Импортируем словари с данными игровых объектов
from data.configs.defenders import DEFENDERS_DATA
from data.configs.enemies import ENEMIES_DATA
from data.configs.neuro_mowers import NEURO_MOWERS_DATA
from data.configs.calamities import CALAMITIES_DATA


# --- ОБЪЕДИНЕННЫЕ СЛОВАРИ ДЛЯ УДОБСТВА ---

# Словарь с цветами по умолчанию для резервной отрисовки.
# Собирается из данных, определенных в специализированных файлах.
# Используется, если не удалось загрузить изображение для какого-либо объекта.
DEFAULT_COLORS = {
    # Распаковка словарей с цветами из данных юнитов
    **{unit: data['fallback_color'] for unit, data in DEFENDERS_DATA.items() if 'fallback_color' in data},
    **{unit: data['fallback_color'] for unit, data in ENEMIES_DATA.items() if 'fallback_color' in data},
    **{unit: data['fallback_color'] for unit, data in NEURO_MOWERS_DATA.items() if 'fallback_color' in data},
    **{unit: data['fallback_color'] for unit, data in CALAMITIES_DATA.items() if 'fallback_color' in data},
    # Добавление цветов для UI-элементов
    **FALLBACK_UI_COLORS,
}

# Словарь с данными для UI элементов, которые не являются юнитами,
# но для которых нужны карточки или иконки (например, иконка стипендии).
UI_ELEMENTS_DATA = {
    'stipend': {'display_name': 'Стипендия', 'category': 'ui'},
    'coffee_bean': {'display_name': 'Кофейные зернышки', 'category': 'resources'}
}