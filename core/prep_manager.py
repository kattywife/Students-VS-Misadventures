# core/prep_manager.py

import random
from typing import List, Dict, Set, Optional, Tuple

import pygame

from data.settings import *
from data.levels import LEVELS
from core.level_manager import LevelManager

# Используем forward reference, чтобы избежать циклического импорта
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui_manager import UIManager
    from core.sound_manager import SoundManager
    from core.level_manager import LevelManager



class PrepManager:
    """
    Обрабатывает всю логику на экране подготовки к бою:
    - Выбор команды защитников.
    - Покупка и расстановка "нейросетей".
    - Улучшение характеристик героев за "стипендию".
    """
    def __init__(self, ui_manager: 'UIManager', stipend: int, level_id: int, sound_manager: 'SoundManager') -> None:
        """
        Инициализирует менеджер подготовки.

        Args:
            ui_manager (UIManager): Менеджер UI для отрисовки.
            stipend (int): Начальное количество "стипендии".
            level_id (int): ID текущего уровня.
            sound_manager (SoundManager): Менеджер звука.
        """
        self.ui_manager = ui_manager
        self.stipend = stipend
        self.level_id = level_id
        self.sound_manager = sound_manager
        self.level_data = LEVELS.get(level_id, LEVELS[1])

        self.team_slots = MAX_TEAM_SIZE
        self.team = []
        self.upgrades = {}

        self.neuro_mower_slots = self.level_data.get('neuro_slots', 2)
        self.chat_gpt_limit = CHAT_GPT_LIMIT
        self.purchased_mowers = []

        self.all_defenders = list(DEFENDERS_DATA.keys())
        self.all_neuro_mowers = list(NEURO_MOWERS_DATA.keys())

        self.selected_card_info = None
        self.info_panel_buttons = {}
        self.random_buttons_rects = {}

        temp_level_manager = LevelManager(self.level_id, None, None)
        self.enemy_types = temp_level_manager.get_enemy_types_for_level()
        self.calamity_types = temp_level_manager.get_calamity_types_for_level()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает события, релевантные для экрана подготовки."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)

    def randomize_team(self) -> None:
        """Формирует случайную команду, возвращая стоимость всех улучшений."""
        self.sound_manager.play_sfx('taking')
        for hero_type, upgraded_stats in self.upgrades.items():
            for stat in upgraded_stats:
                cost = DEFENDERS_DATA[hero_type]['upgrades'][stat]['cost']
                self.stipend += cost
        self.team.clear()
        self.upgrades.clear()
        available_heroes = self.all_defenders.copy()
        random.shuffle(available_heroes)
        self.team = available_heroes[:self.team_slots]

    def randomize_neuro(self) -> None:
        """Покупает случайный набор нейросетей на доступную стипендию."""
        self.sound_manager.play_sfx('taking')
        for mower_type in self.purchased_mowers:
            self.stipend += NEURO_MOWERS_DATA[mower_type]['cost']
        self.purchased_mowers.clear()

        available_mowers = self.all_neuro_mowers.copy()
        while len(self.purchased_mowers) < self.neuro_mower_slots:
            random.shuffle(available_mowers)
            mower_to_buy = available_mowers[0]
            cost = NEURO_MOWERS_DATA[mower_to_buy]['cost']

            if mower_to_buy == 'chat_gpt' and self.purchased_mowers.count('chat_gpt') >= self.chat_gpt_limit:
                continue

            if self.stipend >= cost:
                self.stipend -= cost
                self.purchased_mowers.append(mower_to_buy)
            else:
                break

    def handle_click(self, pos: Tuple[int, int]) -> None:
        """
        Централизованный обработчик кликов на экране подготовки.
        Определяет, на какой элемент UI нажал пользователь.
        """
        # Сначала проверяем клик внутри панели описания (если она открыта)
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

            if 'close' in self.info_panel_buttons and self.info_panel_buttons['close'].collidepoint(pos):
                self.sound_manager.play_sfx('cards');
                self.selected_card_info = None;
                return
            if 'take' in self.info_panel_buttons and self.info_panel_buttons['take'].collidepoint(pos):
                self.try_take_card(card_type);
                self.selected_card_info = None;
                return
            if 'kick' in self.info_panel_buttons and self.info_panel_buttons['kick'].collidepoint(pos):
                self.kick_unit_from_team(card_type);
                self.selected_card_info = None;
                return
            if self.ui_manager.desc_panel_rect and self.ui_manager.desc_panel_rect.collidepoint(pos): return

        if 'team' in self.random_buttons_rects and self.random_buttons_rects['team'].collidepoint(pos):
            self.randomize_team();
            return
        if 'neuro' in self.random_buttons_rects and self.random_buttons_rects['neuro'].collidepoint(pos):
            self.randomize_neuro();
            return

        all_clickable_cards_with_source = {
            'selection': self.ui_manager.selection_cards_rects,
            'team': self.ui_manager.team_card_rects,
            'plan': self.ui_manager.plan_cards_rects
        }
        for source, group in all_clickable_cards_with_source.items():
            for card_key, rect in group.items():
                if rect.collidepoint(pos):
                    key_parts = card_key.split('_')
                    base_type = card_key
                    if len(key_parts) > 1 and key_parts[-1].isdigit():
                        base_type = '_'.join(key_parts[:-1])

                    self.show_card_info(base_type, source)
                    return

    def try_take_card(self, card_type: str) -> None:
        """Пытается добавить юнита или нейросеть в команду."""
        if card_type in self.all_defenders:
            if len(self.team) < self.team_slots and card_type not in self.team:
                self.sound_manager.play_sfx('taking');
                self.team.append(card_type)
        elif card_type in self.all_neuro_mowers:
            if len(self.purchased_mowers) >= self.neuro_mower_slots: return
            if card_type == 'chat_gpt' and self.purchased_mowers.count('chat_gpt') >= self.chat_gpt_limit: return
            cost = NEURO_MOWERS_DATA[card_type]['cost']
            if self.stipend >= cost:
                self.sound_manager.play_sfx('taking');
                self.stipend -= cost;
                self.purchased_mowers.append(
                    card_type)

    def kick_unit_from_team(self, unit_type: str) -> None:
        """Удаляет юнита из команды и возвращает потраченные на него ресурсы."""
        self.sound_manager.play_sfx('taking')
        if unit_type in self.team:
            self.team.remove(unit_type)
            if unit_type in self.upgrades:
                for stat in self.upgrades[unit_type]:
                    cost = DEFENDERS_DATA[unit_type]['upgrades'][stat]['cost']
                    self.stipend += cost
                del self.upgrades[unit_type]
        elif unit_type in self.purchased_mowers:
            try:
                # Находим первый попавшийся экземпляр и удаляем его
                index_to_remove = -1
                for i, mower in enumerate(self.purchased_mowers):
                    if mower == unit_type:
                        index_to_remove = i
                        break

                if index_to_remove != -1:
                    self.purchased_mowers.pop(index_to_remove)
                    cost = NEURO_MOWERS_DATA[unit_type].get('cost', 0)
                    self.stipend += cost
            except ValueError:
                pass

    def try_upgrade_hero(self, hero_type: str, stat: str) -> None:
        """Пытается улучшить характеристику героя, если хватает стипендии."""
        upgrade_info = DEFENDERS_DATA[hero_type].get('upgrades', {}).get(stat)
        if not upgrade_info: return

        cost = upgrade_info['cost']
        if self.stipend >= cost:
            self.sound_manager.play_sfx('tuning')
            self.stipend -= cost
            if hero_type not in self.upgrades:
                self.upgrades[hero_type] = set()
            self.upgrades[hero_type].add(stat)

    def revert_upgrade(self, hero_type: str, stat: str) -> None:
        """Отменяет улучшение и возвращает стипендию."""
        if hero_type in self.upgrades and stat in self.upgrades[hero_type]:
            self.sound_manager.play_sfx('tuning')
            self.upgrades[hero_type].remove(stat)
            if not self.upgrades[hero_type]:
                del self.upgrades[hero_type]

            cost = DEFENDERS_DATA[hero_type]['upgrades'][stat]['cost']
            self.stipend += cost

    def show_card_info(self, card_type: str, source: str) -> None:
        """
        Готовит данные для отображения в панели с описанием.

        Args:
            card_type (str): Тип юнита (e.g., 'programmer').
            source (str): Откуда был сделан клик ('team', 'selection', 'plan').
        """
        self.sound_manager.play_sfx('cards')
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
        description = data.get('description', '').format(**{k: data.get(k, '?') for k in data})
        self.selected_card_info = {
            'type': card_type, 'name': data['display_name'],
            'description': description, 'source': source
        }


    def draw(self, surface: pygame.Surface) -> Tuple[Dict, Dict, Dict]:
        """
        Запускает отрисовку всего экрана подготовки через UIManager.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.

        Returns:
            Tuple[Dict, Dict, Dict]: Кортеж со словарями Rect'ов кнопок для обработки кликов.
        """
        # ИСПРАВЛЕНИЕ: Вызываем метод с правильным количеством аргументов.
        # Лишние аргументы были удалены, так как они теперь не нужны рендереру.
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

    def is_ready(self) -> bool:
        """Проверяет, готова ли команда к началу боя (выбран хотя бы один герой)."""
        return len(self.team) > 0