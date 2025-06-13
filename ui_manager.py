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
        self.font_huge = pygame.font.SysFont('Impact', 120)

        self.shop_items = ['programmer', 'botanist', 'coffee_machine']
        self.shop_rects = {}
        self.shop_panel_surf = pygame.Surface((SCREEN_WIDTH, SHOP_PANEL_HEIGHT), pygame.SRCALPHA)

        # ----- ИЗМЕНЕНИЕ: Делаем кнопку паузы больше и центрируем -----
        button_size = 80
        padding = 20
        # Рассчитываем y, чтобы кнопка была по центру панели
        button_y = (SHOP_PANEL_HEIGHT - button_size) / 2
        self.pause_button_rect = pygame.Rect(SCREEN_WIDTH - button_size - padding, button_y, button_size, button_size)
        # -------------------------------------------------------------

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

        # Шкала БРС
        brs_y = SCREEN_HEIGHT - bar_h - 20
        brs_x = SCREEN_WIDTH - bar_w - 20
        pygame.draw.rect(self.screen, GREY, (brs_x, brs_y, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(self.screen, GREEN, (brs_x, brs_y, bar_w * kill_progress, bar_h), border_radius=5)
        brs_text_surf = self.font_tiny.render(f"БРС: {enemies_killed} / {total_kill}", True, BLACK)
        brs_text_rect = brs_text_surf.get_rect(center=(brs_x + bar_w / 2, brs_y + bar_h / 2))
        self.screen.blit(brs_text_surf, brs_text_rect)
        pygame.draw.rect(self.screen, WHITE, (brs_x, brs_y, bar_w, bar_h), 2, border_radius=5)

        # Шкала Учебного плана
        plan_y = brs_y - bar_h - gap
        plan_x = brs_x
        pygame.draw.rect(self.screen, GREY, (plan_x, plan_y, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(self.screen, PROGRESS_BLUE, (plan_x, plan_y, bar_w * spawn_progress, bar_h), border_radius=5)
        plan_text_surf = self.font_tiny.render(f"Учебный план: {enemies_spawned} / {total_spawn}", True, WHITE)
        plan_text_rect = plan_text_surf.get_rect(center=(plan_x + bar_w / 2, plan_y + bar_h / 2))
        self.screen.blit(plan_text_surf, plan_text_rect)
        pygame.draw.rect(self.screen, WHITE, (plan_x, plan_y, bar_w, bar_h), 2, border_radius=5)

        # ----- ИЗМЕНЕНИЕ: Отрисовка обновленной кнопки паузы -----
        pygame.draw.rect(self.screen, DEFAULT_COLORS['pause_button'], self.pause_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.pause_button_rect, 2, border_radius=10)
        # Рисуем две вертикальные полоски внутри кнопки
        bar_width = 10
        bar_height = 40
        bar1 = pygame.Rect(0, 0, bar_width, bar_height)
        bar1.center = (self.pause_button_rect.centerx - 12, self.pause_button_rect.centery)
        bar2 = pygame.Rect(0, 0, bar_width, bar_height)
        bar2.center = (self.pause_button_rect.centerx + 12, self.pause_button_rect.centery)
        pygame.draw.rect(self.screen, BLACK, bar1, border_radius=3)
        pygame.draw.rect(self.screen, BLACK, bar2, border_radius=3)
        # --------------------------------------------------------
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

    # ----- НОВЫЙ МЕТОД ДЛЯ ГЛАВНОГО МЕНЮ -----
    def draw_main_menu(self, max_level_unlocked):
        # --- 1. Левая панель для выбора уровней ---
        panel_width = 500
        panel_height = 600
        panel_x = 100
        panel_y = (SCREEN_HEIGHT - panel_height) / 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        # Рисуем фон и рамку панели
        pygame.draw.rect(self.screen, DEFAULT_COLORS['shop_panel'], panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3, border_radius=15)

        # Заголовок внутри панели
        title = self.font_large.render("Выбор курса", True, WHITE)
        title_rect = title.get_rect(center=(panel_rect.centerx, panel_rect.top + 70))
        self.screen.blit(title, title_rect)

        # Кнопки уровней внутри панели
        level_buttons = {}
        for level_id, data in LEVELS.items():
            is_unlocked = level_id <= max_level_unlocked
            button_rect = pygame.Rect(0, 0, 400, 70)
            # Позиционируем относительно панели
            button_rect.center = (panel_rect.centerx, panel_rect.top + 180 + (level_id - 1) * 85)

            color = YELLOW if is_unlocked else GREY
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2, border_radius=10)

            text_surf = self.font.render(data['name'], True, BLACK)
            text_rect = text_surf.get_rect(center=button_rect.center)
            self.screen.blit(text_surf, text_rect)

            if is_unlocked:
                level_buttons[level_id] = button_rect

        # --- 2. Правые кнопки управления ---
        control_buttons = {}
        btn_width, btn_height = 300, 90
        btn_x = SCREEN_WIDTH - btn_width - 150

        # Кнопка Настройки
        settings_rect = pygame.Rect(btn_x, 250, btn_width, btn_height)
        pygame.draw.rect(self.screen, DEFAULT_COLORS['button'], settings_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, settings_rect, 2, border_radius=10)
        settings_text = self.font_large.render("?", True, WHITE)  # Пока просто знак вопроса
        self.screen.blit(settings_text, settings_text.get_rect(center=settings_rect.center))
        control_buttons["Настройки"] = settings_rect

        # Кнопка Выход
        exit_rect = pygame.Rect(btn_x, settings_rect.bottom + 30, btn_width, btn_height)
        pygame.draw.rect(self.screen, DEFAULT_COLORS['button'], exit_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, exit_rect, 2, border_radius=10)
        exit_text = self.font.render("Выход", True, WHITE)
        self.screen.blit(exit_text, exit_text.get_rect(center=exit_rect.center))
        control_buttons["Выход"] = exit_rect

        return level_buttons, control_buttons

    def draw_level_clear_message(self):
        text_surf = self.font_huge.render("БРС: 100/100", True, YELLOW)

        # Добавим тень для текста
        shadow_surf = self.font_huge.render("БРС: 100/100", True, BLACK)
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH / 2 + 5, SCREEN_HEIGHT / 2 + 5))
        self.screen.blit(shadow_surf, shadow_rect)

        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.screen.blit(text_surf, text_rect)

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