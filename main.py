# main.py

import pygame # Импортируем pygame для pygame.quit() в конце (хотя он и в game.run())
import sys
# <<<--- Импортируем наш класс Game ---
from game import Game

# Эта конструкция гарантирует, что код ниже выполнится,
# только если мы запустим именно этот файл (main.py)
if __name__ == "__main__":
    # Создаем экземпляр нашей игры
    game_instance = Game()
    # Запускаем основной цикл игры
    game_instance.run()

    # Эта часть выполнится после завершения game_instance.run()
    # pygame.quit() # game.run() уже вызывает pygame.quit()
    # sys.exit()    # game.run() уже вызывает sys.exit()