import math
import random
import pygame
from config import (
    YELLOW, ORANGE, PURPLE, PINK,
    GOLD, DARK_GREEN
)


class Flower:
    TYPES = {
        "油菜": {"nectar": 30, "pollen": 10, "time": 3.0, "color": YELLOW, "restore": 0},
        "向日葵": {"nectar": 10, "pollen": 30, "time": 3.0, "color": ORANGE, "restore": 0},
        "薰衣草": {"nectar": 18, "pollen": 18, "time": 1.5, "color": PURPLE, "restore": 0},
        "三叶草": {"nectar": 8, "pollen": 5, "time": 2.0, "color": PINK, "restore": 20},
    }

    def __init__(self, x, y, flower_type):
        self.x = x
        self.y = y
        self.type = flower_type
        stats = self.TYPES[flower_type]
        self.max_nectar = stats["nectar"]
        self.nectar = stats["nectar"]
        self.pollen = stats["pollen"]
        self.collect_time = stats["time"]
        self.color = stats["color"]
        self.restore_stamina = stats["restore"]
        self.wilted = False
        self.respawn_timer = 0
        self.respawn_delay = random.uniform(8, 15)
        self.sway_offset = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.5, 1.5)

    def update(self, dt, respawn_mult=1.0):
        self.sway_offset += self.sway_speed * dt
        if self.wilted:
            self.respawn_timer += dt * respawn_mult
            if self.respawn_timer >= self.respawn_delay:
                self.respawn()

    def respawn(self):
        self.wilted = False
        self.nectar = self.max_nectar
        self.respawn_timer = 0
        self.type = random.choice(list(self.TYPES.keys()))
        stats = self.TYPES[self.type]
        self.max_nectar = stats["nectar"]
        self.pollen = stats["pollen"]
        self.collect_time = stats["time"]
        self.color = stats["color"]
        self.restore_stamina = stats["restore"]

    def collect(self, max_nectar_need, max_pollen_need):
        if self.wilted:
            return 0, 0, 0

        if max_nectar_need <= 0 and max_pollen_need <= 0:
            return 0, 0, 0

        if max_nectar_need <= 0:
            max_nectar_need = 1
        ratio_from_pollen = 0
        if max_pollen_need > 0 and self.pollen > 0:
            ratio_from_pollen = min(1.0, max_pollen_need / self.pollen)

        max_by_pollen = (self.max_nectar * ratio_from_pollen) if self.pollen > 0 else self.max_nectar
        max_collectible = min(self.nectar, max_nectar_need, max_by_pollen)
        if max_collectible <= 0:
            max_collectible = min(self.nectar, max_nectar_need)

        collected = max_collectible
        pollen_collected = (collected / self.max_nectar) * self.pollen if self.max_nectar > 0 else 0
        self.nectar -= collected
        if self.nectar <= 0:
            self.wilted = True
            self.respawn_timer = 0
        return collected, pollen_collected, self.restore_stamina

    def draw(self, surface, camera_x, camera_y):
        if self.wilted:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        sway = math.sin(self.sway_offset) * 2

        pygame.draw.rect(surface, DARK_GREEN, (sx - 2, sy, 4, 20))

        petal_color = self.color
        for i in range(5):
            angle = (i / 5) * math.pi * 2 + self.sway_offset * 0.1
            px = sx + int(math.cos(angle) * 6 + sway)
            py = sy - 8 + int(math.sin(angle) * 6)
            pygame.draw.circle(surface, petal_color, (px, py), 5)

        center_color = GOLD if self.type == "向日葵" else (255, 200, 50)
        pygame.draw.circle(surface, center_color, (sx + int(sway), sy - 8), 4)

        if self.nectar < self.max_nectar * 0.3:
            pygame.draw.circle(surface, (200, 200, 200), (sx + int(sway), sy - 8), 2)
