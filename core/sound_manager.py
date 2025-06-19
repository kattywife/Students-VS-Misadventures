# core/sound_manager.py

import pygame
from data.assets import SOUNDS, MUSIC
from data.settings import DEFAULT_MUSIC_VOLUME

class SoundManager:
    """
    Отвечает за управление всеми звуковыми эффектами (SFX) и фоновой музыкой.
    Позволяет централизованно включать/выключать звук и музыку.
    """
    def __init__(self):
        """Инициализирует менеджер звука."""
        self.sfx_enabled = True
        self.music_enabled = True
        self.current_music = None  # Хранит имя текущего трека для возобновления

    def toggle_sfx(self):
        """Включает или выключает воспроизведение звуковых эффектов."""
        self.sfx_enabled = not self.sfx_enabled
        if not self.sfx_enabled:
            # Останавливаем все активные звуковые эффекты
            pygame.mixer.stop()

    def toggle_music(self):
        """
        Включает или выключает воспроизведение фоновой музыки.
        При выключении останавливает текущий трек, при включении — возобновляет.
        """
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            pygame.mixer.music.stop()
        else:
            # Если музыка была включена и есть трек для воспроизведения
            if self.current_music:
                self.play_music(self.current_music)

    def play_sfx(self, name):
        """
        Воспроизводит звуковой эффект по его имени, если эффекты включены.
        Ищет свободный звуковой канал для воспроизведения.

        Args:
            name (str): Имя звукового эффекта (ключ в словаре SOUNDS).

        Returns:
            pygame.mixer.Channel | None: Возвращает канал, на котором играет звук, или None.
        """
        if self.sfx_enabled and name in SOUNDS and SOUNDS[name]:
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(SOUNDS[name])
                return channel
        return None

    def get_sfx_length(self, name):
        """
        Возвращает длительность звукового эффекта в секундах.

        Args:
            name (str): Имя звукового эффекта.

        Returns:
            float: Длительность в секундах или 0.0, если звук не найден.
        """
        if name in SOUNDS and SOUNDS[name]:
            return SOUNDS[name].get_length()
        return 0.0

    def play_music(self, name, loops=-1, volume=DEFAULT_MUSIC_VOLUME):
        """
        Загружает и воспроизводит фоновую музыку, если она включена.

        Args:
            name (str): Имя трека (ключ в словаре MUSIC).
            loops (int): Количество повторений (-1 для бесконечного).
            volume (float): Громкость музыки (от 0.0 до 1.0).
        """
        self.current_music = name
        if self.music_enabled and name in MUSIC and MUSIC[name]:
            pygame.mixer.music.load(MUSIC[name])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)

    def stop_music(self):
        """Останавливает и выгружает текущую фоновую музыку."""
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def stop_all_sfx(self):
        """Останавливает воспроизведение всех звуковых эффектов на всех каналах."""
        pygame.mixer.stop()