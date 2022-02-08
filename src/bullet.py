import math
import pygame
import random
from particles import EnemyHitParticle, WallHitParticle, StaffParticle


class Bullet():
    def __init__(self, game, master, room, x, y, target):
        super().__init__()
        self.game = game
        self.master = master
        self.room = room
        self.image = None
        self.rect = None
        self.load_image()
        self.rect.x = x
        self.rect.y = y
        self.pos = (x, y)
        self.dir = pygame.math.Vector2(target[0] - x, target[1] - y)
        self.calculate_dir()
        self.bounce_back = True

    def calculate_dir(self):
        length = math.hypot(*self.dir)
        self.dir = pygame.math.Vector2(self.dir[0] / length, self.dir[1] / length)

    def set_damage(self, value):
        self.damage = value

    def load_image(self):
        self.image = pygame.Surface([self.bullet_size, self.bullet_size])
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()

    def update_position(self):
        self.pos = (self.pos[0] + self.dir[0] * self.speed,
                    self.pos[1] + self.dir[1] * self.speed)

        self.rect.x = self.pos[0]  #
        self.rect.y = self.pos[1]  #

    def kill(self):
        self.game.bullet_manager.bullets.remove(self)

    def update(self):
        self.update_position()
        if self.bounce_back is False:
            for enemy in self.game.enemy_manager.enemy_list:
                if self.rect.colliderect(enemy.hitbox):
                    enemy.hp -= self.damage
                    self.game.particle_manager.particle_list.append(
                        EnemyHitParticle(self.game, self.rect.x, self.rect.y))
                    self.kill()
                    break
        self.player_collision(self.game.player)
        self.bounce()
        if self.rect.y < 0 or self.rect.y > 1000 or self.rect.x < 0 or self.rect.x > 1300:
            self.kill()
        self.wall_collision()

    def draw(self):
        surface = self.master.room.tile_map.map_surface
        pygame.draw.circle(surface, (255, 255, 255), (self.rect.x + self.radius / 2, self.rect.y + self.radius / 2),
                           self.radius)
        pygame.draw.circle(surface, (58, 189, 74), (self.rect.x + self.radius / 2, self.rect.y + self.radius / 2),
                           self.radius - 1)

    def wall_collision(self):
        collide_points = (self.rect.midbottom, self.rect.bottomleft, self.rect.bottomright)
        for wall in self.game.world_manager.current_map.wall_list:
            if any(wall.hitbox.collidepoint(point) for point in collide_points):
                self.game.particle_manager.add_particle(WallHitParticle(self.game, self.rect.x, self.rect.y))
                self.kill()
                break

    def player_collision(self, collision_enemy):
        if self.rect.colliderect(collision_enemy.hitbox) and not self.game.world_manager.switch_room:
            if collision_enemy.shield:
                collision_enemy.shield -= 1
            else:
                self.game.player.hp -= self.damage
                self.game.player.hurt = True
            self.sparkle()
            self.kill()

    def sparkle(self):
        for _ in range(random.randint(2, 4)):
            self.game.particle_manager.particle_list.append(EnemyHitParticle(self.game, self.rect.x, self.rect.y))

    def bounce(self):
        if (
                self.game.player.weapon
                and self.game.player.attacking
                and pygame.sprite.collide_mask(self.game.player.weapon, self)
                and self.bounce_back
        ):
            self.dir = (-self.dir[0] + random.randint(-20, 10) / 100, -self.dir[1] + random.randint(-10, 10) / 100)
            self.speed *= random.randint(10, 20) / 10
            self.bounce_back = False


class ImpBullet(Bullet):
    speed = 5
    bullet_size = 7
    radius = 5

    def __init__(self, game, master, room, x, y, target):
        super().__init__(game, master, room, x, y, target)
        self.damage = master.damage




class StaffBullet(Bullet):
    speed = 9
    bullet_size = 12
    radius = 7

    def __init__(self, game, master, room, x, y, target):
        super().__init__(game, master, room, x, y, target)
        self.damage = 35 * self.game.player.strength
        self.bounce_back = False

    def sparkle(self):
        for _ in range(random.randint(2, 4)):
            self.game.particle_manager.particle_list.append(StaffParticle(self.game, self.rect.x, self.rect.y))

    def update(self):
        self.wall_collision()
        self.update_position()
        self.sparkle()
        if self.bounce_back is False:
            for enemy in self.game.enemy_manager.enemy_list:
                if self.rect.colliderect(enemy.hitbox):
                    enemy.hp -= self.damage
                    enemy.entity_animation.hurt_timer = pygame.time.get_ticks()
                    enemy.hurt = True
                    self.game.particle_manager.particle_list.append(
                        EnemyHitParticle(self.game, self.rect.x, self.rect.y))
                    self.kill()
                    break
        if self.rect.y < 0 or self.rect.y > 1000 or self.rect.x < 0 or self.rect.x > 1400:
            self.kill()

    def draw(self):
        surface = self.game.world_manager.current_map.map_surface
        pygame.draw.circle(surface, (255, 255, 255), (self.rect.x + self.radius / 2, self.rect.y + self.radius / 2),
                           self.radius)
        pygame.draw.circle(surface, (151, 218, 63), (self.rect.x + self.radius / 2, self.rect.y + self.radius / 2),
                           self.radius - 1)


class BossBullet(Bullet):
    speed = 7
    bullet_size = 7
    radius = 5

    def __init__(self, game, master, room, x, y, target, rotation=None):
        super().__init__(game, master, room, x, y, target)
        if rotation:
            self.dir.rotate_ip(rotation)
        self.damage = master.bullet_damage


class BulletManager:

    def __init__(self, game):
        self.game = game
        self.bullets = []

    def add_bullet(self, bullet):
        self.bullets.append(bullet)

    def kill(self, bullet):
        self.bullets.remove(bullet)

    def update(self):
        for bullet in self.bullets:
            bullet.update()

    def draw(self):
        for bullet in self.bullets:
            bullet.draw()
