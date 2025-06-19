# ui/battle_hud_renderer.py

import pygame
from data.settings import *
from data.assets import CARD_IMAGES
from .base_component import BaseUIComponent


class BattleHUDRenderer(BaseUIComponent):
    """
    Отвечает за отрисовку всего боевого интерфейса (HUD).
    Сюда входит верхняя панель магазина с юнитами и ресурсами,
    нижние элементы HUD (прогресс-бары, кнопка паузы) и всплывающие
    уведомления (например, о "напастях").
    """

    def __init__(self, screen):
        """
        Инициализирует рендерер боевого интерфейса.

        Args:
            screen (pygame.Surface): Основная поверхность для отрисовки.
        """
        super().__init__(screen)
        # Атрибуты для магазина
        self.shop_items = []  # Список типов юнитов в магазине
        self.shop_rects = {}  # Словарь для хранения Rect'ов карточек для обработки кликов
        # Поверхность для кэширования статической части магазина (для производительности)
        self.shop_panel_surf = pygame.Surface((SCREEN_WIDTH, SHOP_PANEL_HEIGHT), pygame.SRCALPHA)

        # Кэширование Rect'а кнопки паузы
        self.pause_button_rect = pygame.Rect(
            SCREEN_WIDTH + PAUSE_BUTTON_X_OFFSET,
            (SHOP_PANEL_HEIGHT - PAUSE_BUTTON_SIZE[1]) / 2,
            *PAUSE_BUTTON_SIZE
        )

    def create_shop_surface(self, team):
        """
        Создает и кэширует статическую часть панели магазина.

        Этот метод вызывается один раз в начале боя. Он отрисовывает фон панели,
        область для счетчика кофе и пустые слоты для карточек юнитов.
        Это оптимизация, позволяющая не перерисовывать эти элементы каждый кадр.

        Args:
            team (list): Список типов защитников, доступных для покупки.
        """
        self.shop_items = team
        self.shop_rects = {}  # Очищаем Rect'ы от предыдущего боя
        self.shop_panel_surf.fill(DEFAULT_COLORS['shop_panel'])

        # Отрисовка области для счетчика кофе
        coffee_area_rect = pygame.Rect(0, 0, SHOP_COFFEE_AREA_WIDTH, SHOP_PANEL_HEIGHT)
        pygame.draw.rect(self.shop_panel_surf, DEFAULT_COLORS['shop_card'], coffee_area_rect.inflate(-10, -10),
                         border_radius=DEFAULT_BORDER_RADIUS)
        coffee_icon = CARD_IMAGES.get('coffee_bean')
        if coffee_icon:
            coffee_icon_scaled = pygame.transform.scale(coffee_icon, SHOP_COFFEE_ICON_SIZE)
            icon_rect = coffee_icon_scaled.get_rect(
                midleft=(coffee_area_rect.left + SHOP_COFFEE_ICON_X_OFFSET, coffee_area_rect.centery))
            self.shop_panel_surf.blit(coffee_icon_scaled, icon_rect)

        # Отрисовка слотов для карточек юнитов
        shop_items_start_x = SHOP_COFFEE_AREA_WIDTH
        for i, item_name in enumerate(self.shop_items):
            card_x = shop_items_start_x + i * (SHOP_CARD_SIZE + SHOP_ITEM_PADDING) + SHOP_ITEM_PADDING
            card_y = (SHOP_PANEL_HEIGHT - SHOP_CARD_SIZE) / 2
            card_rect = pygame.Rect(card_x, card_y, SHOP_CARD_SIZE, SHOP_CARD_SIZE)
            self.shop_rects[item_name] = card_rect

            # Рисуем фон и рамку карточки на кэшируемую поверхность
            pygame.draw.rect(self.shop_panel_surf, DEFAULT_COLORS['shop_card'], card_rect,
                             border_radius=SHOP_CARD_BORDER_RADIUS)
            pygame.draw.rect(self.shop_panel_surf, DEFAULT_COLORS['shop_border'], card_rect, THICK_BORDER_WIDTH,
                             border_radius=SHOP_CARD_BORDER_RADIUS)

    def draw_shop(self, surface, selected_defender, coffee, upgrades):
        """
        Отрисовывает всю панель магазина, включая динамические элементы.

        Сначала накладывается кэшированная поверхность, а затем поверх нее
        рисуются изменяющиеся элементы: счетчик кофе, иконки юнитов, их стоимость
        и рамки для выделения улучшенных или выбранных юнитов.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            selected_defender (str | None): Тип юнита, который выбран игроком.
            coffee (int): Текущее количество ресурса "кофе".
            upgrades (dict): Словарь с информацией об улучшениях юнитов.
        """
        # Отрисовка статической части
        surface.blit(self.shop_panel_surf, (0, 0))
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_border'], (0, 0, SCREEN_WIDTH, SHOP_PANEL_HEIGHT),
                         SHOP_BORDER_THICKNESS)

        # Отрисовка динамического счетчика кофе
        coffee_text = self.fonts['default'].render(str(coffee), True, WHITE)
        text_rect = coffee_text.get_rect(midleft=(SHOP_COFFEE_TEXT_X_OFFSET, SHOP_PANEL_HEIGHT / 2))
        surface.blit(coffee_text, text_rect)

        # Отрисовка рамок для улучшенных и выбранных юнитов
        for hero_type in self.shop_items:
            rect = self.shop_rects[hero_type]
            if hero_type in upgrades:
                pygame.draw.rect(surface, AURA_PINK, rect, SHOP_UPGRADE_BORDER_WIDTH,
                                 border_radius=SHOP_CARD_BORDER_RADIUS)
            if hero_type == selected_defender:
                pygame.draw.rect(surface, YELLOW, rect, SHOP_SELECTED_BORDER_WIDTH,
                                 border_radius=SHOP_CARD_BORDER_RADIUS)

        # Отрисовка изображений и стоимости юнитов
        for item_name in self.shop_items:
            card_rect = self.shop_rects[item_name]
            item_image = CARD_IMAGES.get(item_name)
            if item_image:
                img_rect = item_image.get_rect(center=card_rect.center)
                img_rect.y += SHOP_CARD_IMG_Y_OFFSET
                surface.blit(item_image, img_rect)

            cost_text = self.fonts['small'].render(str(DEFENDERS_DATA[item_name]['cost']), True, WHITE)
            cost_rect = cost_text.get_rect(center=(card_rect.centerx, card_rect.bottom + SHOP_CARD_COST_Y_OFFSET))
            surface.blit(cost_text, cost_rect)

    def draw_hud_elements(self, surface, spawn_progress, kill_progress, spawn_data, kill_data, notification):
        """
        Отрисовывает все элементы HUD, кроме верхней панели магазина.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            spawn_progress (float): Прогресс появления врагов (от 0.0 до 1.0).
            kill_progress (float): Прогресс убийства врагов (от 0.0 до 1.0).
            spawn_data (tuple): Кортеж (spawned, total) для текста на баре.
            kill_data (tuple): Кортеж (killed, total) для текста на баре.
            notification (dict | None): Данные для отображения уведомления о напасти.
        """
        self._draw_progress_bars(surface, spawn_progress, kill_progress, spawn_data, kill_data)
        self._draw_pause_button(surface)
        if notification:
            self._draw_calamity_notification(surface, notification)

    def _draw_progress_bars(self, surface, spawn_progress, kill_progress, spawn_data, kill_data):
        """Отрисовывает два прогресс-бара: "Учебный план" и "БРС"."""
        spawned, total_spawn = spawn_data
        killed, total_kill = kill_data

        bar_x = SCREEN_WIDTH - HUD_BAR_WIDTH - HUD_RIGHT_MARGIN
        # Бар "БРС" (Балльно-рейтинговая система) - прогресс убийства врагов
        brs_y = SCREEN_HEIGHT - HUD_BAR_HEIGHT - HUD_BOTTOM_MARGIN
        self._draw_single_progress_bar(surface, (bar_x, brs_y), kill_progress, GREEN, f"БРС: {killed} / {total_kill}",
                                       BLACK)

        # Бар "Учебный план" - прогресс появления врагов
        plan_y = brs_y - HUD_BAR_HEIGHT - HUD_BAR_V_GAP
        self._draw_single_progress_bar(surface, (bar_x, plan_y), spawn_progress, PROGRESS_BLUE,
                                       f"Учебный план: {spawned} / {total_spawn}", WHITE)

    def _draw_single_progress_bar(self, surface, pos, progress, color, text, text_color):
        """Вспомогательный метод для отрисовки одного прогресс-бара."""
        x, y = pos
        bar_rect = pygame.Rect(x, y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT)
        progress_rect = pygame.Rect(x, y, HUD_BAR_WIDTH * progress, HUD_BAR_HEIGHT)

        # Рисуем фон и полосу прогресса
        pygame.draw.rect(surface, GREY, bar_rect, border_radius=5)
        pygame.draw.rect(surface, color, progress_rect, border_radius=5)

        # Рисуем текст поверх бара
        text_surf = self.fonts['tiny'].render(text, True, text_color)
        text_rect = text_surf.get_rect(center=bar_rect.center)
        surface.blit(text_surf, text_rect)

        # Рисуем рамку
        pygame.draw.rect(surface, WHITE, bar_rect, DEFAULT_BORDER_WIDTH, border_radius=5)

    def _draw_pause_button(self, surface):
        """Отрисовывает кнопку паузы."""
        pygame.draw.rect(surface, DEFAULT_COLORS['pause_button'], self.pause_button_rect,
                         border_radius=DEFAULT_BORDER_RADIUS)
        pygame.draw.rect(surface, WHITE, self.pause_button_rect, DEFAULT_BORDER_WIDTH,
                         border_radius=DEFAULT_BORDER_RADIUS)
        # Рисуем две вертикальные полоски - символ паузы
        bar1 = pygame.Rect(0, 0, PAUSE_BAR_WIDTH, PAUSE_BAR_HEIGHT)
        bar1.center = (self.pause_button_rect.centerx - PAUSE_BAR_H_SPACING, self.pause_button_rect.centery)
        bar2 = pygame.Rect(0, 0, PAUSE_BAR_WIDTH, PAUSE_BAR_HEIGHT)
        bar2.center = (self.pause_button_rect.centerx + PAUSE_BAR_H_SPACING, self.pause_button_rect.centery)
        pygame.draw.rect(surface, BLACK, bar1, border_radius=3)
        pygame.draw.rect(surface, BLACK, bar2, border_radius=3)

    def _draw_calamity_notification(self, surface, notification):
        """Отрисовывает всплывающее окно с информацией о начавшейся "напасти"."""
        # Создаем полупрозрачную панель
        panel_rect = pygame.Rect((0, 0), CALAMITY_PANEL_SIZE)
        panel_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel_surf.fill(CALAMITY_PANEL_BG)
        surface.blit(panel_surf, panel_rect.topleft)
        pygame.draw.rect(surface, CALAMITY_BORDER_RED, panel_rect, CALAMITY_PANEL_BORDER_WIDTH,
                         border_radius=CALAMITY_PANEL_BORDER_RADIUS)

        # Иконка напасти слева
        icon = CARD_IMAGES.get(notification['type'])
        icon_rect = None
        if icon:
            icon = pygame.transform.scale(icon, CALAMITY_ICON_SIZE)
            icon_rect = icon.get_rect(centery=panel_rect.centery, left=panel_rect.left + CALAMITY_ICON_LEFT_MARGIN)
            surface.blit(icon, icon_rect)

        # Область для текста справа от иконки
        text_area_left = (icon_rect.right if icon_rect else panel_rect.left) + CALAMITY_TEXT_LEFT_MARGIN
        max_text_width = (panel_rect.right - CALAMITY_TEXT_LEFT_MARGIN) - text_area_left

        # Название напасти
        name_surf = self.fonts['large'].render(notification['name'], True, CALAMITY_ORANGE)
        name_rect = name_surf.get_rect(left=text_area_left, top=panel_rect.top + CALAMITY_NAME_TOP_MARGIN)
        surface.blit(name_surf, name_rect)

        # Описание напасти с переносом строк
        wrapped_lines = self._render_text_wrapped(notification['desc'], self.fonts['small'], WHITE, max_text_width)
        current_y = name_rect.bottom + CALAMITY_DESC_TOP_MARGIN
        for line_surf in wrapped_lines:
            line_rect = line_surf.get_rect(left=text_area_left, top=current_y)
            surface.blit(line_surf, line_rect)
            current_y += line_surf.get_height()

    def handle_click(self, pos):
        """
        Проверяет клик по элементам HUD.

        Args:
            pos (tuple): Координаты (x, y) клика.

        Returns:
            str | None: Имя кликнутого элемента ('pause_button' или тип юнита) или None.
        """
        if self.pause_button_rect.collidepoint(pos):
            return 'pause_button'
        # Проверяем клик по каждой карточке в магазине
        for name, rect in self.shop_rects.items():
            if rect.collidepoint(pos):
                return name
        return None