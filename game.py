# game.py

import pygame
import sys
import random
import time
# <<<--- Импортируем наши модули ---
import settings # Файл с константами
import sprites  # Файл с классами спрайтов
from assets import load_image # Функция загрузки изображений

class Game:
    def __init__(self):
        """Инициализация игры, Pygame, экрана и всех переменных."""
        pygame.init()
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption("Растения против Зомби v0.8 (с поеданием)")
        self.clock = pygame.time.Clock()
        self.running = True

        # Загрузка шрифтов
        self.font = pygame.font.SysFont(None, 36)
        self.shop_font = pygame.font.SysFont(None, 24)
        self.intro_font = pygame.font.SysFont(None, 48)
        self.end_game_font = pygame.font.SysFont(None, 72)
        self.timeline_font = pygame.font.SysFont(None, 20)

        # Загрузка ассетов интерфейса
        self.sun_icon_img = load_image(settings.SUN_ICON_FILE, 30, settings.YELLOW)

        # Создаем группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.plants_group = pygame.sprite.Group() # Содержит ВСЕ растения (PeaShooter, Sunflower)
        self.peashooters = pygame.sprite.Group() # Только горохострелы (для удобства обновления)
        self.sunflowers = pygame.sprite.Group()  # Только подсолнухи (для удобства обновления)
        self.suns = pygame.sprite.Group()       # Собираемые солнышки
        self.zombies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.lawnmowers = pygame.sprite.Group()

        # Инициализация игровых переменных
        try:
            self.sun_points = settings.STARTING_SUN_POINTS
        except AttributeError:
            print("!!! Ошибка: Константа STARTING_SUN_POINTS не найдена в settings.py! Устанавливаю 150.")
            self.sun_points = 150
        self.game_state = "INTRO"
        self.selected_plant_type = None
        self.occupied_cells = set() # Хранит кортежи (row, col) занятых ячеек

        # Инициализация Магазина
        self.plant_shop_items = {
            "peashooter": {
                "cost": settings.PEASHOOTER_COST,
                "class": sprites.PeaShooter,
                "image": load_image(settings.PEASHOOTER_IMAGE_FILE, 40, settings.GREEN)
            },
            "sunflower": {
                "cost": settings.SUNFLOWER_COST,
                "class": sprites.Sunflower,
                "image": load_image(settings.SUNFLOWER_IMAGE_FILE, 40, settings.YELLOW)
            }
        }
        self.shop_item_rects = {} # Rect'ы кнопок магазина

        # Переменные для таймеров и состояний
        self.game_start_time = 0
        self.last_zombie_spawn_time = 0
        self.final_wave_triggered = False
        self.current_time_in_loop = 0
        self.dt = 0

        # Создаем начальные элементы (косилки)
        self._initialize_game_elements()

    def _initialize_game_elements(self):
        """Создает начальные элементы игры (газонокосилки)."""
        self.lawnmowers.empty()
        self.all_sprites.empty() # Очищаем и all_sprites перед добавлением косилок
        print("Создание газонокосилок...")
        for r in range(settings.GRID_ROWS):
            mower = sprites.Lawnmower(r)
            self.all_sprites.add(mower) # Косилки должны быть видимы
            self.lawnmowers.add(mower)

    def new_game(self):
        """Сбрасывает игру в начальное состояние."""
        print("--- Новая игра ---")
        # Очистка групп спрайтов
        self.all_sprites.empty()
        self.plants_group.empty()
        self.peashooters.empty()
        self.sunflowers.empty()
        self.suns.empty()
        self.zombies.empty()
        self.projectiles.empty()
        self.lawnmowers.empty() # Очищаем группу косилок
        self.occupied_cells.clear()
        self.shop_item_rects.clear()

        # Сброс переменных
        try:
            self.sun_points = settings.STARTING_SUN_POINTS
        except AttributeError:
            self.sun_points = 150
        self.selected_plant_type = None
        self.game_state = "INTRO"
        self.game_start_time = 0
        self.last_zombie_spawn_time = 0
        self.final_wave_triggered = False

        # Пересоздаем косилки
        self._initialize_game_elements()


    def run(self):
        """Основной цикл игры."""
        while self.running:
            self.dt = self.clock.tick(settings.FPS) / 1000.0
            self.current_time_in_loop = time.time()

            self._handle_events()
            self._update()
            self._draw()

        pygame.quit()
        sys.exit()

    # ===============================================
    # --- Метод Обработки Событий ---
    # ===============================================
    def _handle_events(self):
        """Обработка всех событий (ввод пользователя)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_r and (self.game_state == "GAME_OVER" or self.game_state == "VICTORY"):
                     self.new_game()

            # --- Обработка кликов Мыши ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                # --- 1. Интро ---
                if self.game_state == "INTRO":
                    self.game_state = "PLAYING"
                    self.game_start_time = self.current_time_in_loop
                    self.last_zombie_spawn_time = self.game_start_time
                    self.final_wave_triggered = False
                    print(f"Игра началась в {self.game_start_time:.2f}")

                # --- 2. Игра ---
                elif self.game_state == "PLAYING":
                    clicked_handled = False

                    # 2а. Клик по солнышку?
                    clicked_suns = [sun for sun in self.suns if sun.rect.collidepoint(mouse_pos)]
                    if clicked_suns:
                        for sun in clicked_suns:
                            self.sun_points += sun.value
                            sun.kill()
                        print(f"Собрано солнышко! Всего: {self.sun_points}")
                        clicked_handled = True

                    # 2б. Клик по Магазину?
                    if not clicked_handled and mouse_pos[1] < settings.SHOP_HEIGHT:
                        for name, rect in self.shop_item_rects.items():
                            if rect.collidepoint(mouse_pos):
                                 if self.sun_points >= self.plant_shop_items[name]['cost']:
                                     self.selected_plant_type = name
                                     print(f"Выбрано растение: {self.selected_plant_type}")
                                 else:
                                     print(f"Недостаточно солнышек для выбора {name}")
                                     self.selected_plant_type = None
                                 clicked_handled = True
                                 break

                    # 2в. Клик для посадки?
                    if not clicked_handled and self.selected_plant_type is not None and mouse_pos[1] > settings.SHOP_HEIGHT:
                        plant_data = self.plant_shop_items[self.selected_plant_type]
                        cost = plant_data["cost"]

                        grid_rect_area = pygame.Rect(settings.GRID_START_X, settings.GRID_START_Y,
                                                    settings.GRID_COLS * settings.CELL_WIDTH,
                                                    settings.GRID_ROWS * settings.CELL_HEIGHT)

                        if grid_rect_area.collidepoint(mouse_pos):
                            clicked_col = (mouse_pos[0] - settings.GRID_START_X) // settings.CELL_WIDTH
                            clicked_row = (mouse_pos[1] - settings.GRID_START_Y) // settings.CELL_HEIGHT

                            if 0 <= clicked_col < settings.GRID_COLS and 0 <= clicked_row < settings.GRID_ROWS:
                                 target_cell = (clicked_row, clicked_col)

                                 if self.sun_points >= cost:
                                     if target_cell not in self.occupied_cells:
                                         plant_center_x = settings.GRID_START_X + clicked_col * settings.CELL_WIDTH + settings.CELL_WIDTH // 2
                                         plant_center_y = settings.GRID_START_Y + clicked_row * settings.CELL_HEIGHT + settings.CELL_HEIGHT // 2
                                         try:
                                             PlantClass = plant_data["class"]
                                             new_plant = PlantClass(plant_center_x, plant_center_y)
                                             # <<<--- Сохраняем позицию сетки в растении ---
                                             new_plant.grid_pos = target_cell

                                             self.all_sprites.add(new_plant)
                                             self.plants_group.add(new_plant)
                                             if isinstance(new_plant, sprites.PeaShooter): self.peashooters.add(new_plant)
                                             elif isinstance(new_plant, sprites.Sunflower): self.sunflowers.add(new_plant)

                                             self.sun_points -= cost
                                             self.occupied_cells.add(target_cell)
                                             print(f"{self.selected_plant_type} посажен в {target_cell}! Солн: {self.sun_points}")
                                             # self.selected_plant_type = None # Раскомментировать, если нужно сбрасывать выбор

                                         except Exception as e: print(f"ОШИБКА посадки: {e}")
                                     else:
                                         print(f"Ячейка {target_cell} занята!")
                                         self.selected_plant_type = None
                                 else:
                                     print(f"Недостаточно солнышек ({cost})!")
                                     self.selected_plant_type = None
                            else:
                                print("Клик в сетке, но вне допустимых ячеек?")
                                self.selected_plant_type = None
                        else:
                            print("Клик вне сетки, выбор сброшен.")
                            self.selected_plant_type = None

                # --- 3. Конец Игры ---
                elif self.game_state == "GAME_OVER" or self.game_state == "VICTORY":
                     self.new_game() # Перезапуск по клику

    # ===============================================
    # --- Метод Обновления (С ИЗМЕНЕНИЯМИ) ---
    # ===============================================
    def _update(self):
        """Обновление состояния всех игровых объектов."""
        if self.game_state != "PLAYING":
            return
        now = self.current_time_in_loop
        elapsed_time = now - self.game_start_time

        # --- Проверка победы по времени ---
        if elapsed_time >= settings.GAME_DURATION:
            self.game_state = "VICTORY"
            print("---------------- VICTORY ----------------")
            return

        # --- Запоминаем, какие ячейки были заняты ДО обновления ---
        occupied_before_update = self.occupied_cells.copy()

        # --- Обновление всех спрайтов ---
        # 1. Подсолнухи производят Солнышки
        for sunflower in self.sunflowers:
            new_sun = sunflower.update()
            if new_sun:
                self.all_sprites.add(new_sun)
                self.suns.add(new_sun)
        # 2. Солнышки исчезают
        self.suns.update()
        # 3. Горохострелы стреляют
        for shooter in self.peashooters:
             zombies_on_row = [z for z in self.zombies if z.row == shooter.row]
             zombies_ahead = [z for z in zombies_on_row if z.rect.left > shooter.rect.right]
             new_projectile = shooter.update(zombies_ahead)
             if new_projectile:
                 self.all_sprites.add(new_projectile)
                 self.projectiles.add(new_projectile)
        # 4. Снаряды летят
        self.projectiles.update()
        # 5. Зомби идут ИЛИ едят <<<--- Передаем группу ВСЕХ растений! ---
        self.zombies.update(self.plants_group)
        # 6. Газонокосилки едут (если активны) и убивают зомби
        self.lawnmowers.update(self.zombies) # Передаем группу зомби

        # --- Освобождение ячеек съеденных/убитых растений ---
        # Собираем ячейки ВСЕХ живых растений ПОСЛЕ обновления
        currently_occupied = set()
        for plant in self.plants_group: # Проверяем группу всех живых растений
            if plant.grid_pos:
                currently_occupied.add(plant.grid_pos)

        # Находим ячейки, которые были заняты, но теперь свободны
        # freed_cells = occupied_before_update - currently_occupied
        # if freed_cells:
        #     print(f"Освобождены ячейки: {freed_cells}") # Отладка
        self.occupied_cells = currently_occupied # Обновляем основной сет занятых ячеек


        # --- Спавн зомби ---
        current_spawn_rate = settings.ZOMBIE_SPAWN_RATE
        if not self.final_wave_triggered and elapsed_time >= settings.FINAL_WAVE_START_TIME:
             print("!!! НАЧАЛАСЬ ФИНАЛЬНАЯ ВОЛНА !!!")
             self.final_wave_triggered = True
        if self.final_wave_triggered:
            current_spawn_rate = settings.FINAL_WAVE_SPAWN_RATE

        if now - self.last_zombie_spawn_time >= current_spawn_rate:
            try:
                chosen_type = random.choice(list(settings.ZOMBIE_TYPES.keys()))
                spawn_row = random.randint(0, settings.GRID_ROWS - 1)
                zombie_y_pos = settings.GRID_START_Y + spawn_row * settings.CELL_HEIGHT + settings.CELL_HEIGHT // 2
                new_zombie = sprites.Zombie(zombie_y_pos, chosen_type)
                self.all_sprites.add(new_zombie)
                self.zombies.add(new_zombie)
                self.last_zombie_spawn_time = now
            except Exception as e: print(f"ОШИБКА при спавне зомби: {e}")

        # --- Проверка столкновений снарядов с зомби ---
        try:
            collisions = pygame.sprite.groupcollide(self.projectiles, self.zombies, True, False)
            for proj, hit_zombies in collisions.items():
                for z in hit_zombies:
                    z.take_damage(settings.PROJECTILE_DAMAGE)
        except Exception as e: print(f"ОШИБКА при проверке столкновений снарядов: {e}")

        # --- Проверка на проигрыш ---
        try:
            zombies_at_end = [z for z in self.zombies if z.rect.left < settings.GRID_START_X]
            if zombies_at_end:
                for zombie in zombies_at_end:
                    zombie_row = zombie.row
                    mower_activated = False
                    for mower in self.lawnmowers:
                        if mower.row == zombie_row and mower.state == "IDLE":
                            mower.activate()
                            zombie.kill()
                            mower_activated = True
                            break
                    if not mower_activated:
                        self.game_state = "GAME_OVER"
                        print(f"---------------- GAME OVER (Зомби на ряду {zombie_row} прорвался!) ----------------")
                        break
                if self.game_state == "GAME_OVER": return
        except Exception as e: print(f"ОШИБКА при проверке проигрыша: {e}")


    # ===============================================
    # --- Методы Отрисовки ---
    # ===============================================
    # Методы _draw_grid, _draw_shop, _draw_intro, _draw_timeline, _draw_end_screen
    # остаются такими же, как в предыдущем шаге (Шаг 8)
    # ... (вставь сюда код методов _draw_grid, _draw_shop, _draw_intro, _draw_timeline, _draw_end_screen) ...

    # КОПИЯ МЕТОДОВ ОТРИСОВКИ ИЗ ПРЕДЫДУЩЕГО ОТВЕТА:
    def _draw_grid(self):
        for row in range(settings.GRID_ROWS):
            for col in range(settings.GRID_COLS):
                cell_rect = pygame.Rect(settings.GRID_START_X + col * settings.CELL_WIDTH,
                                        settings.GRID_START_Y + row * settings.CELL_HEIGHT,
                                        settings.CELL_WIDTH, settings.CELL_HEIGHT)
                pygame.draw.rect(self.screen, settings.GRID_BG_COLOR, cell_rect)
                pygame.draw.rect(self.screen, settings.GRID_LINE_COLOR, cell_rect, 1)

    def _draw_shop(self):
        shop_rect = pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SHOP_HEIGHT)
        pygame.draw.rect(self.screen, settings.LIGHT_BLUE, shop_rect)
        pygame.draw.line(self.screen, settings.BLACK, (0, settings.SHOP_HEIGHT - 1), (settings.SCREEN_WIDTH, settings.SHOP_HEIGHT - 1), 2)
        sun_text = f"{self.sun_points}"
        sun_surf = self.font.render(sun_text, True, settings.BLACK)
        icon_width = self.sun_icon_img.get_width() if self.sun_icon_img else 0
        sun_rect = sun_surf.get_rect(topleft=(15 + icon_width + 5, 15))
        if self.sun_icon_img: self.screen.blit(self.sun_icon_img, (10, 10))
        self.screen.blit(sun_surf, sun_rect)
        start_x = sun_rect.right + 30
        item_y = 10
        padding = 15
        self.shop_item_rects.clear()
        for name, item in self.plant_shop_items.items():
            can_afford = self.sun_points >= item['cost']
            base_color = settings.WHITE if can_afford else settings.GREY
            border_color = settings.BLACK
            text_color = settings.BLACK if can_afford else settings.DARK_GREY
            if self.selected_plant_type == name: border_color = settings.ORANGE
            item_image = item.get("image")
            if not item_image: continue
            item_width = item_image.get_width() + 60
            item_rect = pygame.Rect(start_x, item_y, item_width, settings.SHOP_HEIGHT - 20)
            pygame.draw.rect(self.screen, base_color, item_rect)
            pygame.draw.rect(self.screen, border_color, item_rect, 3)
            icon_rect = item_image.get_rect(center=(item_rect.left + 30, item_rect.centery))
            self.screen.blit(item_image, icon_rect)
            cost_surf = self.shop_font.render(str(item["cost"]), True, text_color)
            cost_rect = cost_surf.get_rect(center=(item_rect.right - 25, item_rect.centery))
            self.screen.blit(cost_surf, cost_rect)
            self.shop_item_rects[name] = item_rect
            start_x += item_width + padding

    def _draw_intro(self):
        self.screen.fill(settings.GREY)
        title_surf = self.intro_font.render("Зомби наступают!", True, settings.RED)
        title_rect = title_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4))
        self.screen.blit(title_surf, title_rect)
        zombie_y = settings.SCREEN_HEIGHT // 2
        start_x = settings.SCREEN_WIDTH // 4
        num_types = len(settings.ZOMBIE_TYPES)
        spacing = settings.SCREEN_WIDTH // 2 // (num_types + 1) if num_types > 0 else settings.SCREEN_WIDTH // 2
        current_x = start_x
        for z_type, z_info in settings.ZOMBIE_TYPES.items():
             img_name = z_info.get("image")
             z_img = load_image(img_name, (settings.ZOMBIE_SIZE * 1.5, settings.ZOMBIE_SIZE * 1.5), z_info["color"])
             z_rect = z_img.get_rect(center=(current_x, zombie_y))
             self.screen.blit(z_img, z_rect)
             label_surf = self.font.render(z_type.capitalize(), True, settings.WHITE)
             label_rect = label_surf.get_rect(center=(current_x, zombie_y + settings.ZOMBIE_SIZE + 10))
             self.screen.blit(label_surf, label_rect)
             current_x += spacing + settings.ZOMBIE_SIZE
        start_surf = self.font.render("Кликните, чтобы начать игру", True, settings.WHITE)
        start_rect = start_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT * 3 // 4))
        self.screen.blit(start_surf, start_rect)

    def _draw_timeline(self):
        bar_width = 150; bar_height = 20; margin = 10
        bar_x = settings.SCREEN_WIDTH - bar_width - margin
        bar_y = settings.SCREEN_HEIGHT - bar_height - margin
        elapsed_time = self.current_time_in_loop - self.game_start_time if self.game_start_time > 0 else 0
        progress = min(elapsed_time / settings.GAME_DURATION, 1.0) if settings.GAME_DURATION > 0 else 0
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, settings.DARK_GREY, bg_rect)
        progress_width = int(bar_width * progress)
        progress_rect = pygame.Rect(bar_x, bar_y, progress_width, bar_height)
        pygame.draw.rect(self.screen, settings.ORANGE, progress_rect)
        pygame.draw.rect(self.screen, settings.BLACK, bg_rect, 2)
        if not self.final_wave_triggered and settings.GAME_DURATION > 0:
            wave_marker_time_ratio = settings.FINAL_WAVE_START_TIME / settings.GAME_DURATION
            wave_marker_x = bar_x + int(bar_width * wave_marker_time_ratio)
            pygame.draw.line(self.screen, settings.RED, (wave_marker_x, bar_y), (wave_marker_x, bar_y + bar_height), 2)
        remaining_time = max(0, int(settings.GAME_DURATION - elapsed_time))
        time_text = f"{remaining_time}s"
        time_surf = self.timeline_font.render(time_text, True, settings.WHITE)
        time_rect = time_surf.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        self.screen.blit(time_surf, time_rect)

    def _draw_end_screen(self, message, color):
        self.screen.fill(settings.BLACK)
        text_surf = self.end_game_font.render(message, True, color)
        text_rect = text_surf.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2))
        self.screen.blit(text_surf, text_rect)
        restart_surf = self.font.render("Кликните или нажмите R, чтобы сыграть снова", True, settings.WHITE)
        restart_rect = restart_surf.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT * 3 / 4))
        self.screen.blit(restart_surf, restart_rect)

    # --- Основной Метод Отрисовки ---
    def _draw(self):
        """Отрисовка всего на экране в зависимости от состояния игры."""
        if self.game_state == "INTRO":
            self._draw_intro()
        elif self.game_state == "PLAYING":
            self.screen.fill(settings.GREY)
            self._draw_grid()
            self.all_sprites.draw(self.screen)
            self._draw_timeline()
            self._draw_shop()
        elif self.game_state == "VICTORY":
            self._draw_end_screen("ПОБЕДА!", settings.GREEN)
        elif self.game_state == "GAME_OVER":
            self._draw_end_screen("ИГРА ОКОНЧЕНА", settings.RED)

        pygame.display.flip()

# --- Конец Класса Game ---