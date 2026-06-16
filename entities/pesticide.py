import math
import random
import pygame


class PesticideZone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(40, 80)
        self.active = False
        self.timer = 0
        self.on_duration = random.uniform(5, 10)
        self.off_duration = random.uniform(8, 15)
        self.phase = "off"

    def update(self, dt):
        self.timer += dt
        if self.phase == "off" and self.timer >= self.off_duration:
            self.phase = "on"
            self.active = True
            self.timer = 0
            self.on_duration = random.uniform(5, 10)
        elif self.phase == "on" and self.timer >= self.on_duration:
            self.phase = "off"
            self.active = False
            self.timer = 0
            self.off_duration = random.uniform(8, 15)

    def draw(self, surface, camera_x, camera_y):
        if not self.active:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        color = (150, 200, 150)
        for i in range(3):
            r = self.radius - i * 15
            if r > 0:
                alpha_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(alpha_surf, (*color, 40 - i * 10), (r, r), r)
                surface.blit(alpha_surf, (sx - r, sy - r))

        drop_offset = self.timer * 30 % 30
        for i in range(5):
            angle = i * math.pi * 2 / 5 + self.timer
            dx = math.cos(angle) * self.radius * 0.7
            dy = math.sin(angle) * self.radius * 0.7 + (drop_offset % 10) - 5
            pygame.draw.circle(surface, (100, 180, 100), (int(sx + dx), int(sy + dy)), 3)
