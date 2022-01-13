import pygame
import random
from map.map_generator import Room
from particles import DeathAnimation
from .entity import Entity


def draw_health_bar(surf, pos, size, border_c, back_c, health_c, progress):
    pygame.draw.rect(surf, back_c, (*pos, *size))
    pygame.draw.rect(surf, border_c, (*pos, *size), 1)
    inner_pos = (pos[0] + 1, pos[1] + 1)
    inner_size = ((size[0] - 2) * progress, size[1] - 2)
    rect = (round(inner_pos[0]), round(inner_pos[1]), round(inner_size[0]), round(inner_size[1]))
    pygame.draw.rect(surf, health_c, rect)


class Enemy(Entity):
    def __init__(self, game, speed, max_hp, room, name):
        Entity.__init__(self, game, name)
        self.max_hp = max_hp  # maximum hp
        self.hp = self.max_hp  # current hp
        self.room = room  # room in which monster resides
        self.speed = speed  # movement speed
        self.death_counter = 30
        self.spawn()

    def detect_collision(self):
        pass

    def spawn(self):
        self.rect.x = random.randint(250, 600)
        self.rect.y = random.randint(250, 600)

    def update(self):
        self.collision()
        if not self.dead and self.hp > 0:
            self.move()
        # self.wall_collision()
        if not self.dead and self.hp > 0:
            self.rect.move_ip(self.velocity)
            self.hitbox.move_ip(self.velocity)
        self.update_hitbox()
        self.entity_animation.update()
        self.can_move = True

    def move(self, dtick=0.06):
        if not self.dead and self.can_move:
            self.move_towards_player(self.game.player, dtick)  # zmiana

    def move_towards_player(self, player, dtick):
        dir_vector = pygame.math.Vector2(player.rect.bottomleft[0] - self.rect.x,
                                         player.rect.bottomleft[1] - 50 - self.rect.y)

        self.direction = 'left' if dir_vector[0] < 0 else 'right'
        if dir_vector.length_squared() > 0:
            dir_vector.normalize()
            dir_vector.scale_to_length(self.speed * 3 * dtick)
        self.set_velocity(dir_vector)

    def collision(self):
        if self.hp <= 0 and self.dead is False:
            self.dead = True
            self.entity_animation.animation_frame = 0
        if self.death_counter == 0:
            self.room.enemy_list.remove(self)
            position = (self.rect.x, self.rect.y)
            self.game.particle_manager.add_particle(DeathAnimation(self.game, *position))
            del self

    def draw_health(self, surf):
        if self.hp < self.max_hp:
            health_rect = pygame.Rect(0, 0, 20, 5)
            health_rect.midbottom = self.rect.centerx, self.rect.top
            health_rect.midbottom = self.rect.centerx, self.rect.top
            draw_health_bar(surf, health_rect.topleft, health_rect.size,
                            (1, 0, 0), (255, 0, 0), (0, 255, 0), self.hp / self.max_hp)

    def draw_shadow(self, surface):  # draw shadows before self.image for all entities
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((50, 50), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color, (0, 0, 15, 7))  # - self.animation_frame % 4
        shape_surf = pygame.transform.scale(shape_surf, (100, 100))
        position = [self.hitbox.bottomleft[0] - 1, self.hitbox.bottomleft[1] - 5]
        surface.blit(shape_surf, position)

    def draw(self, surface):  # if current room or the next room
        self.draw_shadow(self.room.tile_map.map_surface)
        self.room.tile_map.map_surface.blit(self.image, self.rect)
        self.draw_health(self.room.tile_map.map_surface)


class EnemyManager:
    def __init__(self, game):
        self.game = game
        self.enemy_list = []
        self.sprites = None
        self.time = 0

    def draw_enemies(self, surface):
        for enemy in self.game.world_manager.current_room.enemy_list:
            enemy.draw(surface)
        if self.game.world_manager.next_room:
            for enemy in self.game.world_manager.next_room.enemy_list:
                enemy.draw(surface)

    def set_enemy_list(self):
        self.enemy_list.clear()  # unnecessary to clear and repopulate list every loop, but no better idea for now
        for enemy in self.game.world_manager.current_room.enemy_list:
            self.enemy_list.append(enemy)

    def update_enemies(self):
        self.set_enemy_list()
        for enemy in self.game.world_manager.current_room.enemy_list:
            enemy.update()
        if self.game.world_manager.next_room:
            for enemy in self.game.world_manager.next_room.enemy_list:
                enemy.update()
        self.debug()
        self.check_collide()

    def check_collide(self):
        for enemy in self.enemy_list:
            if enemy.hitbox.colliderect(self.game.player.hitbox) and self.game.player.hurt is False:
                self.game.player.time = self.game.game_time
                self.game.player.hurt = True
            if (
                    self.game.player.weapon
                    and pygame.sprite.collide_mask(self.game.player.weapon, enemy)
                    and self.game.player.attacking
                    and self.game.game_time - enemy.time > 200
                    and enemy.dead is False
            ):
                enemy.time = self.game.game_time
                enemy.hurt = True
                enemy.hp -= self.game.player.weapon.damage

    def add_enemies(self):
        for row in self.game.world_manager.world.world:
            for room in row:
                if isinstance(room, Room) and room.type == 'normal':
                    room.enemy_list.append(Enemy(self.game, 15, 100, room, 'demon'))

    def debug(self):
        if pygame.mouse.get_pressed()[2] and pygame.time.get_ticks() - self.time > 100:
            self.time = pygame.time.get_ticks()
            mx, my = pygame.mouse.get_pos()
            mx -= 64  # because we are rendering player on map_surface
            my -= 32
            self.game.world_manager.current_room.enemy_list.append(
                Enemy(self.game, 15, 100, self.game.world_manager.current_room, 'demon'))
            self.game.world_manager.current_room.enemy_list[-1].rect.topleft = (mx, my)
