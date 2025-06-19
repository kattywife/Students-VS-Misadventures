# ui/neuro_placement_renderer.py

import pygame
from data.settings import *
from data.assets import CARD_IMAGES
from .base_component import BaseUIComponent


class NeuroPlacementRenderer(BaseUIComponent):
    """Отвечает за отрисовку экрана расстановки нейросетей."""

    def __init__(self, screen):
        super().__init__(screen)
        self.placement_grid_start_y = (SCREEN_HEIGHT - GRID_ROWS * PLACEMENT_GRID_CELL_H) / 2

    def draw(self, surface, background, purchased_mowers, placed_mowers, dragged_mower_info):
        """Основной метод отрисовки экрана."""
        surface.blit(background, (0, 0))
        self._draw_placement_grid(surface)
        self._draw_placement_slots(surface)

        for row, info in placed_mowers.items():
            self._draw_placed_mower(surface, row, info)

        unplaced_rects, start_rect = self._draw_selection_panel(surface, purchased_mowers, placed_mowers)

        if dragged_mower_info:
            self._draw_dragged_mower(surface, dragged_mower_info)

        return unplaced_rects, start_rect

    def _draw_placement_grid(self, surface):
        """Отрисовка основной сетки поля боя."""
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(PLACEMENT_GRID_START_X + col * PLACEMENT_GRID_CELL_W,
                                   self.placement_grid_start_y + row * PLACEMENT_GRID_CELL_H,
                                   PLACEMENT_GRID_CELL_W, PLACEMENT_GRID_CELL_H)
                s = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(s, GRID_COLOR, s.get_rect(), 1)
                surface.blit(s, rect.topleft)

    def _draw_placement_slots(self, surface):
        """Отрисовка слотов для нейросетей слева."""
        for row in range(GRID_ROWS):
            slot_rect = pygame.Rect(PLACEMENT_ZONE_X, self.placement_grid_start_y + row * PLACEMENT_GRID_CELL_H,
                                    PLACEMENT_GRID_CELL_W, PLACEMENT_GRID_CELL_H)
            pygame.draw.rect(surface, (*BLACK, PLACEMENT_MOWER_SLOT_ALPHA), slot_rect,
                             border_radius=DEFAULT_BORDER_RADIUS)
            pygame.draw.rect(surface, PLACEMENT_MOWER_SLOT_BORDER_COLOR, slot_rect, DEFAULT_BORDER_WIDTH,
                             border_radius=DEFAULT_BORDER_RADIUS)

    def _draw_placed_mower(self, surface, row, info):
        """Отрисовка уже размещенной нейросети."""
        img = CARD_IMAGES.get(info['type'])
        if img:
            img = pygame.transform.scale(img, (
            PLACEMENT_GRID_CELL_W - PLACEMENT_MOWER_IMG_PADDING, PLACEMENT_GRID_CELL_H - PLACEMENT_MOWER_IMG_PADDING))
            rect = img.get_rect(
                centerx=PLACEMENT_ZONE_X + PLACEMENT_GRID_CELL_W / 2,
                centery=self.placement_grid_start_y + row * PLACEMENT_GRID_CELL_H + PLACEMENT_GRID_CELL_H / 2
            )
            surface.blit(img, rect)

    def _draw_selection_panel(self, surface, purchased_mowers, placed_mowers):
        """Отрисовка центральной панели с выбором нейросетей."""
        panel_rect = pygame.Rect((0, 0), PLACEMENT_PANEL_SIZE)
        panel_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self._draw_panel_with_title(surface, panel_rect, "Расставьте нейросети по рядам")

        unplaced_rects = self._draw_unplaced_mowers(surface, panel_rect, purchased_mowers, placed_mowers)
        start_button_rect = self._draw_start_button(surface, panel_rect, len(purchased_mowers) == len(placed_mowers))

        return unplaced_rects, start_button_rect

    def _draw_unplaced_mowers(self, surface, panel_rect, purchased_mowers, placed_mowers):
        unplaced_rects = {}
        placed_indices = [info.get('original_index') for info in placed_mowers.values()]
        unplaced_list = [(i, m) for i, m in enumerate(purchased_mowers) if i not in placed_indices]

        card_size, padding, cols = PLACEMENT_PANEL_CARD_SIZE, PLACEMENT_PANEL_CARD_PADDING, PLACEMENT_PANEL_CARD_COLS
        start_x = panel_rect.left + (panel_rect.width - (cols * card_size + (cols - 1) * padding)) / 2
        start_y = panel_rect.top + PLACEMENT_PANEL_CARDS_TOP_OFFSET

        for i, (original_index, mower_type) in enumerate(unplaced_list):
            row, col = divmod(i, cols)
            x = start_x + col * (card_size + padding)
            y = start_y + row * (card_size + padding)
            rect = pygame.Rect(x, y, card_size, card_size)
            self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])
            unplaced_rects[original_index] = rect

        return unplaced_rects

    def _draw_start_button(self, surface, panel_rect, can_start):
        start_button_rect = pygame.Rect((0, 0), PLACEMENT_PANEL_START_BTN_SIZE)
        start_button_rect.center = (panel_rect.centerx, panel_rect.bottom + PLACEMENT_PANEL_START_BTN_TOP_OFFSET)

        color = GREEN if can_start else GREY
        text_color = BLACK if can_start else DARK_GREY
        self._draw_button(surface, "В Бой!", start_button_rect, color, text_color, self.fonts['large'])

        return start_button_rect if can_start else None

    def _draw_dragged_mower(self, surface, dragged_mower_info):
        """Отрисовка перетаскиваемой нейросети."""
        pos, mower_type = dragged_mower_info['pos'], dragged_mower_info['type']
        rect = pygame.Rect((0, 0), (PLACEMENT_PANEL_CARD_SIZE, PLACEMENT_PANEL_CARD_SIZE))
        rect.center = pos
        self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])

    def _draw_unit_card(self, surface, unit_type, rect, data):
        """Отрисовывает карточку юнита (нейросети)."""
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_card'], rect, border_radius=DEFAULT_BORDER_RADIUS)
        img = CARD_IMAGES.get(unit_type)
        if img:
            img_scaled = pygame.transform.scale(img, (
            rect.width - PLACEMENT_MOWER_CARD_IMG_PADDING, rect.height - PLACEMENT_MOWER_CARD_IMG_PADDING))
            surface.blit(img_scaled, img_scaled.get_rect(center=rect.center))