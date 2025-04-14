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

        # <<<--- Обновление загрузки иконки ---
        self.sun_icon_img = load_image(settings.COFFEE_BEAN_ICON_FILE, 30, settings.YELLOW)  # Теперь иконка зерна

        # <<<--- Обновление названий групп спрайтов (опционально, но рекомендуется) ---
        self.all_sprites = pygame.sprite.Group()
        self.placed_objects = pygame.sprite.Group()  # Вместо plants_group (Jun, Botan, Coffee)
        self.students = pygame.sprite.Group()  # Отдельно студенты (Jun, Botan)
        # self.peashooters -> убираем или переименовываем, если нужно отдельно Jun
        # self.sunflowers -> убираем или переименовываем в coffee_machines
        self.coffee_machines = pygame.sprite.Group()  # Для генераторов
        self.coffee_beans = pygame.sprite.Group()  # Вместо suns
        self.adversities = pygame.sprite.Group()  # Вместо zombies
        self.projectiles = pygame.sprite.Group()  # Общая группа для Gear и Book
        self.academ_mowers = pygame.sprite.Group()  # Вместо lawnmowers

        # Начальное состояние
        self.game_state = "MAIN_MENU"

        # Инициализация игровых переменных
        self.coffee_points = 0  # Переименуем позже, если захочешь
        self.selected_plant_type = None  # Тип выбранного студента/машины
        self.occupied_cells = set()
        self.shop_item_rects = {}
        self.level_buttons = {}

        # Переменные для текущего уровня (остаются)
        self.current_level_id = 0
        # ... (остальные переменные уровня) ...

        # <<<--- Обновление инициализации Магазина ---
        self.plant_shop_items = {
            "jun_boy": {  # Ключ = идентификатор типа
                "cost": settings.JUN_BOY_COST,
                "class": sprites.JunBoy,  # Новый класс
                "image": load_image(settings.JUN_BOY_IMAGE_FILE, 40, settings.GREEN)
            },
            "botan_girl": {  # <<<--- Добавляем Ботана
                "cost": settings.BOTAN_GIRL_COST,
                "class": sprites.BotanGirl,
                "image": load_image(settings.BOTAN_GIRL_IMAGE_FILE, 40, settings.BLUE)
            },
            "coffee_machine": {  # Ключ = идентификатор типа
                "cost": settings.COFFEE_MACHINE_COST,
                "class": sprites.CoffeeMachine,  # Новый класс
                "image": load_image(settings.COFFEE_MACHINE_IMAGE_FILE, 40, settings.YELLOW)
            }
            # Удалили старые peashooter/sunflower
        }
        # Академы (косилки) создаются в start_level()

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

        # <<<--- Обновление очистки групп ---
        self.all_sprites.empty()
        self.placed_objects.empty()
        self.students.empty()
        self.coffee_machines.empty()
        self.coffee_beans.empty()
        self.adversities.empty()
        self.projectiles.empty()
        self.academ_mowers.empty()
        self.occupied_cells.clear()
        self.shop_item_rects.clear()

        # Сброс переменных уровня
        self.coffee_points = self.current_level_data.get("starting_sun", 150)
        self.selected_plant_type = None
        self.game_start_time = self.current_time_in_loop # Устанавливаем время начала
        self.last_zombie_spawn_time = self.game_start_time
        self.zombies_defeated_count = 0
        self.target_zombies = self.current_level_data.get("zombies_to_defeat", 10)
        self.mid_wave_triggered = False # Сбрасываем флаг волны
        print(f"  Цель уровня: победить {self.target_zombies} зомби.") # ОТЛАДКА

        # Создаем косилки (академов)
        print("  Создание 'Академов' для уровня...")
        for r in range(settings.GRID_ROWS):
            try:
                mower = sprites.Academ(r)  # Используем новый класс Academ
                self.all_sprites.add(mower)
                self.academ_mowers.add(mower)  # Добавляем в новую группу
            except Exception as e:
                print(f"!!! ОШИБКА создания 'Академа' {r}: {e}")
        print(f"  'Академы' созданы: {len(self.academ_mowers)}")

        self.game_state = "PLAYING"

    def go_to_main_menu(self):
        print("Возврат в главное меню...")
        self.current_level_id = 0; self.current_level_data = None; self.selected_plant_type = None;
        # <<<--- Обновление очистки групп ---
        self.all_sprites.empty(); self.placed_objects.empty(); self.students.empty();
        self.coffee_machines.empty(); self.coffee_beans.empty(); self.adversities.empty();
        self.projectiles.empty(); self.academ_mowers.empty(); self.occupied_cells.clear();
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
                    clicked_handled = False
                    # <<<--- Обновление: клик по кофейному зерну ---
                    clicked_beans = [bean for bean in self.coffee_beans if bean.rect.collidepoint(mouse_pos)]
                    if clicked_beans:
                        for bean in clicked_beans:
                            self.coffee_points += bean.value  # Очки теперь "кофеин"
                            bean.kill()
                        print(f"Собран кофеин! Всего: {self.coffee_points}")
                        clicked_handled = True
                    if not clicked_handled and mouse_pos[1] < settings.SHOP_HEIGHT:
                        for name, rect in self.shop_item_rects.items():
                            if rect.collidepoint(mouse_pos):
                                 if self.coffee_points >= self.plant_shop_items[name]['cost']: self.selected_plant_type = name; print(f"Выбрано: {name}")
                                 else: print(f"Мало ЗЕ для {name}"); self.selected_plant_type = None;
                                 clicked_handled = True; break;
                    # <<<--- Обновление: клик для посадки ---
                    if not clicked_handled and self.selected_plant_type is not None and mouse_pos[1] > settings.SHOP_HEIGHT:
                        plant_data = self.plant_shop_items[self.selected_plant_type]; cost = plant_data["cost"]; grid_rect_area = pygame.Rect(settings.GRID_START_X, settings.GRID_START_Y, settings.GRID_COLS * settings.CELL_WIDTH, settings.GRID_ROWS * settings.CELL_HEIGHT);
                        if grid_rect_area.collidepoint(mouse_pos):
                            clicked_col = (mouse_pos[0] - settings.GRID_START_X) // settings.CELL_WIDTH; clicked_row = (mouse_pos[1] - settings.GRID_START_Y) // settings.CELL_HEIGHT;
                            if 0 <= clicked_col < settings.GRID_COLS and 0 <= clicked_row < settings.GRID_ROWS:
                                 target_cell = (clicked_row, clicked_col);
                                 if self.coffee_points >= cost:
                                     if target_cell not in self.occupied_cells:
                                         plant_center_x = settings.GRID_START_X + clicked_col * settings.CELL_WIDTH + settings.CELL_WIDTH // 2; plant_center_y = settings.GRID_START_Y + clicked_row * settings.CELL_HEIGHT + settings.CELL_HEIGHT // 2;
                                         try:
                                             PlantClass = plant_data["class"]  # Берем класс JunBoy, BotanGirl или CoffeeMachine
                                             new_object = PlantClass(plant_center_x, plant_center_y)
                                             new_object.grid_pos = target_cell

                                             self.all_sprites.add(new_object)
                                             self.placed_objects.add(new_object)  # Добавляем в общую группу размещаемых

                                             # Добавляем в специфичные группы
                                             if isinstance(new_object, sprites.JunBoy) or isinstance(new_object, sprites.BotanGirl):
                                                 self.students.add(new_object)  # Добавляем в группу студентов
                                             elif isinstance(new_object, sprites.CoffeeMachine):
                                                 self.coffee_machines.add(new_object)  # Добавляем в группу кофе-машин

                                             self.coffee_points -= cost
                                             self.occupied_cells.add(target_cell)
                                             print(f"{self.selected_plant_type} размещен в {target_cell}! Кофеин: {self.coffee_points}")
                                             # self.selected_plant_type = None

                                         except Exception as e:
                                             print(f"ОШИБКА размещения: {e}")
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
        if self.game_state != "PLAYING": return

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

        # --- Обновление Спрайтов ---
        # 1. Кофе-машины -> создают Кофейные Зерна
        for machine in self.coffee_machines:
            new_bean = machine.update() # Возвращает CoffeeBean или None
            if new_bean:
                self.all_sprites.add(new_bean)
                self.coffee_beans.add(new_bean)

        # 2. Кофейные Зерна -> исчезают по таймеру
        self.coffee_beans.update()

        # 3. Студенты -> стреляют, если есть цель
        for student in self.students: # Перебираем всех студентов
             # Находим злоключения на ряду студента и впереди него
             adversities_on_row = [adv for adv in self.adversities if adv.row == student.row]
             adversities_ahead = [adv for adv in adversities_on_row if adv.rect.left > student.rect.right]
             # Метод update студента вернет снаряд (Gear/Book) или None
             new_projectile = student.update(adversities_ahead)
             if new_projectile:
                 self.all_sprites.add(new_projectile)
                 self.projectiles.add(new_projectile) # Добавляем в общую группу снарядов

        # 4. Снаряды (Шестеренки/Книги) -> летят
        self.projectiles.update()

        # 5. Злоключения -> идут или атакуют (передаем группу студентов/машин)
        self.adversities.update(self.placed_objects)

        # 6. Академы -> едут И УБИВАЮТ злоключения
        mower_kills_this_frame = 0
        for mower in self.academ_mowers: # Используем новую группу
            # Передаем группу злоключений
            killed_by_mower = mower.update(self.adversities)
            mower_kills_this_frame += killed_by_mower
        if mower_kills_this_frame > 0:
            print(f"GAME: Убито 'Академами' за кадр: {mower_kills_this_frame}")
            self.zombies_defeated_count += mower_kills_this_frame
            print(f"GAME: Новый счетчик убитых: {self.zombies_defeated_count}/{self.target_zombies}")


        # --- Освобождение Ячеек ---
        currently_occupied = {obj.grid_pos for obj in self.placed_objects if obj.grid_pos}
        self.occupied_cells = currently_occupied

        # --- Спавн Злоключений ---
        base_spawn_rate = self.current_level_data.get("spawn_rate", 5.0)
        allowed_adversity_types = self.current_level_data.get("allowed_zombies", ["alarm_clock"]) # Берем новые типы
        target_zombies_for_wave = int(self.target_zombies * settings.MID_WAVE_THRESHOLD_RATIO)
        current_spawn_rate = base_spawn_rate
        # ... (логика средней волны остается) ...

        if self.target_zombies > 0 and self.zombies_defeated_count < self.target_zombies:
            if now - self.last_zombie_spawn_time >= current_spawn_rate:
                if allowed_adversity_types:
                    try:
                        chosen_type = random.choice(allowed_adversity_types)
                        spawn_row = random.randint(0, settings.GRID_ROWS - 1)
                        adv_y_pos = settings.GRID_START_Y + spawn_row * settings.CELL_HEIGHT + settings.CELL_HEIGHT // 2
                        # Создаем Злоключение
                        new_adversity = sprites.Adversity(adv_y_pos, chosen_type)
                        self.all_sprites.add(new_adversity)
                        self.adversities.add(new_adversity) # Добавляем в группу злоключений
                        self.last_zombie_spawn_time = now
                    except Exception as e: print(f"ОШИБКА спавна злоключения: {e}")

        # --- Проверка столкновений снарядов со злоключениями ---
        try:
            # Проверяем столкновение self.projectiles с self.adversities
            collisions = pygame.sprite.groupcollide(self.projectiles, self.adversities, True, False)
            if collisions:
                for proj, hit_adversities_list in collisions.items():
                    for adv in hit_adversities_list:
                        # Используем урон из снаряда (proj.damage)
                        if hasattr(proj, 'damage'):
                            was_killed = adv.take_damage(proj.damage) # Передаем урон снаряда
                            if was_killed:
                                self.zombies_defeated_count += 1
                                print(f"  !!! Злоключение УБИТО снарядом! Счет: {self.zombies_defeated_count}/{self.target_zombies}")
                        else:
                             print(f"Предупреждение: у снаряда {type(proj)} нет атрибута damage!")
                             # Можно нанести стандартный урон или проигнорировать
                             # adv.take_damage(settings.GEAR_DAMAGE) # Например

        except Exception as e:
            print(f"ОШИБКА столкн. снарядов: {e}"); import traceback; traceback.print_exc()


        # --- Проверка на проигрыш (злоключение дошло до дома) ---
        try:
            # Ищем злоключения, пересекшие черту
            adversities_at_end = [adv for adv in self.adversities if adv.rect.left < settings.GRID_START_X]
            if adversities_at_end:
                for adv in adversities_at_end:
                    adv_row = adv.row
                    mower_activated = False
                    mower_exists_on_row = False # <<<--- Добавим флаг наличия косилки
                    for mower in self.academ_mowers: # Проверяем группу академов
                        if mower.row == adv_row:
                             mower_exists_on_row = True
                             if mower.state == "IDLE":
                                mower.activate()
                                # Злоключение НЕ убиваем здесь, косилка убьет его в своем update
                                mower_activated = True
                                print(f"  'Академ' {adv_row} активирован злоключением.")
                                break # Нашли косилку для этого ряда

                    # Проигрыш, если косилки на этом ряду НЕТ ВООБЩЕ
                    if not mower_exists_on_row:
                         self.game_state = "GAME_OVER"
                         print(f"--- GAME OVER (Ур. {self.current_level_id}, {adv.adversity_type} на {adv_row} прорвался! 'Академа' нет.) ---")
                         break # Выход из цикла проверки злоключений

                if self.game_state == "GAME_OVER": return
        except Exception as e:
            print(f"ОШИБКА проверки проигрыша: {e}"); import traceback; traceback.print_exc()

        # --- Проверка на победу (по количеству убитых) ---
        # (Логика остается прежней, только сообщение можно обновить)
        if self.target_zombies > 0 and self.zombies_defeated_count >= self.target_zombies:
            self.game_state = "LEVEL_COMPLETE"
            print(f"---------------- УРОВЕНЬ {self.current_level_id} ПРОЙДЕН! ({self.zombies_defeated_count}/{self.target_zombies}) ----------------")

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
        shop_rect = pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SHOP_HEIGHT); pygame.draw.rect(self.screen, settings.LIGHT_BLUE, shop_rect); pygame.draw.line(self.screen, settings.BLACK, (0, settings.SHOP_HEIGHT - 1), (settings.SCREEN_WIDTH, settings.SHOP_HEIGHT - 1), 2); sun_text = f"{self.coffee_points}"; sun_surf = self.font.render(sun_text, True, settings.BLACK); icon_width = self.sun_icon_img.get_width() if self.sun_icon_img else 0; sun_rect = sun_surf.get_rect(topleft=(15 + icon_width + 5, 15));
        if self.sun_icon_img: self.screen.blit(self.sun_icon_img, (10, 10))

        try:
            # 1. Получаем значение очков ("кофеина")
            points_text = f"{self.coffee_points}"  # Убедись, что используешь правильный атрибут (self.coffee_points)

            # 2. Рендерим текст с помощью шрифта self.font
            # Убедись, что self.font загружен в __init__ и цвет settings.BLACK существует
            points_surf = self.font.render(points_text, True, settings.BLACK)

            # 3. Получаем Rect для текста и определяем его позицию
            # Убедись, что self.sun_icon_img загружен в __init__
            icon_width = self.sun_icon_img.get_width() if self.sun_icon_img else 0
            # Позиция текста - справа от иконки
            points_rect = points_surf.get_rect(topleft=(15 + icon_width + 5, 15))

            # 4. Рисуем иконку (если она есть)
            if self.sun_icon_img:
                self.screen.blit(self.sun_icon_img, (10, 10))

            # 5. Рисуем сам текст
            self.screen.blit(points_surf, points_rect)
            # --- Конец проверяемого блока ---

        except Exception as e:
            print(f"ОШИБКА отрисовки счетчика кофеина: {e}")  # Ловим возможные ошибки

        start_x = sun_rect.right + 30; item_y = 10; padding = 15
        self.shop_item_rects.clear()
        for name, item in self.plant_shop_items.items():
            can_afford = self.coffee_points >= item['cost']
            base_color = settings.WHITE if can_afford else settings.GREY
            border_color = settings.BLACK
            text_color = settings.BLACK if can_afford else settings.DARK_GREY

            # Выделяем выбранный элемент
            if self.selected_plant_type == name:  # Сравниваем с self.selected_plant_type
                border_color = settings.ORANGE

            item_image = item.get("image")  # Получаем картинку из словаря item
            if not item_image: continue  # Пропускаем, если картинки нет

            item_width = item_image.get_width() + 60
            item_rect = pygame.Rect(start_x, item_y, item_width, settings.SHOP_HEIGHT - 20)

            pygame.draw.rect(self.screen, base_color, item_rect, border_radius=5)
            pygame.draw.rect(self.screen, border_color, item_rect, 3, border_radius=5)

            icon_rect = item_image.get_rect(center=(item_rect.left + 30, item_rect.centery))
            self.screen.blit(item_image, icon_rect)  # Рисуем иконку (Джун, Ботан, КофеМашина)

            cost_surf = self.shop_font.render(str(item["cost"]), True, text_color)  # Рисуем цену
            cost_rect = cost_surf.get_rect(center=(item_rect.right - 25, item_rect.centery))
            self.screen.blit(cost_surf, cost_rect)

            self.shop_item_rects[name] = item_rect  # Сохраняем рект для кликов
            start_x += item_width + padding

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

        # game.py -> class Game
    def _draw_level_complete_screen(self):
            """Рисует экран завершения уровня."""
            self.screen.fill(settings.DARK_GREEN)  # Цвет фона победы
            # <<<--- ИЗМЕНЕНИЕ: Текст сообщения ---
            message = f"СЕССИЯ ЗАКРЫТА! (Уровень {self.current_level_id})"
            text_surf = self.end_game_font.render(message, True, settings.YELLOW)  # Цвет текста победы
            text_rect = text_surf.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2))
            self.screen.blit(text_surf, text_rect)

            restart_surf = self.font.render("Кликните, чтобы вернуться в меню", True, settings.WHITE)
            restart_rect = restart_surf.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT * 3 / 4))
            self.screen.blit(restart_surf, restart_rect)

    def _draw_game_over_screen(self):
            """Рисует экран проигрыша."""
            self.screen.fill(settings.BLACK)  # Цвет фона проигрыша
            # <<<--- ИЗМЕНЕНИЕ: Текст сообщения ---
            message = f"ОТЧИСЛЕН! (Уровень {self.current_level_id})"
            text_surf = self.end_game_font.render(message, True, settings.RED)  # Цвет текста проигрыша
            text_rect = text_surf.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2))
            self.screen.blit(text_surf, text_rect)

            restart_surf = self.font.render("Кликните, чтобы вернуться в меню", True, settings.WHITE)
            restart_rect = restart_surf.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT * 3 / 4))
            self.screen.blit(restart_surf, restart_rect)

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