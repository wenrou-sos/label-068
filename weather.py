import random
import math
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT


WEATHER_SUNNY = "sunny"
WEATHER_RAINY = "rainy"
WEATHER_WINDY = "windy"
WEATHER_HOT = "hot"

WEATHER_INFO = {
    WEATHER_SUNNY: {"name": "☀️ 晴天", "desc": "天气晴朗"},
    WEATHER_RAINY: {"name": "🌧️ 下雨", "desc": "花朵恢复加快，视野模糊"},
    WEATHER_WINDY: {"name": "🌬️ 刮风", "desc": "逆风减速，顺风加速"},
    WEATHER_HOT: {"name": "🔥 高温", "desc": "体力消耗加快"},
}

SEASON_WEATHER_WEIGHTS = {
    "春": {WEATHER_SUNNY: 3, WEATHER_RAINY: 6, WEATHER_WINDY: 2, WEATHER_HOT: 1},
    "夏": {WEATHER_SUNNY: 2, WEATHER_RAINY: 2, WEATHER_WINDY: 1, WEATHER_HOT: 7},
    "秋": {WEATHER_SUNNY: 3, WEATHER_RAINY: 2, WEATHER_WINDY: 6, WEATHER_HOT: 1},
    "冬": {WEATHER_SUNNY: 5, WEATHER_RAINY: 1, WEATHER_WINDY: 3, WEATHER_HOT: 0},
}


class RainDrop:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(-50, 850)
        self.y = random.uniform(-50, -10)
        self.speed = random.uniform(300, 500)
        self.length = random.randint(8, 18)
        self.alpha = random.randint(80, 180)

    def update(self, dt, wind_dx=0):
        self.y += self.speed * dt
        self.x += wind_dx * 80 * dt
        if self.y > 620:
            self.reset()

    def draw(self, surface):
        end_y = int(self.y + self.length)
        color = (150, 180, 255, self.alpha)
        pygame_line = getattr(self, '_draw_line', None)
        start = (int(self.x), int(self.y))
        end = (int(self.x + 1), end_y)
        try:
            pygame.draw.line(surface, (150, 180, 255), start, end, 1)
        except Exception:
            pass


class WindLine:
    def __init__(self):
        self.reset()

    def reset(self, wind_angle=0):
        angle = wind_angle + random.uniform(-0.2, 0.2)
        self.angle = angle
        self.length = random.randint(30, 80)
        self.speed = random.uniform(200, 400)
        self.alpha = random.randint(60, 140)
        self.life = random.uniform(0.5, 1.5)
        self.max_life = self.life
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)

    def update(self, dt, wind_angle=0):
        self.angle = wind_angle + random.uniform(-0.1, 0.1)
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        self.life -= dt
        if self.life <= 0 or self.x < -100 or self.x > SCREEN_WIDTH + 100 or self.y < -100 or self.y > SCREEN_HEIGHT + 100:
            self.reset(wind_angle)

    def draw(self, surface):
        fade = max(0, self.life / self.max_life)
        alpha_val = int(self.alpha * fade)
        if alpha_val < 10:
            return
        start_x = int(self.x)
        start_y = int(self.y)
        end_x = int(self.x + math.cos(self.angle) * self.length)
        end_y = int(self.y + math.sin(self.angle) * self.length)
        pygame.draw.line(surface, (200, 200, 220), (start_x, start_y), (end_x, end_y), 1)


class HeatParticle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, 800)
        self.y = random.uniform(0, 600)
        self.speed = random.uniform(20, 60)
        self.amplitude = random.uniform(3, 8)
        self.freq = random.uniform(1, 3)
        self.phase = random.uniform(0, math.pi * 2)
        self.life = random.uniform(1, 3)
        self.max_life = self.life

    def update(self, dt):
        self.y -= self.speed * dt
        self.phase += self.freq * dt
        self.life -= dt
        if self.life <= 0 or self.y < -20:
            self.reset()

    def draw(self, surface):
        fade = max(0, self.life / self.max_life)
        wobble_x = int(self.x + math.sin(self.phase) * self.amplitude)
        alpha_val = int(80 * fade)
        if alpha_val < 5:
            return
        color = (255, min(255, 200 + int(55 * fade)), min(255, 150 + int(105 * fade)))
        pygame.draw.circle(surface, color, (wobble_x, int(self.y)), 2)


class WeatherSystem:
    def __init__(self):
        self.current = WEATHER_SUNNY
        self.timer = 0
        self.next_change = random.uniform(15, 30)
        self.notification = ""
        self.notification_timer = 0
        self.notification_duration = 3.0
        self.wind_angle = random.uniform(0, math.pi * 2)
        self.rain_drops = [RainDrop() for _ in range(80)]
        self.wind_lines = [WindLine() for _ in range(15)]
        self.heat_particles = [HeatParticle() for _ in range(40)]

    def update(self, dt, season):
        self.timer += dt
        if self.timer >= self.next_change:
            self.timer = 0
            self.next_change = random.uniform(15, 30)
            self._change_weather(season)

        if self.notification_timer > 0:
            self.notification_timer -= dt

        if self.current == WEATHER_WINDY:
            self.wind_angle += random.uniform(-0.3, 0.3) * dt
            self.wind_angle = self.wind_angle % (math.pi * 2)

        if self.current == WEATHER_RAINY:
            for drop in self.rain_drops:
                drop.update(dt)
        elif self.current == WEATHER_WINDY:
            for line in self.wind_lines:
                line.update(dt, self.wind_angle)
        elif self.current == WEATHER_HOT:
            for particle in self.heat_particles:
                particle.update(dt)

    def _change_weather(self, season):
        weights = SEASON_WEATHER_WEIGHTS.get(season, SEASON_WEATHER_WEIGHTS["春"])
        types = list(weights.keys())
        w = [weights[t] for t in types]
        total = sum(w)
        if total == 0:
            new_weather = WEATHER_SUNNY
        else:
            new_weather = random.choices(types, weights=w, k=1)[0]

        if new_weather != self.current:
            self.current = new_weather
            info = WEATHER_INFO[new_weather]
            self.notification = f"{info['name']} - {info['desc']}"
            self.notification_timer = self.notification_duration

            if new_weather == WEATHER_WINDY:
                self.wind_angle = random.uniform(0, math.pi * 2)

            if new_weather == WEATHER_RAINY:
                for drop in self.rain_drops:
                    drop.reset()
            elif new_weather == WEATHER_WINDY:
                for line in self.wind_lines:
                    line.reset(self.wind_angle)
            elif new_weather == WEATHER_HOT:
                for particle in self.heat_particles:
                    particle.reset()

    def get_speed_mult(self, bee_angle):
        if self.current != WEATHER_WINDY:
            return 1.0
        angle_diff = math.cos(bee_angle - self.wind_angle)
        return 1.0 + angle_diff * 0.35

    def get_stamina_drain_mult(self):
        if self.current == WEATHER_HOT:
            return 1.5
        return 1.0

    def get_flower_respawn_mult(self):
        if self.current == WEATHER_RAINY:
            return 2.0
        return 1.0

    def is_rainy(self):
        return self.current == WEATHER_RAINY

    def draw_effects(self, surface):
        if self.current == WEATHER_RAINY:
            for drop in self.rain_drops:
                drop.draw(surface)
        elif self.current == WEATHER_WINDY:
            for line in self.wind_lines:
                line.draw(surface)
        elif self.current == WEATHER_HOT:
            for particle in self.heat_particles:
                particle.draw(surface)

    def draw_fog(self, surface):
        if self.current != WEATHER_RAINY:
            return
        fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fog.fill((150, 170, 200, 50))
        surface.blit(fog, (0, 0))

    def draw_notification(self, surface):
        if self.notification_timer <= 0:
            return
        alpha = min(255, int(self.notification_timer / 0.5 * 255))
        if self.notification_timer > self.notification_duration - 0.5:
            alpha = int((self.notification_duration - (self.notification_duration - self.notification_timer)) / 0.5 * 255)
            alpha = min(255, max(0, alpha))

        font = pygame.font.SysFont("SimHei", 28)
        text = font.render(self.notification, True, (255, 255, 100))
        text.set_alpha(alpha)
        x = SCREEN_WIDTH // 2 - text.get_width() // 2
        y = 70
        bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, min(150, alpha)))
        surface.blit(bg, (x - 10, y - 5))
        surface.blit(text, (x, y))
