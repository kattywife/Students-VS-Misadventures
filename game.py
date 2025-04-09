# game.py

import pygame
import sys
import random
import time
# <<<--- Импортируем наши модули ---
import settings # Файл с константами
import sprites  # Файл с классами спрайтов
import levels   # Файл с данными уровней
from assets import load_image # Функция загрузки изображений

class Game:
    def __init__(self):
        """Инициализация игры, Pygame, экрана и всех переменных."""
        pygame.init()
        pygame.font.init() # Инициализация модуля шрифтов

        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption("Студенты Против Злоключений v1.0")
        self.clock = pygame.time.Clock()
        self.running = True

        # Загрузка шрифтов
        self.font = pygame.font.SysFont(None, 36)
        self.shop_font = pygame.font.SysFont(None, 24)
        self.end_game_font = pygame.font.SysFont(None, 72)
        self.menu_title_font = pygame.font.SysFont(None, settings.MENU_TITLE_FONT_SIZE)
        self.menu_button_font = pygame.font.SysFont(None, settings.MENU_BUTTON_FONT_SIZE)
        self.progress_font = pygame.font.SysFont(None, 20) # Шрифт для прогресс-бара

        # Загрузка ассетов интерфейса
        self.sun_icon_img = load_image(settings.SUN_ICON_FILE, 30, settings.YELLOW)

        # Создаем группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.plants_group = pygame.sprite.Group()
        self.peashooters = pygame.sprite.Group()
        self.sunflowers = pygame.sprite.Group()
        self.suns = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.lawnmowers = pygame.sprite.Group()

        # Начальное состояние
        self.game_state = "MAIN_MENU"

        # Инициализация игровых переменных
        self.sun_points = 0
        self.selected_plant_type = None
        self.occupied_cells = set()
        self.shop_item_rects = {}
        self.level_buttons = {}

        # Переменные для текущего уровня
        self.current_level_id = 0
        self.current_level_data = None
        self.game_start_time = 0
        self.last_zombie_spawn_time = 0
        self.zombies_defeated_count = 0
        self.target_zombies = 0
        self.mid_wave_triggered = False # Флаг для средней волны

        # Переменные для цикла
        self.current_time_in_loop = 0
        self.dt = 0

        # Инициализация данных магазина
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
        # Косилки создаются в start_level()

    def start_level(self, level_id):
        """Начинает или перезапускает указанный уровень."""
        print(f"--- Внутри start_level({level_id}) ---") # ОТЛАДКА

        if level_id <= 0 or level_id >= len(levels.LEVEL_DATA) or levels.LEVEL_DATA[level_id] is None:
             print(f"Ошибка: Неверный ID уровня {level_id} или данные отсутствуют.")
             self.go_to_main_menu(); return

        self.current_level_id = level_id
        self.current_level_data = levels.LEVEL_DATA[level_id]
        print(f"  Загружены данные: {self.current_level_data}") # ОТЛАДКА
        if not self.current_level_data:
            print("!!! Ошибка: current_level_data пустые!"); self.go_to_main_menu(); return

        # Очистка групп
        self.all_sprites.empty(); self.plants_group.empty(); self.peashooters.empty()
        self.sunflowers.empty(); self.suns.empty(); self.zombies.empty()
        self.projectiles.empty(); self.lawnmowers.empty(); self.occupied_cells.clear()
        self.shop_item_rects.clear()

        # Сброс переменных уровня
        self.sun_points = self.current_level_data.get("starting_sun", 150)
        self.selected_plant_type = None
        self.game_start_time = self.current_time_in_loop # Устанавливаем время начала
        self.last_zombie_spawn_time = self.game_start_time
        self.zombies_defeated_count = 0
        self.target_zombies = self.current_level_data.get("zombies_to_defeat", 10)
        self.mid_wave_triggered = False # Сбрасываем флаг волны
        print(f"  Цель уровня: победить {self.target_zombies} зомби.") # ОТЛАДКА

        # Создаем косилки
        print("  Создание газонокосилок для уровня...") # ОТЛАДКА
        for r in range(settings.GRID_ROWS):
            try:
                mower = sprites.Lawnmower(r); self.all_sprites.add(mower); self.lawnmowers.add(mower)
            except Exception as e: print(f"!!! ОШИБКА создания косилки {r}: {e}")
        print(f"  Косилки созданы: {len(self.lawnmowers)}") # ОТЛАДКА

        self.game_state = "PLAYING"
        print(f"--- Уровень {level_id} успешно запущен. Состояние: {self.game_state} ---") # ОТЛАДКА

    def go_to_main_menu(self):
        """Возвращает игру в главное меню."""
        print("Возврат в главное меню...")
        self.current_level_id = 0; self.current_level_data = None; self.selected_plant_type = None;
        self.all_sprites.empty(); self.plants_group.empty(); self.peashooters.empty();
        self.sunflowers.empty(); self.suns.empty(); self.zombies.empty();
        self.projectiles.empty(); self.lawnmowers.empty(); self.occupied_cells.clear();
        self.game_state = "MAIN_MENU"

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
    # --- Метод Обработки Событий (С ОТЛАДКОЙ) ---
    # ===============================================
    def _handle_events(self):
        """Обработка всех событий (ввод пользователя)."""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "PLAYING": self.go_to_main_menu()
                    else: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_state == "MAIN_MENU":
                    for level_id, rect in self.level_buttons.items():
                        if rect.collidepoint(mouse_pos):
                            print(f"Нажата кнопка уровня {level_id}. Вызов start_level...") # ОТЛАДКА
                            try: self.start_level(level_id)
                            except Exception as e: print(f"!!! КРИТ. ОШИБКА start_level({level_id}): {e}"); import traceback; traceback.print_exc(); pygame.quit(); sys.exit();
                            break # Выходим из цикла for, если кнопка нажата
                elif self.game_state == "PLAYING":
                    clicked_handled = False; clicked_suns = [sun for sun in self.suns if sun.rect.collidepoint(mouse_pos)];
                    if clicked_suns:
                        for sun in clicked_suns: self.sun_points += sun.value; sun.kill();
                        print(f"Собрано! ЗЕ: {self.sun_points}"); clicked_handled = True;
                    if not clicked_handled and mouse_pos[1] < settings.SHOP_HEIGHT:
                        for name, rect in self.shop_item_rects.items():
                            if rect.collidepoint(mouse_pos):
                                 if self.sun_points >= self.plant_shop_items[name]['cost']: self.selected_plant_type = name; print(f"Выбрано: {name}")
                                 else: print(f"Мало ЗЕ для {name}"); self.selected_plant_type = None;
                                 clicked_handled = True; break;
                    if not clicked_handled and self.selected_plant_type is not None and mouse_pos[1] > settings.SHOP_HEIGHT:
                        plant_data = self.plant_shop_items[self.selected_plant_type]; cost = plant_data["cost"]; grid_rect_area = pygame.Rect(settings.GRID_START_X, settings.GRID_START_Y, settings.GRID_COLS * settings.CELL_WIDTH, settings.GRID_ROWS * settings.CELL_HEIGHT);
                        if grid_rect_area.collidepoint(mouse_pos):
                            clicked_col = (mouse_pos[0] - settings.GRID_START_X) // settings.CELL_WIDTH; clicked_row = (mouse_pos[1] - settings.GRID_START_Y) // settings.CELL_HEIGHT;
                            if 0 <= clicked_col < settings.GRID_COLS and 0 <= clicked_row < settings.GRID_ROWS:
                                 target_cell = (clicked_row, clicked_col);
                                 if self.sun_points >= cost:
                                     if target_cell not in self.occupied_cells:
                                         plant_center_x = settings.GRID_START_X + clicked_col * settings.CELL_WIDTH + settings.CELL_WIDTH // 2; plant_center_y = settings.GRID_START_Y + clicked_row * settings.CELL_HEIGHT + settings.CELL_HEIGHT // 2;
                                         try:
                                             PlantClass = plant_data["class"]; new_plant = PlantClass(plant_center_x, plant_center_y); new_plant.grid_pos = target_cell; self.all_sprites.add(new_plant); self.plants_group.add(new_plant);
                                             if isinstance(new_plant, sprites.PeaShooter): self.peashooters.add(new_plant);
                                             elif isinstance(new_plant, sprites.Sunflower): self.sunflowers.add(new_plant);
                                             self.sun_points -= cost; self.occupied_cells.add(target_cell); print(f"{self.selected_plant_type} в {target_cell}! ЗЕ: {self.sun_points}");
                                         except Exception as e: print(f"ОШИБКА посадки: {e}");
                                     else: print(f"Ячейка {target_cell} занята!"); self.selected_plant_type = None;
                                 else: print(f"Мало ЗЕ ({cost})!"); self.selected_plant_type = None;
                            else: print("Клик в сетке, но мимо?"); self.selected_plant_type = None;
                        else: print("Клик вне сетки"); self.selected_plant_type = None;
                elif self.game_state == "GAME_OVER" or self.game_state == "LEVEL_COMPLETE":
                     self.go_to_main_menu() # Клик возвращает в меню

    # ===============================================
    # --- Метод Обновления (С ИСПРАВЛЕННОЙ ЛОГИКОЙ ВОЛНЫ) ---
    # ===============================================
        # game.py -> class Game

        # ===============================================
        # --- Метод Обновления (С ДОПОЛНИТЕЛЬНОЙ ОТЛАДКОЙ) ---
        # ===============================================
        # game.py -> class Game

        # ===============================================
        # --- Метод Обновления (С ИСПРАВЛЕННЫМ ПОДСЧЕТОМ УБИЙСТВ КОСИЛКОЙ) ---
        # ===============================================
    def _update(self):
        """Обновление состояния игровых объектов."""
        # Обновляем только если игра идет
        if self.game_state != "PLAYING":
            return

        # Раскомментируй для проверки, что _update вызывается
        # print(f"--- Внутри _update (PLAYING). Уровень: {self.current_level_id} ---")

        # Проверяем наличие данных уровня
        if not self.current_level_data:
            print("!!! Ошибка в _update: Нет данных текущего уровня!")
            self.go_to_main_menu();
            return

        # Получаем текущее время (установлено в self.run)
        now = self.current_time_in_loop

        # --- Запоминаем занятые ячейки ДО обновления (для освобождения) ---
        occupied_before_update = self.occupied_cells.copy()

        # --- Обновление Спрайтов ---
        # Порядок важен: сначала генерируем ресурсы/снаряды, потом двигаем/атакуем

        # 1. Подсолнухи -> создают Солнышки
        for sunflower in self.sunflowers:
            new_sun = sunflower.update()
            if new_sun:
                self.all_sprites.add(new_sun)
                self.suns.add(new_sun)

        # 2. Солнышки -> исчезают по таймеру
        self.suns.update()

        # 3. Горохострелы -> создают Снаряды, если есть цель
        for shooter in self.peashooters:
            zombies_on_row = [z for z in self.zombies if z.row == shooter.row]
            zombies_ahead = [z for z in zombies_on_row if z.rect.left > shooter.rect.right]
            new_projectile = shooter.update(zombies_ahead)
            if new_projectile:
                self.all_sprites.add(new_projectile)
                self.projectiles.add(new_projectile)

        # 4. Снаряды -> летят
        self.projectiles.update()

        # 5. Зомби -> идут или едят (передаем группу растений для проверки)
        self.zombies.update(self.plants_group)

        # 6. Газонокосилки -> едут И УБИВАЮТ (обрабатываем результат с ОТЛАДКОЙ)
        mower_kills_this_frame = 0
        # <<<--- PRINT D ---
        # print(f"GAME: Обновление косилок. Всего в группе: {len(self.lawnmowers)}")
        for mower in self.lawnmowers:
            # <<<--- PRINT E ---
            # print(f"GAME: Вызов update для косилки на ряду {mower.row}")
            killed_by_mower = mower.update(self.zombies)  # Передаем группу зомби
            # <<<--- PRINT F ---
            if killed_by_mower > 0:
                # Если косилка убила кого-то, выводим сообщение
                print(f"GAME: Косилка {mower.row} вернула killed_by_mower = {killed_by_mower}")
            # Суммируем убийства всех косилок за этот кадр
            mower_kills_this_frame += killed_by_mower

        # Если косилки убили кого-то в этом кадре, обновляем общий счетчик
        if mower_kills_this_frame > 0:
            # <<<--- PRINT G ---
            print(f"GAME: Всего убито косилками за кадр: {mower_kills_this_frame}. Обновляем счетчик...")
            self.zombies_defeated_count += mower_kills_this_frame
            # <<<--- PRINT H ---
            print(f"GAME: Новый общий счетчик убитых: {self.zombies_defeated_count}/{self.target_zombies}")
        # else:
        # print("GAME: Косилки никого не убили в этом кадре.") # Отладка

        # --- Освобождение Ячеек ---
        currently_occupied = {plant.grid_pos for plant in self.plants_group if plant.grid_pos}
        self.occupied_cells = currently_occupied

        # --- Спавн Зомби (с учетом средней волны) ---
        base_spawn_rate = self.current_level_data.get("spawn_rate", 5.0)
        allowed_zombie_types = self.current_level_data.get("allowed_zombies", ["regular"])
        target_zombies_for_wave = int(self.target_zombies * settings.MID_WAVE_THRESHOLD_RATIO)
        current_spawn_rate = base_spawn_rate
        if not self.mid_wave_triggered and self.zombies_defeated_count >= target_zombies_for_wave:
            print(f"!!! НАЧАЛАСЬ СРЕДНЯЯ ВОЛНА (достигнуто {self.zombies_defeated_count}/{self.target_zombies}) !!!")
            self.mid_wave_triggered = True
        if self.mid_wave_triggered:
            try:
                current_spawn_rate = settings.MID_WAVE_SPAWN_RATE
            except AttributeError:
                print("Предупреждение: MID_WAVE_SPAWN_RATE не найдена.")

        if self.target_zombies > 0 and self.zombies_defeated_count < self.target_zombies:
            if now - self.last_zombie_spawn_time >= current_spawn_rate:
                if allowed_zombie_types:
                    try:
                        chosen_type = random.choice(allowed_zombie_types)
                        spawn_row = random.randint(0, settings.GRID_ROWS - 1)
                        zombie_y_pos = settings.GRID_START_Y + spawn_row * settings.CELL_HEIGHT + settings.CELL_HEIGHT // 2
                        new_zombie = sprites.Zombie(zombie_y_pos, chosen_type)
                        self.all_sprites.add(new_zombie);
                        self.zombies.add(new_zombie)
                        self.last_zombie_spawn_time = now
                    except Exception as e:
                        print(f"ОШИБКА спавна: {e}")

        # --- Проверка столкновений снарядов с зомби (С подсчетом убитых и отладкой) ---
        try:
            collisions = pygame.sprite.groupcollide(self.projectiles, self.zombies, True, False)
            if collisions:
                # print(f"Обнаружены столкновения: {collisions}") # Отладка
                for proj, hit_zombies_list in collisions.items():
                    for z in hit_zombies_list:
                        print(f"  Проверка объекта z: тип={type(z)}")  # Отладка типа
                        if not hasattr(z, 'take_damage'):
                            print(f"  !!! У объекта z НЕТ метода take_damage!")
                            continue
                        was_killed = z.take_damage(settings.PROJECTILE_DAMAGE)
                        if was_killed:
                            self.zombies_defeated_count += 1
                            print(
                                f"  !!! Зомби УБИТ снарядом! Новый счет: {self.zombies_defeated_count}/{self.target_zombies}")

        except Exception as e:
            print(f"ОШИБКА столкн. снарядов: {e}")
            import traceback
            traceback.print_exc()

        # --- Проверка на проигрыш (зомби дошел до дома) ---
        try:
            # Собираем зомби, чей левый край зашел за левую границу сетки
            zombies_at_end = [z for z in self.zombies if z.rect.left < settings.GRID_START_X]

            if zombies_at_end:  # Если такие зомби есть
                # Проверяем КАЖДОГО дошедшего зомби
                for zombie in zombies_at_end:
                    zombie_row = zombie.row  # Определяем ряд зомби
                    mower_found_on_row = False
                    mower_was_activated = False  # Флаг, что косилка БЫЛА активирована в этой итерации

                    # Ищем косилку на этом ряду
                    for mower in self.lawnmowers:
                        if mower.row == zombie_row:
                            mower_found_on_row = True  # Косилка (любая) на этом ряду есть
                            # Если она еще не активна (IDLE), активируем ее
                            if mower.state == "IDLE":
                                mower.activate()
                                mower_was_activated = True  # Отмечаем, что активировали сейчас
                                # <<<--- НЕ УБИВАЕМ ЗОМБИ ЗДЕСЬ ---
                                # zombie.kill() # Убрали kill() отсюда
                                print(f"  Косилка {zombie_row} активирована зомби.")  # Отладка
                            # Если косилка уже активна, просто игнорируем (она сама разберется)
                            break  # Нашли косилку на этом ряду, дальше не ищем

                    # Если мы прошли всех косилок И НЕ нашли косилку на этом ряду ВООБЩЕ,
                    # ИЛИ нашли, но она была уже ACTIVE (т.е. mower_was_activated остался False),
                    # то это проигрыш.
                    # Мы не можем просто проверить !mower_found_on_row, т.к. косилка может быть уже ACTIVE
                    if not mower_was_activated and not mower_found_on_row:
                        # Если косилки на ряду нет СОВСЕМ, тогда точно проигрыш
                        self.game_state = "GAME_OVER"
                        print(
                            f"--- GAME OVER (Ур. {self.current_level_id}, Зомби {zombie_row} прорвался! Косилки нет.) ---")
                        break  # Выходим из цикла проверки зомби

                    # --- Дополнительная проверка на случай, если косилка уже уехала ---
                    # Если косилка НА РЯДУ ЕСТЬ (mower_found_on_row == True),
                    # но она НЕ БЫЛА активирована СЕЙЧАС (mower_was_activated == False),
                    # это значит, что косилка уже ACTIVE и едет.
                    # Зомби все еще жив, но косилка его должна будет сбить в mower.update().
                    # Однако, если зомби УСПЕЛ пройти МИМО УЖЕ ЕДУЩЕЙ косилки
                    # (например, если скорость зомби >> скорости косилки), то это тоже проигрыш.
                    # Эта проверка более сложная и для текущей игры, возможно, избыточна,
                    # т.к. косилка активируется, когда зомби еще слева от нее.
                    # Но для полноты картины:
                    # if mower_found_on_row and not mower_was_activated:
                    # (Здесь можно добавить проверку, не прошел ли зомби мимо активной косилки)
                    # pass

                # Если состояние изменилось на GAME_OVER, выходим из _update
                if self.game_state == "GAME_OVER":
                    return
        except Exception as e:
            print(f"ОШИБКА проверки проигрыша: {e}")
            import traceback
            traceback.print_exc()  # Выводим полный traceback

        # --- Проверка на победу (по количеству убитых зомби) ---
        if self.target_zombies > 0 and self.zombies_defeated_count >= self.target_zombies:
            self.game_state = "LEVEL_COMPLETE"
            print(
                f"---------------- УРОВЕНЬ {self.current_level_id} ПРОЙДЕН! (Побеждено {self.zombies_defeated_count}) ----------------")


    # ===============================================
    # --- Методы Отрисовки (С ИСПРАВЛЕНИЯМИ) ---
    # ===============================================
    def _draw_grid(self):
        for row in range(settings.GRID_ROWS):
            for col in range(settings.GRID_COLS):
                cell_rect = pygame.Rect(settings.GRID_START_X + col * settings.CELL_WIDTH, settings.GRID_START_Y + row * settings.CELL_HEIGHT, settings.CELL_WIDTH, settings.CELL_HEIGHT)
                pygame.draw.rect(self.screen, settings.GRID_BG_COLOR, cell_rect); pygame.draw.rect(self.screen, settings.GRID_LINE_COLOR, cell_rect, 1)

    def _draw_shop(self):
        """Рисует панель магазина. (ИСПРАВЛЕН ЦИКЛ)"""
        shop_rect = pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SHOP_HEIGHT); pygame.draw.rect(self.screen, settings.LIGHT_BLUE, shop_rect); pygame.draw.line(self.screen, settings.BLACK, (0, settings.SHOP_HEIGHT - 1), (settings.SCREEN_WIDTH, settings.SHOP_HEIGHT - 1), 2); sun_text = f"{self.sun_points}"; sun_surf = self.font.render(sun_text, True, settings.BLACK); icon_width = self.sun_icon_img.get_width() if self.sun_icon_img else 0; sun_rect = sun_surf.get_rect(topleft=(15 + icon_width + 5, 15));
        if self.sun_icon_img: self.screen.blit(self.sun_icon_img, (10, 10)); self.screen.blit(sun_surf, sun_rect);

        # --- Начало ИСПРАВЛЕННОГО Цикла ---
        start_x = sun_rect.right + 30; item_y = 10; padding = 15; self.shop_item_rects.clear();
        for name, item in self.plant_shop_items.items():
            can_afford = self.sun_points >= item['cost']; base_color = settings.WHITE if can_afford else settings.GREY; border_color = settings.BLACK; text_color = settings.BLACK if can_afford else settings.DARK_GREY;
            if self.selected_plant_type == name: border_color = settings.ORANGE;
            item_image = item.get("image");
            if not item_image: print(f"Предупреждение: Нет изображения для '{name}' в _draw_shop"); continue; # <<<--- Пропуск итерации
            # --- Код ниже выполняется ТОЛЬКО если item_image существует ---
            item_width = item_image.get_width() + 60; item_rect = pygame.Rect(start_x, item_y, item_width, settings.SHOP_HEIGHT - 20);
            pygame.draw.rect(self.screen, base_color, item_rect, border_radius=5); pygame.draw.rect(self.screen, border_color, item_rect, 3, border_radius=5);
            icon_rect = item_image.get_rect(center=(item_rect.left + 30, item_rect.centery)); self.screen.blit(item_image, icon_rect);
            cost_surf = self.shop_font.render(str(item["cost"]), True, text_color); cost_rect = cost_surf.get_rect(center=(item_rect.right - 25, item_rect.centery)); self.screen.blit(cost_surf, cost_rect);
            self.shop_item_rects[name] = item_rect; start_x += item_width + padding;
        # --- Конец ИСПРАВЛЕННОГО Цикла ---

    def _draw_main_menu(self):
        """Рисует главный экран выбора уровня. (ИСПРАВЛЕН ЦИКЛ)"""
        self.screen.fill(settings.DARK_GREEN); title_surf = self.menu_title_font.render("Студенты Против Злоключений", True, settings.WHITE); title_rect = title_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4)); self.screen.blit(title_surf, title_rect);
        self.level_buttons.clear(); button_x = settings.SCREEN_WIDTH // 2 - settings.MENU_BUTTON_WIDTH // 2; button_start_y = title_rect.bottom + 50; button_spacing = settings.MENU_BUTTON_HEIGHT + 15; mouse_pos = pygame.mouse.get_pos();

        # --- Начало ИСПРАВЛЕННОГО Цикла ---
        for i, level_info in enumerate(levels.LEVEL_DATA):
            if i == 0 or level_info is None: continue; # Пропускаем индекс 0
            button_y = button_start_y + (i - 1) * button_spacing;
            button_rect = pygame.Rect(button_x, button_y, settings.MENU_BUTTON_WIDTH, settings.MENU_BUTTON_HEIGHT);
            # Определяем цвет кнопки
            if button_rect.collidepoint(mouse_pos): button_color = settings.MENU_BUTTON_HOVER_COLOR;
            else: button_color = settings.MENU_BUTTON_COLOR;
            # Рисуем кнопку
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5);
            pygame.draw.rect(self.screen, settings.WHITE, button_rect, 2, border_radius=5);
            # Рисуем текст
            level_name = level_info.get("name", f"Уровень {i}");
            text_surf = self.menu_button_font.render(level_name, True, settings.MENU_BUTTON_TEXT_COLOR);
            text_rect = text_surf.get_rect(center=button_rect.center);
            self.screen.blit(text_surf, text_rect);
            # Сохраняем rect
            self.level_buttons[i] = button_rect;
        # --- Конец ИСПРАВЛЕННОГО Цикла ---

    def _draw_progress_bar(self): # Добавлен этот метод
        if self.game_state != "PLAYING" or self.target_zombies <= 0: return
        bar_width = settings.PROGRESS_BAR_WIDTH; bar_height = settings.PROGRESS_BAR_HEIGHT; margin = 10; bar_x = settings.SCREEN_WIDTH - bar_width - margin; bar_y = settings.SCREEN_HEIGHT - bar_height - margin;
        progress = min(self.zombies_defeated_count / self.target_zombies, 1.0);
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height); pygame.draw.rect(self.screen, settings.DARK_GREY, bg_rect);
        progress_width = int(bar_width * progress); progress_rect = pygame.Rect(bar_x, bar_y, progress_width, bar_height); pygame.draw.rect(self.screen, settings.ORANGE, progress_rect);
        pygame.draw.rect(self.screen, settings.BLACK, bg_rect, 2);
        if not self.mid_wave_triggered:
             wave_marker_ratio = settings.MID_WAVE_THRESHOLD_RATIO; wave_marker_x = bar_x + int(bar_width * wave_marker_ratio);
             pygame.draw.line(self.screen, settings.RED, (wave_marker_x, bar_y), (wave_marker_x, bar_y + bar_height), 2);
        progress_text = f"{self.zombies_defeated_count} / {self.target_zombies}"; text_surf = self.progress_font.render(progress_text, True, settings.WHITE); text_rect = text_surf.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2)); self.screen.blit(text_surf, text_rect)

    def _draw_level_complete_screen(self):
        self.screen.fill(settings.DARK_GREEN); message = f"УРОВЕНЬ {self.current_level_id} ПРОЙДЕН!"; text_surf = self.end_game_font.render(message, True, settings.YELLOW); text_rect = text_surf.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)); self.screen.blit(text_surf, text_rect); restart_surf = self.font.render("Кликните, чтобы вернуться в меню", True, settings.WHITE); restart_rect = restart_surf.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT * 3 / 4)); self.screen.blit(restart_surf, restart_rect)

    def _draw_game_over_screen(self):
        self.screen.fill(settings.BLACK); message = f"ИГРА ОКОНЧЕНА (Уровень {self.current_level_id})"; text_surf = self.end_game_font.render(message, True, settings.RED); text_rect = text_surf.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)); self.screen.blit(text_surf, text_rect); restart_surf = self.font.render("Кликните, чтобы вернуться в меню", True, settings.WHITE); restart_rect = restart_surf.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT * 3 / 4)); self.screen.blit(restart_surf, restart_rect)


    # --- Основной Метод Отрисовки (С ИСПРАВЛЕНИЯМИ И PROGRESS_BAR) ---
    def _draw(self):
        """Отрисовка всего на экране в зависимости от состояния игры."""
        if self.game_state == "MAIN_MENU":
            self._draw_main_menu()
        elif self.game_state == "PLAYING":
             # <<<--- PRINT 5 (РАСКОММЕНТИРОВАН) ---
             #print(f"--- Внутри _draw (PLAYING). Уровень: {self.current_level_id} ---")
             if not self.current_level_data:
                 print("!!! Ошибка в _draw: Нет данных текущего уровня!")
                 self.screen.fill(settings.RED)
             else:
                 self.screen.fill(settings.GREY)
                 self._draw_grid()
                 self.all_sprites.draw(self.screen)
                 self._draw_progress_bar() # <<<--- Добавлен вызов прогресс-бара
                 self._draw_shop()
        elif self.game_state == "LEVEL_COMPLETE":
            self._draw_level_complete_screen()
        elif self.game_state == "GAME_OVER":
            self._draw_game_over_screen()

        pygame.display.flip()

# --- Конец Класса Game ---