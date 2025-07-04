# ui/ui_manager.py

import pygame
from data.settings import *
from data.assets import load_image
from ui.main_menu_renderer import MainMenuRenderer
from ui.menu_renderer import MenuRenderer
from ui.settings_menu_renderer import SettingsMenuRenderer
from ui.battle_hud_renderer import BattleHUDRenderer
from ui.prep_screen_renderer import PrepScreenRenderer
from ui.neuro_placement_renderer import NeuroPlacementRenderer


class UIManager:
    """
    Фасад (Facade) для управления всеми компонентами пользовательского интерфейса.
    Этот класс является единой точкой входа для `GameManager` и других
    менеджеров для отрисовки UI. Он не рисует ничего сам, а инициализирует
    все специализированные рендереры и делегирует им вызовы отрисовки.

    Это позволяет основной логике игры не зависеть от деталей реализации
    каждого конкретного экрана, что упрощает поддержку и расширение кода.
    """

    def __init__(self, screen):
        """
        Инициализирует UIManager.

        Args:
            screen (pygame.Surface): Основная поверхность для отрисовки.
        """
        self.screen = screen

        # Загрузка общих ресурсов, которые могут использоваться несколькими рендерерами
        self.prep_background = load_image('prep_background.png', DEFAULT_COLORS['background'],
                                          (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Инициализация всех специализированных рендереров
        self.main_menu_renderer = MainMenuRenderer(screen)
        self.menu_renderer = MenuRenderer(screen)
        self.settings_renderer = SettingsMenuRenderer(screen)
        self.battle_hud_renderer = BattleHUDRenderer(screen)
        self.prep_screen_renderer = PrepScreenRenderer(screen)
        self.neuro_placement_renderer = NeuroPlacementRenderer(screen)

        # Сохраняем ссылки на важные Rect'ы из дочерних рендереров для
        # удобства доступа извне (например, для обработки кликов).
        self.shop_rects = self.battle_hud_renderer.shop_rects
        self.pause_button_rect = self.battle_hud_renderer.pause_button_rect
        self.desc_panel_rect = self.prep_screen_renderer.description_panel_renderer.panel_rect

    # --- Методы-делегаты для каждого экрана ---
    # Эти методы просто вызывают соответствующие методы у специализированных рендереров,
    # передавая им необходимые аргументы.

    def draw_start_screen(self, surface, title_text, buttons):
        """Делегирует отрисовку стартового экрана."""
        self.main_menu_renderer.draw_start_screen(surface, title_text, buttons)

    def draw_main_menu(self, surface, max_level_unlocked):
        """Делегирует отрисовку главного меню."""
        return self.main_menu_renderer.draw_main_menu(surface, max_level_unlocked)

    def draw_menu(self, surface, title_text, buttons):
        """Делегирует отрисовку универсального меню (пауза, победа и т.д.)."""
        self.menu_renderer.draw(surface, title_text, buttons)

    def draw_level_clear_message(self, surface):
        """Делегирует отрисовку сообщения о завершении уровня."""
        self.menu_renderer.draw_level_clear_message(surface)

    def draw_settings_menu(self, surface, music_enabled, sfx_enabled):
        """Делегирует отрисовку меню настроек."""
        return self.settings_renderer.draw(surface, music_enabled, sfx_enabled)

    def create_battle_shop(self, team):
        """Делегирует создание и кэширование панели магазина перед боем."""
        self.battle_hud_renderer.create_shop_surface(team)
        # Обновляем ссылки на Rect'ы после создания магазина, так как они изменились
        self.shop_rects = self.battle_hud_renderer.shop_rects

    def draw_shop_and_hud(self, surface, selected_defender, coffee, upgrades, spawn_progress, kill_progress, spawn_data,
                          kill_data, notification):
        """Делегирует отрисовку всего боевого интерфейса."""
        self.battle_hud_renderer.draw_shop(surface, selected_defender, coffee, upgrades)
        self.battle_hud_renderer.draw_hud_elements(surface, spawn_progress, kill_progress, spawn_data, kill_data,
                                                   notification)

    def handle_shop_click(self, pos):
        """Делегирует обработку кликов по магазину и кнопке паузы."""
        return self.battle_hud_renderer.handle_click(pos)

    def draw_preparation_screen(self, surface, stipend, team, upgrades, purchased_mowers, neuro_slots, enemy_types,
                                calamity_types, selected_card_info):
        """Делегирует отрисовку сложного экрана подготовки."""
        prep_buttons, random_buttons, info_buttons = self.prep_screen_renderer.draw(surface, stipend, team, upgrades,
                                                                                    purchased_mowers, neuro_slots,
                                                                                    enemy_types, calamity_types,
                                                                                    selected_card_info)
        # Передаем Rect'ы карточек из рендерера в UIManager, чтобы PrepManager
        # мог легко получить к ним доступ для обработки кликов.
        self.selection_cards_rects = self.prep_screen_renderer.selection_cards_rects
        self.team_card_rects = self.prep_screen_renderer.team_card_rects
        self.plan_cards_rects = self.prep_screen_renderer.plan_cards_rects
        return prep_buttons, random_buttons, info_buttons

    def draw_neuro_placement_screen(self, surface, purchased_mowers, placed_mowers, dragged_mower_info):
        """Делегирует отрисовку экрана расстановки нейросетей."""
        return self.neuro_placement_renderer.draw(surface, self.prep_background, purchased_mowers, placed_mowers,
                                                  dragged_mower_info)

    def draw_grid(self, surface):
        """Отрисовывает боевую сетку. Этот метод не делегируется, так как сетка проста
        и не требует отдельного рендерера."""
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(GRID_START_X + col * CELL_SIZE_W, GRID_START_Y + row * CELL_SIZE_H, CELL_SIZE_W,
                                   CELL_SIZE_H)
                # Рисуем на временной полупрозрачной поверхности для поддержки альфа-канала
                s = pygame.Surface((CELL_SIZE_W, CELL_SIZE_H), pygame.SRCALPHA)
                pygame.draw.rect(s, GRID_COLOR, s.get_rect(), 1)
                surface.blit(s, (rect.x, rect.y))