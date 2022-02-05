import math
import pygame
import random
from particles import EnemyHitParticle, WallHitParticle


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
        self.draw_surface = self.game.screen

    def calculate_dir(self):
        length = math.hypot(*self.dir)
        self.dir = (self.dir[0] / length, self.dir[1] / length)

    def load_image(self):
        self.image = pygame.Surface([self.bullet_size, self.bullet_size])
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()

    def update_position(self):
        self.pos = (self.pos[0] + self.dir[0] * self.speed,
                     self.pos[1] + self.dir[1] * self.speed)

        self.rect.x = self.pos[0] #
        self.rect.y = self.pos[1] #

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
        self.player_collision(self.game.player)
        self.bounce()
        if self.rect.y < 0 or self.rect.y > 1000 or self.rect.x < 0 or self.rect.x > 1200:
            self.kill()

    def draw(self):
        pygame.draw.circle(self.draw_surface, (255, 255, 255), (self.rect.x + self.radius / 2, self.rect.y + self.radius / 2),
                           self.radius)
        pygame.draw.circle(self.draw_surface, (58, 189, 74), (self.rect.x + self.radius / 2, self.rect.y + self.radius / 2),
                           self.radius - 1)

    def wall_collision(self):
        lower_boundary = ()
        upper_boundary = ()

    def player_collision(self, collision_enemy):
        if self.rect.colliderect(collision_enemy.hitbox):
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
    damage = 10
    bullet_size = 7
    radius = 5

    def __init__(self, game, master, room, x, y, target):
        super().__init__(game, master, room, x, y, target)


class StaffBullet(Bullet):
    pass


class BossBullet(Bullet):

    def __init__(self, rotation=None):
        if rotation:
            self.dir.rotate_ip(rotation)


class BulletManager:

    def __init__(self, game):
        self.game = game
        self.bullets = []

    def add_bullet(self, bullet):
        self.bullets.append(bullet)

    def update(self):
        for bullet in self.bullets:
            bullet.update()

    def draw(self):
        for bullet in self.bullets:
            bullet.draw()
