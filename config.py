import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WORLD_WIDTH = 1600
WORLD_HEIGHT = 1200

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
