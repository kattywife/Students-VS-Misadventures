# core/prep_manager.py

import pygame
import random
from data.settings import *
from data.levels import LEVELS
from core.level_manager import LevelManager


class PrepManager:
    """
    Управляет логикой экрана подготовки к бою.
    Отвечает за:
    - Выбор команды защитников и нейросетей.
    - Покупку улучшений для защитников.
    - Управление бюджетом ("стипендией").
    - Отображение информации о юнитах и уровне.
    - Генерацию случайной команды/нейросетей.
    """

    def __init__(self, ui_manager, stipend, level_id, sound_manager):
        """
        Инициализирует менеджер подготовки.

        Args:
            ui_manager (UIManager): Менеджер интерфейса для отрисовки экрана.
            stipend (int): Начальная стипендия игрока.
            level_id (int): ID текущего уровня.
            sound_manager (SoundManager): Менеджер звука.
        """
        self.ui_manager = ui_manager
        self.stipend = stipend
        self.level_id = level_id
        self.sound_manager = sound_manager
        self.level_data = LEVELS.get(level_id, LEVELS[1])

        # --- Состояние команды и улучшений ---
        self.team_slots = MAX_TEAM_SIZE
        self.team = []
        self.upgrades = {}  # { 'hero_type': {'stat1', 'stat2'} }

        # --- Состояние нейросетей ---
        self.neuro_mower_slots = self.level_data.get('neuro_slots', 2)
        self.chat_gpt_limit = CHAT_GPT_LIMIT
        self.purchased_mowers = []

        # --- Справочные данные ---
        self.all_defenders = list(DEFENDERS_DATA.keys())
        self.all_neuro_mowers = list(NEURO_MOWERS_DATA.keys())

        # --- Состояние UI ---
        self.selected_card_info = None
        self.info_panel_buttons = {}  # Кнопки на панели описания
        self.random_buttons_rects = {}  # Кнопки случайного выбора

        # --- Информация об уровне ---
        # Создаем временный LevelManager только для получения данных об уровне
        temp_level_manager = LevelManager(self.level_id, None, None)
        self.enemy_types = temp_level_manager.get_enemy_types_for_level()
        self.calamity_types = temp_level_manager.get_calamity_types_for_level()

    def handle_event(self, event):
        """Обрабатывает пользовательский ввод на экране подготовки."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)

    def randomize_team(self):
        """
        Генерирует случайную команду защитников.
        Сбрасывает текущую команду и возвращает стоимость всех улучшений в бюджет.
        """
        self.sound_manager.play_sfx('taking')
        # Возвращаем деньги за апгрейды
        for hero_type, upgraded_stats in self.upgrades.items():
            for stat in upgraded_stats:
                cost = DEFENDERS_DATA[hero_type]['upgrades'][stat]['cost']
                self.stipend += cost
        self.team.clear()
        self.upgrades.clear()

        # Формируем новую случайную команду
        available_heroes = self.all_defenders.copy()
        random.shuffle(available_heroes)
        self.team = available_heroes[:self.team_slots]

    def randomize_neuro(self):
        """
        Генерирует случайный набор купленных нейросетей.
        Сбрасывает текущий набор и пытается купить новые на все доступные деньги.
        """
        self.sound_manager.play_sfx('taking')
        # Возвращаем деньги за купленные нейросети
        for mower_type in self.purchased_mowers:
            self.stipend += NEURO_MOWERS_DATA[mower_type]['cost']
        self.purchased_mowers.clear()

        # Покупаем случайные нейросети, пока есть деньги и слоты
        available_mowers = self.all_neuro_mowers.copy()
        while len(self.purchased_mowers) < self.neuro_mower_slots:
            random.shuffle(available_mowers)
            mower_to_buy = available_mowers[0]
            cost = NEURO_MOWERS_DATA[mower_to_buy]['cost']

            # Проверка на лимит для ChatGPT
            if mower_to_buy == 'chat_gpt' and self.purchased_mowers.count('chat_gpt') >= self.chat_gpt_limit:
                continue

            if self.stipend >= cost:
                self.stipend -= cost
                self.purchased_mowers.append(mower_to_buy)
            else:
                # Если денег не хватает, прекращаем покупки
                break

    def handle_click(self, pos):
        """
        Обрабатывает клики по различным элементам экрана: карточкам, кнопкам.

        Args:
            pos (tuple[int, int]): Координаты клика.
        """
        # 1. Приоритет у кнопок на открытой панели описания
        if self.selected_card_info:
            card_type = self.selected_card_info['type']
            for key, rect in self.info_panel_buttons.items():
                if rect.collidepoint(pos):
                    if key.startswith('upgrade_'):
                        stat_to_upgrade = key.split('_', 1)[1]
                        self.try_upgrade_hero(card_type, stat_to_upgrade)
                        return
                    if key.startswith('revert_'):
                        stat_to_revert = key.split('_', 1)[1]
                        self.revert_upgrade(card_type, stat_to_revert)
                        return
                    if key == 'close':
                        self.sound_manager.play_sfx('cards')
                        self.selected_card_info = None
                        return
                    if key == 'take':
                        self.try_take_card(card_type)
                        self.selected_card_info = None
                        return
                    if key == 'kick':
                        self.kick_unit_from_team(card_type)
                        self.selected_card_info = None
                        return
            # Если клик был внутри панели, но не по кнопке - игнорируем, чтобы не закрыть случайно
            if self.ui_manager.desc_panel_rect and self.ui_manager.desc_panel_rect.collidepoint(pos):
                return

        # 2. Клик по кнопкам случайного выбора
        if 'team' in self.random_buttons_rects and self.random_buttons_rects['team'].collidepoint(pos):
            self.randomize_team()
            return
        if 'neuro' in self.random_buttons_rects and self.random_buttons_rects['neuro'].collidepoint(pos):
            self.randomize_neuro()
            return

        # 3. Клик по любой карточке юнита на экране
        all_clickable_cards_with_source = {
            'selection': self.ui_manager.selection_cards_rects,
            'team': self.ui_manager.team_card_rects,
            'plan': self.ui_manager.plan_cards_rects
        }
        for source, group in all_clickable_cards_with_source.items():
            for card_key, rect in group.items():
                if rect.collidepoint(pos):
                    # Для нейросетей в команде ключ может иметь суффикс (e.g., 'chat_gpt_0'), убираем его
                    base_type = card_key.rsplit('_', 1)[0] if card_key.rsplit('_', 1)[-1].isdigit() else card_key
                    self.show_card_info(base_type, source)
                    return

    def try_take_card(self, card_type):
        """
        Пытается добавить юнита или нейросеть в команду/набор.
        Проверяет наличие свободных слотов и бюджета.

        Args:
            card_type (str): Тип юнита/нейросети для добавления.
        """
        if card_type in self.all_defenders:
            if len(self.team) < self.team_slots and card_type not in self.team:
                self.sound_manager.play_sfx('taking')
                self.team.append(card_type)
        elif card_type in self.all_neuro_mowers:
            if len(self.purchased_mowers) >= self.neuro_mower_slots: return
            if card_type == 'chat_gpt' and self.purchased_mowers.count('chat_gpt') >= self.chat_gpt_limit: return
            cost = NEURO_MOWERS_DATA[card_type]['cost']
            if self.stipend >= cost:
                self.sound_manager.play_sfx('taking')
                self.stipend -= cost
                self.purchased_mowers.append(card_type)

    def kick_unit_from_team(self, unit_type):
        """
        Удаляет юнита или нейросеть из команды/набора.
        Возвращает стоимость в бюджет.

        Args:
            unit_type (str): Тип юнита/нейросети для удаления.
        """
        self.sound_manager.play_sfx('taking')
        if unit_type in self.team:
            self.team.remove(unit_type)
            # Если у удаляемого героя были апгрейды, возвращаем их стоимость
            if unit_type in self.upgrades:
                for stat in self.upgrades[unit_type]:
                    cost = DEFENDERS_DATA[unit_type]['upgrades'][stat]['cost']
                    self.stipend += cost
                del self.upgrades[unit_type]
        elif unit_type in self.purchased_mowers:
            # Удаляем первый найденный экземпляр, так как их может быть несколько одинаковых
            if unit_type in self.purchased_mowers:
                self.purchased_mowers.remove(unit_type)
                cost = NEURO_MOWERS_DATA[unit_type].get('cost', 0)
                self.stipend += cost

    def try_upgrade_hero(self, hero_type, stat):
        """
        Пытается улучшить характеристику героя.
        Проверяет наличие средств и применяет улучшение.

        Args:
            hero_type (str): Тип героя.
            stat (str): Название характеристики для улучшения (e.g., 'damage').
        """
        upgrade_info = DEFENDERS_DATA[hero_type].get('upgrades', {}).get(stat)
        if not upgrade_info: return

        cost = upgrade_info['cost']
        if self.stipend >= cost:
            self.sound_manager.play_sfx('tuning')
            self.stipend -= cost
            if hero_type not in self.upgrades:
                self.upgrades[hero_type] = set()
            self.upgrades[hero_type].add(stat)

    def revert_upgrade(self, hero_type, stat):
        """
        Отменяет улучшение характеристики героя и возвращает деньги.

        Args:
            hero_type (str): Тип героя.
            stat (str): Название характеристики для отмены.
        """
        if hero_type in self.upgrades and stat in self.upgrades[hero_type]:
            self.sound_manager.play_sfx('tuning')
            self.upgrades[hero_type].remove(stat)
            # Если у героя больше не осталось улучшений, удаляем его из словаря
            if not self.upgrades[hero_type]:
                del self.upgrades[hero_type]

            cost = DEFENDERS_DATA[hero_type]['upgrades'][stat]['cost']
            self.stipend += cost

    def show_card_info(self, card_type, source):
        """
        Готовит данные для отображения на панели описания.

        Args:
            card_type (str): Тип выбранного юнита/врага.
            source (str): Источник клика ('team', 'selection', 'plan').
        """
        self.sound_manager.play_sfx('cards')
        # Определяем, откуда брать данные
        data_source = {}
        if card_type in DEFENDERS_DATA:
            data_source = DEFENDERS_DATA
        elif card_type in ENEMIES_DATA:
            data_source = ENEMIES_DATA
        elif card_type in NEURO_MOWERS_DATA:
            data_source = NEURO_MOWERS_DATA
        elif card_type in CALAMITIES_DATA:
            data_source = CALAMITIES_DATA
        else:
            return

        data = data_source[card_type]
        # Форматируем описание, подставляя реальные значения характеристик
        description = data.get('description', '').format(**data)
        self.selected_card_info = {
            'type': card_type, 'name': data['display_name'],
            'description': description, 'source': source
        }

    def draw(self, surface):
        """
        Отрисовывает весь экран подготовки, делегируя вызов UIManager'у.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.

        Returns:
            dict: Словарь с Rect'ами кликабельных кнопок на экране.
        """
        prep_buttons, self.random_buttons_rects, self.info_panel_buttons = self.ui_manager.draw_preparation_screen(
            surface,
            self.stipend,
            self.team,
            self.upgrades,
            self.purchased_mowers,
            self.neuro_mower_slots,
            self.enemy_types,
            self.calamity_types,
            self.selected_card_info
        )
        return prep_buttons

    def is_ready(self):
        """
        Проверяет, готова ли команда к бою.
        Условие: в команде должен быть хотя бы один защитник.

        Returns:
            bool: True, если команда готова.
        """
        return len(self.team) > 0