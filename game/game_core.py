import random
import math
import sys
import pygame

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WORLD_WIDTH, WORLD_HEIGHT,
    SEASON_DURATION, SEASONS,
    LIGHT_GREEN
)
from entities import Bee, Hive, Flower, PesticideZone, Hornet
from game.ui import draw_background, draw_hud, draw_menu, draw_gameover


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("蜜蜂采蜜模拟器")
        self.clock = pygame.time.Clock()
        self.state = "menu"
        self.reset()

    def reset(self):
        hive_x, hive_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
        self.hive = Hive(hive_x, hive_y)
        self.bee = Bee(hive_x, hive_y - 30)

        self.flowers = []
        flower_types = ["油菜", "向日葵", "薰衣草", "三叶草"]
        weights = [3, 2, 2, 3]
        for _ in range(60):
            while True:
                fx = random.randint(50, WORLD_WIDTH - 50)
                fy = random.randint(50, WORLD_HEIGHT - 50)
                dist = math.sqrt((fx - hive_x) ** 2 + (fy - hive_y) ** 2)
                if dist > 80:
                    break
            ftype = random.choices(flower_types, weights=weights)[0]
            self.flowers.append(Flower(fx, fy, ftype))

        self.pesticides = []
        for _ in range(4):
            px = random.randint(100, WORLD_WIDTH - 100)
            py = random.randint(100, WORLD_HEIGHT - 100)
            self.pesticides.append(PesticideZone(px, py))

        self.hornets = []
        self.hornet_timer = 0
        self.hornet_spawn_interval = 20

        self.season_index = 0
        self.season_timer = 0
        self.day_count = 1
        self.total_honey = 0
        self.flowers_pollinated_total = 0
        self.camera_x = 0
        self.camera_y = 0
        self.score_for_speed = 0

    def get_season(self):
        return SEASONS[self.season_index % 4]

    def spawn_hornet(self):
        side = random.randint(0, 3)
        if side == 0:
            x, y = random.randint(0, WORLD_WIDTH), 0
        elif side == 1:
            x, y = random.randint(0, WORLD_WIDTH), WORLD_HEIGHT
        elif side == 2:
            x, y = 0, random.randint(0, WORLD_HEIGHT)
        else:
            x, y = WORLD_WIDTH, random.randint(0, WORLD_HEIGHT)
        self.hornets.append(Hornet(x, y))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.state = "playing"
                        self.reset()
                elif self.state == "playing":
                    if event.key == pygame.K_SPACE:
                        self.bee.quick_return()
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                elif self.state == "gameover":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.state = "menu"

    def update(self, dt):
        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()

        score = self.hive.get_score()
        speed_bonus = min(score / 300, 1.5)
        self.bee.speed = self.bee.speed_base * (1 + speed_bonus * 0.5)

        self.bee.update(dt, keys, self.flowers, self.hive, self.pesticides, self.hornets)

        for flower in self.flowers:
            flower.update(dt)

        for pest in self.pesticides:
            pest.update(dt)

        for hornet in self.hornets:
            hornet.update(dt, self.bee, score)

        self.hornet_timer += dt
        spawn_interval = max(8, self.hornet_spawn_interval - score / 100)
        max_hornets = min(8, 2 + score // 200)
        if self.hornet_timer >= spawn_interval and len(self.hornets) < max_hornets:
            self.hornet_timer = 0
            self.spawn_hornet()

        self.season_timer += dt
        if self.season_timer >= SEASON_DURATION:
            self.season_timer = 0
            self.season_index += 1
            if self.season_index % 4 == 0:
                self.day_count += 1

            if self.season_index >= 16:
                self.game_over("season_end")

        if self.bee.dead:
            self.game_over("death")

        self.camera_x = self.bee.x - SCREEN_WIDTH // 2
        self.camera_y = self.bee.y - SCREEN_HEIGHT // 2
        self.camera_x = max(0, min(WORLD_WIDTH - SCREEN_WIDTH, self.camera_x))
        self.camera_y = max(0, min(WORLD_HEIGHT - SCREEN_HEIGHT, self.camera_y))

    def game_over(self, reason):
        self.state = "gameover"
        self.game_over_reason = reason
        self.total_honey = self.hive.honey
        self.flowers_pollinated_total = self.hive.flowers_pollinated
        self.final_score = self.hive.get_score()

    def _draw_world_objects(self):
        for pest in self.pesticides:
            pest.draw(self.screen, self.camera_x, self.camera_y)

        for flower in self.flowers:
            flower.draw(self.screen, self.camera_x, self.camera_y)

        self.hive.draw(self.screen, self.camera_x, self.camera_y)

        for hornet in self.hornets:
            hornet.draw(self.screen, self.camera_x, self.camera_y)

        self.bee.draw(self.screen, self.camera_x, self.camera_y)

    def draw(self):
        if self.state == "menu":
            self.screen.fill(LIGHT_GREEN)
            draw_menu(self.screen)
        elif self.state == "playing":
            draw_background(self.screen, self.camera_x, self.camera_y, self.season_index)
            self._draw_world_objects()
            draw_hud(
                self.screen, self.hive, self.bee,
                self.season_index, self.season_timer, self.day_count,
                self.hornets, self.flowers, self.camera_x, self.camera_y
            )
        elif self.state == "gameover":
            draw_background(self.screen, self.camera_x, self.camera_y, self.season_index)
            self._draw_world_objects()
            draw_gameover(
                self.screen, self.game_over_reason,
                self.total_honey, self.flowers_pollinated_total,
                self.day_count, self.final_score
            )

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_input()
            self.update(dt)
            self.draw()
