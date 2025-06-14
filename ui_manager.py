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

        # --- Ректы для кликов на экране подготовки ---
        self.team_panel_rect = pygame.Rect(50, 50, 300, SCREEN_HEIGHT - 100)
        self.selection_panel_rect = pygame.Rect(self.team_panel_rect.right + 20, 50, 460, SCREEN_HEIGHT - 100)
        self.field_panel_rect = pygame.Rect(self.selection_panel_rect.right + 20, 50, 400, SCREEN_HEIGHT - 100)
        self.selection_cards_rects = {}
        self.team_card_rects = {}
        self.upgrade_buttons = {}

        # --- Переменные для магазина в бою ---
        self.shop_items = []
        self.shop_rects = {}
        self.shop_panel_surf = pygame.Surface((SCREEN_WIDTH, SHOP_PANEL_HEIGHT), pygame.SRCALPHA)
        self.pause_button_rect = pygame.Rect(SCREEN_WIDTH - 130, (SHOP_PANEL_HEIGHT - 80) / 2, 80, 80)

    def create_battle_shop(self, team):
        self.shop_items = team
        self.shop_rects = {}
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

    def draw_shop(self, surface, selected_defender, coffee_beans):
        surface.blit(self.shop_panel_surf, (0, 0))
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_border'], (0, 0, SCREEN_WIDTH, SHOP_PANEL_HEIGHT), 5)
        coffee_text = self.font.render(f"{coffee_beans}", True, WHITE)
        text_rect = coffee_text.get_rect(midleft=(90, SHOP_PANEL_HEIGHT / 2))
        surface.blit(coffee_text, text_rect)
        if selected_defender:
            rect = self.shop_rects[selected_defender]
            pygame.draw.rect(surface, YELLOW, rect, 4, border_radius=5)

    def draw_hud(self, surface, spawn_progress, kill_progress, spawn_count_data, kill_count_data):
        enemies_spawned, total_spawn = spawn_count_data
        enemies_killed, total_kill = kill_count_data
        bar_w, bar_h, gap = 250, 20, 5
        brs_y = SCREEN_HEIGHT - bar_h - 20
        brs_x = SCREEN_WIDTH - bar_w - 20
        pygame.draw.rect(surface, GREY, (brs_x, brs_y, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(surface, GREEN, (brs_x, brs_y, bar_w * kill_progress, bar_h), border_radius=5)
        brs_text_surf = self.font_tiny.render(f"БРС: {enemies_killed} / {total_kill}", True, BLACK)
        surface.blit(brs_text_surf, brs_text_surf.get_rect(center=(brs_x + bar_w / 2, brs_y + bar_h / 2)))
        pygame.draw.rect(surface, WHITE, (brs_x, brs_y, bar_w, bar_h), 2, border_radius=5)
        plan_y, plan_x = brs_y - bar_h - gap, brs_x
        pygame.draw.rect(surface, GREY, (plan_x, plan_y, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(surface, PROGRESS_BLUE, (plan_x, plan_y, bar_w * spawn_progress, bar_h), border_radius=5)
        plan_text_surf = self.font_tiny.render(f"Учебный план: {enemies_spawned} / {total_spawn}", True, WHITE)
        surface.blit(plan_text_surf, plan_text_surf.get_rect(center=(plan_x + bar_w / 2, plan_y + bar_h / 2)))
        pygame.draw.rect(surface, WHITE, (plan_x, plan_y, bar_w, bar_h), 2, border_radius=5)
        pygame.draw.rect(surface, DEFAULT_COLORS['pause_button'], self.pause_button_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.pause_button_rect, 2, border_radius=10)
        bar1 = pygame.Rect(0, 0, 10, 40)
        bar1.center = (self.pause_button_rect.centerx - 12, self.pause_button_rect.centery)
        bar2 = pygame.Rect(0, 0, 10, 40)
        bar2.center = (self.pause_button_rect.centerx + 12, self.pause_button_rect.centery)
        pygame.draw.rect(surface, BLACK, bar1, border_radius=3)
        pygame.draw.rect(surface, BLACK, bar2, border_radius=3)

    def draw_grid(self, surface):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(GRID_START_X + col * CELL_SIZE_W, GRID_START_Y + row * CELL_SIZE_H, CELL_SIZE_W,
                                   CELL_SIZE_H)
                s = pygame.Surface((CELL_SIZE_W, CELL_SIZE_H), pygame.SRCALPHA)
                pygame.draw.rect(s, (255, 255, 255, 30), s.get_rect(), 1)
                surface.blit(s, (rect.x, rect.y))

    def draw_menu(self, surface, title_text, buttons):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        title = self.font_large.render(title_text, True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)))
        for name, rect in buttons.items():
            pygame.draw.rect(surface, DEFAULT_COLORS['button'], rect, border_radius=10)
            pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
            text = self.font.render(name, True, WHITE)
            surface.blit(text, text.get_rect(center=rect.center))

    def draw_main_menu(self, surface, max_level_unlocked):
        panel_rect = pygame.Rect(100, (SCREEN_HEIGHT - 600) / 2, 500, 600)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], panel_rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, panel_rect, 3, border_radius=15)
        title = self.font_large.render("Главное меню", True, WHITE)
        surface.blit(title, title.get_rect(center=(panel_rect.centerx, panel_rect.top + 70)))
        level_buttons = {}
        for level_id, data in LEVELS.items():
            is_unlocked = level_id <= max_level_unlocked
            button_rect = pygame.Rect(0, 0, 400, 70)
            button_rect.center = (panel_rect.centerx, panel_rect.top + 180 + (level_id - 1) * 85)
            color = YELLOW if is_unlocked else GREY
            pygame.draw.rect(surface, color, button_rect, border_radius=10)
            pygame.draw.rect(surface, WHITE, button_rect, 2, border_radius=10)
            text_surf = self.font.render(data['name'], True, BLACK)
            surface.blit(text_surf, text_surf.get_rect(center=button_rect.center))
            if is_unlocked:
                level_buttons[level_id] = button_rect
        control_buttons = {}
        btn_width, btn_height = 300, 90
        btn_x = SCREEN_WIDTH - btn_width - 150
        settings_rect = pygame.Rect(btn_x, 250, btn_width, btn_height)
        pygame.draw.rect(surface, DEFAULT_COLORS['button'], settings_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, settings_rect, 2, border_radius=10)
        settings_text = self.font.render("Настройки", True, WHITE)
        surface.blit(settings_text, settings_text.get_rect(center=settings_rect.center))
        control_buttons["Настройки"] = settings_rect
        exit_rect = pygame.Rect(btn_x, settings_rect.bottom + 30, btn_width, btn_height)
        pygame.draw.rect(surface, DEFAULT_COLORS['button'], exit_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, exit_rect, 2, border_radius=10)
        exit_text = self.font.render("Выход", True, WHITE)
        surface.blit(exit_text, exit_text.get_rect(center=exit_rect.center))
        control_buttons["Выход"] = exit_rect
        return level_buttons, control_buttons

    def draw_level_clear_message(self, surface):
        text_surf = self.font_huge.render("БРС: 100/100", True, YELLOW)
        shadow_surf = self.font_huge.render("БРС: 100/100", True, BLACK)
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(SCREEN_WIDTH / 2 + 5, SCREEN_HEIGHT / 2 + 5)))
        surface.blit(text_surf, text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))

    def draw_character_intro_screen(self, surface, defender_types, enemy_types, selected_card_data):
        surface.fill(DEFAULT_COLORS['background'])
        left_panel_rect = pygame.Rect(50, 50, 580, SCREEN_HEIGHT - 120)
        right_panel_rect = pygame.Rect(left_panel_rect.right + 20, 50, 580, SCREEN_HEIGHT - 120)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], left_panel_rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, left_panel_rect, 3, border_radius=15)
        title_left = self.font.render("Знакомство с коллективом", True, WHITE)
        surface.blit(title_left, title_left.get_rect(center=(left_panel_rect.centerx, left_panel_rect.top + 40)))
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], right_panel_rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, right_panel_rect, 3, border_radius=15)
        title_right = self.font.render("Учебный план", True, YELLOW)
        surface.blit(title_right, title_right.get_rect(center=(right_panel_rect.centerx, right_panel_rect.top + 40)))
        defender_card_rects = self._draw_cards_on_panel(surface, left_panel_rect, defender_types, DEFENDERS_DATA)
        enemy_card_rects = self._draw_cards_on_panel(surface, right_panel_rect, enemy_types, ENEMIES_DATA)
        start_button_rect = pygame.Rect(0, 0, 300, 80)
        start_button_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50)
        close_button_rect = None
        if selected_card_data:
            close_button_rect = self._draw_description_panel(surface, selected_card_data)
            pygame.draw.rect(surface, GREY, start_button_rect, border_radius=10)
        else:
            pygame.draw.rect(surface, GREEN, start_button_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, start_button_rect, 2, border_radius=10)
        start_text = self.font_large.render("В Бой!", True, BLACK)
        surface.blit(start_text, start_text.get_rect(center=start_button_rect.center))
        return defender_card_rects, enemy_card_rects, start_button_rect, close_button_rect

    def _draw_cards_on_panel(self, surface, panel_rect, types, data_source):
        card_rects = {}
        card_size = 100
        padding = 20
        cols = 4
        for i, item_type in enumerate(types):
            row, col = divmod(i, cols)
            x = panel_rect.left + padding + col * (card_size + padding)
            y = panel_rect.top + 80 + row * (card_size + padding + 40)
            card_rect = pygame.Rect(x, y, card_size, card_size)
            card_rects[item_type] = card_rect
            pygame.draw.rect(surface, DEFAULT_COLORS['shop_card'], card_rect, border_radius=10)
            img = load_image(f"{item_type}.png", DEFAULT_COLORS[item_type], (card_size - 10, card_size - 10))
            surface.blit(img, img.get_rect(center=card_rect.center))
            name = data_source[item_type].get('display_name', item_type)
            wrapped_name_lines = self._render_text_wrapped(name, self.font_tiny, WHITE, card_size + 5)
            line_y = card_rect.bottom + 5
            for line_surf in wrapped_name_lines:
                surface.blit(line_surf, line_surf.get_rect(centerx=card_rect.centerx, top=line_y))
                line_y += line_surf.get_height()
        return card_rects

    def _draw_description_panel(self, surface, card_data):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        panel_w, panel_h = 700, 500
        panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
        panel_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], panel_rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, panel_rect, 3, border_radius=15)
        img_size = 150
        img = load_image(f"{card_data['type']}.png", DEFAULT_COLORS[card_data['type']], (img_size, img_size))
        img_rect = img.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 30)
        surface.blit(img, img_rect)
        name_surf = self.font_large.render(card_data['name'], True, YELLOW)
        name_rect = name_surf.get_rect(centerx=panel_rect.centerx, top=img_rect.bottom + 15)
        surface.blit(name_surf, name_rect)
        description_parts = card_data['description'].split('\n')
        line_y = name_rect.bottom + 25
        for part in description_parts:
            wrapped_lines = self._render_text_wrapped(part, self.font_small, WHITE, panel_w - 60)
            for line_surf in wrapped_lines:
                line_rect = line_surf.get_rect(centerx=panel_rect.centerx, top=line_y)
                surface.blit(line_surf, line_rect)
                line_y += line_surf.get_height()
            line_y += 10
        close_button_size = 40
        close_rect = pygame.Rect(panel_rect.right - close_button_size - 10, panel_rect.top + 10, close_button_size,
                                 close_button_size)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_card'], close_rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, close_rect, 2, border_radius=5)
        pygame.draw.line(surface, WHITE, close_rect.topleft, close_rect.bottomright, 4)
        pygame.draw.line(surface, WHITE, close_rect.topright, close_rect.bottomleft, 4)
        return close_rect

    def _render_text_wrapped(self, text, font, color, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(font.render(current_line, True, color))
                current_line = word + " "
        lines.append(font.render(current_line, True, color))
        return lines

    def handle_shop_click(self, pos):
        for name, rect in self.shop_rects.items():
            if rect.collidepoint(pos):
                return name
        return None

    def draw_preparation_screen(self, surface, stipend, team, upgraded_heroes, neuro_mowers, all_defenders,
                                all_neuro_mowers, selected_card, mouse_pos, selected_card_info):
        surface.fill(DEFAULT_COLORS['background'])

        self._draw_panel_with_title(surface, self.team_panel_rect, "Твоя команда")
        self._draw_panel_with_title(surface, self.selection_panel_rect, "Выбор юнитов")
        self._draw_panel_with_title(surface, self.field_panel_rect, "Арсенал Нейросетей")

        self.team_card_rects, self.upgrade_buttons = self._draw_team_panel(surface, self.team_panel_rect, team,
                                                                           upgraded_heroes)
        self.selection_cards_rects = self._draw_selection_panel(surface, self.selection_panel_rect, all_defenders,
                                                                all_neuro_mowers)
        self.neuro_card_rects = self._draw_field_panel(surface, self.field_panel_rect, neuro_mowers)

        start_button_rect = self._draw_prep_hud(surface, stipend, len(team) > 0)

        if selected_card and mouse_pos:
            img_size = 80
            data_source = DEFENDERS_DATA if selected_card in all_defenders else NEURO_MOWERS_DATA
            img = load_image(f"{selected_card}.png", DEFAULT_COLORS[selected_card], (img_size, img_size))
            surface.blit(img, img.get_rect(center=mouse_pos))

        close_button_rect = None
        if selected_card_info:
            close_button_rect = self._draw_description_panel(surface, selected_card_info)

        return start_button_rect, close_button_rect

    def _draw_panel_with_title(self, surface, rect, title):
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, rect, 3, border_radius=15)
        title_surf = self.font.render(title, True, WHITE)
        surface.blit(title_surf, title_surf.get_rect(center=(rect.centerx, rect.top + 40)))

    def _draw_team_panel(self, surface, panel_rect, team, upgraded_heroes):
        team_card_rects, upgrade_buttons = {}, {}
        for i in range(5):
            y = panel_rect.top + 80 + i * 110
            slot_rect = pygame.Rect(panel_rect.centerx - 50, y, 100, 100)
            if i < len(team):
                hero_type = team[i]
                is_upgraded = hero_type in upgraded_heroes
                self._draw_unit_card(surface, hero_type, slot_rect, DEFENDERS_DATA[hero_type], is_upgraded)
                team_card_rects[hero_type] = slot_rect
                if 'upgrade' in DEFENDERS_DATA[hero_type] and not is_upgraded:
                    upgrade_rect = pygame.Rect(slot_rect.right + 10, slot_rect.centery - 20, 80, 40)
                    pygame.draw.rect(surface, YELLOW, upgrade_rect, border_radius=5)
                    cost = DEFENDERS_DATA[hero_type]['upgrade']['cost']
                    cost_surf = self.font_tiny.render(f"LVL UP\n{cost}", True, BLACK)
                    surface.blit(cost_surf, cost_surf.get_rect(center=upgrade_rect.center))
                    upgrade_buttons[hero_type] = upgrade_rect
            else:
                pygame.draw.rect(surface, (0, 0, 0, 50), slot_rect, border_radius=10)
        return team_card_rects, upgrade_buttons

    def _draw_selection_panel(self, surface, panel_rect, defenders, neuro_mowers):
        selection_cards_rects = {}
        title_surf = self.font_small.render("Герои:", True, WHITE)
        surface.blit(title_surf, (panel_rect.left + 15, panel_rect.top + 80))
        rects1 = self._draw_card_selection_list(surface, panel_rect, defenders, DEFENDERS_DATA, 110)
        title_surf = self.font_small.render("Нейросети:", True, WHITE)
        surface.blit(title_surf, (panel_rect.left + 15, panel_rect.top + 350))
        rects2 = self._draw_card_selection_list(surface, panel_rect, neuro_mowers, NEURO_MOWERS_DATA, 380)
        return {**rects1, **rects2}

    def _draw_card_selection_list(self, surface, panel_rect, types, data_source, start_y):
        card_rects = {}
        card_size = 80
        padding = 15
        cols = 4
        for i, item_type in enumerate(types):
            row, col = divmod(i, cols)
            x = panel_rect.left + padding + col * (card_size + padding)
            y = panel_rect.top + start_y + row * (card_size + padding + 30)
            card_rect = pygame.Rect(x, y, card_size, card_size)
            self._draw_unit_card(surface, item_type, card_rect, data_source[item_type])
            card_rects[item_type] = card_rect
        return card_rects

    def _draw_field_panel(self, surface, panel_rect, neuro_mowers):
        neuro_card_rects = {}
        for r in range(GRID_ROWS):
            rect = pygame.Rect(panel_rect.centerx - CELL_SIZE_W / 2, panel_rect.top + 80 + r * (CELL_SIZE_H + 5),
                               CELL_SIZE_W, CELL_SIZE_H)
            pygame.draw.rect(surface, (0, 0, 0, 50), rect, border_radius=5)
            if r in neuro_mowers:
                mower_type = neuro_mowers[r]
                neuro_card_rects[mower_type] = rect
                img = load_image(f"{mower_type}.png", DEFAULT_COLORS[mower_type], (CELL_SIZE_W - 10, CELL_SIZE_H - 10))
                surface.blit(img, img.get_rect(center=rect.center))
        return neuro_card_rects

    def _draw_prep_hud(self, surface, stipend, team_is_ready):
        stipend_text = self.font.render(f"Стипендия: {stipend}", True, YELLOW)
        surface.blit(stipend_text, (self.selection_panel_rect.left, SCREEN_HEIGHT - 60))
        start_button_rect = pygame.Rect(0, 0, 300, 80)
        start_button_rect.center = (self.selection_panel_rect.centerx, SCREEN_HEIGHT - 60)
        color = GREEN if team_is_ready else GREY
        pygame.draw.rect(surface, color, start_button_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, start_button_rect, 2, border_radius=10)
        start_text = self.font_large.render("Начать", True, BLACK)
        surface.blit(start_text, start_text.get_rect(center=start_button_rect.center))
        return start_button_rect

    def _draw_unit_card(self, surface, unit_type, rect, data, is_upgraded=False):
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_card'], rect, border_radius=10)
        if is_upgraded:
            pygame.draw.rect(surface, AURA_PINK, rect, 4, border_radius=10)

        img = load_image(f"{unit_type}.png", DEFAULT_COLORS[unit_type], (rect.width - 10, rect.height - 10))
        surface.blit(img, img.get_rect(center=rect.center))
        cost = data.get('cost', 0)
        if cost > 0:
            cost_surf = self.font_tiny.render(str(cost), True, YELLOW)
            surface.blit(cost_surf, cost_surf.get_rect(bottomright=rect.bottomright))