# core/ui_manager.py

import pygame
from data.settings import *
from data.assets import CARD_IMAGES, load_image, UI_IMAGES
from data.levels import LEVELS

# УБИРАЕМ ПРОБЛЕМНЫЙ ИМПОРТ:
# from core.level_manager import LevelManager

STAT_DISPLAY_NAMES = {
    'health': 'Здоровье:', 'damage': 'Урон:', 'cooldown': 'Перезарядка:', 'radius': 'Радиус:',
    'production': 'Производство:', 'buff': 'Усиление:', 'heal_amount': 'Запас лечения:',
    'slow_duration': 'Длит. замедл.:', 'slow_factor': 'Сила замедл.:',
    'speed': 'Скорость:', 'projectile_speed': 'Скор. снаряда:'
}


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(FONT_FAMILY_DEFAULT, FONT_SIZE_NORMAL)
        self.font_small = pygame.font.SysFont(FONT_FAMILY_DEFAULT, FONT_SIZE_SMALL)
        self.font_small_bold = pygame.font.SysFont(FONT_FAMILY_DEFAULT, FONT_SIZE_SMALL, bold=True)
        self.font_tiny = pygame.font.SysFont(FONT_FAMILY_DEFAULT, FONT_SIZE_TINY)
        self.font_large = pygame.font.SysFont(FONT_FAMILY_DEFAULT, FONT_SIZE_LARGE)
        self.font_huge = pygame.font.SysFont(FONT_FAMILY_IMPACT, FONT_SIZE_HUGE)

        self.prep_background_image = load_image('prep_background.png', DEFAULT_COLORS['background'],
                                                (SCREEN_WIDTH, SCREEN_HEIGHT))

        panel_width = (SCREEN_WIDTH - 4 * PREP_PANEL_MARGIN) / 3
        panel_height = SCREEN_HEIGHT - 150
        self.team_panel_rect = pygame.Rect(PREP_PANEL_MARGIN, PREP_TOP_Y, panel_width, panel_height)
        self.selection_panel_rect = pygame.Rect(self.team_panel_rect.right + PREP_PANEL_MARGIN, PREP_TOP_Y, panel_width,
                                                panel_height)
        self.plan_panel_rect = pygame.Rect(self.selection_panel_rect.right + PREP_PANEL_MARGIN, PREP_TOP_Y, panel_width,
                                           panel_height)
        self.selection_cards_rects = {}
        self.team_card_rects = {}
        self.plan_cards_rects = {}
        self.desc_panel_rect = None
        self.shop_items = []
        self.shop_rects = {}
        self.shop_panel_surf = pygame.Surface((SCREEN_WIDTH, SHOP_PANEL_HEIGHT), pygame.SRCALPHA)
        self.pause_button_rect = pygame.Rect(
            SCREEN_WIDTH + PAUSE_BUTTON_X_OFFSET,
            (SHOP_PANEL_HEIGHT - PAUSE_BUTTON_SIZE[1]) / 2,
            *PAUSE_BUTTON_SIZE
        )

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

            title_font = pygame.font.SysFont(FONT_FAMILY_TITLE, FONT_SIZE_TITLE)
            title_surf = title_font.render(title_text, True, TITLE_BROWN)
            title_rect = title_surf.get_rect(
                center=(plaque_rect.centerx, plaque_rect.centery + TITLE_PLAQUE_TEXT_V_OFFSET))
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

            pygame.draw.rect(surface, button_color, rect, border_radius=DEFAULT_BORDER_RADIUS)
            pygame.draw.rect(surface, WHITE, rect, DEFAULT_BORDER_WIDTH, border_radius=DEFAULT_BORDER_RADIUS)
            text = self.font.render(name, True, WHITE)
            surface.blit(text, text.get_rect(center=rect.center))

    def create_battle_shop(self, team):
        self.shop_items = team
        self.shop_rects = {}
        self.shop_panel_surf.fill(DEFAULT_COLORS['shop_panel'])

        coffee_area_rect = pygame.Rect(0, 0, SHOP_COFFEE_AREA_WIDTH, SHOP_PANEL_HEIGHT)
        pygame.draw.rect(self.shop_panel_surf, DEFAULT_COLORS['shop_card'], coffee_area_rect.inflate(-10, -10),
                         border_radius=DEFAULT_BORDER_RADIUS)
        coffee_icon = CARD_IMAGES.get('coffee_bean')
        if coffee_icon:
            coffee_icon = pygame.transform.scale(coffee_icon, SHOP_COFFEE_ICON_SIZE)
            icon_rect = coffee_icon.get_rect(
                midleft=(coffee_area_rect.left + SHOP_COFFEE_ICON_X_OFFSET, coffee_area_rect.centery))
            self.shop_panel_surf.blit(coffee_icon, icon_rect)

        shop_items_start_x = SHOP_COFFEE_AREA_WIDTH
        for i, item_name in enumerate(self.shop_items):
            card_x = shop_items_start_x + i * (SHOP_CARD_SIZE + SHOP_ITEM_PADDING) + SHOP_ITEM_PADDING
            card_y = (SHOP_PANEL_HEIGHT - SHOP_CARD_SIZE) / 2
            card_rect = pygame.Rect(card_x, card_y, SHOP_CARD_SIZE, SHOP_CARD_SIZE)
            self.shop_rects[item_name] = card_rect

            pygame.draw.rect(self.shop_panel_surf, DEFAULT_COLORS['shop_card'], card_rect, border_radius=5)
            pygame.draw.rect(self.shop_panel_surf, DEFAULT_COLORS['shop_border'], card_rect, THICK_BORDER_WIDTH,
                             border_radius=5)

    def draw_shop(self, surface, selected_defender, coffee_beans, upgrades):
        surface.blit(self.shop_panel_surf, (0, 0))
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_border'], (0, 0, SCREEN_WIDTH, SHOP_PANEL_HEIGHT), 5)

        coffee_text = self.font.render(f"{coffee_beans}", True, WHITE)
        text_rect = coffee_text.get_rect(midleft=(90, SHOP_PANEL_HEIGHT / 2))
        surface.blit(coffee_text, text_rect)

        for hero_type in self.shop_items:
            if hero_type in upgrades:
                rect = self.shop_rects[hero_type]
                pygame.draw.rect(surface, AURA_PINK, rect, SHOP_UPGRADE_BORDER_WIDTH, border_radius=5)

        if selected_defender:
            rect = self.shop_rects[selected_defender]
            pygame.draw.rect(surface, YELLOW, rect, SHOP_SELECTED_BORDER_WIDTH, border_radius=5)

        for item_name in self.shop_items:
            card_rect = self.shop_rects[item_name]

            item_image = CARD_IMAGES.get(item_name)
            if item_image:
                img_rect = item_image.get_rect(center=card_rect.center)
                img_rect.y += SHOP_CARD_IMG_Y_OFFSET
                surface.blit(item_image, img_rect)

            cost_text = self.font_small.render(f"{DEFENDERS_DATA[item_name]['cost']}", True, WHITE)
            text_rect = cost_text.get_rect(center=(card_rect.centerx, card_rect.bottom + SHOP_CARD_COST_Y_OFFSET))
            surface.blit(cost_text, text_rect)

    def draw_hud(self, surface, spawn_progress, kill_progress, spawn_count_data, kill_count_data,
                 calamity_notification):
        enemies_spawned, total_spawn = spawn_count_data
        enemies_killed, total_kill = kill_count_data

        brs_y = SCREEN_HEIGHT - HUD_BAR_HEIGHT - HUD_BOTTOM_MARGIN
        brs_x = SCREEN_WIDTH - HUD_BAR_WIDTH - HUD_RIGHT_MARGIN
        pygame.draw.rect(surface, GREY, (brs_x, brs_y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT), border_radius=5)
        pygame.draw.rect(surface, GREEN, (brs_x, brs_y, HUD_BAR_WIDTH * kill_progress, HUD_BAR_HEIGHT), border_radius=5)
        brs_text_surf = self.font_tiny.render(f"БРС: {enemies_killed} / {total_kill}", True, BLACK)
        surface.blit(brs_text_surf,
                     brs_text_surf.get_rect(center=(brs_x + HUD_BAR_WIDTH / 2, brs_y + HUD_BAR_HEIGHT / 2)))
        pygame.draw.rect(surface, WHITE, (brs_x, brs_y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT), DEFAULT_BORDER_WIDTH,
                         border_radius=5)

        plan_y, plan_x = brs_y - HUD_BAR_HEIGHT - HUD_BAR_V_GAP, brs_x
        pygame.draw.rect(surface, GREY, (plan_x, plan_y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT), border_radius=5)
        pygame.draw.rect(surface, PROGRESS_BLUE, (plan_x, plan_y, HUD_BAR_WIDTH * spawn_progress, HUD_BAR_HEIGHT),
                         border_radius=5)
        plan_text_surf = self.font_tiny.render(f"Учебный план: {enemies_spawned} / {total_spawn}", True, WHITE)
        surface.blit(plan_text_surf,
                     plan_text_surf.get_rect(center=(plan_x + HUD_BAR_WIDTH / 2, plan_y + HUD_BAR_HEIGHT / 2)))
        pygame.draw.rect(surface, WHITE, (plan_x, plan_y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT), DEFAULT_BORDER_WIDTH,
                         border_radius=5)

        pygame.draw.rect(surface, DEFAULT_COLORS['pause_button'], self.pause_button_rect,
                         border_radius=DEFAULT_BORDER_RADIUS)
        pygame.draw.rect(surface, WHITE, self.pause_button_rect, DEFAULT_BORDER_WIDTH,
                         border_radius=DEFAULT_BORDER_RADIUS)
        bar1 = pygame.Rect(0, 0, PAUSE_BAR_WIDTH, PAUSE_BAR_HEIGHT)
        bar1.center = (self.pause_button_rect.centerx - PAUSE_BAR_H_SPACING, self.pause_button_rect.centery)
        bar2 = pygame.Rect(0, 0, PAUSE_BAR_WIDTH, PAUSE_BAR_HEIGHT)
        bar2.center = (self.pause_button_rect.centerx + PAUSE_BAR_H_SPACING, self.pause_button_rect.centery)
        pygame.draw.rect(surface, BLACK, bar1, border_radius=3)
        pygame.draw.rect(surface, BLACK, bar2, border_radius=3)

        if calamity_notification:
            panel_rect = pygame.Rect((0, 0), CALAMITY_PANEL_SIZE)
            panel_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            panel_surf.fill(CALAMITY_PANEL_BG)
            surface.blit(panel_surf, panel_rect.topleft)
            pygame.draw.rect(surface, CALAMITY_BORDER_RED, panel_rect, CALAMITY_PANEL_BORDER_WIDTH,
                             border_radius=CALAMITY_PANEL_BORDER_RADIUS)

            icon = CARD_IMAGES.get(calamity_notification['type'])
            icon_rect = None
            if icon:
                icon = pygame.transform.scale(icon, CALAMITY_ICON_SIZE)
                icon_rect = icon.get_rect(centery=panel_rect.centery, left=panel_rect.left + CALAMITY_ICON_LEFT_MARGIN)
                surface.blit(icon, icon_rect)

            text_area_left_margin = (icon_rect.right if icon_rect else panel_rect.left) + CALAMITY_TEXT_LEFT_MARGIN
            max_text_width = (panel_rect.right - CALAMITY_TEXT_LEFT_MARGIN) - text_area_left_margin

            name_surf = self.font_large.render(calamity_notification['name'], True, CALAMITY_ORANGE)
            name_rect = name_surf.get_rect(left=text_area_left_margin, top=panel_rect.top + CALAMITY_NAME_TOP_MARGIN)
            surface.blit(name_surf, name_rect)

            wrapped_lines = self._render_text_wrapped(
                calamity_notification['desc'], self.font_small, WHITE, max_text_width
            )

            current_y = name_rect.bottom + CALAMITY_DESC_TOP_MARGIN
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
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MENU_OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))
        title = self.font_large.render(title_text, True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)))
        for name, rect in buttons.items():
            pygame.draw.rect(surface, DEFAULT_COLORS['button'], rect, border_radius=DEFAULT_BORDER_RADIUS)
            pygame.draw.rect(surface, WHITE, rect, DEFAULT_BORDER_WIDTH, border_radius=DEFAULT_BORDER_RADIUS)
            text = self.font.render(name, True, WHITE)
            surface.blit(text, text.get_rect(center=rect.center))

    def draw_settings_menu(self, surface, music_enabled, sfx_enabled):
        panel_rect = pygame.Rect(
            (SCREEN_WIDTH - SETTINGS_PANEL_SIZE[0]) / 2,
            (SCREEN_HEIGHT - SETTINGS_PANEL_SIZE[1]) / 2,
            *SETTINGS_PANEL_SIZE
        )
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], panel_rect, border_radius=SETTINGS_BORDER_RADIUS)
        pygame.draw.rect(surface, WHITE, panel_rect, THICK_BORDER_WIDTH, border_radius=SETTINGS_BORDER_RADIUS)

        title_surf = self.font_large.render("Настройки", True, WHITE)
        surface.blit(title_surf,
                     title_surf.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + SETTINGS_TITLE_TOP_MARGIN))

        buttons = {}

        music_label_surf = self.font.render("Фоновая музыка", True, WHITE)
        music_label_rect = music_label_surf.get_rect(
            midleft=(panel_rect.left + SETTINGS_LABEL_LEFT_MARGIN, panel_rect.centery - SETTINGS_LABEL_V_OFFSET))
        surface.blit(music_label_surf, music_label_rect)

        music_toggle_img = UI_IMAGES['toggle_on'] if music_enabled else UI_IMAGES['toggle_off']
        music_toggle_rect = music_toggle_img.get_rect(
            midright=(panel_rect.right - SETTINGS_TOGGLE_RIGHT_MARGIN, music_label_rect.centery))
        surface.blit(music_toggle_img, music_toggle_rect)
        buttons['toggle_music'] = music_toggle_rect

        sfx_label_surf = self.font.render("Звуковые эффекты", True, WHITE)
        sfx_label_rect = sfx_label_surf.get_rect(
            midleft=(panel_rect.left + SETTINGS_LABEL_LEFT_MARGIN, panel_rect.centery + SETTINGS_LABEL_V_OFFSET))
        surface.blit(sfx_label_surf, sfx_label_rect)

        sfx_toggle_img = UI_IMAGES['toggle_on'] if sfx_enabled else UI_IMAGES['toggle_off']
        sfx_toggle_rect = sfx_toggle_img.get_rect(
            midright=(panel_rect.right - SETTINGS_TOGGLE_RIGHT_MARGIN, sfx_label_rect.centery))
        surface.blit(sfx_toggle_img, sfx_toggle_rect)
        buttons['toggle_sfx'] = sfx_toggle_rect

        close_rect = pygame.Rect(
            panel_rect.right - SETTINGS_CLOSE_BUTTON_SIZE - SETTINGS_CLOSE_BUTTON_MARGIN,
            panel_rect.top + SETTINGS_CLOSE_BUTTON_MARGIN,
            SETTINGS_CLOSE_BUTTON_SIZE, SETTINGS_CLOSE_BUTTON_SIZE
        )
        pygame.draw.line(surface, WHITE, close_rect.topleft, close_rect.bottomright, SETTINGS_CLOSE_BUTTON_LINE_WIDTH)
        pygame.draw.line(surface, WHITE, close_rect.topright, close_rect.bottomleft, SETTINGS_CLOSE_BUTTON_LINE_WIDTH)
        buttons['close'] = close_rect

        return buttons

    def draw_main_menu(self, surface, max_level_unlocked):
        panel_rect = pygame.Rect(MAIN_MENU_PANEL_X_OFFSET, (SCREEN_HEIGHT - MAIN_MENU_PANEL_SIZE[1]) / 2,
                                 *MAIN_MENU_PANEL_SIZE)
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], panel_rect, border_radius=SETTINGS_BORDER_RADIUS)
        pygame.draw.rect(surface, WHITE, panel_rect, THICK_BORDER_WIDTH, border_radius=SETTINGS_BORDER_RADIUS)
        title = self.font_large.render("Главное меню", True, WHITE)
        surface.blit(title, title.get_rect(center=(panel_rect.centerx, panel_rect.top + MAIN_MENU_TITLE_TOP_OFFSET)))

        level_buttons = {}
        for level_id, data in LEVELS.items():
            if level_id == 0: continue
            is_unlocked = level_id <= max_level_unlocked
            button_rect = pygame.Rect((0, 0), MAIN_MENU_LEVEL_BUTTON_SIZE)
            button_rect.center = (panel_rect.centerx, panel_rect.top + MAIN_MENU_LEVEL_BUTTON_TOP_OFFSET + (
                        level_id - 1) * MAIN_MENU_LEVEL_BUTTON_V_SPACING)
            color = YELLOW if is_unlocked else GREY
            pygame.draw.rect(surface, color, button_rect, border_radius=DEFAULT_BORDER_RADIUS)
            pygame.draw.rect(surface, WHITE, button_rect, DEFAULT_BORDER_WIDTH, border_radius=DEFAULT_BORDER_RADIUS)
            text_surf = self.font.render(data['name'], True, BLACK)
            surface.blit(text_surf, text_surf.get_rect(center=button_rect.center))
            if is_unlocked: level_buttons[level_id] = button_rect

        control_buttons = {}
        btn_width, btn_height = MAIN_MENU_CONTROL_BUTTON_SIZE
        base_x = SCREEN_WIDTH - MAIN_MENU_CONTROL_RIGHT_OFFSET - btn_width
        settings_x = base_x - (btn_width / 2 + MAIN_MENU_CONTROL_H_GAP / 2)
        test_x = base_x + (btn_width / 2 + MAIN_MENU_CONTROL_H_GAP / 2)

        settings_rect = pygame.Rect((0, 0), (btn_width, btn_height))
        settings_rect.center = (settings_x, MAIN_MENU_CONTROL_TOP_OFFSET)
        self._draw_button(surface, "Настройки", settings_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Настройки"] = settings_rect

        test_rect = pygame.Rect((0, 0), (btn_width, btn_height))
        test_rect.center = (test_x, MAIN_MENU_CONTROL_TOP_OFFSET)
        self._draw_button(surface, "Тест", test_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Тест"] = test_rect

        exit_rect = pygame.Rect((0, 0), (btn_width * 2 + MAIN_MENU_CONTROL_H_GAP, btn_height))
        exit_rect.center = (base_x, MAIN_MENU_CONTROL_TOP_OFFSET + btn_height + MAIN_MENU_CONTROL_V_GAP)
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
                                all_defenders, all_neuro_mowers, selected_card_info, neuro_slots,
                                current_team, current_mowers, enemy_types, calamity_types):
        surface.blit(self.prep_background_image, (0, 0))

        random_buttons = self._draw_team_panel(surface, self.team_panel_rect, team,
                                               upgrades, purchased_mowers, neuro_slots)
        self.selection_cards_rects = self._draw_selection_panel(surface, self.selection_panel_rect, upgrades,
                                                                current_team, current_mowers)
        self.plan_cards_rects = self._draw_plan_panel(surface, self.plan_panel_rect, enemy_types, calamity_types)
        prep_buttons = self._draw_prep_hud(surface, len(team) > 0)

        stipend_bg_rect = pygame.Rect((0, 0), (PREP_STIPEND_PANEL_WIDTH, PREP_STIPEND_PANEL_HEIGHT))
        stipend_bg_rect.centerx = SCREEN_WIDTH / 2
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], stipend_bg_rect, border_radius=DEFAULT_BORDER_RADIUS)

        stipend_text = self.font.render(f"Стипендия: {stipend}", True, YELLOW)
        text_rect = stipend_text.get_rect(center=stipend_bg_rect.center)

        stipend_icon = CARD_IMAGES.get('stipend')
        if stipend_icon:
            text_rect.centerx += PREP_STIPEND_ICON_X_OFFSET
            surface.blit(stipend_text, text_rect)
            icon_rect = stipend_icon.get_rect(
                midleft=(text_rect.right + PREP_STIPEND_ICON_TEXT_GAP, stipend_bg_rect.centery))
            surface.blit(stipend_icon, icon_rect)
        else:
            surface.blit(stipend_text, text_rect)

        info_buttons = {}
        if selected_card_info:
            info_buttons = self._draw_description_panel(surface, selected_card_info, team,
                                                        upgrades, purchased_mowers, neuro_slots)

        return prep_buttons, random_buttons, info_buttons

    def _draw_unit_card(self, surface, unit_type, rect, data, is_upgraded=False, is_selected=False):
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_card'], rect, border_radius=DEFAULT_BORDER_RADIUS)
        if is_upgraded:
            pygame.draw.rect(surface, AURA_PINK, rect.inflate(4, 4), SHOP_UPGRADE_BORDER_WIDTH, border_radius=12)
        if is_selected:
            pygame.draw.rect(surface, YELLOW, rect, THICK_BORDER_WIDTH, border_radius=12)

        img = CARD_IMAGES.get(unit_type)
        if img:
            if img.get_size() != (rect.width - 10, rect.height - 10):
                img = pygame.transform.scale(img, (rect.width - 10, rect.height - 10))
            surface.blit(img, img.get_rect(center=rect.center))

        cost = data.get('cost')
        if cost is not None:
            cost_color = COFFEE_COST_COLOR
            if unit_type in NEURO_MOWERS_DATA:
                cost_color = YELLOW
            cost_surf = self.font_tiny.render(str(cost), True, cost_color)
            surface.blit(cost_surf, cost_surf.get_rect(bottomright=(rect.right - 5, rect.bottom - 2)))

    def _draw_desc_panel_header(self, surface, card_type, name):
        img_size = DESC_PANEL_IMG_SIZE
        img = CARD_IMAGES.get(card_type)
        if img:
            img = pygame.transform.scale(img, (img_size, img_size))
            img_rect = img.get_rect(centerx=self.desc_panel_rect.centerx,
                                    top=self.desc_panel_rect.top + DESC_PANEL_IMG_TOP_MARGIN)
            surface.blit(img, img_rect)
        else:
            img_rect = pygame.Rect(0, 0, img_size, img_size)
            img_rect.centerx = self.desc_panel_rect.centerx
            img_rect.top = self.desc_panel_rect.top + DESC_PANEL_IMG_TOP_MARGIN

        name_surf = self.font.render(name, True, YELLOW)
        name_rect = name_surf.get_rect(centerx=self.desc_panel_rect.centerx,
                                       top=img_rect.bottom + DESC_PANEL_NAME_TOP_MARGIN)
        surface.blit(name_surf, name_rect)
        return name_rect

    def _draw_team_panel(self, surface, panel_rect, team, upgrades, purchased_mowers, neuro_slots):
        self._draw_panel_with_title(surface, panel_rect, "Твоя команда")
        random_buttons = {}

        hero_slots_bottom_y = self._render_hero_slots(surface, panel_rect, team, upgrades)
        random_team_rect = pygame.Rect((0, 0), PREP_RANDOM_TEAM_BTN_SIZE)
        random_team_rect.center = (panel_rect.centerx, hero_slots_bottom_y + PREP_RANDOM_TEAM_BTN_TOP_OFFSET)
        self._draw_button(surface, "Случайная команда", random_team_rect, RANDOM_BUTTON_COLOR, WHITE)
        random_buttons['team'] = random_team_rect
        neuro_slots_bottom_y = self._render_neuro_slots(surface, panel_rect, purchased_mowers, neuro_slots,
                                                        random_team_rect.bottom + PREP_NEURO_SLOTS_TOP_MARGIN)
        random_neuro_rect = pygame.Rect((0, 0), PREP_RANDOM_TEAM_BTN_SIZE)
        random_neuro_rect.center = (panel_rect.centerx, neuro_slots_bottom_y + PREP_RANDOM_NEURO_BTN_TOP_OFFSET)
        self._draw_button(surface, "Случайные нейросети", random_neuro_rect, RANDOM_BUTTON_COLOR, WHITE)
        random_buttons['neuro'] = random_neuro_rect
        return random_buttons

    def _render_hero_slots(self, surface, panel_rect, team, upgrades):
        self._render_text_with_title(surface, "Одногруппники:", self.font_small, YELLOW, panel_rect.centerx,
                                     panel_rect.top + PREP_HERO_SLOTS_TITLE_TOP_OFFSET)
        card_size, padding_x, padding_y, cols = PREP_TEAM_CARD_SIZE, PREP_TEAM_CARD_PADDING_X, PREP_TEAM_CARD_PADDING_Y, PREP_TEAM_COLS
        start_x = panel_rect.centerx - (cols * card_size + (cols - 1) * padding_x) / 2
        start_y = panel_rect.top + PREP_HERO_SLOTS_TOP_OFFSET
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
                pygame.draw.rect(surface, (0, 0, 0, 50), slot_rect, border_radius=DEFAULT_BORDER_RADIUS)
            bottom_y = slot_rect.bottom
        return bottom_y

    def _render_neuro_slots(self, surface, panel_rect, purchased_mowers, neuro_slots, start_y):
        self._render_text_with_title(surface, f"Нейросети ({len(purchased_mowers)}/{neuro_slots}):", self.font_small,
                                     YELLOW, panel_rect.centerx, start_y)
        card_size, spacing = PREP_NEURO_CARD_SIZE, PREP_NEURO_CARD_H_SPACING
        neuro_start_x = panel_rect.centerx - (neuro_slots * card_size + (neuro_slots - 1) * spacing) / 2
        neuro_cards_y = start_y + PREP_NEURO_CARD_TOP_OFFSET
        bottom_y = neuro_cards_y
        for i in range(neuro_slots):
            rect = pygame.Rect(neuro_start_x + i * (card_size + spacing), neuro_cards_y, card_size, card_size)
            if i < len(purchased_mowers):
                mower_type = purchased_mowers[i]
                self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])
                unique_key = f"{mower_type}_{i}"
                self.team_card_rects[unique_key] = rect
            else:
                pygame.draw.rect(surface, (0, 0, 0, 50), rect, border_radius=DEFAULT_BORDER_RADIUS)
            bottom_y = rect.bottom
        return bottom_y

    def _draw_selection_panel(self, surface, panel_rect, upgrades, current_team, current_mowers):
        self._draw_panel_with_title(surface, panel_rect, "Выбор юнитов")
        all_defenders = list(DEFENDERS_DATA.keys())
        all_neuro_mowers = list(NEURO_MOWERS_DATA.keys())
        self._render_text_with_title(surface, "Герои:", self.font_small, WHITE, panel_rect.centerx,
                                     panel_rect.top + PREP_SELECTION_HEROES_TITLE_TOP)
        rects1 = self._draw_card_selection_list(surface, panel_rect, all_defenders, DEFENDERS_DATA,
                                                PREP_SELECTION_HEROES_LIST_TOP, upgrades,
                                                current_team, current_mowers)
        self._render_text_with_title(surface, "Нейросети:", self.font_small, WHITE, panel_rect.centerx,
                                     panel_rect.top + PREP_SELECTION_NEURO_TITLE_TOP)
        rects2 = self._draw_card_selection_list(surface, panel_rect, all_neuro_mowers, NEURO_MOWERS_DATA,
                                                PREP_SELECTION_NEURO_LIST_TOP,
                                                upgrades, current_team, current_mowers)
        return {**rects1, **rects2}

    def _draw_plan_panel(self, surface, panel_rect, enemy_types, calamity_types):
        self._draw_panel_with_title(surface, panel_rect, "Учебный план")
        self._render_text_with_title(surface, "Ожидаемые враги:", self.font_small, WHITE, panel_rect.centerx,
                                     panel_rect.top + PREP_SELECTION_HEROES_TITLE_TOP)
        enemy_rects = self._draw_card_selection_list(surface, panel_rect, enemy_types, ENEMIES_DATA,
                                                     PREP_SELECTION_HEROES_LIST_TOP)
        if calamity_types:
            self._render_text_with_title(surface, "Возможные напасти:", self.font_small, YELLOW, panel_rect.centerx,
                                         panel_rect.top + PREP_SELECTION_NEURO_TITLE_TOP)
            calamity_rects = self._draw_card_selection_list(surface, panel_rect, calamity_types, CALAMITIES_DATA,
                                                            PREP_SELECTION_NEURO_LIST_TOP)
            return {**enemy_rects, **calamity_rects}
        return enemy_rects

    def _draw_card_selection_list(self, surface, panel_rect, types, data_source, start_y_offset, upgrades=None,
                                  current_team=None, current_mowers=None):
        card_rects = {}
        if not types: return card_rects

        card_size, padding, cols = PREP_SELECTION_CARD_SIZE, PREP_SELECTION_CARD_PADDING, PREP_SELECTION_COLS

        items_in_row = min(len(types), cols)
        total_width = items_in_row * card_size + (items_in_row - 1) * padding
        start_x_base = panel_rect.left + (panel_rect.width - total_width) / 2

        for i, item_type in enumerate(types):
            row, col = divmod(i, cols)
            x = start_x_base + col * (card_size + padding)
            y = panel_rect.top + start_y_offset + row * (card_size + padding + PREP_SELECTION_CARD_V_SPACING)
            card_rect = pygame.Rect(x, y, card_size, card_size)
            if item_type in data_source:
                is_upgraded = upgrades and item_type in upgrades
                is_selected = (current_team and item_type in current_team) or \
                              (current_mowers and item_type in current_mowers)
                self._draw_unit_card(surface, item_type, card_rect, data_source[item_type], is_upgraded, is_selected)
                card_rects[item_type] = card_rect
        return card_rects

    def _draw_prep_hud(self, surface, team_is_ready):
        btn_width, btn_height = PREP_HUD_BUTTON_SIZE
        buttons = {}
        back_button_rect = pygame.Rect(PREP_HUD_BOTTOM_MARGIN, SCREEN_HEIGHT - btn_height - PREP_HUD_BOTTOM_MARGIN,
                                       btn_width, btn_height)
        self._draw_button(surface, "Назад", back_button_rect, GREY, WHITE, self.font)
        buttons['back'] = back_button_rect
        start_button_rect = pygame.Rect(SCREEN_WIDTH - btn_width - PREP_HUD_BOTTOM_MARGIN,
                                        SCREEN_HEIGHT - btn_height - PREP_HUD_BOTTOM_MARGIN,
                                        btn_width, btn_height)
        color = GREEN if team_is_ready else GREY
        text_color = BLACK if team_is_ready else DARK_GREY
        self._draw_button(surface, "К расстановке", start_button_rect, color, text_color, self.font)
        buttons['start'] = start_button_rect
        return buttons

    def _draw_button(self, surface, text, rect, color, text_color, font=None):
        if font is None: font = self.font_small
        pygame.draw.rect(surface, color, rect, border_radius=DEFAULT_BORDER_RADIUS)
        pygame.draw.rect(surface, WHITE, rect, DEFAULT_BORDER_WIDTH, border_radius=DEFAULT_BORDER_RADIUS)
        text_surf = font.render(text, True, text_color)
        surface.blit(text_surf, text_surf.get_rect(center=rect.center))

    def _draw_description_panel(self, surface, card_data, team, upgrades, purchased_mowers, neuro_slots):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MENU_OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))
        self.desc_panel_rect = pygame.Rect(
            (SCREEN_WIDTH - DESC_PANEL_SIZE[0]) / 2,
            (SCREEN_HEIGHT - DESC_PANEL_SIZE[1]) / 2,
            *DESC_PANEL_SIZE
        )
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], self.desc_panel_rect,
                         border_radius=DESC_PANEL_BORDER_RADIUS)
        pygame.draw.rect(surface, WHITE, self.desc_panel_rect, THICK_BORDER_WIDTH,
                         border_radius=DESC_PANEL_BORDER_RADIUS)

        card_type = card_data['type']
        img_rect = self._draw_desc_panel_header(surface, card_type, card_data['name'])
        buttons, current_y = self._draw_desc_panel_stats(surface, card_type, team, upgrades,
                                                         img_rect.bottom + DESC_PANEL_STATS_TOP_MARGIN)

        left_margin = self.desc_panel_rect.left + DESC_PANEL_LEFT_MARGIN
        desc_title_surf = self.font_small_bold.render("Описание:", True, WHITE)
        surface.blit(desc_title_surf, (left_margin, current_y + DESC_PANEL_DESC_TITLE_V_OFFSET))

        current_y_desc = current_y + DESC_PANEL_DESC_TEXT_V_OFFSET
        wrapped_lines = self._render_text_wrapped(card_data['description'], self.font_small, WHITE,
                                                  self.desc_panel_rect.width - 2 * DESC_PANEL_LEFT_MARGIN)
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

        left_margin, right_margin = self.desc_panel_rect.left + DESC_PANEL_LEFT_MARGIN, self.desc_panel_rect.right - DESC_PANEL_RIGHT_MARGIN
        line_height, line_y = DESC_PANEL_LINE_HEIGHT, start_y

        for key, title in STAT_DISPLAY_NAMES.items():
            if line_y > self.desc_panel_rect.bottom - 150:
                break
            if key in unit_data:
                base_value, value_color, value_str = self._get_stat_display_values(unit_data, card_type, key, upgrades)

                title_surf = self.font_small_bold.render(title, True, WHITE)
                value_surf = self.font_small.render(value_str, True, value_color)
                surface.blit(title_surf, (left_margin, line_y))
                surface.blit(value_surf, (left_margin + DESC_PANEL_VALUE_X_OFFSET, line_y))

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
            btn_rect = pygame.Rect(0, 0, DESC_PANEL_UPGRADE_BTN_WIDTH,
                                   line_height + DESC_PANEL_UPGRADE_BTN_HEIGHT_ADJUST)
            btn_rect.midleft = (right_margin - btn_rect.width, line_y + line_height / 2)
            self._draw_button(surface, "Отменить", btn_rect, RED, WHITE, self.font_tiny)
            buttons[f'revert_{key}'] = btn_rect
        else:
            bonus = upgrade_info['value']
            bonus_str = f"+{bonus:.1f}".replace('.0', '') if bonus > 0 else f"{bonus:.1f}".replace('.0', '')
            if key == 'radius': bonus_str = f"+{int(bonus)}"
            btn_text = f"Улучшить ({bonus_str}) ({cost}$)"
            btn_rect = pygame.Rect(0, 0, DESC_PANEL_UPGRADE_BTN_WIDTH_WIDE,
                                   line_height + DESC_PANEL_UPGRADE_BTN_HEIGHT_ADJUST)
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

        action_button_rect = pygame.Rect((0, 0), DESC_PANEL_ACTION_BTN_SIZE)
        action_button_rect.center = (
        self.desc_panel_rect.centerx, self.desc_panel_rect.bottom + DESC_PANEL_ACTION_BTN_BOTTOM_OFFSET)

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
            chat_gpt_limit_reached = (card_type == 'chat_gpt' and purchased_mowers.count('chat_gpt') >= CHAT_GPT_LIMIT)
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

        close_rect = pygame.Rect(
            self.desc_panel_rect.right - DESC_PANEL_CLOSE_BUTTON_SIZE - DESC_PANEL_CLOSE_BUTTON_MARGIN,
            self.desc_panel_rect.top + DESC_PANEL_CLOSE_BUTTON_MARGIN,
            DESC_PANEL_CLOSE_BUTTON_SIZE, DESC_PANEL_CLOSE_BUTTON_SIZE
        )
        pygame.draw.line(surface, WHITE, close_rect.topleft, close_rect.bottomright, THICK_BORDER_WIDTH)
        pygame.draw.line(surface, WHITE, close_rect.topright, close_rect.bottomleft, THICK_BORDER_WIDTH)
        buttons['close'] = close_rect
        return buttons

    def _draw_panel_with_title(self, surface, rect, title):
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], rect, border_radius=SETTINGS_BORDER_RADIUS)
        pygame.draw.rect(surface, WHITE, rect, THICK_BORDER_WIDTH, border_radius=SETTINGS_BORDER_RADIUS)
        self._render_text_with_title(surface, title, self.font, WHITE, rect.centerx,
                                     rect.top + PREP_TEAM_PANEL_TITLE_TOP_OFFSET)

    def _render_text_with_title(self, surface, text, font, color, center_x, top_y):
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, text_surf.get_rect(centerx=center_x, top=top_y))

    def _draw_placement_grid(self, surface):
        placement_grid_start_y = (SCREEN_HEIGHT - GRID_ROWS * PLACEMENT_GRID_CELL_H) / 2
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(PLACEMENT_GRID_START_X + col * PLACEMENT_GRID_CELL_W,
                                   placement_grid_start_y + row * PLACEMENT_GRID_CELL_H,
                                   PLACEMENT_GRID_CELL_W, PLACEMENT_GRID_CELL_H)
                s = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(s, GRID_COLOR, s.get_rect(), 1)
                surface.blit(s, rect.topleft)

    def _draw_placement_slots(self, surface):
        placement_grid_start_y = (SCREEN_HEIGHT - GRID_ROWS * PLACEMENT_GRID_CELL_H) / 2
        for row in range(GRID_ROWS):
            slot_rect = pygame.Rect(PLACEMENT_ZONE_X, placement_grid_start_y + row * PLACEMENT_GRID_CELL_H,
                                    PLACEMENT_GRID_CELL_W, PLACEMENT_GRID_CELL_H)
            pygame.draw.rect(surface, (20, 20, 20, 200), slot_rect, border_radius=DEFAULT_BORDER_RADIUS)
            pygame.draw.rect(surface, WHITE, slot_rect, DEFAULT_BORDER_WIDTH, border_radius=DEFAULT_BORDER_RADIUS)

    def _draw_placement_mower(self, surface, row, info):
        placement_grid_start_y = (SCREEN_HEIGHT - GRID_ROWS * PLACEMENT_GRID_CELL_H) / 2
        img = CARD_IMAGES.get(info['type'])
        if img:
            img = pygame.transform.scale(img, (PLACEMENT_GRID_CELL_W - 10, PLACEMENT_GRID_CELL_H - 10))
            rect = img.get_rect(
                centerx=PLACEMENT_ZONE_X + PLACEMENT_GRID_CELL_W / 2,
                centery=placement_grid_start_y + row * PLACEMENT_GRID_CELL_H + PLACEMENT_GRID_CELL_H / 2
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
            rect = pygame.Rect((0, 0), (PLACEMENT_PANEL_CARD_SIZE, PLACEMENT_PANEL_CARD_SIZE))
            rect.center = pos
            self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])

        return unplaced_mowers_rects, start_button_rect

    def _draw_neuro_selection_panel(self, surface, purchased_mowers, placed_mowers):
        unplaced_mowers_rects = {}
        placed_indices = [info.get('original_index') for info in placed_mowers.values()]
        unplaced_mower_list_with_indices = [(i, m) for i, m in enumerate(purchased_mowers) if i not in placed_indices]

        panel_w, panel_h = PLACEMENT_PANEL_SIZE
        panel_x = (SCREEN_WIDTH - panel_w) / 2
        panel_y = (SCREEN_HEIGHT - panel_h) / 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        self._draw_panel_with_title(surface, panel_rect, "Расставьте нейросети по рядам")

        card_size, padding, cols = PLACEMENT_PANEL_CARD_SIZE, PLACEMENT_PANEL_CARD_PADDING, PLACEMENT_PANEL_CARD_COLS
        start_x = panel_rect.left + (panel_rect.width - (cols * card_size + (cols - 1) * padding)) / 2
        start_y = panel_rect.top + PLACEMENT_PANEL_CARDS_TOP_OFFSET
        for i, (original_index, mower_type) in enumerate(unplaced_mower_list_with_indices):
            row, col = divmod(i, cols)
            x, y = start_x + col * (card_size + padding), start_y + row * (card_size + padding)
            rect = pygame.Rect(x, y, card_size, card_size)
            self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])
            unplaced_mowers_rects[original_index] = rect

        can_start = len(purchased_mowers) == len(placed_mowers)
        start_button_rect = pygame.Rect((0, 0), PLACEMENT_PANEL_START_BTN_SIZE)
        start_button_rect.center = (panel_rect.centerx, panel_rect.bottom + PLACEMENT_PANEL_START_BTN_TOP_OFFSET)

        color = GREEN if can_start else GREY
        text_color = BLACK if can_start else DARK_GREY
        self._draw_button(surface, "В Бой!", start_button_rect, color, text_color, self.font_large)

        return unplaced_mowers_rects, start_button_rect