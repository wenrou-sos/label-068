import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT,
    SEASONS, SEASON_COLORS, SEASON_DURATION,
    FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_TITLE,
    DARK_GREEN, LIGHT_GREEN, BROWN, PURPLE, BLACK,
    GOLD, GREEN, YELLOW, RED, WHITE, LIGHT_BROWN
)


def draw_background(screen, camera_x, camera_y, season_index):
    season = SEASONS[season_index % 4]
    base_color = SEASON_COLORS[season]
    screen.fill(base_color)

    grass_color = (
        DARK_GREEN
        if season == "夏"
        else (
            (180, 160, 80)
            if season == "秋"
            else (200, 220, 200) if season == "冬" else LIGHT_GREEN
        )
    )

    for gx in range(0, WORLD_WIDTH, 40):
        for gy in range(0, WORLD_HEIGHT, 40):
            sx = gx - camera_x
            sy = gy - camera_y
            if -40 < sx < SCREEN_WIDTH + 40 and -40 < sy < SCREEN_HEIGHT + 40:
                offset = (gx + gy) % 20
                pygame.draw.circle(screen, grass_color, (sx + offset, sy + offset), 3)


def draw_hud(screen, hive, bee, season_index, season_timer, day_count, hornets, flowers, camera_x, camera_y):
    honey_text = FONT_SMALL.render(f"🍯 蜂蜜: {int(hive.honey)}", True, BROWN)
    pollen_text = FONT_SMALL.render(f"🌸 花粉: {int(hive.beebread)}", True, PURPLE)
    score_text = FONT_MEDIUM.render(f"得分: {hive.get_score()}", True, BLACK)
    season = SEASONS[season_index % 4]
    season_text = FONT_MEDIUM.render(f"第{day_count}天 · {season}", True, BLACK)

    screen.blit(honey_text, (10, 10))
    screen.blit(pollen_text, (10, 32))
    screen.blit(score_text, (10, 56))
    screen.blit(season_text, (SCREEN_WIDTH - 160, 10))

    season_pct = season_timer / SEASON_DURATION
    bar_w = 140
    bar_h = 8
    bx = SCREEN_WIDTH - 160
    by = 45
    pygame.draw.rect(screen, BLACK, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
    pygame.draw.rect(screen, GOLD, (bx, by, int(bar_w * season_pct), bar_h))

    stamina_pct = bee.stamina / bee.max_stamina
    stam_w = 200
    stam_h = 16
    sx = SCREEN_WIDTH // 2 - stam_w // 2
    sy = SCREEN_HEIGHT - 35
    pygame.draw.rect(screen, BLACK, (sx - 2, sy - 2, stam_w + 4, stam_h + 4))
    if stamina_pct > 0.3:
        color = GREEN
    elif stamina_pct > 0.15:
        color = YELLOW
    else:
        color = RED
    pygame.draw.rect(screen, color, (sx, sy, int(stam_w * stamina_pct), stam_h))
    stam_text = FONT_SMALL.render(f"体力 {int(bee.stamina)}", True, WHITE)
    screen.blit(stam_text, (sx + 6, sy + 1))

    nectar_pct = bee.nectar_carried / bee.max_nectar_carried
    nect_w = 100
    nect_h = 10
    nx = 10
    ny = SCREEN_HEIGHT - 30
    pygame.draw.rect(screen, BLACK, (nx - 1, ny - 1, nect_w + 2, nect_h + 2))
    pygame.draw.rect(screen, GOLD, (nx, ny, int(nect_w * nectar_pct), nect_h))
    nect_text = FONT_SMALL.render(f"携带花蜜 {int(bee.nectar_carried)}", True, BROWN)
    screen.blit(nect_text, (nx + nect_w + 8, ny - 2))

    pollen_carry_pct = bee.pollen_carried / bee.max_pollen_carried
    pol_w = 100
    pol_h = 10
    px = 10
    py = SCREEN_HEIGHT - 15
    pygame.draw.rect(screen, BLACK, (px - 1, py - 1, pol_w + 2, pol_h + 2))
    pygame.draw.rect(screen, PURPLE, (px, py, int(pol_w * pollen_carry_pct), pol_h))
    pol_text = FONT_SMALL.render(f"携带花粉 {int(bee.pollen_carried)}", True, PURPLE)
    screen.blit(pol_text, (px + pol_w + 8, py - 2))

    mini_size = 120
    mini_x = SCREEN_WIDTH - mini_size - 10
    mini_y = SCREEN_HEIGHT - mini_size - 10
    pygame.draw.rect(screen, BLACK, (mini_x - 2, mini_y - 2, mini_size + 4, mini_size + 4))
    pygame.draw.rect(screen, LIGHT_GREEN, (mini_x, mini_y, mini_size, mini_size))

    hive_mx = mini_x + int(hive.x / WORLD_WIDTH * mini_size)
    hive_my = mini_y + int(hive.y / WORLD_HEIGHT * mini_size)
    pygame.draw.circle(screen, BROWN, (hive_mx, hive_my), 4)

    for flower in flowers:
        if not flower.wilted:
            fx = mini_x + int(flower.x / WORLD_WIDTH * mini_size)
            fy = mini_y + int(flower.y / WORLD_HEIGHT * mini_size)
            screen.set_at((fx, fy), flower.color)

    for hornet in hornets:
        hx = mini_x + int(hornet.x / WORLD_WIDTH * mini_size)
        hy = mini_y + int(hornet.y / WORLD_HEIGHT * mini_size)
        pygame.draw.circle(screen, RED, (hx, hy), 2)

    bee_mx = mini_x + int(bee.x / WORLD_WIDTH * mini_size)
    bee_my = mini_y + int(bee.y / WORLD_HEIGHT * mini_size)
    pygame.draw.circle(screen, YELLOW, (bee_mx, bee_my), 3)
    pygame.draw.circle(screen, BLACK, (bee_mx, bee_my), 1)


def draw_menu(screen):
    title = FONT_TITLE.render("🐝 蜜蜂采蜜模拟器 🌸", True, BROWN)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))

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
        screen.blit(text, (SCREEN_WIDTH // 2 - 180, y))
        y += 24


def draw_gameover(screen, game_over_reason, total_honey, flowers_pollinated_total, day_count, final_score):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    if game_over_reason == "death":
        title_text = "💀 蜜蜂坠亡了..."
        title_color = RED
    else:
        title_text = "🌙 一年结束了"
        title_color = GOLD

    title = FONT_LARGE.render(title_text, True, title_color)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

    rank, rank_msg = _get_rank(final_score, day_count)

    rank_title = FONT_LARGE.render(f"评级: {rank}", True, GOLD)
    screen.blit(rank_title, (SCREEN_WIDTH // 2 - rank_title.get_width() // 2, 150))

    rank_msg_surf = FONT_MEDIUM.render(rank_msg, True, WHITE)
    screen.blit(rank_msg_surf, (SCREEN_WIDTH // 2 - rank_msg_surf.get_width() // 2, 200))

    stats = [
        f"🍯 产蜜总量: {int(total_honey)}",
        f"🌸 授粉花朵数: {int(flowers_pollinated_total)}",
        f"📅 存活天数: {day_count} 天",
        f"⭐ 最终得分: {final_score}",
    ]

    y = 270
    for stat in stats:
        text = FONT_MEDIUM.render(stat, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
        y += 40

    hint = FONT_SMALL.render("按 空格键 或 回车 返回主菜单", True, (200, 200, 200))
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50))


def _get_rank(score, days):
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
