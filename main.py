# main.py

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.game_manager import Game

if __name__ == '__main__':
    game = Game()
    game.run()