# core/ui_manager.py

import pygame
from data.settings import *
from data.assets import CARD_IMAGES, load_image, UI_IMAGES
from data.levels import LEVELS
from core.level_manager import LevelManager

STAT_DISPLAY_NAMES = {
    'health': 'Здоровье:', 'damage': 'Урон:', 'cooldown': 'Перезарядка:', 'radius': 'Радиус:',
    'production': 'Производство:', 'buff': 'Усиление:', 'heal_amount': 'Запас лечения:',
    'slow_duration': 'Длит. замедл.:', 'slow_factor': 'Сила замедл.:',
    'speed': 'Скорость:', 'projectile_speed': 'Скор. снаряда:'
}


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 32)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.font_small_bold = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_tiny = pygame.font.SysFont('Arial', 18)
        self.font_large = pygame.font.SysFont('Arial', 60)
        self.font_huge = pygame.font.SysFont('Impact', 120)

        self.prep_background_image = load_image('prep_background.png', DEFAULT_COLORS['background'],
                                                (SCREEN_WIDTH, SCREEN_HEIGHT))

        margin = 20
        panel_width = (SCREEN_WIDTH - 4 * margin) / 3
        panel_height = SCREEN_HEIGHT - 150
        top_y = 70
        self.team_panel_rect = pygame.Rect(margin, top_y, panel_width, panel_height)
        self.selection_panel_rect = pygame.Rect(self.team_panel_rect.right + margin, top_y, panel_width, panel_height)
        self.plan_panel_rect = pygame.Rect(self.selection_panel_rect.right + margin, top_y, panel_width, panel_height)
        self.selection_cards_rects = {}
        self.team_card_rects = {}
        self.plan_cards_rects = {}
        self.desc_panel_rect = None
        self.shop_items = []
        self.shop_rects = {}
        self.shop_panel_surf = pygame.Surface((SCREEN_WIDTH, SHOP_PANEL_HEIGHT), pygame.SRCALPHA)
        self.pause_button_rect = pygame.Rect(SCREEN_WIDTH - 120, (SHOP_PANEL_HEIGHT - 60) / 2, 60, 60)

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

    def draw_start_screen(self, surface, title_text, buttons):
        plaque_img = UI_IMAGES.get('title_plaque')
        if plaque_img:
            plaque_rect = plaque_img.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
            surface.blit(plaque_img, plaque_rect)

            title_font = pygame.font.SysFont('Georgia', 55)
            title_surf = title_font.render(title_text, True, TITLE_BROWN)
            title_rect = title_surf.get_rect(center=(plaque_rect.centerx, plaque_rect.centery + 5))
            surface.blit(title_surf, title_rect)
        else:
            title = self.font_large.render(title_text, True, WHITE)
            surface.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)))

        for name, rect in buttons.items():
            button_color = DEFAULT_COLORS['button']
            if name == "Начать обучение":
                button_color = START_BUTTON_GREEN
            elif name == "Выход":
                button_color = EXIT_BUTTON_RED

            pygame.draw.rect(surface, button_color, rect, border_radius=10)

            pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
            text = self.font.render(name, True, WHITE)
            surface.blit(text, text.get_rect(center=rect.center))

    def create_battle_shop(self, team):
        self.shop_items = team
        self.shop_rects = {}
        self.shop_panel_surf.fill(DEFAULT_COLORS['shop_panel'])

        coffee_area_width = 180
        coffee_area_rect = pygame.Rect(0, 0, coffee_area_width, SHOP_PANEL_HEIGHT)
        pygame.draw.rect(self.shop_panel_surf, DEFAULT_COLORS['shop_card'], coffee_area_rect.inflate(-10, -10),
                         border_radius=10)
        coffee_icon = CARD_IMAGES.get('coffee_bean')
        if coffee_icon:
            coffee_icon = pygame.transform.scale(coffee_icon, (50, 50))
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

    def draw_shop(self, surface, selected_defender, coffee_beans, upgrades):
        surface.blit(self.shop_panel_surf, (0, 0))
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_border'], (0, 0, SCREEN_WIDTH, SHOP_PANEL_HEIGHT), 5)

        coffee_text = self.font.render(f"{coffee_beans}", True, WHITE)
        text_rect = coffee_text.get_rect(midleft=(90, SHOP_PANEL_HEIGHT / 2))
        surface.blit(coffee_text, text_rect)

        for hero_type in self.shop_items:
            if hero_type in upgrades:
                rect = self.shop_rects[hero_type]
                pygame.draw.rect(surface, AURA_PINK, rect, 4, border_radius=5)

        if selected_defender:
            rect = self.shop_rects[selected_defender]
            pygame.draw.rect(surface, YELLOW, rect, 4, border_radius=5)

        for item_name in self.shop_items:
            card_rect = self.shop_rects[item_name]

            item_image = CARD_IMAGES.get(item_name)
            if item_image:
                img_rect = item_image.get_rect(center=card_rect.center)
                img_rect.y -= 10
                surface.blit(item_image, img_rect)

            cost_text = self.font_small.render(f"{DEFENDERS_DATA[item_name]['cost']}", True, WHITE)
            text_rect = cost_text.get_rect(center=(card_rect.centerx, card_rect.bottom - 15))
            surface.blit(cost_text, text_rect)

    def draw_hud(self, surface, spawn_progress, kill_progress, spawn_count_data, kill_count_data,
                 calamity_notification):
        enemies_spawned, total_spawn = spawn_count_data
        enemies_killed, total_kill = kill_count_data
        bar_w, bar_h, gap = 250, 20, 5
        brs_y = SCREEN_HEIGHT - bar_h - 20;
        brs_x = SCREEN_WIDTH - bar_w - 20
        pygame.draw.rect(surface, GREY, (brs_x, brs_y, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(surface, GREEN, (brs_x, brs_y, bar_w * kill_progress, bar_h), border_radius=5)
        brs_text_surf = self.font_tiny.render(f"БРС: {enemies_killed} / {total_kill}", True, BLACK);
        surface.blit(brs_text_surf, brs_text_surf.get_rect(center=(brs_x + bar_w / 2, brs_y + bar_h / 2)))
        pygame.draw.rect(surface, WHITE, (brs_x, brs_y, bar_w, bar_h), 2, border_radius=5)
        plan_y, plan_x = brs_y - bar_h - gap, brs_x
        pygame.draw.rect(surface, GREY, (plan_x, plan_y, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(surface, PROGRESS_BLUE, (plan_x, plan_y, bar_w * spawn_progress, bar_h), border_radius=5)
        plan_text_surf = self.font_tiny.render(f"Учебный план: {enemies_spawned} / {total_spawn}", True, WHITE);
        surface.blit(plan_text_surf, plan_text_surf.get_rect(center=(plan_x + bar_w / 2, plan_y + bar_h / 2)))
        pygame.draw.rect(surface, WHITE, (plan_x, plan_y, bar_w, bar_h), 2, border_radius=5)

        pygame.draw.rect(surface, DEFAULT_COLORS['pause_button'], self.pause_button_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.pause_button_rect, 2, border_radius=10)
        bar1 = pygame.Rect(0, 0, 8, 30);
        bar1.center = (self.pause_button_rect.centerx - 10, self.pause_button_rect.centery)
        bar2 = pygame.Rect(0, 0, 8, 30);
        bar2.center = (self.pause_button_rect.centerx + 10, self.pause_button_rect.centery)
        pygame.draw.rect(surface, BLACK, bar1, border_radius=3);
        pygame.draw.rect(surface, BLACK, bar2, border_radius=3)

        if calamity_notification:
            panel_w, panel_h = 800, 250
            panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
            panel_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

            panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            panel_surf.fill(CALAMITY_PANEL_BG)

            surface.blit(panel_surf, panel_rect.topleft)
            pygame.draw.rect(surface, CALAMITY_BORDER_RED, panel_rect, 5, border_radius=15)

            icon = CARD_IMAGES.get(calamity_notification['type'])
            icon_rect = None
            if icon:
                icon = pygame.transform.scale(icon, (120, 120))
                icon_rect = icon.get_rect(centery=panel_rect.centery, left=panel_rect.left + 40)
                surface.blit(icon, icon_rect)

            text_area_left_margin = icon_rect.right + 40 if icon_rect else panel_rect.left + 40
            max_text_width = (panel_rect.right - 40) - text_area_left_margin

            name_surf = self.font_large.render(calamity_notification['name'], True, CALAMITY_ORANGE)
            name_rect = name_surf.get_rect(left=text_area_left_margin, top=panel_rect.top + 40)
            surface.blit(name_surf, name_rect)

            wrapped_lines = self._render_text_wrapped(
                calamity_notification['desc'], self.font_small, WHITE, max_text_width
            )

            current_y = name_rect.bottom + 15
            for line_surf in wrapped_lines:
                line_rect = line_surf.get_rect(left=text_area_left_margin, top=current_y)
                surface.blit(line_surf, line_rect)
                current_y += line_surf.get_height()

    def draw_grid(self, surface):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(GRID_START_X + col * CELL_SIZE_W, GRID_START_Y + row * CELL_SIZE_H, CELL_SIZE_W,
                                   CELL_SIZE_H)
                s = pygame.Surface((CELL_SIZE_W, CELL_SIZE_H), pygame.SRCALPHA)
                pygame.draw.rect(s, GRID_COLOR, s.get_rect(), 1)
                surface.blit(s, (rect.x, rect.y))

    def draw_menu(self, surface, title_text, buttons):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA);
        overlay.fill((0, 0, 0, 150));
        surface.blit(overlay, (0, 0))
        title = self.font_large.render(title_text, True, WHITE);
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)))
        for name, rect in buttons.items():
            pygame.draw.rect(surface, DEFAULT_COLORS['button'], rect, border_radius=10)
            pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
            text = self.font.render(name, True, WHITE);
            surface.blit(text, text.get_rect(center=rect.center))

    def draw_settings_menu(self, surface, music_enabled, sfx_enabled):
        panel_w, panel_h = 600, 400
        panel_rect = pygame.Rect((SCREEN_WIDTH - panel_w) / 2, (SCREEN_HEIGHT - panel_h) / 2, panel_w, panel_h)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], panel_rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, panel_rect, 3, border_radius=15)

        title_surf = self.font_large.render("Настройки", True, WHITE)
        surface.blit(title_surf, title_surf.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 30))

        buttons = {}

        music_label_surf = self.font.render("Фоновая музыка", True, WHITE)
        music_label_rect = music_label_surf.get_rect(midleft=(panel_rect.left + 50, panel_rect.centery - 50))
        surface.blit(music_label_surf, music_label_rect)

        music_toggle_img = UI_IMAGES['toggle_on'] if music_enabled else UI_IMAGES['toggle_off']
        music_toggle_rect = music_toggle_img.get_rect(midright=(panel_rect.right - 50, music_label_rect.centery))
        surface.blit(music_toggle_img, music_toggle_rect)
        buttons['toggle_music'] = music_toggle_rect

        sfx_label_surf = self.font.render("Звуковые эффекты", True, WHITE)
        sfx_label_rect = sfx_label_surf.get_rect(midleft=(panel_rect.left + 50, panel_rect.centery + 50))
        surface.blit(sfx_label_surf, sfx_label_rect)

        sfx_toggle_img = UI_IMAGES['toggle_on'] if sfx_enabled else UI_IMAGES['toggle_off']
        sfx_toggle_rect = sfx_toggle_img.get_rect(midright=(panel_rect.right - 50, sfx_label_rect.centery))
        surface.blit(sfx_toggle_img, sfx_toggle_rect)
        buttons['toggle_sfx'] = sfx_toggle_rect

        close_rect = pygame.Rect(panel_rect.right - 45, panel_rect.top + 10, 35, 35)
        pygame.draw.line(surface, WHITE, close_rect.topleft, close_rect.bottomright, 3)
        pygame.draw.line(surface, WHITE, close_rect.topright, close_rect.bottomleft, 3)
        buttons['close'] = close_rect

        return buttons

    def draw_main_menu(self, surface, max_level_unlocked):
        panel_rect = pygame.Rect(100, (SCREEN_HEIGHT - 600) / 2, 500, 600)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], panel_rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, panel_rect, 3, border_radius=15)
        title = self.font_large.render("Главное меню", True, WHITE)
        surface.blit(title, title.get_rect(center=(panel_rect.centerx, panel_rect.top + 70)))
        level_buttons = {}
        for level_id, data in LEVELS.items():
            if level_id == 0: continue
            is_unlocked = level_id <= max_level_unlocked
            button_rect = pygame.Rect(0, 0, 400, 70)
            button_rect.center = (panel_rect.centerx, panel_rect.top + 180 + (level_id - 1) * 85)
            color = YELLOW if is_unlocked else GREY
            pygame.draw.rect(surface, color, button_rect, border_radius=10)
            pygame.draw.rect(surface, WHITE, button_rect, 2, border_radius=10)
            text_surf = self.font.render(data['name'], True, BLACK)
            surface.blit(text_surf, text_surf.get_rect(center=button_rect.center))
            if is_unlocked: level_buttons[level_id] = button_rect

        control_buttons = {}
        btn_width, btn_height = 200, 80
        gap = 20

        base_x = SCREEN_WIDTH - 150 - btn_width
        settings_x = base_x - (btn_width / 2 + gap / 2)
        test_x = base_x + (btn_width / 2 + gap / 2)
        top_y = 250

        settings_rect = pygame.Rect(0, 0, btn_width, btn_height)
        settings_rect.center = (settings_x, top_y)
        self._draw_button(surface, "Настройки", settings_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Настройки"] = settings_rect

        test_rect = pygame.Rect(0, 0, btn_width, btn_height)
        test_rect.center = (test_x, top_y)
        self._draw_button(surface, "Тест", test_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Тест"] = test_rect

        exit_rect = pygame.Rect(0, 0, btn_width * 2 + gap, btn_height)
        exit_rect.center = (base_x, top_y + btn_height + gap)
        self._draw_button(surface, "Выход", exit_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Выход"] = exit_rect

        return level_buttons, control_buttons

    def draw_level_clear_message(self, surface):
        text_surf = self.font_huge.render("БРС: 100/100", True, YELLOW)
        shadow_surf = self.font_huge.render("БРС: 100/100", True, BLACK)
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(SCREEN_WIDTH / 2 + 5, SCREEN_HEIGHT / 2 + 5)))
        surface.blit(text_surf, text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))

    def handle_shop_click(self, pos):
        if self.pause_button_rect.collidepoint(pos): return 'pause_button'
        for name, rect in self.shop_rects.items():
            if rect.collidepoint(pos): return name
        return None

    def draw_preparation_screen(self, surface, stipend, team, upgrades, purchased_mowers,
                                all_defenders, all_neuro_mowers, level_id, selected_card_info, neuro_slots,
                                current_team, current_mowers):
        surface.blit(self.prep_background_image, (0, 0))

        random_buttons = self._draw_team_panel(surface, self.team_panel_rect, team,
                                               upgrades, purchased_mowers, neuro_slots)
        self.selection_cards_rects = self._draw_selection_panel(surface, self.selection_panel_rect, upgrades,
                                                                current_team, current_mowers)
        self.plan_cards_rects = self._draw_plan_panel(surface, self.plan_panel_rect, level_id)
        prep_buttons = self._draw_prep_hud(surface, len(team) > 0)

        stipend_bg_rect = pygame.Rect(0, 0, 320, 50)
        stipend_bg_rect.centerx = SCREEN_WIDTH / 2
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], stipend_bg_rect, border_radius=10)

        stipend_text = self.font.render(f"Стипендия: {stipend}", True, YELLOW)
        text_rect = stipend_text.get_rect(center=stipend_bg_rect.center)

        stipend_icon = CARD_IMAGES.get('stipend')
        if stipend_icon:
            text_rect.centerx -= 20
            surface.blit(stipend_text, text_rect)
            icon_rect = stipend_icon.get_rect(midleft=(text_rect.right + 10, stipend_bg_rect.centery))
            surface.blit(stipend_icon, icon_rect)
        else:
            surface.blit(stipend_text, text_rect)

        info_buttons = {}
        if selected_card_info:
            info_buttons = self._draw_description_panel(surface, selected_card_info, team,
                                                        upgrades, purchased_mowers, neuro_slots)

        return prep_buttons, random_buttons, info_buttons

    def _draw_unit_card(self, surface, unit_type, rect, data, is_upgraded=False, is_selected=False):
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_card'], rect, border_radius=10)
        if is_upgraded:
            pygame.draw.rect(surface, AURA_PINK, rect.inflate(4, 4), 4, border_radius=12)
        if is_selected:
            pygame.draw.rect(surface, YELLOW, rect, 3, border_radius=12)

        img = CARD_IMAGES.get(unit_type)
        if img:
            if img.get_size() != (rect.width - 10, rect.height - 10):
                img = pygame.transform.scale(img, (rect.width - 10, rect.height - 10))
            surface.blit(img, img.get_rect(center=rect.center))

        cost = data.get('cost')
        if cost is not None:
            # --- НАЧАЛО ИЗМЕНЕНИЙ: Умный выбор цвета ---
            # По умолчанию, цена отображается цветом кофе
            cost_color = COFFEE_COST_COLOR

            # Но если это нейросеть, то цена отображается желтым (цвет стипендии)
            if unit_type in NEURO_MOWERS_DATA:
                cost_color = YELLOW

            cost_surf = self.font_tiny.render(str(cost), True, cost_color)
            surface.blit(cost_surf, cost_surf.get_rect(bottomright=(rect.right - 5, rect.bottom - 2)))
            # --- КОНЕЦ ИЗМЕНЕНИЙ ---
    def _draw_desc_panel_header(self, surface, card_type, name):
        img_size = 120
        img = CARD_IMAGES.get(card_type)
        if img:
            img = pygame.transform.scale(img, (img_size, img_size))
            img_rect = img.get_rect(centerx=self.desc_panel_rect.centerx, top=self.desc_panel_rect.top + 20)
            surface.blit(img, img_rect)
        else:
            img_rect = pygame.Rect(0, 0, img_size, img_size)
            img_rect.centerx = self.desc_panel_rect.centerx
            img_rect.top = self.desc_panel_rect.top + 20

        name_surf = self.font.render(name, True, YELLOW)
        name_rect = name_surf.get_rect(centerx=self.desc_panel_rect.centerx, top=img_rect.bottom + 10)
        surface.blit(name_surf, name_rect)
        return name_rect

    def _draw_team_panel(self, surface, panel_rect, team, upgrades, purchased_mowers, neuro_slots):
        self._draw_panel_with_title(surface, panel_rect, "Твоя команда")
        random_buttons = {}

        hero_slots_bottom_y = self._render_hero_slots(surface, panel_rect, team, upgrades)
        random_team_rect = pygame.Rect(0, 0, 220, 40)
        random_team_rect.center = (panel_rect.centerx, hero_slots_bottom_y + 35)
        self._draw_button(surface, "Случайная команда", random_team_rect, RANDOM_BUTTON_COLOR, WHITE)
        random_buttons['team'] = random_team_rect
        neuro_slots_bottom_y = self._render_neuro_slots(surface, panel_rect, purchased_mowers, neuro_slots,
                                                        random_team_rect.bottom + 30)
        random_neuro_rect = pygame.Rect(0, 0, 220, 40)
        random_neuro_rect.center = (panel_rect.centerx, neuro_slots_bottom_y + 30)
        self._draw_button(surface, "Случайные нейросети", random_neuro_rect, RANDOM_BUTTON_COLOR, WHITE)
        random_buttons['neuro'] = random_neuro_rect
        return random_buttons

    def _render_hero_slots(self, surface, panel_rect, team, upgrades):
        self._render_text_with_title(surface, "Одногруппники:", self.font_small, YELLOW, panel_rect.centerx,
                                     panel_rect.top + 70)
        card_size, padding_x, padding_y, cols = 80, 25, 15, 3
        start_x = panel_rect.centerx - (cols * card_size + (cols - 1) * padding_x) / 2
        start_y = panel_rect.top + 110
        bottom_y = start_y
        self.team_card_rects = {}
        for i in range(MAX_TEAM_SIZE):
            row, col = divmod(i, cols)
            x, y = start_x + col * (card_size + padding_x), start_y + row * (card_size + padding_y)
            slot_rect = pygame.Rect(x, y, card_size, card_size)
            if i < len(team):
                hero_type = team[i]
                is_upgraded = hero_type in upgrades
                self._draw_unit_card(surface, hero_type, slot_rect, DEFENDERS_DATA[hero_type], is_upgraded)
                self.team_card_rects[hero_type] = slot_rect
            else:
                pygame.draw.rect(surface, (0, 0, 0, 50), slot_rect, border_radius=10)
            bottom_y = slot_rect.bottom
        return bottom_y

    def _render_neuro_slots(self, surface, panel_rect, purchased_mowers, neuro_slots, start_y):
        self._render_text_with_title(surface, f"Нейросети ({len(purchased_mowers)}/{neuro_slots}):", self.font_small,
                                     YELLOW, panel_rect.centerx, start_y)
        neuro_start_x = panel_rect.centerx - (neuro_slots * 80 + (neuro_slots - 1) * 10) / 2
        neuro_cards_y = start_y + 40
        bottom_y = neuro_cards_y
        for i in range(neuro_slots):
            rect = pygame.Rect(neuro_start_x + i * 90, neuro_cards_y, 80, 80)
            if i < len(purchased_mowers):
                mower_type = purchased_mowers[i]
                self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])
                unique_key = f"{mower_type}_{i}"
                self.team_card_rects[unique_key] = rect
            else:
                pygame.draw.rect(surface, (0, 0, 0, 50), rect, border_radius=10)
            bottom_y = rect.bottom
        return bottom_y

    def _draw_selection_panel(self, surface, panel_rect, upgrades, current_team, current_mowers):
        self._draw_panel_with_title(surface, panel_rect, "Выбор юнитов")
        all_defenders = list(DEFENDERS_DATA.keys());
        all_neuro_mowers = list(NEURO_MOWERS_DATA.keys())
        self._render_text_with_title(surface, "Герои:", self.font_small, WHITE, panel_rect.centerx, panel_rect.top + 70)
        rects1 = self._draw_card_selection_list(surface, panel_rect, all_defenders, DEFENDERS_DATA, 100, upgrades,
                                                current_team, current_mowers)
        self._render_text_with_title(surface, "Нейросети:", self.font_small, WHITE, panel_rect.centerx,
                                     panel_rect.top + 350)
        rects2 = self._draw_card_selection_list(surface, panel_rect, all_neuro_mowers, NEURO_MOWERS_DATA, 380,
                                                upgrades, current_team, current_mowers)
        return {**rects1, **rects2}

    def _draw_plan_panel(self, surface, panel_rect, level_id):
        self._draw_panel_with_title(surface, panel_rect, "Учебный план")
        temp_level_manager = LevelManager(level_id, None, None, None)
        enemy_types = temp_level_manager.get_enemy_types_for_level();
        calamity_types = temp_level_manager.get_calamity_types_for_level()
        self._render_text_with_title(surface, "Ожидаемые враги:", self.font_small, WHITE, panel_rect.centerx,
                                     panel_rect.top + 70)
        enemy_rects = self._draw_card_selection_list(surface, panel_rect, enemy_types, ENEMIES_DATA, 100)
        if calamity_types:
            self._render_text_with_title(surface, "Возможные напасти:", self.font_small, YELLOW, panel_rect.centerx,
                                         panel_rect.top + 350)
            calamity_rects = self._draw_card_selection_list(surface, panel_rect, calamity_types, CALAMITIES_DATA, 380)
            return {**enemy_rects, **calamity_rects}
        return enemy_rects

    def _draw_card_selection_list(self, surface, panel_rect, types, data_source, start_y_offset, upgrades=None,
                                  current_team=None, current_mowers=None):
        card_rects = {}
        if not types: return card_rects

        card_size, padding, cols = 80, 15, 4

        items_in_row = min(len(types), cols)
        total_width = items_in_row * card_size + (items_in_row - 1) * padding
        start_x_base = panel_rect.left + (panel_rect.width - total_width) / 2

        for i, item_type in enumerate(types):
            row, col = divmod(i, cols)
            x = start_x_base + col * (card_size + padding)
            y = panel_rect.top + start_y_offset + row * (card_size + padding + 20)
            card_rect = pygame.Rect(x, y, card_size, card_size)
            if item_type in data_source:
                is_upgraded = upgrades and item_type in upgrades
                is_selected = (current_team and item_type in current_team) or \
                              (current_mowers and item_type in current_mowers)
                self._draw_unit_card(surface, item_type, card_rect, data_source[item_type], is_upgraded, is_selected)
                card_rects[item_type] = card_rect
        return card_rects

    def _draw_prep_hud(self, surface, team_is_ready):
        margin = 30
        btn_width, btn_height = 250, 60
        buttons = {}
        back_button_rect = pygame.Rect(margin, SCREEN_HEIGHT - btn_height - margin, btn_width, btn_height)
        self._draw_button(surface, "Назад", back_button_rect, GREY, WHITE, self.font)
        buttons['back'] = back_button_rect
        start_button_rect = pygame.Rect(SCREEN_WIDTH - btn_width - margin, SCREEN_HEIGHT - btn_height - margin,
                                        btn_width, btn_height)
        color = GREEN if team_is_ready else GREY
        text_color = BLACK if team_is_ready else DARK_GREY
        self._draw_button(surface, "К расстановке", start_button_rect, color, text_color, self.font)
        buttons['start'] = start_button_rect
        return buttons

    def _draw_button(self, surface, text, rect, color, text_color, font=None):
        if font is None: font = self.font_small
        pygame.draw.rect(surface, color, rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
        text_surf = font.render(text, True, text_color)
        surface.blit(text_surf, text_surf.get_rect(center=rect.center))

    def _draw_description_panel(self, surface, card_data, team, upgrades, purchased_mowers, neuro_slots):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        panel_w, panel_h = 700, 600
        self.desc_panel_rect = pygame.Rect((SCREEN_WIDTH - panel_w) / 2, (SCREEN_HEIGHT - panel_h) / 2, panel_w,
                                           panel_h)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], self.desc_panel_rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, self.desc_panel_rect, 3, border_radius=15)
        card_type = card_data['type']
        img_rect = self._draw_desc_panel_header(surface, card_type, card_data['name'])
        buttons, current_y = self._draw_desc_panel_stats(surface, card_type, team, upgrades, img_rect.bottom + 25)

        # --- ИСПРАВЛЕНИЕ: Используем _render_text_wrapped для описания ---
        left_margin = self.desc_panel_rect.left + 30
        desc_title_surf = self.font_small_bold.render("Описание:", True, WHITE)
        surface.blit(desc_title_surf, (left_margin, current_y + 15))

        current_y_desc = current_y + 50  # Немного отступаем от заголовка "Описание"
        wrapped_lines = self._render_text_wrapped(card_data['description'], self.font_small, WHITE,
                                                  self.desc_panel_rect.width - 60)
        for line_surf in wrapped_lines:
            surface.blit(line_surf, (left_margin, current_y_desc))
            current_y_desc += line_surf.get_height()

        action_buttons = self._draw_desc_panel_actions(surface, card_data, team, purchased_mowers, neuro_slots)
        buttons.update(action_buttons)
        return buttons

    def _draw_desc_panel_stats(self, surface, card_type, team, upgrades, start_y):
        buttons = {}
        all_data_sources = {**DEFENDERS_DATA, **ENEMIES_DATA, **NEURO_MOWERS_DATA, **CALAMITIES_DATA}
        unit_data = all_data_sources.get(card_type)
        if not unit_data:
            return buttons, start_y

        left_margin, right_margin = self.desc_panel_rect.left + 30, self.desc_panel_rect.right - 20
        line_height, line_y = 35, start_y

        for key, title in STAT_DISPLAY_NAMES.items():
            if line_y > self.desc_panel_rect.bottom - 150:
                break
            if key in unit_data:
                base_value, value_color, value_str = self._get_stat_display_values(unit_data, card_type, key, upgrades)

                title_surf = self.font_small_bold.render(title, True, WHITE)
                value_surf = self.font_small.render(value_str, True, value_color)
                surface.blit(title_surf, (left_margin, line_y))
                surface.blit(value_surf, (left_margin + 200, line_y))

                is_in_team = team and card_type in team
                if is_in_team and 'upgrades' in unit_data and key in unit_data['upgrades']:
                    upgrade_buttons = self._draw_upgrade_buttons_for_stat(surface, unit_data, card_type, key, upgrades,
                                                                          line_y, line_height, right_margin)
                    buttons.update(upgrade_buttons)

                line_y += line_height

        return buttons, line_y

    def _get_stat_display_values(self, unit_data, card_type, key, upgrades):
        base_value = unit_data[key]
        value_color = WHITE
        if base_value is None:
            return None, WHITE, "Нет"
        upgraded_stats_set = upgrades.get(card_type, set())
        if key in upgraded_stats_set:
            base_value += unit_data['upgrades'][key]['value']
            value_color = AURA_PINK
        if key == 'radius':
            value_str = f"{base_value} кл."
        elif key == "slow_factor":
            value_str = f"{1 - base_value:.0%}"
        elif key == "slow_duration":
            value_str = f"{base_value / 1000:.1f} сек."
        elif key == "cooldown":
            value_str = f"{base_value:.1f} сек."
        else:
            value_str = f"{base_value:.1f}".replace('.0', '')
        return base_value, value_color, value_str

    def _draw_upgrade_buttons_for_stat(self, surface, unit_data, card_type, key, upgrades, line_y, line_height,
                                       right_margin):
        buttons = {}
        upgrade_info = unit_data['upgrades'][key]
        cost = upgrade_info['cost']
        upgraded_stats_set = upgrades.get(card_type, set())
        if key in upgraded_stats_set:
            btn_rect = pygame.Rect(0, 0, 120, line_height - 5)
            btn_rect.midleft = (right_margin - btn_rect.width, line_y + line_height / 2)
            self._draw_button(surface, "Отменить", btn_rect, RED, WHITE, self.font_tiny)
            buttons[f'revert_{key}'] = btn_rect
        else:
            bonus = upgrade_info['value']
            bonus_str = f"+{bonus:.1f}".replace('.0', '') if bonus > 0 else f"{bonus:.1f}".replace('.0', '')
            if key == 'radius': bonus_str = f"+{int(bonus)}"
            btn_text = f"Улучшить ({bonus_str}) ({cost}$)"
            btn_rect = pygame.Rect(0, 0, 250, line_height - 5)
            btn_rect.midleft = (right_margin - btn_rect.width, line_y + line_height / 2)
            self._draw_button(surface, btn_text, btn_rect, GREEN, BLACK, self.font_tiny)
            buttons[f'upgrade_{key}'] = btn_rect
        return buttons

    def _draw_desc_panel_actions(self, surface, card_data, team, purchased_mowers, neuro_slots):
        buttons = {}
        card_type = card_data['type']
        source = card_data.get('source')
        is_hero, is_mower = card_type in DEFENDERS_DATA, card_type in NEURO_MOWERS_DATA
        is_in_team_panel = source == 'team'
        action_button_rect = pygame.Rect(0, 0, 250, 50)
        action_button_rect.center = (self.desc_panel_rect.centerx, self.desc_panel_rect.bottom - 45)
        if is_in_team_panel:
            text = "Выгнать" if is_hero else "Удалить"
            self._draw_button(surface, text, action_button_rect, RED, WHITE, self.font)
            buttons['kick'] = action_button_rect
        elif is_hero:
            is_in_team = team and card_type in team
            team_is_full = team and len(team) >= MAX_TEAM_SIZE
            is_clickable = not is_in_team and not team_is_full
            color = GREEN if is_clickable else GREY
            text = "Взять"
            if is_in_team:
                text = "Уже в команде"
            elif team_is_full:
                text = "Команда полна"
            text_color = BLACK if is_clickable else DARK_GREY
            self._draw_button(surface, text, action_button_rect, color, text_color, self.font)
            if is_clickable: buttons['take'] = action_button_rect
        elif is_mower:
            slots_are_full = purchased_mowers and len(purchased_mowers) >= neuro_slots
            chat_gpt_limit_reached = (card_type == 'chat_gpt' and purchased_mowers.count('chat_gpt') >= 2)
            is_clickable = not slots_are_full and not chat_gpt_limit_reached
            color = GREEN if is_clickable else GREY
            text = "Взять"
            if slots_are_full:
                text = "Слоты полны"
            elif chat_gpt_limit_reached:
                text = "Достигнут лимит"
            text_color = BLACK if is_clickable else DARK_GREY
            self._draw_button(surface, text, action_button_rect, color, text_color, self.font)
            if is_clickable: buttons['take'] = action_button_rect
        close_rect = pygame.Rect(self.desc_panel_rect.right - 45, self.desc_panel_rect.top + 10, 35, 35)
        pygame.draw.line(surface, WHITE, close_rect.topleft, close_rect.bottomright, 3);
        pygame.draw.line(surface, WHITE, close_rect.topright, close_rect.bottomleft, 3);
        buttons['close'] = close_rect
        return buttons

    def _draw_panel_with_title(self, surface, rect, title):
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, rect, 3, border_radius=15)
        self._render_text_with_title(surface, title, self.font, WHITE, rect.centerx, rect.top + 30)

    def _render_text_with_title(self, surface, text, font, color, center_x, top_y):
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, text_surf.get_rect(centerx=center_x, top=top_y))

    def _draw_placement_grid(self, surface):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(PLACEMENT_GRID_START_X + col * PLACEMENT_GRID_CELL_W,
                                   PLACEMENT_GRID_START_Y + row * PLACEMENT_GRID_CELL_H,
                                   PLACEMENT_GRID_CELL_W, PLACEMENT_GRID_CELL_H)
                s = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(s, GRID_COLOR, s.get_rect(), 1)
                surface.blit(s, rect.topleft)

    def _draw_placement_slots(self, surface):
        for row in range(GRID_ROWS):
            slot_rect = pygame.Rect(PLACEMENT_ZONE_X, PLACEMENT_GRID_START_Y + row * PLACEMENT_GRID_CELL_H,
                                    PLACEMENT_GRID_CELL_W, PLACEMENT_GRID_CELL_H)
            pygame.draw.rect(surface, (20, 20, 20, 200), slot_rect, border_radius=10)
            pygame.draw.rect(surface, WHITE, slot_rect, 2, border_radius=10)

    def _draw_placement_mower(self, surface, row, info):
        img = CARD_IMAGES.get(info['type'])
        if img:
            img = pygame.transform.scale(img, (PLACEMENT_GRID_CELL_W - 10, PLACEMENT_GRID_CELL_H - 10))
            rect = img.get_rect(
                centerx=PLACEMENT_ZONE_X + PLACEMENT_GRID_CELL_W / 2,
                centery=PLACEMENT_GRID_START_Y + row * PLACEMENT_GRID_CELL_H + PLACEMENT_GRID_CELL_H / 2
            )
            surface.blit(img, rect)

    def draw_neuro_placement_screen(self, surface, purchased_mowers, placed_mowers, dragged_mower_info):
        surface.blit(self.prep_background_image, (0, 0))
        self._draw_placement_grid(surface)
        self._draw_placement_slots(surface)
        for row, info in placed_mowers.items():
            self._draw_placement_mower(surface, row, info)

        unplaced_mowers_rects, start_button_rect = self._draw_neuro_selection_panel(surface, purchased_mowers,
                                                                                    placed_mowers)
        if dragged_mower_info:
            pos, mower_type = dragged_mower_info['pos'], dragged_mower_info['type']
            rect = pygame.Rect(0, 0, 100, 100)
            rect.center = pos
            self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])

        return unplaced_mowers_rects, start_button_rect

    def _draw_neuro_selection_panel(self, surface, purchased_mowers, placed_mowers):
        unplaced_mowers_rects = {}
        placed_indices = [info.get('original_index') for info in placed_mowers.values()]
        unplaced_mower_list_with_indices = [(i, m) for i, m in enumerate(purchased_mowers) if i not in placed_indices]

        panel_w, panel_h = 600, 250
        panel_x = (SCREEN_WIDTH - panel_w) / 2
        panel_y = (SCREEN_HEIGHT - panel_h) / 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        self._draw_panel_with_title(surface, panel_rect, "Расставьте нейросети по рядам")

        card_size, padding, cols = 100, 20, 4
        start_x = panel_rect.left + (panel_rect.width - (cols * card_size + (cols - 1) * padding)) / 2
        start_y = panel_rect.top + 100
        for i, (original_index, mower_type) in enumerate(unplaced_mower_list_with_indices):
            row, col = divmod(i, cols)
            x, y = start_x + col * (card_size + padding), start_y + row * (card_size + padding)
            rect = pygame.Rect(x, y, card_size, card_size)
            self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])
            unplaced_mowers_rects[original_index] = rect

        can_start = len(purchased_mowers) == len(placed_mowers)
        start_button_rect = pygame.Rect(0, 0, 300, 70)
        start_button_rect.center = (panel_rect.centerx, panel_rect.bottom + 60)

        color = GREEN if can_start else GREY
        text_color = BLACK if can_start else DARK_GREY
        self._draw_button(surface, "В Бой!", start_button_rect, color, text_color, self.font_large)

        return unplaced_mowers_rects, start_button_rect