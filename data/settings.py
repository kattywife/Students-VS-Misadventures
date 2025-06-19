# data/settings.py

# Этот файл служит единой точкой входа для всех настроек проекта.
# Он не хранит константы сам, а импортирует их из специализированных модулей
# в папке 'configs'. Это позволяет сохранять чистоту и порядок, разделяя
# настройки по категориям (принцип разделения ответственности).
# Благодаря этому, для изменения баланса или UI достаточно редактировать
# только соответствующие файлы в 'configs', не трогая основную логику.

import pygame

# Используем абсолютные импорты от корня проекта.
# Это становится возможным благодаря добавлению пути проекта в sys.path в main.py,
# что делает импорты более явными и надежными.
from data.configs.game import *
from data.configs.audio import *
from data.configs.colors import *
from data.configs.fonts import *
from data.configs.ui import *
from data.configs.mechanics import *

# Импортируем словари с данными игровых объектов.
# Эти словари являются основой Data-Driven подхода в проекте.
from data.configs.defenders import DEFENDERS_DATA
from data.configs.enemies import ENEMIES_DATA
from data.configs.neuro_mowers import NEURO_MOWERS_DATA
from data.configs.calamities import CALAMITIES_DATA


# --- ОБЪЕДИНЕННЫЕ СЛОВАРИ ДЛЯ УДОБСТВА ---

# Словарь с цветами по умолчанию для резервной отрисовки спрайтов.
# Он собирается из данных, определенных в специализированных файлах.
# Если изображение для юнита не будет найдено, игра использует цвет из этого словаря.
DEFAULT_COLORS = {
    **{unit: data['fallback_color'] for unit, data in DEFENDERS_DATA.items() if 'fallback_color' in data},
    **{unit: data['fallback_color'] for unit, data in ENEMIES_DATA.items() if 'fallback_color' in data},
    **{unit: data['fallback_color'] for unit, data in NEURO_MOWERS_DATA.items() if 'fallback_color' in data},
    **{unit: data['fallback_color'] for unit, data in CALAMITIES_DATA.items() if 'fallback_color' in data},
    **FALLBACK_UI_COLORS,
}

# Словарь с данными UI элементов, которые должны иметь карточки,
# но не являются игровыми юнитами (например, иконка стипендии).
UI_ELEMENTS_DATA = {
    'stipend': {'display_name': 'Стипендия', 'category': 'ui'},
    'coffee_bean': {'display_name': 'Кофейные зернышки', 'category': 'resources'}
}