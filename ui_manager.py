# ui_manager.py

import pygame
from settings import *
from assets import load_image
from levels import LEVELS
from level_manager import LevelManager


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 32)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.font_small_bold = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_tiny = pygame.font.SysFont('Arial', 18)
        self.font_large = pygame.font.SysFont('Arial', 60)
        self.font_huge = pygame.font.SysFont('Impact', 120)

        # Координаты панелей на экране подготовки
        margin = 20
        panel_width = (SCREEN_WIDTH - 4 * margin) / 3
        panel_height = SCREEN_HEIGHT - 150
        top_y = 70

        self.team_panel_rect = pygame.Rect(margin, top_y, panel_width, panel_height)
        self.selection_panel_rect = pygame.Rect(self.team_panel_rect.right + margin, top_y, panel_width, panel_height)
        self.plan_panel_rect = pygame.Rect(self.selection_panel_rect.right + margin, top_y, panel_width, panel_height)

        # Словари для хранения кликабельных областей
        self.selection_cards_rects = {}
        self.team_card_rects = {}
        self.plan_cards_rects = {}
        self.upgrade_buttons = {}
        self.desc_panel_rect = None

        # Переменные для магазина в бою
        self.shop_items = []
        self.shop_rects = {}
        self.shop_panel_surf = pygame.Surface((SCREEN_WIDTH, SHOP_PANEL_HEIGHT), pygame.SRCALPHA)
        self.pause_button_rect = pygame.Rect(SCREEN_WIDTH - 120, (SHOP_PANEL_HEIGHT - 60) / 2, 60, 60)

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
            name_surf = self.font_large.render(calamity_notification['name'], True, CALAMITY_ORANGE)
            desc_surf = self.font_small.render(calamity_notification['desc'], True, WHITE)
            name_rect = name_surf.get_rect(centerx=SCREEN_WIDTH / 2, centery=SCREEN_HEIGHT / 2 - 20)
            desc_rect = desc_surf.get_rect(centerx=SCREEN_WIDTH / 2, top=name_rect.bottom + 5)
            surface.blit(name_surf, name_rect)
            surface.blit(desc_surf, desc_rect)

    def draw_grid(self, surface):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(GRID_START_X + col * CELL_SIZE_W, GRID_START_Y + row * CELL_SIZE_H, CELL_SIZE_W,
                                   CELL_SIZE_H)
                s = pygame.Surface((CELL_SIZE_W, CELL_SIZE_H), pygame.SRCALPHA)
                pygame.draw.rect(s, (255, 255, 255, 30), s.get_rect(), 1)
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

    def draw_main_menu(self, surface, max_level_unlocked):
        panel_rect = pygame.Rect(100, (SCREEN_HEIGHT - 600) / 2, 500, 600)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], panel_rect, border_radius=15);
        pygame.draw.rect(surface, WHITE, panel_rect, 3, border_radius=15)
        title = self.font_large.render("Главное меню", True, WHITE);
        surface.blit(title, title.get_rect(center=(panel_rect.centerx, panel_rect.top + 70)))
        level_buttons = {}
        for level_id, data in LEVELS.items():
            is_unlocked = level_id <= max_level_unlocked
            button_rect = pygame.Rect(0, 0, 400, 70);
            button_rect.center = (panel_rect.centerx, panel_rect.top + 180 + (level_id - 1) * 85)
            color = YELLOW if is_unlocked else GREY
            pygame.draw.rect(surface, color, button_rect, border_radius=10);
            pygame.draw.rect(surface, WHITE, button_rect, 2, border_radius=10)
            text_surf = self.font.render(data['name'], True, BLACK);
            surface.blit(text_surf, text_surf.get_rect(center=button_rect.center))
            if is_unlocked: level_buttons[level_id] = button_rect
        control_buttons = {}
        btn_width, btn_height = 300, 90;
        btn_x = SCREEN_WIDTH - btn_width - 150
        settings_rect = pygame.Rect(btn_x, 250, btn_width, btn_height)
        pygame.draw.rect(surface, DEFAULT_COLORS['button'], settings_rect, border_radius=10);
        pygame.draw.rect(surface, WHITE, settings_rect, 2, border_radius=10)
        settings_text = self.font.render("Настройки", True, WHITE);
        surface.blit(settings_text, settings_text.get_rect(center=settings_rect.center));
        control_buttons["Настройки"] = settings_rect
        exit_rect = pygame.Rect(btn_x, settings_rect.bottom + 30, btn_width, btn_height)
        pygame.draw.rect(surface, DEFAULT_COLORS['button'], exit_rect, border_radius=10);
        pygame.draw.rect(surface, WHITE, exit_rect, 2, border_radius=10)
        exit_text = self.font.render("Выход", True, WHITE);
        surface.blit(exit_text, exit_text.get_rect(center=exit_rect.center));
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

    def draw_preparation_screen(self, surface, stipend, team, upgraded_heroes, purchased_mowers,
                                all_defenders, all_neuro_mowers, level_id, selected_card_info, neuro_slots):
        surface.fill(DEFAULT_COLORS['background'])

        random_buttons, self.team_card_rects, self.upgrade_buttons = self._draw_team_panel(surface,
                                                                                           self.team_panel_rect, team,
                                                                                           upgraded_heroes,
                                                                                           purchased_mowers,
                                                                                           neuro_slots)
        self.selection_cards_rects = self._draw_selection_panel(surface, self.selection_panel_rect)
        self.plan_cards_rects = self._draw_plan_panel(surface, self.plan_panel_rect, level_id)

        start_button_rect = self._draw_prep_hud(surface, len(team) > 0)

        stipend_bg_rect = pygame.Rect(0, 0, 300, 50);
        stipend_bg_rect.centerx = SCREEN_WIDTH / 2
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], stipend_bg_rect, border_radius=10)
        stipend_text = self.font.render(f"Стипендия: {stipend}", True, YELLOW)
        surface.blit(stipend_text, stipend_text.get_rect(center=stipend_bg_rect.center))

        info_buttons = {}
        if selected_card_info:
            is_purchasable = selected_card_info['type'] in all_defenders or selected_card_info[
                'type'] in all_neuro_mowers
            info_buttons = self._draw_description_panel(surface, selected_card_info, can_be_taken=is_purchasable)

        return start_button_rect, random_buttons, info_buttons

    def _draw_team_panel(self, surface, panel_rect, team, upgraded_heroes, purchased_mowers, neuro_slots):
        self._draw_panel_with_title(surface, panel_rect, "Твоя команда")
        team_card_rects, upgrade_buttons = {}, {}

        # --- Блок команды ---
        self._render_text_with_title(surface, "Одногруппники:", self.font_small, YELLOW, panel_rect.centerx,
                                     panel_rect.top + 70)
        card_size = 80;
        padding_x = 25;
        padding_y = 15;
        cols = 3
        start_x = panel_rect.centerx - (cols * card_size + (cols - 1) * padding_x) / 2
        start_y = panel_rect.top + 110
        for i in range(MAX_TEAM_SIZE):
            row, col = divmod(i, cols);
            x = start_x + col * (card_size + padding_x);
            y = start_y + row * (card_size + padding_y)
            slot_rect = pygame.Rect(x, y, card_size, card_size)
            if i < len(team):
                hero_type = team[i];
                is_upgraded = hero_type in upgraded_heroes
                self._draw_unit_card(surface, hero_type, slot_rect, DEFENDERS_DATA[hero_type], is_upgraded)
                team_card_rects[hero_type] = slot_rect
                if 'upgrade' in DEFENDERS_DATA[hero_type] and not is_upgraded:
                    upgrade_rect = pygame.Rect(slot_rect.centerx - 50, slot_rect.bottom + 5, 100, 30)
                    pygame.draw.rect(surface, YELLOW, upgrade_rect, border_radius=5)
                    cost = DEFENDERS_DATA[hero_type]['upgrade']['cost']
                    cost_surf = self.font_tiny.render(f"Улучшить ({cost})", True, BLACK)
                    surface.blit(cost_surf, cost_surf.get_rect(center=upgrade_rect.center))
                    upgrade_buttons[hero_type] = upgrade_rect
            else:
                pygame.draw.rect(surface, (0, 0, 0, 50), slot_rect, border_radius=10)

        team_block_end_y = start_y + 2 * (card_size + padding_y)

        # --- Кнопка "Случайная команда" ---
        random_buttons = {}
        random_team_rect = pygame.Rect(0, 0, 220, 40)
        random_team_rect.center = (panel_rect.centerx, team_block_end_y + 35)
        pygame.draw.rect(surface, BLUE, random_team_rect, border_radius=10);
        pygame.draw.rect(surface, WHITE, random_team_rect, 2, border_radius=10)
        random_text = self.font_small.render("Случайная команда", True, WHITE);
        surface.blit(random_text, random_text.get_rect(center=random_team_rect.center))
        random_buttons['team'] = random_team_rect

        # --- Блок Нейросетей ---
        neuro_y_start = random_team_rect.bottom + 15
        self._render_text_with_title(surface, f"Нейросети ({len(purchased_mowers)}/{neuro_slots}):", self.font_small,
                                     YELLOW, panel_rect.centerx, neuro_y_start)
        neuro_start_x = panel_rect.centerx - (neuro_slots * 80 + (neuro_slots - 1) * 10) / 2
        for i in range(neuro_slots):
            rect = pygame.Rect(neuro_start_x + i * 90, neuro_y_start + 40, 80, 80)
            if i < len(purchased_mowers):
                self._draw_unit_card(surface, purchased_mowers[i], rect, NEURO_MOWERS_DATA[purchased_mowers[i]])
            else:
                pygame.draw.rect(surface, (0, 0, 0, 50), rect, border_radius=10)

        # --- Кнопка "Случайные нейросети" ---
        random_neuro_rect = pygame.Rect(0, 0, 220, 40)
        random_neuro_rect.center = (panel_rect.centerx, neuro_y_start + 140)
        pygame.draw.rect(surface, BLUE, random_neuro_rect, border_radius=10);
        pygame.draw.rect(surface, WHITE, random_neuro_rect, 2, border_radius=10)
        random_text = self.font_small.render("Случайные нейросети", True, WHITE);
        surface.blit(random_text, random_text.get_rect(center=random_neuro_rect.center))
        random_buttons['neuro'] = random_neuro_rect

        return random_buttons, team_card_rects, upgrade_buttons

    def _draw_selection_panel(self, surface, panel_rect):
        self._draw_panel_with_title(surface, panel_rect, "Выбор юнитов")
        all_defenders = list(DEFENDERS_DATA.keys());
        all_neuro_mowers = list(NEURO_MOWERS_DATA.keys())
        self._render_text_with_title(surface, "Герои:", self.font_small, WHITE, panel_rect.centerx, panel_rect.top + 70)
        rects1 = self._draw_card_selection_list(surface, panel_rect, all_defenders, DEFENDERS_DATA, 100)
        self._render_text_with_title(surface, "Нейросети:", self.font_small, WHITE, panel_rect.centerx,
                                     panel_rect.top + 350)
        rects2 = self._draw_card_selection_list(surface, panel_rect, all_neuro_mowers, NEURO_MOWERS_DATA, 380)
        return {**rects1, **rects2}

    def _draw_plan_panel(self, surface, panel_rect, level_id):
        self._draw_panel_with_title(surface, panel_rect, "Учебный план")
        temp_level_manager = LevelManager(level_id, None, None)
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

    def _draw_card_selection_list(self, surface, panel_rect, types, data_source, start_y_offset):
        card_rects = {}
        card_size, padding, cols = 80, 15, 4
        for i, item_type in enumerate(types):
            row, col = divmod(i, cols)
            x = panel_rect.left + padding + col * (card_size + padding)
            y = panel_rect.top + start_y_offset + row * (card_size + padding + 20)
            card_rect = pygame.Rect(x, y, card_size, card_size)
            if item_type in data_source:
                self._draw_unit_card(surface, item_type, card_rect, data_source[item_type])
                card_rects[item_type] = card_rect
        return card_rects

    def _draw_prep_hud(self, surface, team_is_ready):
        start_button_rect = pygame.Rect(0, 0, 300, 60)
        start_button_rect.center = (self.selection_panel_rect.centerx, self.selection_panel_rect.bottom + 40)
        color = GREEN if team_is_ready else GREY
        pygame.draw.rect(surface, color, start_button_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, start_button_rect, 2, border_radius=10)
        start_text = self.font.render("К расстановке", True, BLACK)
        surface.blit(start_text, start_text.get_rect(center=start_button_rect.center))
        return start_button_rect

    def _draw_unit_card(self, surface, unit_type, rect, data, is_upgraded=False):
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_card'], rect, border_radius=10)
        if is_upgraded:
            pygame.draw.rect(surface, AURA_PINK, rect.inflate(4, 4), 4, border_radius=12)
        default_color = DEFAULT_COLORS.get(unit_type, RED)
        img = load_image(f"{unit_type}.png", default_color, (rect.width - 10, rect.height - 10))
        surface.blit(img, img.get_rect(center=rect.center))
        cost = data.get('cost')
        if cost is not None:
            cost_surf = self.font_tiny.render(str(cost), True, YELLOW)
            surface.blit(cost_surf, cost_surf.get_rect(bottomright=(rect.right - 5, rect.bottom - 2)))

    def _draw_description_panel(self, surface, card_data, can_be_taken=False):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA);
        overlay.fill((0, 0, 0, 180));
        surface.blit(overlay, (0, 0))
        panel_w, panel_h = 600, 450
        self.desc_panel_rect = pygame.Rect((SCREEN_WIDTH - panel_w) / 2, (SCREEN_HEIGHT - panel_h) / 2, panel_w,
                                           panel_h)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], self.desc_panel_rect, border_radius=15);
        pygame.draw.rect(surface, WHITE, self.desc_panel_rect, 3, border_radius=15)
        img_size = 120;
        default_color = DEFAULT_COLORS.get(card_data['type'], RED)
        img = load_image(f"{card_data['type']}.png", default_color, (img_size, img_size));
        img_rect = img.get_rect(centerx=self.desc_panel_rect.centerx, top=self.desc_panel_rect.top + 20);
        surface.blit(img, img_rect)
        name_surf = self.font.render(card_data['name'], True, YELLOW);
        name_rect = name_surf.get_rect(centerx=self.desc_panel_rect.centerx, top=img_rect.bottom + 10);
        surface.blit(name_surf, name_rect)

        left_margin = self.desc_panel_rect.left + 40;
        line_height = 30;
        line_y = name_rect.bottom + 20
        all_data_sources = {**DEFENDERS_DATA, **ENEMIES_DATA}
        unit_data = all_data_sources.get(card_data['type'])

        if unit_data:
            stats_to_render = {"Здоровье:": unit_data.get('health'), "Урон:": unit_data.get('damage'),
                               "Перезарядка:": unit_data.get('cooldown')}
            for title, value in stats_to_render.items():
                if value is None:
                    value_str = "Нет"
                elif value == 0:
                    value_str = "0"
                else:
                    value_str = f"{value}" + (" сек." if title == "Перезарядка:" else "")
                title_surf = self.font_small_bold.render(title, True, WHITE);
                value_surf = self.font_small.render(value_str, True, WHITE)
                surface.blit(title_surf, (left_margin, line_y));
                surface.blit(value_surf, (left_margin + 180, line_y));
                line_y += line_height
            line_y += 10

        desc_title_surf = self.font_small_bold.render("Описание:", True, WHITE);
        surface.blit(desc_title_surf, (left_margin, line_y));
        line_y += line_height
        wrapped_lines = self._render_text_wrapped(card_data['description'], self.font_small, WHITE, panel_w - 80)
        for line_surf in wrapped_lines: surface.blit(line_surf, (left_margin, line_y)); line_y += line_surf.get_height()

        buttons = {}
        close_rect = pygame.Rect(self.desc_panel_rect.right - 45, self.desc_panel_rect.top + 10, 35, 35)
        pygame.draw.line(surface, WHITE, close_rect.topleft, close_rect.bottomright, 3);
        pygame.draw.line(surface, WHITE, close_rect.topright, close_rect.bottomleft, 3);
        buttons['close'] = close_rect
        if can_be_taken:
            take_rect = pygame.Rect(0, 0, 180, 50);
            take_rect.center = (self.desc_panel_rect.centerx, self.desc_panel_rect.bottom - 45);
            pygame.draw.rect(surface, GREEN, take_rect, border_radius=10);
            pygame.draw.rect(surface, WHITE, take_rect, 2, border_radius=10)
            take_text = self.font.render("Взять", True, BLACK);
            surface.blit(take_text, take_text.get_rect(center=take_rect.center));
            buttons['take'] = take_rect
        return buttons

    def _render_text_wrapped(self, text, font, color, max_width):
        words = text.split(' ');
        lines = [];
        current_line = ""
        for word in words:
            test_line = current_line + word + " ";
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(font.render(current_line, True, color)); current_line = word + " "
        lines.append(font.render(current_line, True, color));
        return lines

    def _draw_panel_with_title(self, surface, rect, title):
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, rect, 3, border_radius=15)
        self._render_text_with_title(surface, title, self.font, WHITE, rect.centerx, rect.top + 30)

    def _render_text_with_title(self, surface, text, font, color, center_x, top_y):
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, text_surf.get_rect(centerx=center_x, top=top_y))

    def draw_neuro_placement_screen(self, surface, purchased_mowers, placed_mowers, dragged_mower_info):
        """
        Отрисовывает новый экран расстановки нейросетей с центральной панелью.
        """
        surface.blit(load_image('background.png', DEFAULT_COLORS['background'], (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        self.draw_grid(surface)

        # --- 1. Рисуем ячейки для размещения слева от основного поля ---
        placement_zone_width = CELL_SIZE_W + 20
        placement_zone_x = GRID_START_X - placement_zone_width

        for row in range(GRID_ROWS):
            # Координаты для центра ячейки
            slot_center_x = placement_zone_x + placement_zone_width / 2
            slot_center_y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2

            # Рисуем "черную ячейку" для посадки
            slot_rect = pygame.Rect(0, 0, CELL_SIZE_W, CELL_SIZE_H)
            slot_rect.center = (slot_center_x, slot_center_y)

            pygame.draw.rect(surface, (20, 20, 20, 200), slot_rect, border_radius=10)  # Полупрозрачный темный фон
            pygame.draw.rect(surface, WHITE, slot_rect, 2, border_radius=10)  # Белая рамка

        # --- 2. Рисуем уже размещенные нейросети в их ячейках ---
        for row, info in placed_mowers.items():
            y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
            x = placement_zone_x + placement_zone_width / 2
            img = load_image(f"{info['type']}.png", DEFAULT_COLORS[info['type']], (CELL_SIZE_W - 10, CELL_SIZE_H - 10))
            surface.blit(img, img.get_rect(center=(x, y)))

        # --- 3. Рисуем центральную панель для выбора нейросетей ---
        panel_w, panel_h = 600, 550
        # Смещаем панель немного вправо от центра, как вы и хотели
        panel_x = (SCREEN_WIDTH - panel_w) / 2 + 100
        panel_y = (SCREEN_HEIGHT - panel_h) / 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Рисуем саму панель (коричневую, как вы просили)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], panel_rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, panel_rect, 3, border_radius=15)

        # Заголовок на панели
        self._render_text_with_title(surface, "Расставьте нейросети по рядам", self.font, WHITE, panel_rect.centerx,
                                     panel_rect.top + 30)

        # --- 4. Отображаем карточки неразмещенных нейросетей на панели ---
        card_size, padding, cols = 100, 20, 4
        unplaced_mowers_rects = {}
        # Получаем список тех, что еще не размещены
        placed_indices = [info.get('original_index') for info in placed_mowers.values()]
        unplaced_mower_list_with_indices = [
            (i, m) for i, m in enumerate(purchased_mowers) if i not in placed_indices
        ]

        start_x = panel_rect.left + (panel_rect.width - (cols * card_size + (cols - 1) * padding)) / 2
        start_y = panel_rect.top + 100

        for i, (original_index, mower_type) in enumerate(unplaced_mower_list_with_indices):
            row, col = divmod(i, cols)
            x = start_x + col * (card_size + padding)
            y = start_y + row * (card_size + padding)
            rect = pygame.Rect(x, y, card_size, card_size)
            self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])
            unplaced_mowers_rects[original_index] = rect

        # --- 5. Рисуем кнопку "В Бой!" под центральной панелью ---
        can_start = len(purchased_mowers) == len(placed_mowers)
        start_button_rect = pygame.Rect(0, 0, 300, 70)
        start_button_rect.center = (panel_rect.centerx, panel_rect.bottom - 60)  # Позиция внутри панели
        color = GREEN if can_start else GREY

        pygame.draw.rect(surface, color, start_button_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, start_button_rect, 2, border_radius=10)
        start_text = self.font_large.render("В Бой!", True, BLACK)
        surface.blit(start_text, start_text.get_rect(center=start_button_rect.center))

        # --- 6. Рисуем перетаскиваемую нейросеть поверх всего ---
        if dragged_mower_info:
            pos = dragged_mower_info['pos']
            mower_type = dragged_mower_info['type']
            # Используем card_size, чтобы перетаскиваемый юнит был того же размера, что и на панели
            rect = pygame.Rect(0, 0, card_size, card_size)
            rect.center = pos
            self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])

        return unplaced_mowers_rects, start_button_rect