# sprites.py

import pygame
from settings import *
from assets import load_image, SOUNDS


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.last_update = pygame.time.get_ticks()


class Defender(BaseSprite):
    def __init__(self, x, y, groups, defender_type):
        super().__init__(groups)
        self.data = DEFENDERS_DATA[defender_type]
        self.health = self.data['health']
        self.cost = self.data['cost']
        self.image = load_image(f'{defender_type}.png', DEFAULT_COLORS[defender_type],
                                (CELL_SIZE_W - 10, CELL_SIZE_H - 10))
        self.rect = self.image.get_rect(center=(x, y))
        self.is_animate = False
        self.is_being_eaten = False
        self.scream_channel = None

    def update(self, *args, **kwargs):
        if self.is_animate:
            self.manage_scream_sound()
        if self.health <= 0:
            if self.is_animate and SOUNDS.get('hero_dead'):
                SOUNDS['hero_dead'].play()
            self.stop_scream()
            self.kill()

    def manage_scream_sound(self):
        scream_sound = SOUNDS.get('scream')
        if not scream_sound: return

        if self.is_being_eaten and not (self.scream_channel and self.scream_channel.get_busy()):
            self.scream_channel = pygame.mixer.find_channel()
            if self.scream_channel: self.scream_channel.play(scream_sound, -1)
        elif not self.is_being_eaten and self.scream_channel:
            self.stop_scream()

    def stop_scream(self):
        if self.scream_channel:
            self.scream_channel.stop()
            self.scream_channel = None


class ProgrammerBoy(Defender):
    def __init__(self, x, y, groups, all_sprites_group, projectile_group, enemies_group):
        super().__init__(x, y, groups, 'programmer')
        self.is_animate = True
        self.all_sprites_group = all_sprites_group
        self.projectile_group = projectile_group
        self.enemies_group = enemies_group
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_shot = pygame.time.get_ticks()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        now = pygame.time.get_ticks()
        has_enemy_in_row = any(enemy.rect.centery == self.rect.centery for enemy in self.enemies_group)
        if self.alive() and has_enemy_in_row and now - self.last_shot > self.attack_cooldown:
            self.last_shot = now
            Bracket(self.rect.right, self.rect.centery, (self.all_sprites_group, self.projectile_group),
                    self.data['damage'])


class BotanistGirl(Defender):
    def __init__(self, x, y, groups, all_sprites_group, enemies_group):
        super().__init__(x, y, groups, 'botanist')
        self.is_animate = True
        self.all_sprites_group = all_sprites_group
        self.enemies_group = enemies_group
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_attack = pygame.time.get_ticks()
        self.attack_radius = self.data['radius']

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        now = pygame.time.get_ticks()
        if self.alive():
            enemies_in_range = any(
                pygame.math.Vector2(self.rect.center).distance_to(enemy.rect.center) < self.attack_radius
                for enemy in self.enemies_group
            )
            if enemies_in_range and now - self.last_attack > self.attack_cooldown:
                self.last_attack = now
                self.attack()

    def attack(self):
        BookAttackEffect(self.rect.center, self.all_sprites_group, self.attack_radius * 2)
        for enemy in self.enemies_group:
            if self.alive() and pygame.math.Vector2(self.rect.center).distance_to(
                    enemy.rect.center) < self.attack_radius:
                enemy.get_hit(self.data['damage'])


class BookAttackEffect(BaseSprite):
    def __init__(self, center_pos, groups, diameter):
        super().__init__(groups)
        self.image = load_image('book_attack.png', DEFAULT_COLORS['book_attack'], (diameter, diameter))
        self.image.set_alpha(150)
        self.rect = self.image.get_rect(center=center_pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 200

    def update(self, *args, **kwargs):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


class CoffeeMachine(Defender):
    def __init__(self, x, y, groups, all_sprites_group, coffee_bean_group):
        # ----- ВОТ ИСПРАВЛЕНИЕ -----
        super().__init__(x, y, groups, 'coffee_machine')
        # ---------------------------
        self.all_sprites_group = all_sprites_group
        self.coffee_bean_group = coffee_bean_group
        self.production_cooldown = self.data['cooldown'] * 1000
        self.last_production = pygame.time.get_ticks()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        now = pygame.time.get_ticks()
        if self.alive() and now - self.last_production > self.production_cooldown:
            self.last_production = now
            CoffeeBean(self.rect.centerx, self.rect.top, (self.all_sprites_group, self.coffee_bean_group),
                       self.data['production'])


class CoffeeBean(BaseSprite):
    def __init__(self, x, y, groups, value):
        super().__init__(groups)
        self.value = value
        self.image = load_image('coffee_bean.png', DEFAULT_COLORS['coffee_bean'], (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 8000

    def update(self, *args, **kwargs):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


class Bracket(BaseSprite):
    def __init__(self, x, y, groups, damage):
        super().__init__(groups)
        self.damage = damage
        self.image = load_image('bracket.png', DEFAULT_COLORS['bracket'], (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self, *args, **kwargs):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()


class Enemy(BaseSprite):
    def __init__(self, row, groups, enemy_type):
        super().__init__(groups)
        self.data = ENEMIES_DATA[enemy_type]
        self.health = self.data['health']
        self.speed = self.data['speed']
        self.damage = self.data['damage']

        self.original_image = load_image(f'{enemy_type}.png', DEFAULT_COLORS[enemy_type],
                                         (CELL_SIZE_W - 20, CELL_SIZE_H - 10))
        self.image = self.original_image.copy()
        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        self.rect = self.image.get_rect(midleft=(SCREEN_WIDTH, y))

        self.is_attacking = False
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 100

        self.attack_cooldown = 1000
        self.last_attack_time = 0
        self.eating_channel = None
        self.current_target = None

    def get_hit(self, damage):
        self.health -= damage
        self.is_hit = True
        self.hit_timer = pygame.time.get_ticks()
        if SOUNDS.get('damage'): SOUNDS.get('damage').play()

    def manage_hit_flash(self):
        if self.is_hit:
            now = pygame.time.get_ticks()
            if now - self.hit_timer > self.hit_duration:
                self.is_hit = False
            else:
                flash_image = self.original_image.copy()
                flash_image.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                self.image = flash_image
                return
        self.image = self.original_image

    def update(self, defenders_group):
        self.manage_hit_flash()
        if self.health <= 0:
            if SOUNDS.get('enemy_dead'): SOUNDS['enemy_dead'].play()
            self.stop_eating_sound()
            if self.current_target:
                self.current_target.is_being_eaten = False
            self.kill()
            return

        target_found = False
        for defender in defenders_group:
            if defender.alive() and defender.rect.colliderect(self.rect) and defender.rect.centery == self.rect.centery:
                target_found = True
                self.is_attacking = True

                if self.current_target != defender:
                    if self.current_target:
                        self.current_target.is_being_eaten = False
                    self.current_target = defender

                self.current_target.is_being_eaten = True

                now = pygame.time.get_ticks()
                if now - self.last_attack_time > self.attack_cooldown:
                    self.play_eating_sound()
                    self.last_attack_time = now
                    defender.health -= self.damage
                break

        if not target_found:
            if self.is_attacking:
                self.is_attacking = False
                self.stop_eating_sound()
                if self.current_target:
                    self.current_target.is_being_eaten = False
                    self.current_target = None

        if not self.is_attacking:
            self.rect.x -= self.speed

    def kill(self):
        # Проверяем, жив ли еще спрайт, чтобы избежать двойного вызова
        if self.alive():
            if SOUNDS.get('enemy_dead'):
                SOUNDS['enemy_dead'].play()

            self.stop_eating_sound()
            if self.current_target:
                self.current_target.is_being_eaten = False

            # Вызываем оригинальный метод kill() из pygame.sprite.Sprite
            super().kill()
    def play_eating_sound(self):
        eating_sound = SOUNDS.get('eating')
        if eating_sound and not (self.eating_channel and self.eating_channel.get_busy()):
            self.eating_channel = pygame.mixer.find_channel()
            if self.eating_channel: self.eating_channel.play(eating_sound)

    def stop_eating_sound(self):
        if self.eating_channel:
            self.eating_channel.stop()
            self.eating_channel = None


class Calculus(Enemy):
    def __init__(self, row, groups):
        super().__init__(row, groups, 'calculus')
        self.has_jumped = False

    def update(self, defenders_group):
        if not self.has_jumped:
            for defender in defenders_group:
                if defender.alive() and defender.rect.colliderect(
                        self.rect) and defender.rect.centery == self.rect.centery:
                    self.rect.x = defender.rect.left - self.rect.width
                    self.has_jumped = True
                    return
        super().update(defenders_group)


class Akadem(BaseSprite):
    def __init__(self, row, groups):
        super().__init__(groups)
        self.image = load_image('akadem.png', DEFAULT_COLORS['akadem'], (CELL_SIZE_W, CELL_SIZE_H - 10))
        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        self.rect = self.image.get_rect(center=(GRID_START_X / 2, y))
        self.is_active = False
        self.speed = 8

    def activate(self):
        self.is_active = True

    def update(self, *args, **kwargs):
        if self.is_active:
            self.rect.x += self.speed
            if self.rect.left > SCREEN_WIDTH:
                self.kill()