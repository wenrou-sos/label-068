import pygame
from config import (
    LIGHT_BROWN, BROWN, GOLD, BLACK
)


class Hive:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.honey = 0
        self.beebread = 0
        self.flowers_pollinated = 0

    def store_nectar(self, amount):
        self.honey += amount
        self.flowers_pollinated += 1

    def store_pollen(self, amount):
        self.beebread += amount

    def get_score(self):
        return int(self.honey + self.beebread * 2)

    def draw(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        pygame.draw.ellipse(surface, LIGHT_BROWN, (sx - 40, sy - 30, 80, 60))
        pygame.draw.ellipse(surface, BROWN, (sx - 35, sy - 25, 70, 50))

        for row in range(3):
            for col in range(5):
                hx = sx - 25 + col * 12
                hy = sy - 15 + row * 12
                pygame.draw.polygon(
                    surface,
                    GOLD,
                    [
                        (hx, hy),
                        (hx + 10, hy),
                        (hx + 12, hy + 6),
                        (hx + 10, hy + 12),
                        (hx, hy + 12),
                        (hx - 2, hy + 6),
                    ],
                    2,
                )

        pygame.draw.circle(surface, BLACK, (sx, sy + 15), 10)
        pygame.draw.circle(surface, (50, 30, 10), (sx, sy + 15), 7)
