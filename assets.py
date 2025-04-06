# assets.py

import pygame
import os
# <<<--- Важно: Импортируем файл с настройками! ---
import settings

def load_image(filename, size=None, default_color=settings.RED): # Используем цвет ошибки из настроек
    """Загружает изображение, масштабирует и обрабатывает ошибки."""
    if not filename:
         # print("!!! Предупреждение: Попытка загрузить изображение без имени файла.")
         fallback_size = size if size else (settings.PLANT_SIZE, settings.PLANT_SIZE) # Размер по умолчанию из настроек
         if isinstance(fallback_size, (int, float)): fallback_size = (fallback_size, fallback_size)
         fallback_surface = pygame.Surface(fallback_size)
         fallback_surface.fill(default_color)
         return fallback_surface

    # <<<--- Изменено: Формируем путь относительно папки images ---
    # Теперь предполагаем, что filename - это ТОЛЬКО имя файла (e.g., "peashooter.png")
    try:
        # Собираем полный путь: корень_проекта/assets/images/имя_файла.png
        base_path = os.path.dirname(os.path.dirname(__file__)) # Папка PvZ_Clone
        # Используем settings.IMAGE_FOLDER для пути к картинкам
        filepath = os.path.join(base_path, settings.IMAGE_FOLDER, filename)
        # print(f"Пытаемся загрузить: {filepath}") # Для отладки пути

        image = pygame.image.load(filepath).convert_alpha()
        if size:
            if isinstance(size, (int, float)):
                 orig_w, orig_h = image.get_size()
                 if orig_h > 0:
                     aspect_ratio = orig_w / orig_h
                     new_height = int(size / aspect_ratio) if aspect_ratio > 0 else size
                     image = pygame.transform.smoothscale(image, (size, new_height))
                 else:
                     image = pygame.transform.smoothscale(image, (size, size))
            else:
                 image = pygame.transform.smoothscale(image, size)
        return image
    except Exception as e:
        # Выводим имя файла, а не полный путь, для краткости
        print(f"!!! Ошибка загрузки изображения '{filename}': {e}")
        fallback_size = size if size else (settings.PLANT_SIZE, settings.PLANT_SIZE)
        if isinstance(fallback_size, (int, float)): fallback_size = (fallback_size, fallback_size)
        fallback_surface = pygame.Surface(fallback_size)
        fallback_surface.fill(default_color)
        return fallback_surface

# Сюда позже можно добавить load_sound(filename), load_font(name, size) и т.д.