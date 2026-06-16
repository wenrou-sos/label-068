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
from game.ui import (
    draw_background, draw_hud, draw_menu,
    draw_gameover, draw_leaderboard, draw_name_input,
    draw_upgrade_panel
)
from leaderboard import load_leaderboard, add_entry, is_high_score
from upgrade import UpgradeSystem
from weather import WeatherSystem


MENU_ITEMS = ["开始游戏", "排行榜", "退出游戏"]


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("蜜蜂采蜜模拟器")
        self.clock = pygame.time.Clock()
        self.state = "menu"
        self.menu_selected = 0
        self.leaderboard_entries = []
        self.leaderboard_new_index = -1
        self.player_name = ""
        self.name_cursor_timer = 0
        self.name_cursor_visible = True
        self.final_score = 0
        self.final_rank = ""
        self.upgrade = UpgradeSystem()
        self.upgrade_selected = 0
        self.weather = WeatherSystem()
        self.reset()

    def reset(self):
        hive_x, hive_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
        self.hive = Hive(hive_x, hive_y)
        self.upgrade.reset()
        self.bee = Bee(hive_x, hive_y - 30, self.upgrade)

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
        self.upgrade_selected = 0
        self.weather = WeatherSystem()

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

    def _get_current_rank(self):
        from game.ui import _get_rank
        return _get_rank(self.final_score, self.day_count)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    self._handle_menu_input(event)
                elif self.state == "playing":
                    self._handle_playing_input(event)
                elif self.state == "upgrade_panel":
                    self._handle_upgrade_input(event)
                elif self.state == "gameover":
                    self._handle_gameover_input(event)
                elif self.state == "leaderboard":
                    self._handle_leaderboard_input(event)
                elif self.state == "name_input":
                    self._handle_name_input(event)

    def _handle_menu_input(self, event):
        if event.key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % len(MENU_ITEMS)
        elif event.key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % len(MENU_ITEMS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            choice = MENU_ITEMS[self.menu_selected]
            if choice == "开始游戏":
                self.state = "playing"
                self.reset()
            elif choice == "排行榜":
                self.state = "leaderboard"
                self.leaderboard_entries = load_leaderboard()
                self.leaderboard_new_index = -1
            elif choice == "退出游戏":
                pygame.quit()
                sys.exit()

    def _handle_playing_input(self, event):
        if event.key == pygame.K_SPACE:
            self.bee.quick_return()
        elif event.key == pygame.K_ESCAPE:
            self.state = "menu"
        elif event.key == pygame.K_u:
            self.state = "upgrade_panel"
            self.upgrade_selected = 0

    def _handle_upgrade_input(self, event):
        if event.key == pygame.K_UP:
            self.upgrade_selected = (self.upgrade_selected - 1) % 4
        elif event.key == pygame.K_DOWN:
            self.upgrade_selected = (self.upgrade_selected + 1) % 4
        elif event.key == pygame.K_RETURN:
            skill_keys = ["speed", "capacity", "stamina", "collect"]
            if self.upgrade.upgrade(skill_keys[self.upgrade_selected]):
                self.bee.apply_upgrades()
                if self.bee.stamina > self.bee.max_stamina:
                    self.bee.stamina = self.bee.max_stamina
        elif event.key in (pygame.K_u, pygame.K_ESCAPE):
            self.state = "playing"

    def _handle_gameover_input(self, event):
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if is_high_score(self.final_score):
                self.state = "name_input"
                self.player_name = ""
                self.name_cursor_timer = 0
                self.name_cursor_visible = True
                self.final_rank = self._get_current_rank()[0]
            else:
                self.state = "menu"

    def _handle_leaderboard_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.state = "menu"

    def _handle_name_input(self, event):
        if event.key == pygame.K_RETURN:
            name = self.player_name.strip()
            if not name:
                name = "无名蜂"
            self.leaderboard_entries, self.leaderboard_new_index = add_entry(
                name, self.final_score, self.day_count, self.final_rank
            )
            self.state = "leaderboard"
        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.state = "menu"
        else:
            if len(self.player_name) < 10:
                char = event.unicode
                if char and char.isprintable() and char != '\r' and char != '\n':
                    self.player_name += char

    def update(self, dt):
        if self.state == "name_input":
            self.name_cursor_timer += dt
            if self.name_cursor_timer >= 0.5:
                self.name_cursor_timer = 0
                self.name_cursor_visible = not self.name_cursor_visible

        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()

        score = self.hive.get_score()
        speed_bonus = min(score / 300, 1.5)
        self.bee.speed = self.bee.speed_base * (1 + speed_bonus * 0.5)

        self.bee.update(dt, keys, self.flowers, self.hive, self.pesticides, self.hornets, self.weather)

        respawn_mult = self.weather.get_flower_respawn_mult()
        for flower in self.flowers:
            flower.update(dt, respawn_mult)

        for pest in self.pesticides:
            pest.update(dt)

        for hornet in self.hornets:
            hornet.update(dt, self.bee, score)

        self.weather.update(dt, self.get_season())

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
            draw_menu(self.screen, self.menu_selected)
        elif self.state in ("playing", "upgrade_panel"):
            draw_background(self.screen, self.camera_x, self.camera_y, self.season_index)
            self._draw_world_objects()
            draw_hud(
                self.screen, self.hive, self.bee, self.upgrade,
                self.season_index, self.season_timer, self.day_count,
                self.hornets, self.flowers, self.camera_x, self.camera_y,
                self.weather
            )
            self.weather.draw_effects(self.screen)
            self.weather.draw_fog(self.screen)
            self.weather.draw_notification(self.screen)
            if self.state == "upgrade_panel":
                draw_upgrade_panel(self.screen, self.upgrade, self.upgrade_selected)
        elif self.state == "gameover":
            draw_background(self.screen, self.camera_x, self.camera_y, self.season_index)
            self._draw_world_objects()
            draw_gameover(
                self.screen, self.game_over_reason,
                self.total_honey, self.flowers_pollinated_total,
                self.day_count, self.final_score
            )
        elif self.state == "leaderboard":
            self.screen.fill(LIGHT_GREEN)
            draw_leaderboard(self.screen, self.leaderboard_entries, self.leaderboard_new_index)
        elif self.state == "name_input":
            draw_background(self.screen, self.camera_x, self.camera_y, self.season_index)
            self._draw_world_objects()
            draw_name_input(
                self.screen, self.player_name, self.name_cursor_visible,
                self.final_score, self.day_count, self.final_rank
            )

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_input()
            self.update(dt)
            self.draw()
