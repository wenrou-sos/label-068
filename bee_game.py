import pygame
import random
import math
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
RED = (220, 50, 50)
PURPLE = (147, 112, 219)
PINK = (255, 182, 193)
GREEN = (50, 180, 50)
DARK_GREEN = (30, 120, 30)
BROWN = (139, 90, 43)
LIGHT_BROWN = (205, 170, 125)
BLUE = (100, 149, 237)
GRAY = (128, 128, 128)
LIGHT_GREEN = (144, 238, 144)

SEASON_DURATION = 60
SEASONS = ["春", "夏", "秋", "冬"]
SEASON_COLORS = {
    "春": (144, 238, 144),
    "夏": (50, 180, 50),
    "秋": (210, 180, 140),
    "冬": (200, 220, 240),
}

FONT_SMALL = pygame.font.SysFont("SimHei", 16)
FONT_MEDIUM = pygame.font.SysFont("SimHei", 24)
FONT_LARGE = pygame.font.SysFont("SimHei", 40)
FONT_TITLE = pygame.font.SysFont("SimHei", 56)


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

    def update(self, dt):
        self.sway_offset += self.sway_speed * dt
        if self.wilted:
            self.respawn_timer += dt
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

    def collect(self, amount):
        if self.wilted:
            return 0, 0, 0
        collected = min(amount, self.nectar)
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


class Bee:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hive_x = x
        self.hive_y = y
        self.speed_base = 120
        self.speed = self.speed_base
        self.stamina = 100
        self.max_stamina = 100
        self.nectar_carried = 0
        self.max_nectar_carried = 50
        self.pollen_carried = 0
        self.max_pollen_carried = 40
        self.collecting = False
        self.collect_target = None
        self.collect_progress = 0
        self.angle = 0
        self.wing_frame = 0
        self.wing_timer = 0
        self.returning = False
        self.dead = False
        self.poisoned = False
        self.poison_timer = 0

    def update(self, dt, keys, flowers, hive, pesticides, hornets):
        if self.dead:
            return

        self.wing_timer += dt
        if self.wing_timer >= 0.05:
            self.wing_timer = 0
            self.wing_frame = (self.wing_frame + 1) % 2

        self.poisoned = False
        for pest in pesticides:
            if pest.active and self._in_circle(pest.x, pest.y, pest.radius):
                self.poisoned = True
                self.stamina -= 15 * dt
                break

        if self.poisoned:
            self.poison_timer += dt
        else:
            self.poison_timer = 0

        dx, dy = 0, 0
        if not self.collecting and not self.returning:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1

            if dx != 0 or dy != 0:
                length = math.sqrt(dx * dx + dy * dy)
                dx /= length
                dy /= length
                self.angle = math.atan2(dy, dx)
                self.stamina -= 5 * dt

        if self.returning:
            dx = self.hive_x - self.x
            dy = self.hive_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 20:
                self.returning = False
            else:
                dx /= dist
                dy /= dist
                self.angle = math.atan2(dy, dx)
                self.stamina -= 3 * dt

        move_speed = self.speed * (0.6 if self.poisoned else 1.0)
        self.x += dx * move_speed * dt
        self.y += dy * move_speed * dt

        world_w = 1600
        world_h = 1200
        self.x = max(20, min(world_w - 20, self.x))
        self.y = max(20, min(world_h - 20, self.y))

        if not self.collecting and not self.returning:
            for flower in flowers:
                if not flower.wilted:
                    dist = math.sqrt((self.x - flower.x) ** 2 + (self.y - flower.y) ** 2)
                    if dist < 20:
                        self.collecting = True
                        self.collect_target = flower
                        self.collect_progress = 0
                        break

        if self.collecting and self.collect_target:
            if self.collect_target.wilted:
                self.collecting = False
                self.collect_target = None
            else:
                self.collect_progress += dt
                self.stamina -= 2 * dt
                if self.collect_progress >= self.collect_target.collect_time:
                    nectar_got, pollen_got, restore = self.collect_target.collect(
                        self.collect_target.max_nectar
                    )
                    space_n = self.max_nectar_carried - self.nectar_carried
                    space_p = self.max_pollen_carried - self.pollen_carried
                    actual_n = min(nectar_got, space_n)
                    actual_p = min(pollen_got, space_p)
                    self.nectar_carried += actual_n
                    self.pollen_carried += actual_p
                    self.stamina = min(self.max_stamina, self.stamina + restore)
                    self.collect_progress = 0
                    if (
                        self.nectar_carried >= self.max_nectar_carried
                        or self.pollen_carried >= self.max_pollen_carried
                    ):
                        self.collecting = False
                        self.collect_target = None
                    elif self.collect_target.wilted:
                        self.collecting = False
                        self.collect_target = None

        dist_hive = math.sqrt((self.x - self.hive_x) ** 2 + (self.y - self.hive_y) ** 2)
        if dist_hive < 30:
            if self.nectar_carried > 0 or self.pollen_carried > 0:
                hive.store_nectar(self.nectar_carried)
                hive.store_pollen(self.pollen_carried)
                self.nectar_carried = 0
                self.pollen_carried = 0
            if self.stamina < self.max_stamina:
                self.stamina = min(self.max_stamina, self.stamina + 40 * dt)

        for hornet in hornets:
            dist = math.sqrt((self.x - hornet.x) ** 2 + (self.y - hornet.y) ** 2)
            if dist < 15:
                self.stamina -= 25 * dt

        if self.stamina <= 0:
            self.stamina = 0
            self.dead = True

    def _in_circle(self, cx, cy, r):
        return (self.x - cx) ** 2 + (self.y - cy) ** 2 < r * r

    def quick_return(self):
        if not self.dead:
            self.returning = True
            self.collecting = False
            self.collect_target = None

    def draw(self, surface, camera_x, camera_y):
        if self.dead:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if self.poisoned:
            flash = int(math.sin(self.poison_timer * 20) * 30) + 30
            pygame.draw.circle(surface, (0, 200, 0, 100), (sx, sy), 18 + flash // 3, 2)

        body_color = YELLOW
        if self.poisoned:
            body_color = (200, 255, 100)

        if self.wing_frame == 0:
            pygame.draw.ellipse(surface, (220, 240, 255), (sx - 8, sy - 10, 6, 12))
            pygame.draw.ellipse(surface, (220, 240, 255), (sx + 2, sy - 10, 6, 12))
        else:
            pygame.draw.ellipse(surface, (200, 230, 255), (sx - 10, sy - 8, 8, 10))
            pygame.draw.ellipse(surface, (200, 230, 255), (sx + 2, sy - 8, 8, 10))

        pygame.draw.ellipse(surface, body_color, (sx - 8, sy - 5, 16, 10))
        pygame.draw.rect(surface, BLACK, (sx - 6, sy - 3, 3, 6))
        pygame.draw.rect(surface, BLACK, (sx + 3, sy - 3, 3, 6))

        head_x = sx + int(math.cos(self.angle) * 10)
        head_y = sy + int(math.sin(self.angle) * 5)
        pygame.draw.circle(surface, BLACK, (head_x, head_y), 4)

        if self.collecting and self.collect_target:
            bar_w = 24
            bar_h = 4
            pct = self.collect_progress / self.collect_target.collect_time
            pygame.draw.rect(surface, BLACK, (sx - bar_w // 2 - 1, sy - 18, bar_w + 2, bar_h + 2))
            pygame.draw.rect(surface, GOLD, (sx - bar_w // 2, sy - 17, int(bar_w * pct), bar_h))


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

        world_w = 1600
        world_h = 1200
        if self.x < 20 or self.x > world_w - 20:
            self.wander_angle = math.pi - self.wander_angle
            self.x = max(20, min(world_w - 20, self.x))
        if self.y < 20 or self.y > world_h - 20:
            self.wander_angle = -self.wander_angle
            self.y = max(20, min(world_h - 20, self.y))

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


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("蜜蜂采蜜模拟器")
        self.clock = pygame.time.Clock()
        self.state = "menu"
        self.reset()

    def reset(self):
        world_w, world_h = 1600, 1200
        hive_x, hive_y = world_w // 2, world_h // 2
        self.hive = Hive(hive_x, hive_y)
        self.bee = Bee(hive_x, hive_y - 30)

        self.flowers = []
        flower_types = ["油菜", "向日葵", "薰衣草", "三叶草"]
        weights = [3, 2, 2, 3]
        for _ in range(60):
            while True:
                fx = random.randint(50, world_w - 50)
                fy = random.randint(50, world_h - 50)
                dist = math.sqrt((fx - hive_x) ** 2 + (fy - hive_y) ** 2)
                if dist > 80:
                    break
            ftype = random.choices(flower_types, weights=weights)[0]
            self.flowers.append(Flower(fx, fy, ftype))

        self.pesticides = []
        for _ in range(4):
            px = random.randint(100, world_w - 100)
            py = random.randint(100, world_h - 100)
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
        world_w, world_h = 1600, 1200
        side = random.randint(0, 3)
        if side == 0:
            x, y = random.randint(0, world_w), 0
        elif side == 1:
            x, y = random.randint(0, world_w), world_h
        elif side == 2:
            x, y = 0, random.randint(0, world_h)
        else:
            x, y = world_w, random.randint(0, world_h)
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
        world_w, world_h = 1600, 1200
        self.camera_x = max(0, min(world_w - SCREEN_WIDTH, self.camera_x))
        self.camera_y = max(0, min(world_h - SCREEN_HEIGHT, self.camera_y))

    def game_over(self, reason):
        self.state = "gameover"
        self.game_over_reason = reason
        self.total_honey = self.hive.honey
        self.flowers_pollinated_total = self.hive.flowers_pollinated
        self.final_score = self.hive.get_score()

    def get_rank(self):
        score = self.final_score
        days = self.day_count
        total = score + days * 50

        ranks = [
            ("蜂王传说", 3000, "🐝👑 你是传奇！"),
            ("黄金蜜蜂", 2000, "🏆 荣耀加身！"),
            ("采蜜大师", 1200, "🌟 技艺精湛！"),
            ("勤劳工蜂", 600, "💪 继续努力！"),
            ("见习蜜蜂", 200, "🍯 初露锋芒！"),
            ("工蜂新丁", 0, "🌸 多多加油！"),
        ]
        for rank, threshold, msg in ranks:
            if total >= threshold:
                return rank, msg
        return ranks[-1]

    def draw_background(self):
        season = self.get_season()
        base_color = SEASON_COLORS[season]
        self.screen.fill(base_color)

        world_w, world_h = 1600, 1200
        grass_color = (
            DARK_GREEN
            if season == "夏"
            else (
                (180, 160, 80)
                if season == "秋"
                else (200, 220, 200) if season == "冬" else LIGHT_GREEN
            )
        )

        for gx in range(0, world_w, 40):
            for gy in range(0, world_h, 40):
                sx = gx - self.camera_x
                sy = gy - self.camera_y
                if -40 < sx < SCREEN_WIDTH + 40 and -40 < sy < SCREEN_HEIGHT + 40:
                    offset = (gx + gy) % 20
                    pygame.draw.circle(self.screen, grass_color, (sx + offset, sy + offset), 3)

    def draw_hud(self):
        honey_text = FONT_SMALL.render(f"🍯 蜂蜜: {int(self.hive.honey)}", True, BROWN)
        pollen_text = FONT_SMALL.render(f"🌸 花粉: {int(self.hive.beebread)}", True, PURPLE)
        score_text = FONT_MEDIUM.render(f"得分: {self.hive.get_score()}", True, BLACK)
        season_text = FONT_MEDIUM.render(f"第{self.day_count}天 · {self.get_season()}", True, BLACK)

        self.screen.blit(honey_text, (10, 10))
        self.screen.blit(pollen_text, (10, 32))
        self.screen.blit(score_text, (10, 56))
        self.screen.blit(season_text, (SCREEN_WIDTH - 160, 10))

        season_pct = self.season_timer / SEASON_DURATION
        bar_w = 140
        bar_h = 8
        bx = SCREEN_WIDTH - 160
        by = 45
        pygame.draw.rect(self.screen, BLACK, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(self.screen, GOLD, (bx, by, int(bar_w * season_pct), bar_h))

        stamina_pct = self.bee.stamina / self.bee.max_stamina
        stam_w = 200
        stam_h = 16
        sx = SCREEN_WIDTH // 2 - stam_w // 2
        sy = SCREEN_HEIGHT - 35
        pygame.draw.rect(self.screen, BLACK, (sx - 2, sy - 2, stam_w + 4, stam_h + 4))
        if stamina_pct > 0.3:
            color = GREEN
        elif stamina_pct > 0.15:
            color = YELLOW
        else:
            color = RED
        pygame.draw.rect(self.screen, color, (sx, sy, int(stam_w * stamina_pct), stam_h))
        stam_text = FONT_SMALL.render(f"体力 {int(self.bee.stamina)}", True, WHITE)
        self.screen.blit(stam_text, (sx + 6, sy + 1))

        nectar_pct = self.bee.nectar_carried / self.bee.max_nectar_carried
        nect_w = 100
        nect_h = 10
        nx = 10
        ny = SCREEN_HEIGHT - 30
        pygame.draw.rect(self.screen, BLACK, (nx - 1, ny - 1, nect_w + 2, nect_h + 2))
        pygame.draw.rect(self.screen, GOLD, (nx, ny, int(nect_w * nectar_pct), nect_h))
        nect_text = FONT_SMALL.render(f"携带花蜜 {int(self.bee.nectar_carried)}", True, BROWN)
        self.screen.blit(nect_text, (nx + nect_w + 8, ny - 2))

        pollen_carry_pct = self.bee.pollen_carried / self.bee.max_pollen_carried
        pol_w = 100
        pol_h = 10
        px = 10
        py = SCREEN_HEIGHT - 15
        pygame.draw.rect(self.screen, BLACK, (px - 1, py - 1, pol_w + 2, pol_h + 2))
        pygame.draw.rect(self.screen, PURPLE, (px, py, int(pol_w * pollen_carry_pct), pol_h))
        pol_text = FONT_SMALL.render(f"携带花粉 {int(self.bee.pollen_carried)}", True, PURPLE)
        self.screen.blit(pol_text, (px + pol_w + 8, py - 2))

        mini_size = 120
        mini_x = SCREEN_WIDTH - mini_size - 10
        mini_y = SCREEN_HEIGHT - mini_size - 10
        pygame.draw.rect(self.screen, BLACK, (mini_x - 2, mini_y - 2, mini_size + 4, mini_size + 4))
        pygame.draw.rect(self.screen, LIGHT_GREEN, (mini_x, mini_y, mini_size, mini_size))
        mw, mh = 1600, 1200
        scale = mini_size / max(mw, mh)

        hive_mx = mini_x + int(self.hive.x * scale * (mini_size / (mw * scale)))
        hive_my = mini_y + int(self.hive.y * scale * (mini_size / (mh * scale)))
        pygame.draw.circle(self.screen, BROWN, (hive_mx, hive_my), 4)

        for flower in self.flowers:
            if not flower.wilted:
                fx = mini_x + int(flower.x / mw * mini_size)
                fy = mini_y + int(flower.y / mh * mini_size)
                self.screen.set_at((fx, fy), flower.color)

        for hornet in self.hornets:
            hx = mini_x + int(hornet.x / mw * mini_size)
            hy = mini_y + int(hornet.y / mh * mini_size)
            pygame.draw.circle(self.screen, RED, (hx, hy), 2)

        bee_mx = mini_x + int(self.bee.x / mw * mini_size)
        bee_my = mini_y + int(self.bee.y / mh * mini_size)
        pygame.draw.circle(self.screen, YELLOW, (bee_mx, bee_my), 3)
        pygame.draw.circle(self.screen, BLACK, (bee_mx, bee_my), 1)

    def draw_menu(self):
        title = FONT_TITLE.render("🐝 蜜蜂采蜜模拟器 🌸", True, BROWN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))

        instructions = [
            "【游戏目标】",
            "  控制小蜜蜂在花园中采集花蜜和花粉，",
            "  回到蜂巢酿蜜，获得尽可能高的分数！",
            "",
            "【操作说明】",
            "  方向键 / WASD — 移动蜜蜂",
            "  空格键 — 快速返回蜂巢",
            "  ESC — 返回主菜单",
            "",
            "【花朵类型】",
            "  🌼 油菜花 — 花蜜多，花粉少",
            "  🌻 向日葵 — 花蜜少，花粉多",
            "  💜 薰衣草 — 花蜜花粉中等，采得快",
            "  🍀 三叶草 — 花蜜少，能恢复体力",
            "",
            "【注意事项】",
            "  ⚠️ 避开绿色农药区域（持续掉体力）",
            "  🐝 小心红色马蜂（追上会扣体力）",
            "  体力耗尽会坠亡！及时回巢休息",
            "",
            "按 空格键 或 回车 开始游戏",
        ]

        y = 140
        for line in instructions:
            color = BLACK
            if line.startswith("【"):
                color = BROWN
            if line.startswith("按"):
                color = RED
            text = FONT_SMALL.render(line, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - 180, y))
            y += 24

    def draw_gameover(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        if self.game_over_reason == "death":
            title_text = "💀 蜜蜂坠亡了..."
            title_color = RED
        else:
            title_text = "🌙 一年结束了"
            title_color = GOLD

        title = FONT_LARGE.render(title_text, True, title_color)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        rank, rank_msg = self.get_rank()

        rank_title = FONT_LARGE.render(f"评级: {rank}", True, GOLD)
        self.screen.blit(rank_title, (SCREEN_WIDTH // 2 - rank_title.get_width() // 2, 150))

        rank_msg_surf = FONT_MEDIUM.render(rank_msg, True, WHITE)
        self.screen.blit(rank_msg_surf, (SCREEN_WIDTH // 2 - rank_msg_surf.get_width() // 2, 200))

        stats = [
            f"🍯 产蜜总量: {int(self.total_honey)}",
            f"🌸 授粉花朵数: {int(self.flowers_pollinated_total)}",
            f"📅 存活天数: {self.day_count} 天",
            f"⭐ 最终得分: {self.final_score}",
        ]

        y = 270
        for stat in stats:
            text = FONT_MEDIUM.render(stat, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 40

        hint = FONT_SMALL.render("按 空格键 或 回车 返回主菜单", True, (200, 200, 200))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50))

    def draw(self):
        if self.state == "menu":
            self.screen.fill(LIGHT_GREEN)
            self.draw_menu()
        elif self.state == "playing":
            self.draw_background()

            for pest in self.pesticides:
                pest.draw(self.screen, self.camera_x, self.camera_y)

            for flower in self.flowers:
                flower.draw(self.screen, self.camera_x, self.camera_y)

            self.hive.draw(self.screen, self.camera_x, self.camera_y)

            for hornet in self.hornets:
                hornet.draw(self.screen, self.camera_x, self.camera_y)

            self.bee.draw(self.screen, self.camera_x, self.camera_y)

            self.draw_hud()
        elif self.state == "gameover":
            self.draw_background()
            for pest in self.pesticides:
                pest.draw(self.screen, self.camera_x, self.camera_y)
            for flower in self.flowers:
                flower.draw(self.screen, self.camera_x, self.camera_y)
            self.hive.draw(self.screen, self.camera_x, self.camera_y)
            for hornet in self.hornets:
                hornet.draw(self.screen, self.camera_x, self.camera_y)
            self.bee.draw(self.screen, self.camera_x, self.camera_y)
            self.draw_gameover()

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_input()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    game = Game()
    game.run()
