import pygame
from pygame.math import Vector2
from utils import get_mask_rect
import math


class Weapon(pygame.sprite.Sprite):
    def __init__(self, game, damage, name, width, *groups):
        super().__init__(*groups)
        self.width = width
        self.damage = damage
        self.name = name
        self.blade_length = int(width)
        self.original_image = None
        self.image = None
        self.mask = None
        self.rect = None
        self.rect_mask = None
        self.hitbox = None
        self.game = game
        self.image_size = (16, 108)
        self.load_image()
        self.angle = 0
        self.offset = Vector2(0, -50)
        self.angle_change_factor = 8.5 * 1.5
        self.counter = 0
        self.swing_side = 1

    def load_image(self):  # Change name of the function
        """Load weapon image and initialize instance variables"""
        self.original_image = pygame.image.load('../assets/weapon/' + self.name + '.png')
        self.original_image = pygame.transform.scale(self.original_image, self.image_size)
        self.mask = pygame.mask.from_surface(self.original_image)
        self.rect = self.mask.get_rect()
        self.rect_mask = get_mask_rect(self.original_image, *self.rect.topleft)
        self.hitbox = self.rect_mask
        self.image = self.original_image

    def collision(self, collision_obj):
        if self.rect_mask.colliderect(collision_obj.rect):
            collision_obj.assign_weapon(self)  # if collided, assigning weapon to player

    def attack_enemy(self, enemy):

        if self.rect_mask.colliderect(enemy.hitbox):
            pass

    def update_weapon_size(self):
        self.image_size = (75, 75)
        self.image_size = tuple(int(self.game.zoom_level * x) for x in self.image_size)

    def rotate(self):
        # mx, my = pygame.mouse.get_pos()
        #
        # mouse_vector = pygame.math.Vector2(pygame.mouse.get_pos())
        # player_center_vector = pygame.math.Vector2(self.game.player.hitbox.center)
        # dx = mx - self.rect.centerx
        # dy = my - self.rect.centery
        # self.angle = (300/math.pi) * math.atan2(-dy, dx)
        #
        # #dx, dy = pass
        # """Rotate the image around a pivot point."""
        # # Termination condition
        # if self.angle >= 180 or self.angle < 0:
        #     self.game.player.attacking = False
        #     self.angle = 0
        #     self.image = self.original_image.copy()
        #     self.rect = self.image.get_rect(
        #         center=self.game.player.hitbox.center + self.offset)  # offset to fit as close as possible
        #     self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)
        # else:
        #     # Different angle and position, depending on player's direction
        #     if self.game.player.direction in ("RIGHT", "UP", "DOWN"):
        #         angle = -self.angle
        #         position = self.game.player.hitbox.center
        #     else:
        #         angle = self.angle
        #         position = self.game.player.hitbox.center
        #     # Rotate the image.
        #     self.image = pygame.transform.rotozoom(self.original_image, angle, 1)
        #     # Rotate the offset vector.
        #     offset_rotated = self.offset.rotate(-angle)
        #     # Create a new rect with the center of the sprite + the offset.
        #     self.rect = self.image.get_rect(center=position + offset_rotated)
        #
        #     self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)
        #     # Update angle
        #     #self.angle += self.angle_change_factor/2
        #     # Update mask
        #     self.mask = pygame.mask.from_surface(self.image)
        mx, my = pygame.mouse.get_pos()
        dx = mx - self.game.player.hitbox.centerx
        dy = my - self.game.player.hitbox.centery
        if self.swing_side == 1:
            self.angle = (180 / math.pi) * math.atan2(-self.swing_side * dy, dx)
        else:
            self.angle = (180 / math.pi) * math.atan2(self.swing_side * dy, dx) - 200

        position = self.game.player.hitbox.center
        # Rotate the image.
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        # Rotate the offset vector.
        offset_rotated = self.offset.rotate(-self.angle)
        # Create a new rect with the center of the sprite + the offset.
        self.rect = self.image.get_rect(center=position + offset_rotated)

        self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)
        # Update mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        """Update weapon position and state"""
        # If player attacks with weapon, it rotates
        if self.counter == 10:
            self.game.player.attacking = False
            self.game.player.attacked = True
            self.counter = 0

        # Animation/mask hitbox
        if self.game.player.attacking and self.counter <= 10:
            self.angle += 20 * self.swing_side

            position = self.game.player.hitbox.center
            # Rotate the image.
            self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
            # Rotate the offset vector.
            offset_rotated = self.offset.rotate(-self.angle)
            # Create a new rect with the center of the sprite + the offset.
            self.rect = self.image.get_rect(center=position + offset_rotated)
            self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)
            # Update mask
            self.mask = pygame.mask.from_surface(self.image)
            self.counter += 1

        else:
            self.rotate()
            self.game.player.attacked = True

        # else, it just follows the player
        # else:
        #     if self.game.player.direction in ("RIGHT", "UP", "DOWN"):
        #         self.image = pygame.transform.flip(self.original_image.copy(), True, False)
        #         self.rect = self.image.get_rect(
        #             center=self.game.player.hitbox.center + self.offset)  # offset to fit as close as possible
        #         self.rect.bottomright = self.game.player.hitbox.center
        #     else:
        #         self.image = self.original_image.copy()
        #         offset_new = self.offset + Vector2(-10, 0)  # update offset
        #         self.rect = self.image.get_rect(
        #             center=self.game.player.hitbox.center + offset_new)
        #         self.rect.bottomleft = self.game.player.hitbox.center
        #
        #     self.image = pygame.transform.scale(self.image, self.image_size)
        #     self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)
        #     self.mask = pygame.mask.from_surface(self.image)
        # Draw hitbox and rect
        # pygame.draw.rect(self.game.screen, self.game.RED, self.rect_mask, 1)
        # pygame.draw.rect(self.game.screen, self.game.GREEN, self.rect, 1)
