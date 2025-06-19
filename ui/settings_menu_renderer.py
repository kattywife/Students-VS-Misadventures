# ui/settings_menu_renderer.py

import pygame
from data.settings import *
from data.assets import UI_IMAGES
from ui.base_component import BaseUIComponent


class SettingsMenuRenderer(BaseUIComponent):
    """Отвечает за отрисовку всплывающего меню настроек."""

    def __init__(self, screen):
        super().__init__(screen)
        self.panel_rect = pygame.Rect(
            (SCREEN_WIDTH - SETTINGS_PANEL_SIZE[0]) / 2,
            (SCREEN_HEIGHT - SETTINGS_PANEL_SIZE[1]) / 2,
            *SETTINGS_PANEL_SIZE
        )

    def draw(self, surface, music_enabled, sfx_enabled):
        """
        Отрисовывает меню настроек.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            music_enabled (bool): Включена ли музыка.
            sfx_enabled (bool): Включены ли звуковые эффекты.

        Returns:
            dict: Словарь с Rect'ами кликабельных элементов ('toggle_music', 'toggle_sfx', 'close').
        """
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MENU_OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))

        # Отрисовка основной панели
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], self.panel_rect, border_radius=SETTINGS_BORDER_RADIUS)
        pygame.draw.rect(surface, WHITE, self.panel_rect, THICK_BORDER_WIDTH, border_radius=SETTINGS_BORDER_RADIUS)

        title_surf = self.fonts['large'].render("Настройки", True, WHITE)
        title_rect = title_surf.get_rect(centerx=self.panel_rect.centerx,
                                         top=self.panel_rect.top + SETTINGS_TITLE_TOP_MARGIN)
        surface.blit(title_surf, title_rect)

        buttons = {}
        buttons.update(
            self._draw_toggle(surface, "Фоновая музыка", music_enabled, -SETTINGS_LABEL_V_OFFSET, 'toggle_music'))
        buttons.update(
            self._draw_toggle(surface, "Звуковые эффекты", sfx_enabled, SETTINGS_LABEL_V_OFFSET, 'toggle_sfx'))
        buttons['close'] = self._draw_close_button(surface)

        return buttons

    def _draw_toggle(self, surface, label_text, is_enabled, y_offset, button_key):
        """Отрисовывает одну строку с текстом и переключателем."""
        # Текст
        label_surf = self.fonts['default'].render(label_text, True, WHITE)
        label_rect = label_surf.get_rect(
            midleft=(self.panel_rect.left + SETTINGS_LABEL_LEFT_MARGIN, self.panel_rect.centery + y_offset)
        )
        surface.blit(label_surf, label_rect)

        # Изображение переключателя
        toggle_img = UI_IMAGES['toggle_on'] if is_enabled else UI_IMAGES['toggle_off']
        toggle_rect = toggle_img.get_rect(
            midright=(self.panel_rect.right - SETTINGS_TOGGLE_RIGHT_MARGIN, label_rect.centery)
        )
        surface.blit(toggle_img, toggle_rect)

        return {button_key: toggle_rect}

    def _draw_close_button(self, surface):
        """Отрисовывает кнопку закрытия (крестик)."""
        close_rect = pygame.Rect(
            self.panel_rect.right - SETTINGS_CLOSE_BUTTON_SIZE - SETTINGS_CLOSE_BUTTON_MARGIN,
            self.panel_rect.top + SETTINGS_CLOSE_BUTTON_MARGIN,
            SETTINGS_CLOSE_BUTTON_SIZE, SETTINGS_CLOSE_BUTTON_SIZE
        )

        pygame.draw.line(surface, WHITE, close_rect.topleft, close_rect.bottomright, SETTINGS_CLOSE_BUTTON_LINE_WIDTH)
        pygame.draw.line(surface, WHITE, close_rect.topright, close_rect.bottomleft, SETTINGS_CLOSE_BUTTON_LINE_WIDTH)

        return close_rect