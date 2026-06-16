import math
import pygame
from config import (
    BLACK, YELLOW, GOLD, RED, GREEN,
    WORLD_WIDTH, WORLD_HEIGHT
)


class Bee:
    def __init__(self, x, y, upgrade_system):
        self.x = x
        self.y = y
        self.hive_x = x
        self.hive_y = y
        self.speed_base = 120
        self.speed = self.speed_base
        self.base_max_stamina = 100
        self.max_stamina = 100
        self.stamina = 100
        self.base_max_nectar = 50
        self.max_nectar_carried = 50
        self.nectar_carried = 0
        self.base_max_pollen = 40
        self.max_pollen_carried = 40
        self.pollen_carried = 0
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
        self.upgrade = upgrade_system
        self.apply_upgrades()

    def apply_upgrades(self):
        self.max_stamina = int(self.base_max_stamina * self.upgrade.get_stamina_mult())
        self.max_nectar_carried = int(self.base_max_nectar * self.upgrade.get_capacity_mult())
        self.max_pollen_carried = int(self.base_max_pollen * self.upgrade.get_capacity_mult())
        self.speed = self.speed_base * self.upgrade.get_speed_mult()

    def has_carry_space(self):
        space_n = self.max_nectar_carried - self.nectar_carried
        space_p = self.max_pollen_carried - self.pollen_carried
        return space_n > 0 or space_p > 0

    def update(self, dt, keys, flowers, hive, pesticides, hornets, weather=None):
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

        stamina_mult = weather.get_stamina_drain_mult() if weather else 1.0

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
                self.stamina -= 5 * stamina_mult * dt

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
                self.stamina -= 3 * stamina_mult * dt

        weather_speed = weather.get_speed_mult(self.angle) if weather else 1.0
        move_speed = self.speed * self.upgrade.get_speed_mult() * weather_speed * (0.6 if self.poisoned else 1.0)
        self.x += dx * move_speed * dt
        self.y += dy * move_speed * dt

        self.x = max(20, min(WORLD_WIDTH - 20, self.x))
        self.y = max(20, min(WORLD_HEIGHT - 20, self.y))

        if not self.collecting and not self.returning and self.has_carry_space():
            for flower in flowers:
                if not flower.wilted:
                    dist = math.sqrt((self.x - flower.x) ** 2 + (self.y - flower.y) ** 2)
                    if dist < 20:
                        self.collecting = True
                        self.collect_target = flower
                        self.collect_progress = 0
                        break

        if self.collecting and self.collect_target:
            if self.collect_target.wilted or not self.has_carry_space():
                self.collecting = False
                self.collect_target = None
            else:
                effective_time = self.collect_target.collect_time * self.upgrade.get_collect_speed_mult()
                self.collect_progress += dt
                self.stamina -= 2 * stamina_mult * dt
                if self.collect_progress >= effective_time:
                    space_n = self.max_nectar_carried - self.nectar_carried
                    space_p = self.max_pollen_carried - self.pollen_carried
                    nectar_got, pollen_got, restore = self.collect_target.collect(
                        space_n, space_p
                    )
                    actual_n = min(nectar_got, space_n)
                    actual_p = min(pollen_got, space_p)
                    self.nectar_carried += actual_n
                    self.pollen_carried += actual_p
                    self.stamina = min(self.max_stamina, self.stamina + restore)
                    if actual_n > 0 or actual_p > 0:
                        self.upgrade.add_exp(actual_n, actual_p)
                    self.collect_progress = 0
                    if (
                        self.nectar_carried >= self.max_nectar_carried
                        or self.pollen_carried >= self.max_pollen_carried
                        or not self.has_carry_space()
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
            effective_time = self.collect_target.collect_time * self.upgrade.get_collect_speed_mult()
            pct = self.collect_progress / effective_time
            pygame.draw.rect(surface, BLACK, (sx - bar_w // 2 - 1, sy - 18, bar_w + 2, bar_h + 2))
            pygame.draw.rect(surface, GOLD, (sx - bar_w // 2, sy - 17, int(bar_w * pct), bar_h))
