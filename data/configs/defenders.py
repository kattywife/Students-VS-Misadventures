# data/configs/defenders.py

# Этот файл содержит словарь с данными для всех защитников (студентов) в игре.
# Является центральным местом для настройки баланса и добавления новых героев.
#
# Структура данных для каждого защитника:
#   - 'cost': Стоимость покупки в бою (в кофе).
#   - 'health': Здоровье.
#   - 'damage': Базовый урон.
#   - 'cooldown': Время между атаками/действиями в секундах.
#   - ... другие уникальные характеристики (radius, buff, production и т.д.)
#   - 'display_name': Имя, отображаемое в UI.
#   - 'category': Категория для поиска ассетов ('defenders').
#   - 'fallback_color': Цвет для резервной отрисовки.
#   - 'description': Текст с описанием для UI.
#   - 'upgrades': Словарь с доступными улучшениями.
#       - 'stat_name': {'value': бонус к стату, 'cost': стоимость в стипендии}.
#   - 'animation_data': Словарь с настройками анимации (аналогично врагам).

DEFENDERS_DATA = {
    'programmer': {
        'cost': 100, 'health': 300, 'damage': 25, 'cooldown': 1.5, 'display_name': 'Мальчик-джун',
        'category': 'defenders', 'fallback_color': (60, 179, 113),
        'description': "Стандартный стрелок, эффективный против одиночных целей. Его атаки быстры и точны, как идеально написанный код.",
        'upgrades': { 'damage': {'value': 10, 'cost': 20}, 'cooldown': {'value': -0.3, 'cost': 25} },
        'animation_data': { 'folder': 'programmer', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }
    },
    'botanist': {
        'cost': 150, 'health': 300, 'damage': 50, 'cooldown': 2.5, 'radius': 2, 'display_name': 'Девочка-ботан',
        'category': 'defenders', 'fallback_color': (255, 105, 180),
        'description': "Находит самого 'жирного' врага на поле и обрушивает на него и его соседей всю тяжесть своих знаний. Атакует по области.",
        'upgrades': { 'damage': {'value': 25, 'cost': 30}, 'radius': {'value': 1, 'cost': 20} },
        'animation_data': { 'folder': 'botanist', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }
    },
    'coffee_machine': {
        'cost': 50, 'health': 200, 'damage': 0, 'cooldown': 5, 'production': 25, 'display_name': 'Кофемашина',
        'category': 'defenders', 'fallback_color': (255, 215, 0),
        'description': "Источник жизни и бодрости. Не атакует, но исправно генерирует кофейные зернышки, необходимые для вызова новых защитников.",
        'upgrades': { 'production': {'value': 15, 'cost': 25}, 'health': {'value': 150, 'cost': 20} },
        'animation_data': { 'folder': 'coffee_machine', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }
    },
    'activist': {
        'cost': 75, 'health': 400, 'damage': 0, 'cooldown': None, 'radius': 2, 'buff': 1.5, 'display_name': 'Активист',
        'category': 'defenders', 'fallback_color': (0, 128, 128),
        'description': "Его пламенные речи вдохновляют всех вокруг. Создает ауру, которая значительно увеличивает урон союзников в радиусе.",
        'upgrades': {'buff': {'value': 0.3, 'cost': 30}, 'radius': {'value': 1, 'cost': 25}},
        'animation_data': { 'folder': 'activist', 'speed': 0.3, 'idle': [], 'hit': [] }
    },
    'guitarist': {
        'cost': 150, 'health': 300, 'damage': 20, 'cooldown': 4, 'projectile_speed': 5, 'display_name': 'Гитарист',
        'category': 'defenders', 'fallback_color': (218, 112, 214),
        'description': "Атакует всех врагов на своей линии мощной звуковой волной, которая пробивает их насквозь.",
        'upgrades': { 'projectile_speed': {'value': 3, 'cost': 20}, 'damage': {'value': 15, 'cost': 25} },
        'animation_data': { 'folder': 'guitarist', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }
    },
    'medic': {
        'cost': 50, 'health': 250, 'damage': 0, 'cooldown': 1.0, 'heal_amount': 200, 'radius': 2, 'display_name': 'Студент-медик',
        'category': 'defenders', 'fallback_color': (240, 255, 255),
        'description': "Живая аптечка. Постепенно отдает свое здоровье самому раненому союзнику в радиусе. Когда его запас здоровья иссякнет, он исчезнет.",
        'upgrades': { 'radius': {'value': 1, 'cost': 20}, 'heal_amount': {'value': 150, 'cost': 25} },
        'animation_data': { 'folder': 'medic', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }
    },
    'artist': {
        'cost': 125, 'health': 300, 'damage': 10, 'cooldown': 2, 'slow_duration': 2000, 'slow_factor': 0.5, 'display_name': 'Художница',
        'category': 'defenders', 'fallback_color': (255, 165, 0),
        'description': "Её кляксы краски, попадая во врагов, не только наносят урон, но и значительно замедляют их передвижение.",
        'upgrades': { 'slow_factor': {'value': -0.15, 'cost': 25}, 'damage': {'value': 15, 'cost': 20} },
        'animation_data': { 'folder': 'artist', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }
    },
    'modnik': {
        'cost': 125, 'health': 300, 'damage': 1800, 'radius': 2, 'speed': 1.5, 'display_name': 'Модник',
        'category': 'defenders', 'fallback_color': (128, 0, 128),
        'description': "Быстрый юнит-камикадзе. Находит ближайшего врага, подбегает и взрывается, нанося огромный урон по большой площади.",
        'upgrades': { 'radius': {'value': 1, 'cost': 30}, 'damage': {'value': 400, 'cost': 35} },
        'animation_data': { 'folder': 'modnik', 'speed': 0.3, 'idle': [], 'hit': [] }
    }
}