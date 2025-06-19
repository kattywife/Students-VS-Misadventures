# core/sound_manager.py

from typing import Optional
import pygame
from data.assets import SOUNDS, MUSIC
from data.settings import DEFAULT_MUSIC_VOLUME

class SoundManager:
    """
    Управляет воспроизведением всех звуковых эффектов (SFX) и фоновой музыки.
    Позволяет включать/выключать музыку и звуки по отдельности.
    """

    def __init__(self) -> None:
        """Инициализирует менеджер звука с включенными по умолчанию настройками."""
        self.sfx_enabled = True
        self.music_enabled = True
        self.current_music = None

    def toggle_sfx(self) -> None:
        """Переключает состояние воспроизведения звуковых эффектов (вкл/выкл)."""
        self.sfx_enabled = not self.sfx_enabled

    def toggle_music(self) -> None:
        """
        Переключает состояние воспроизведения музыки (вкл/выкл).
        Останавливает музыку, если она выключается, и возобновляет, если включается.
        """
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            pygame.mixer.music.stop()
        else:
            if self.current_music:
                self.play_music(self.current_music)

    def play_sfx(self, name: str) -> Optional[pygame.mixer.Channel]:
        """
        Воспроизводит звуковой эффект по его имени, если SFX включены.

        Args:
            name (str): Имя звукового эффекта (ключ в словаре SOUNDS).

        Returns:
            Optional[pygame.mixer.Channel]: Возвращает канал, на котором проигрывается звук,
                                             или None, если звук не был воспроизведен.
        """
        if self.sfx_enabled and name in SOUNDS and SOUNDS[name]:
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(SOUNDS[name])
                return channel
        return None

    def get_sfx_length(self, name: str) -> float:
        """
        Возвращает длительность звукового эффекта в секундах.

        Args:
            name (str): Имя звукового эффекта.

        Returns:
            float: Длительность звука в секундах, или 0.0 если звук не найден.
        """
        if name in SOUNDS and SOUNDS[name]:
            return SOUNDS[name].get_length()
        return 0.0

    def play_music(self, name: str, loops: int = -1, volume: float = DEFAULT_MUSIC_VOLUME) -> None:
        """
        Загружает и воспроизводит фоновую музыку.

        Args:
            name (str): Имя музыкального трека (ключ в словаре MUSIC).
            loops (int): Количество повторений (-1 для бесконечного цикла).
            volume (float): Громкость музыки (от 0.0 до 1.0).
        """
        self.current_music = name
        if self.music_enabled and name in MUSIC and MUSIC[name]:
            pygame.mixer.music.load(MUSIC[name])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)

    def stop_music(self) -> None:
        """Останавливает и выгружает текущую фоновую музыку."""
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def stop_all_sfx(self) -> None:
        """Останавливает все активные звуковые эффекты на всех каналах."""
        pygame.mixer.stop()