import math
import random
import pygame
from config import (
    BLACK, RED, WORLD_WIDTH, WORLD_HEIGHT
)


class Hornet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed_base = 60
        self.speed = self.speed_base
        self.state = "wander"
        self.wander_angle = random.uniform(0, math.pi * 2)
        self.wander_timer = 0
        self.chase_timer = 0
        self.angle = 0

    def update(self, dt, bee, score):
        if bee.dead:
            self.state = "wander"

        speed_mult = 1 + min(score / 500, 2.0)
        self.speed = self.speed_base * speed_mult

        dist = math.sqrt((self.x - bee.x) ** 2 + (self.y - bee.y) ** 2)

        if self.state == "wander":
            if dist < 150 and not bee.dead:
                self.state = "chase"
                self.chase_timer = 0
            else:
                self.wander_timer += dt
                if self.wander_timer > 2:
                    self.wander_timer = 0
                    self.wander_angle += random.uniform(-math.pi / 2, math.pi / 2)

                self.angle = self.wander_angle
                self.x += math.cos(self.wander_angle) * self.speed * 0.5 * dt
                self.y += math.sin(self.wander_angle) * self.speed * 0.5 * dt

        elif self.state == "chase":
            if dist > 250 or bee.dead:
                self.state = "wander"
            else:
                dx = bee.x - self.x
                dy = bee.y - self.y
                self.angle = math.atan2(dy, dx)
                self.x += math.cos(self.angle) * self.speed * dt
                self.y += math.sin(self.angle) * self.speed * dt
                self.chase_timer += dt

        if self.x < 20 or self.x > WORLD_WIDTH - 20:
            self.wander_angle = math.pi - self.wander_angle
            self.x = max(20, min(WORLD_WIDTH - 20, self.x))
        if self.y < 20 or self.y > WORLD_HEIGHT - 20:
            self.wander_angle = -self.wander_angle
            self.y = max(20, min(WORLD_HEIGHT - 20, self.y))

    def draw(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        pygame.draw.ellipse(surface, (255, 180, 0), (sx - 10, sy - 6, 20, 12))
        pygame.draw.rect(surface, BLACK, (sx - 8, sy - 4, 4, 8))
        pygame.draw.rect(surface, BLACK, (sx + 4, sy - 4, 4, 8))

        head_x = sx + int(math.cos(self.angle) * 12)
        head_y = sy + int(math.sin(self.angle) * 6)
        pygame.draw.circle(surface, (40, 20, 0), (head_x, head_y), 5)

        pygame.draw.polygon(
            surface,
            BLACK,
            [
                (sx - int(math.cos(self.angle) * 10), sy - int(math.sin(self.angle) * 6)),
                (sx - int(math.cos(self.angle) * 18), sy - int(math.sin(self.angle) * 10)),
                (sx - int(math.cos(self.angle) * 10), sy - int(math.sin(self.angle) * 4)),
            ],
        )

        if self.state == "chase":
            pygame.draw.circle(surface, RED, (head_x - 3, head_y - 2), 2)
            pygame.draw.circle(surface, RED, (head_x + 3, head_y - 2), 2)
