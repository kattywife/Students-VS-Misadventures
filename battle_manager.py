# battle_manager.py

import pygame
from settings import *
from assets import SOUNDS
from sprites import *


class BattleManager:
    def __init__(self, all_sprites, defenders, enemies, projectiles, coffee_beans, neuro_mowers, ui_manager,
                 level_manager, team, upgrades, placed_mowers):
        self.all_sprites = all_sprites
        self.defenders = defenders
        self.enemies = enemies
        self.projectiles = projectiles
        self.coffee_beans = coffee_beans
        self.neuro_mowers = neuro_mowers

        self.ui_manager = ui_manager
        self.level_manager = level_manager
        self.is_game_over = False

        self.team = team
        self.upgrades = upgrades
        self.placed_mowers_data = placed_mowers

        self.coffee = level_manager.level_data.get('start_coffee', 150)
        self.selected_defender = None

        self.ui_manager.create_battle_shop(self.team)
        self.place_neuro_mowers()

    def start(self):
        self.level_manager.start()

    def place_neuro_mowers(self):
        for row, mower_type in self.placed_mowers_data.items():
            NeuroMower(row, (self.all_sprites, self.neuro_mowers), mower_type)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'PAUSE'

    def handle_click(self, pos):
        clicked_shop_item = self.ui_manager.handle_shop_click(pos)
        if clicked_shop_item:
            if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
            self.selected_defender = clicked_shop_item if self.selected_defender != clicked_shop_item else None
            return

        for bean in list(self.coffee_beans):
            if bean.alive() and bean.rect.collidepoint(pos):
                if SOUNDS.get('money'): SOUNDS['money'].play()
                self.coffee += bean.value
                bean.kill()
                return

        if self.selected_defender:
            cost = DEFENDERS_DATA[self.selected_defender]['cost']
            if self.coffee >= cost:
                grid_pos = self._get_grid_cell(pos)
                if grid_pos and not self._is_cell_occupied(grid_pos):
                    self.coffee -= cost
                    self._place_defender(grid_pos)
                    self.selected_defender = None

    def _get_grid_cell(self, pos):
        x, y = pos
        if GRID_START_X <= x < GRID_START_X + GRID_WIDTH and GRID_START_Y <= y < GRID_START_Y + GRID_HEIGHT:
            col, row = (x - GRID_START_X) // CELL_SIZE_W, (y - GRID_START_Y) // CELL_SIZE_H
            return col, row
        return None

    def _is_cell_occupied(self, grid_pos):
        col, row = grid_pos
        center_x, center_y = GRID_START_X + col * CELL_SIZE_W + CELL_SIZE_W / 2, GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        return any(d.alive() and d.rect.collidepoint(center_x, center_y) for d in self.defenders)

    def _place_defender(self, grid_pos):
        if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
        col, row = grid_pos
        x, y = GRID_START_X + col * CELL_SIZE_W + CELL_SIZE_W / 2, GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        groups = (self.all_sprites, self.defenders)
        defender_type = self.selected_defender
        data = DEFENDERS_DATA[defender_type].copy()

        if defender_type in self.upgrades:
            upgrade_info = data.get('upgrade', {})
            for key, value in upgrade_info.items():
                if key != 'cost': data[key] += value

        unit_map = {
            'programmer': ProgrammerBoy, 'botanist': BotanistGirl, 'coffee_machine': CoffeeMachine,
            'activist': Activist, 'guitarist': Guitarist, 'medic': Medic, 'artist': Artist
        }
        constructor_args = {'x': x, 'y': y, 'groups': groups, 'data': data}

        if defender_type in ['programmer', 'artist']:
            constructor_args.update(
                {'all_sprites': self.all_sprites, 'projectile_group': self.projectiles, 'enemies_group': self.enemies})
        elif defender_type in ['botanist', 'guitarist']:
            constructor_args.update({'all_sprites': self.all_sprites, 'enemies_group': self.enemies})
        elif defender_type == 'coffee_machine':
            constructor_args.update({'all_sprites': self.all_sprites, 'coffee_bean_group': self.coffee_beans})
        elif defender_type == 'medic':
            constructor_args.update({'defenders_group': self.defenders})

        defender_class = unit_map.get(defender_type)
        if defender_class:
            defender = defender_class(**constructor_args)
            if defender_type in self.upgrades: defender.is_upgraded = True

    def update(self):
        enemies_before_update = len(self.enemies)

        self.all_sprites.update(self.defenders, self.all_sprites, self.projectiles)
        self.apply_auras()
        self.check_collisions()

        enemies_after_update = len(self.enemies)
        killed_this_frame = enemies_before_update - enemies_after_update
        for _ in range(killed_this_frame):
            self.level_manager.enemy_killed()

        self.level_manager.update()

        for enemy in list(self.enemies):
            if enemy.alive() and enemy.rect.right < GRID_START_X:
                mower_activated = False
                for mower in self.neuro_mowers:
                    if mower.rect.centery == enemy.rect.centery and not mower.is_active:
                        mower.activate(self.enemies)
                        enemy.kill()
                        mower_activated = True
                        break
                if not mower_activated:
                    self.is_game_over = True
                    return

    def check_collisions(self):
        # Снаряды героев -> Враги
        for proj in list(self.projectiles):
            if proj.alive() and not isinstance(proj, Integral):
                hits = pygame.sprite.spritecollide(proj, self.enemies, False)
                if hits:
                    target = hits[0]
                    if target.alive():
                        if isinstance(proj, PaintSplat):
                            target.slow_down(proj.artist.data['slow_factor'], proj.artist.data['slow_duration'])
                            target.get_hit(proj.damage)
                        else:
                            target.get_hit(proj.damage)
                    proj.kill()

        # Снаряды врагов (интегралы) -> Герои
        for proj in list(self.projectiles):
            if proj.alive() and isinstance(proj, Integral):
                hits = pygame.sprite.spritecollide(proj, self.defenders, True)  # Уничтожаем героя
                if hits: proj.kill()

        # Звуковые волны гитариста -> Враги
        for wave in [s for s in self.all_sprites if isinstance(s, SoundWave)]:
            for enemy in self.enemies:
                if wave.rect.colliderect(enemy.rect) and enemy not in wave.hit_enemies:
                    enemy.get_hit(wave.damage)
                    wave.hit_enemies.add(enemy)

        # Нейросети -> Враги
        for mower in list(self.neuro_mowers):
            if not mower.is_active:
                if pygame.sprite.spritecollide(mower, self.enemies, False):
                    mower.activate(self.enemies)

    def apply_auras(self):
        for d in self.defenders: d.buff_multiplier, d.debuff_multiplier = 1.0, 1.0

        for activist in [s for s in self.defenders if isinstance(s, Activist) and s.alive()]:
            for defender in self.defenders:
                if pygame.math.Vector2(activist.rect.center).distance_to(defender.rect.center) < activist.data[
                    'radius']:
                    defender.buff_multiplier *= activist.data['buff']

        for prof in [s for s in self.enemies if isinstance(s, StuffyProf) and s.alive()]:
            for defender in self.defenders:
                if pygame.math.Vector2(prof.rect.center).distance_to(defender.rect.center) < prof.data['radius']:
                    defender.debuff_multiplier *= prof.data['debuff']

    def draw(self, surface):
        self._draw_world(surface)

    def _draw_world(self, surface):
        surface.blit(load_image('background.png', DEFAULT_COLORS['background'], (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        self.ui_manager.draw_grid(surface)

        for sprite in self.all_sprites:
            if hasattr(sprite, 'draw_aura'): sprite.draw_aura(surface)

        self.all_sprites.draw(surface)
        self.ui_manager.draw_shop(surface, self.selected_defender, self.coffee)

        spawn_progress = self.level_manager.get_spawn_progress()
        kill_progress = self.level_manager.get_kill_progress()
        spawn_data = self.level_manager.get_spawn_count_data()
        kill_data = self.level_manager.get_kill_count_data()
        self.ui_manager.draw_hud(surface, spawn_progress, kill_progress, spawn_data, kill_data)