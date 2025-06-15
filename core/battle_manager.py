# core/battle_manager.py

import pygame
import random
from data.settings import *
from data.assets import SOUNDS, load_image
from data.assets import SOUNDS
from entities.defenders import Defender, ProgrammerBoy, BotanistGirl, CoffeeMachine, Activist, Guitarist, Medic, Artist, Fashionista
from entities.enemies import Enemy, StuffyProf
from entities.projectiles import Integral, PaintSplat, SoundWave
from entities.other_sprites import NeuroMower, CoffeeBean


class BattleManager:
    def __init__(self, all_sprites, defenders, enemies, projectiles, coffee_beans, neuro_mowers, ui_manager,
                 level_manager, team, upgrades, placed_mowers):
        self.all_sprites = all_sprites;
        self.defenders = defenders;
        self.enemies = enemies;
        self.projectiles = projectiles
        self.coffee_beans = coffee_beans;
        self.neuro_mowers = neuro_mowers;
        self.ui_manager = ui_manager
        self.level_manager = level_manager;
        self.is_game_over = False;
        self.team_data = team
        self.upgrades = upgrades;
        self.placed_mowers_data = placed_mowers
        self.coffee = level_manager.level_data.get('start_coffee', 150);
        self.selected_defender = None

        self.ui_manager.create_battle_shop(self.team_data);
        self.place_neuro_mowers()

        self.pending_calamities = self.level_manager.calamities.copy();
        random.shuffle(self.pending_calamities)
        self.calamity_triggers = [0.3, 0.7]
        self.calamity_notification = None;
        self.calamity_notification_timer = 0;
        self.notification_duration = 3000

        self.active_calamity = None;
        self.calamity_end_time = 0;
        self.calamity_duration = 15000

    def start(self):
        self.level_manager.start()

    def place_neuro_mowers(self):
        for row, mower_type in self.placed_mowers_data.items():
            NeuroMower(row, (self.all_sprites, self.neuro_mowers), mower_type)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.ui_manager.pause_button_rect.collidepoint(pos): return 'PAUSE'
            self.handle_click(pos)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return 'PAUSE'
        return None

    def handle_click(self, pos):
        clicked_shop_item = self.ui_manager.handle_shop_click(pos)
        if clicked_shop_item:
            if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
            self.selected_defender = clicked_shop_item if self.selected_defender != clicked_shop_item else None
            return
        for bean in list(self.coffee_beans):
            if bean.alive() and bean.rect.collidepoint(pos):
                if SOUNDS.get('money'): SOUNDS['money'].play()
                self.coffee += bean.value;
                bean.kill();
                return
        if self.selected_defender:
            cost = DEFENDERS_DATA[self.selected_defender]['cost']
            if self.coffee >= cost:
                grid_pos = self._get_grid_cell(pos)
                if grid_pos and not self._is_cell_occupied(grid_pos):
                    self.coffee -= cost;
                    self._place_defender(grid_pos);
                    self.selected_defender = None

    def _get_grid_cell(self, pos):
        x, y = pos
        if GRID_START_X <= x < GRID_START_X + GRID_WIDTH and GRID_START_Y <= y < GRID_START_Y + GRID_HEIGHT:
            return (x - GRID_START_X) // CELL_SIZE_W, (y - GRID_START_Y) // CELL_SIZE_H
        return None

    def _is_cell_occupied(self, grid_pos):
        col, row = grid_pos
        center_x = GRID_START_X + col * CELL_SIZE_W + CELL_SIZE_W / 2
        center_y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        return any(d.alive() and d.rect.collidepoint(center_x, center_y) for d in self.defenders)

    def _place_defender(self, grid_pos):
        if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
        col, row = grid_pos
        x = GRID_START_X + col * CELL_SIZE_W + CELL_SIZE_W / 2;
        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        groups = (self.all_sprites, self.defenders);
        defender_type = self.selected_defender
        data = DEFENDERS_DATA[defender_type].copy();
        data['type'] = defender_type

        if defender_type in self.upgrades:
            upgraded_stats = self.upgrades[defender_type]
            for stat_name in upgraded_stats:
                upgrade_info = DEFENDERS_DATA[defender_type]['upgrades'][stat_name]
                data[stat_name] += upgrade_info['value']

        unit_map = {'programmer': ProgrammerBoy, 'botanist': BotanistGirl, 'coffee_machine': CoffeeMachine,
                    'activist': Activist, 'guitarist': Guitarist, 'medic': Medic, 'artist': Artist,
                    'modnik': Fashionista}
        constructor = unit_map[defender_type];
        common_args = {'x': x, 'y': y, 'groups': groups, 'data': data}
        specific_args = {'programmer': {'all_sprites': self.all_sprites, 'projectile_group': self.projectiles,
                                        'enemies_group': self.enemies},
                         'botanist': {'all_sprites': self.all_sprites, 'enemies_group': self.enemies},
                         'coffee_machine': {'all_sprites': self.all_sprites, 'coffee_bean_group': self.coffee_beans},
                         'guitarist': {'all_sprites': self.all_sprites, 'enemies_group': self.enemies},
                         'medic': {'defenders_group': self.defenders},
                         'artist': {'all_sprites': self.all_sprites, 'projectile_group': self.projectiles,
                                    'enemies_group': self.enemies},
                         'modnik': {'all_sprites': self.all_sprites, 'enemies_group': self.enemies}}
        all_args = {**common_args, **specific_args.get(defender_type, {})};
        defender = constructor(**all_args)
        if defender_type in self.upgrades: defender.is_upgraded = True

    def update(self):
        now = pygame.time.get_ticks()
        enemies_before_update = len(self.enemies)
        self.all_sprites.update(self.defenders, self.all_sprites, self.projectiles, enemies_group=self.enemies)
        self.apply_auras();
        self.check_collisions()
        self._check_calamity_triggers(now)

        enemies_after_update = len(self.enemies)
        killed_this_frame = enemies_before_update - enemies_after_update
        for _ in range(killed_this_frame): self.level_manager.enemy_killed()
        self.level_manager.update()

        for enemy in list(self.enemies):
            if enemy.alive() and enemy.rect.right < GRID_START_X:
                mower_activated = False
                for mower in self.neuro_mowers:
                    if mower.rect.centery == enemy.rect.centery and not mower.is_active:
                        enemies_before_activation = set(self.enemies.sprites())
                        mower.activate(self.enemies)
                        if mower.mower_type == 'chat_gpt':
                            enemy.kill()
                        enemies_after_activation = set(self.enemies.sprites())
                        killed_by_mower = len(enemies_before_activation - enemies_after_activation)
                        for _ in range(killed_by_mower):
                            self.level_manager.enemy_killed()
                        mower_activated = True
                        break
                if not mower_activated: self.is_game_over = True; return

        if self.calamity_notification and now > self.calamity_notification_timer: self.calamity_notification = None
        if self.active_calamity and now > self.calamity_end_time: self._end_calamity()

    def _check_calamity_triggers(self, now):
        if self.active_calamity: return
        spawn_progress = self.level_manager.get_spawn_progress()
        for trigger_point in self.calamity_triggers:
            if spawn_progress >= trigger_point:
                self.calamity_triggers.remove(trigger_point);
                self._trigger_random_calamity(now);
                break

    def _trigger_random_calamity(self, now):
        if not self.pending_calamities: return
        self.active_calamity = self.pending_calamities.pop()
        calamity_data = CALAMITIES_DATA[self.active_calamity]

        if SOUNDS.get('misfortune'): SOUNDS['misfortune'].play()

        self.calamity_notification = {'name': calamity_data['display_name'], 'desc': calamity_data['description']}
        self.calamity_notification_timer = now + self.notification_duration
        self.calamity_end_time = now + self.calamity_duration

        if self.active_calamity == 'big_party':
            heroes_to_consider = [d for d in self.defenders if d.alive() and not isinstance(d, CoffeeMachine)]
            if heroes_to_consider:
                num_to_remove = int(len(heroes_to_consider) * 0.8)
                heroes_to_remove = random.sample(heroes_to_consider, k=min(num_to_remove, len(heroes_to_consider)))
                for hero in heroes_to_remove:
                    hero.kill()
            self.active_calamity = None
        else:
            for sprite in self.all_sprites:
                if hasattr(sprite, 'apply_calamity_effect'): sprite.apply_calamity_effect(self.active_calamity)

    def _end_calamity(self):
        if not self.active_calamity: return
        for sprite in self.all_sprites:
            if hasattr(sprite, 'revert_calamity_effect'): sprite.revert_calamity_effect(self.active_calamity)
        self.active_calamity = None

    def check_collisions(self):
        professors = [e for e in self.enemies if isinstance(e, StuffyProf) and e.alive()]

        for proj in list(self.projectiles):
            if not proj.alive(): continue

            if not isinstance(proj, Integral):
                debuff = 1.0
                for prof in professors:
                    aura_rect = prof.rect.inflate(prof.data['radius'], prof.data['radius'])
                    if aura_rect.colliderect(proj.rect):
                        debuff = prof.data['debuff']
                        break

                hits = pygame.sprite.spritecollide(proj, self.enemies, False)
                if hits:
                    target = hits[0]
                    if target.alive():
                        if isinstance(proj, PaintSplat):
                            target.slow_down(proj.artist.data['slow_factor'], proj.artist.data['slow_duration'])
                        target.get_hit(proj.damage * debuff)
                        proj.kill()
            elif isinstance(proj, Integral):
                if pygame.sprite.spritecollide(proj, self.defenders, True):
                    proj.kill()

        for wave in [s for s in self.all_sprites if isinstance(s, SoundWave)]:
            for enemy in self.enemies:
                if wave.rect.colliderect(enemy.rect) and enemy not in wave.hit_enemies:
                    enemy.get_hit(wave.damage)
                    wave.hit_enemies.add(enemy)

        for mower in list(self.neuro_mowers):
            if not mower.is_active:
                if pygame.sprite.spritecollide(mower, self.enemies, False):
                    mower.activate(self.enemies)

    def apply_auras(self):
        for d in self.defenders:
            d.buff_multiplier = 1.0

        for activist in [s for s in self.defenders if isinstance(s, Activist) and s.alive()]:
            for defender in self.defenders:
                if pygame.math.Vector2(activist.rect.center).distance_to(defender.rect.center) < activist.data['radius']:
                    defender.buff_multiplier *= activist.data['buff']

    def draw(self, surface):
        self.draw_world(surface)
        self.ui_manager.draw_shop(surface, self.selected_defender, self.coffee)
        spawn_progress = self.level_manager.get_spawn_progress()
        kill_progress = self.level_manager.get_kill_progress()
        spawn_data = self.level_manager.get_spawn_count_data()
        kill_data = self.level_manager.get_kill_count_data()
        self.ui_manager.draw_hud(surface, spawn_progress, kill_progress, spawn_data, kill_data,
                                 self.calamity_notification)

    def draw_world(self, surface):
        surface.blit(load_image('background.png', DEFAULT_COLORS['background'], (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        self.ui_manager.draw_grid(surface)

        sprites_to_draw = sorted(self.all_sprites, key=lambda s: s.rect.bottom)
        for sprite in sprites_to_draw:
            if hasattr(sprite, 'draw_aura'): sprite.draw_aura(surface)
            if hasattr(sprite, 'draw'):
                sprite.draw(surface)
            else:
                surface.blit(sprite.image, sprite.rect)