# core/sound_manager.py

import pygame
from data.assets import SOUNDS, MUSIC
from data.settings import DEFAULT_MUSIC_VOLUME

class SoundManager:
    def __init__(self):
        self.sfx_enabled = True
        self.music_enabled = True
        self.current_music = None

    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            pygame.mixer.music.stop()
        else:
            if self.current_music:
                self.play_music(self.current_music)

    def play_sfx(self, name):
        if self.sfx_enabled and name in SOUNDS and SOUNDS[name]:
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(SOUNDS[name])
                return channel
        return None

    def get_sfx_length(self, name):
        """Возвращает длительность звукового эффекта в секундах."""
        if name in SOUNDS and SOUNDS[name]:
            return SOUNDS[name].get_length()
        return 0.0

    def play_music(self, name, loops=-1, volume=DEFAULT_MUSIC_VOLUME):
        self.current_music = name
        if self.music_enabled and name in MUSIC and MUSIC[name]:
            pygame.mixer.music.load(MUSIC[name])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)

    def stop_music(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def stop_all_sfx(self):
        pygame.mixer.stop()