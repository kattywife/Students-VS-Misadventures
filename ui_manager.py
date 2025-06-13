# ui_manager.py

import pygame
from settings import *
from assets import load_image
from levels import LEVELS


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 40)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.font_tiny = pygame.font.SysFont('Arial', 18)
        self.font_large = pygame.font.SysFont('Arial', 72)

        self.shop_items = ['programmer', 'botanist', 'coffee_machine']
        self.shop_rects = {}
        self.shop_panel_surf = pygame.Surface((SCREEN_WIDTH, SHOP_PANEL_HEIGHT), pygame.SRCALPHA)
        self.pause_button_rect = pygame.Rect(SCREEN_WIDTH - 70, 10, 60, 60)
        self._create_shop()

    def _create_shop(self):
        self.shop_panel_surf.fill(DEFAULT_COLORS['shop_panel'])

        coffee_area_width = 180
        coffee_area_rect = pygame.Rect(0, 0, coffee_area_width, SHOP_PANEL_HEIGHT)
        pygame.draw.rect(self.shop_panel_surf, DEFAULT_COLORS['shop_card'], coffee_area_rect.inflate(-10, -10),
                         border_radius=10)

        coffee_icon = load_image('coffee_bean.png', DEFAULT_COLORS['coffee_bean'], (50, 50))
        icon_rect = coffee_icon.get_rect(midleft=(coffee_area_rect.left + 20, coffee_area_rect.centery))
        self.shop_panel_surf.blit(coffee_icon, icon_rect)

        shop_items_start_x = coffee_area_width
        for i, item_name in enumerate(self.shop_items):
            card_x = shop_items_start_x + i * (SHOP_CARD_SIZE + SHOP_ITEM_PADDING) + SHOP_ITEM_PADDING
            card_y = (SHOP_PANEL_HEIGHT - SHOP_CARD_SIZE) / 2
            card_rect = pygame.Rect(card_x, card_y, SHOP_CARD_SIZE, SHOP_CARD_SIZE)

            self.shop_rects[item_name] = card_rect

            pygame.draw.rect(self.shop_panel_surf, DEFAULT_COLORS['shop_card'], card_rect, border_radius=5)
            pygame.draw.rect(self.shop_panel_surf, DEFAULT_COLORS['shop_border'], card_rect, 3, border_radius=5)

            item_image = load_image(f'{item_name}.png', DEFAULT_COLORS[item_name],
                                    (SHOP_CARD_SIZE - 20, SHOP_CARD_SIZE - 20))
            img_rect = item_image.get_rect(center=card_rect.center)
            img_rect.y -= 10
            self.shop_panel_surf.blit(item_image, img_rect)

            cost_text = self.font_small.render(f"{DEFENDERS_DATA[item_name]['cost']}", True, WHITE)
            text_rect = cost_text.get_rect(center=(card_rect.centerx, card_rect.bottom - 15))
            self.shop_panel_surf.blit(cost_text, text_rect)

    def draw_shop(self, selected_defender, coffee_beans):
        self.screen.blit(self.shop_panel_surf, (0, 0))
        pygame.draw.rect(self.screen, DEFAULT_COLORS['shop_border'], (0, 0, SCREEN_WIDTH, SHOP_PANEL_HEIGHT), 5)

        coffee_text = self.font.render(f"{coffee_beans}", True, WHITE)
        text_rect = coffee_text.get_rect(midleft=(90, SHOP_PANEL_HEIGHT / 2))
        self.screen.blit(coffee_text, text_rect)

        if selected_defender:
            rect = self.shop_rects[selected_defender]
            pygame.draw.rect(self.screen, YELLOW, rect, 4, border_radius=5)

    def draw_hud(self, spawn_progress, kill_progress, spawn_count_data, kill_count_data):
        enemies_spawned, total_spawn = spawn_count_data
        enemies_killed, total_kill = kill_count_data

        bar_w, bar_h = 250, 20
        gap = 5

        # --- Шкала БРС (убитые враги, зеленая) ---
        brs_y = SCREEN_HEIGHT - bar_h - 20
        brs_x = SCREEN_WIDTH - bar_w - 20

        pygame.draw.rect(self.screen, GREY, (brs_x, brs_y, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(self.screen, GREEN, (brs_x, brs_y, bar_w * kill_progress, bar_h), border_radius=5)
        brs_text_surf = self.font_tiny.render(f"БРС: {enemies_killed} / {total_kill}", True, BLACK)
        brs_text_rect = brs_text_surf.get_rect(center=(brs_x + bar_w / 2, brs_y + bar_h / 2))
        self.screen.blit(brs_text_surf, brs_text_rect)
        pygame.draw.rect(self.screen, WHITE, (brs_x, brs_y, bar_w, bar_h), 2, border_radius=5)

        # --- Шкала Учебного плана (выпущенные враги, синяя) ---
        plan_y = brs_y - bar_h - gap
        plan_x = brs_x

        pygame.draw.rect(self.screen, GREY, (plan_x, plan_y, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(self.screen, PROGRESS_BLUE, (plan_x, plan_y, bar_w * spawn_progress, bar_h), border_radius=5)
        # Добавляем текстовый счетчик для этой шкалы
        plan_text_surf = self.font_tiny.render(f"Учебный план: {enemies_spawned} / {total_spawn}", True, WHITE)
        plan_text_rect = plan_text_surf.get_rect(center=(plan_x + bar_w / 2, plan_y + bar_h / 2))
        self.screen.blit(plan_text_surf, plan_text_rect)
        pygame.draw.rect(self.screen, WHITE, (plan_x, plan_y, bar_w, bar_h), 2, border_radius=5)
        # -------------------------------------------------------------

        # Кнопка паузы
        pygame.draw.rect(self.screen, DEFAULT_COLORS['pause_button'], self.pause_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.pause_button_rect, 2, border_radius=5)
        bar1 = pygame.Rect(self.pause_button_rect.centerx - 10, self.pause_button_rect.y + 15, 8, 30)
        bar2 = pygame.Rect(self.pause_button_rect.centerx + 2, self.pause_button_rect.y + 15, 8, 30)
        pygame.draw.rect(self.screen, BLACK, bar1)
        pygame.draw.rect(self.screen, BLACK, bar2)

    def draw_grid(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(GRID_START_X + col * CELL_SIZE_W,
                                   GRID_START_Y + row * CELL_SIZE_H,
                                   CELL_SIZE_W, CELL_SIZE_H)
                s = pygame.Surface((CELL_SIZE_W, CELL_SIZE_H), pygame.SRCALPHA)
                pygame.draw.rect(s, (255, 255, 255, 30), s.get_rect(), 1)
                self.screen.blit(s, (rect.x, rect.y))

    def draw_menu(self, title_text, buttons):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        self.screen.blit(title, title_rect)

        for name, rect in buttons.items():
            pygame.draw.rect(self.screen, DEFAULT_COLORS['button'], rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)
            text = self.font.render(name, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def draw_level_select(self, max_level_unlocked):
        title = self.font_large.render("Главное меню", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, 100))
        self.screen.blit(title, title_rect)

        buttons = {}
        for level_id, data in LEVELS.items():
            is_unlocked = level_id <= max_level_unlocked

            button_rect = pygame.Rect(0, 0, 400, 70)
            button_rect.center = (SCREEN_WIDTH / 2, 200 + (level_id - 1) * 90)

            color = YELLOW if is_unlocked else GREY
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2, border_radius=10)

            text_surf = self.font.render(data['name'], True, BLACK)
            text_rect = text_surf.get_rect(center=button_rect.center)
            self.screen.blit(text_surf, text_rect)

            if is_unlocked:
                buttons[level_id] = button_rect
        return buttons

    def draw_level_intro(self, enemy_types):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("Злоключения этого курса:", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, 150))
        self.screen.blit(title, title_rect)

        start_x = SCREEN_WIDTH / 2 - (len(enemy_types) - 1) * 120 / 2
        for i, enemy_type in enumerate(enemy_types):
            x = start_x + i * 120
            y = SCREEN_HEIGHT / 2

            img_size = (CELL_SIZE_W, CELL_SIZE_H)
            enemy_img = load_image(f'{enemy_type}.png', DEFAULT_COLORS[enemy_type], img_size)
            img_rect = enemy_img.get_rect(center=(x, y))
            self.screen.blit(enemy_img, img_rect)

            display_name = ENEMIES_DATA[enemy_type].get('display_name', enemy_type)
            name_surf = self.font_small.render(display_name, True, WHITE)
            name_rect = name_surf.get_rect(center=(x, y + CELL_SIZE_H / 2 + 20))
            self.screen.blit(name_surf, name_rect)

        start_button_rect = pygame.Rect(0, 0, 300, 80)
        start_button_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 150)
        pygame.draw.rect(self.screen, GREEN, start_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, start_button_rect, 2, border_radius=10)

        start_text = self.font_large.render("В Бой!", True, BLACK)
        text_rect = start_text.get_rect(center=start_button_rect.center)
        self.screen.blit(start_text, text_rect)

        return start_button_rect

    def handle_shop_click(self, pos):
        for name, rect in self.shop_rects.items():
            if rect.collidepoint(pos):
                return name
        return None