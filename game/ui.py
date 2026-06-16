import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT,
    SEASONS, SEASON_COLORS, SEASON_DURATION,
    FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_TITLE,
    DARK_GREEN, LIGHT_GREEN, BROWN, PURPLE, BLACK,
    GOLD, GREEN, YELLOW, RED, WHITE, LIGHT_BROWN, GRAY, BLUE
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


def draw_hud(screen, hive, bee, upgrade, season_index, season_timer, day_count, hornets, flowers, camera_x, camera_y, weather=None):
    honey_text = FONT_SMALL.render(f"🍯 蜂蜜: {int(hive.honey)}", True, BROWN)
    pollen_text = FONT_SMALL.render(f"🌸 花粉: {int(hive.beebread)}", True, PURPLE)
    score_text = FONT_MEDIUM.render(f"得分: {hive.get_score()}", True, BLACK)
    season = SEASONS[season_index % 4]
    season_text = FONT_MEDIUM.render(f"第{day_count}天 · {season}", True, BLACK)
    level_text = FONT_MEDIUM.render(f"Lv.{upgrade.level}", True, GOLD)
    sp_text = FONT_SMALL.render(f"技能点: {upgrade.skill_points}", True, RED if upgrade.skill_points > 0 else BLACK)

    screen.blit(honey_text, (10, 10))
    screen.blit(pollen_text, (10, 32))
    screen.blit(score_text, (10, 56))
    screen.blit(level_text, (130, 58))
    if upgrade.skill_points > 0:
        screen.blit(sp_text, (220, 62))
    screen.blit(season_text, (SCREEN_WIDTH - 160, 10))

    if weather:
        from weather import WEATHER_INFO
        w_info = WEATHER_INFO.get(weather.current, {})
        w_name = w_info.get("name", "")
        w_text = FONT_MEDIUM.render(w_name, True, WHITE)
        screen.blit(w_text, (SCREEN_WIDTH - 160, 65))

    exp_w = 120
    exp_h = 8
    exp_x = 130
    exp_y = 92
    exp_pct = upgrade.exp / upgrade.exp_for_next_level()
    pygame.draw.rect(screen, BLACK, (exp_x - 1, exp_y - 1, exp_w + 2, exp_h + 2))
    pygame.draw.rect(screen, BLUE, (exp_x, exp_y, int(exp_w * exp_pct), exp_h))
    exp_text = FONT_SMALL.render(f"EXP {upgrade.exp}/{upgrade.exp_for_next_level()}", True, BLACK)
    screen.blit(exp_text, (exp_x, exp_y + exp_h + 2))

    u_hint = FONT_SMALL.render("按 U 键升级", True, RED if upgrade.skill_points > 0 else GRAY)
    screen.blit(u_hint, (130, 112))

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


def draw_menu(screen, selected_index):
    title = FONT_TITLE.render("🐝 蜜蜂采蜜模拟器 🌸", True, BROWN)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    menu_items = ["开始游戏", "排行榜", "退出游戏"]

    start_y = 200
    for i, item in enumerate(menu_items):
        if i == selected_index:
            color = GOLD
            prefix = "▸ "
        else:
            color = BLACK
            prefix = "  "
        text = FONT_LARGE.render(f"{prefix}{item}", True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, start_y + i * 60))

    instructions = [
        "【操作说明】",
        "  方向键 / WASD — 移动蜜蜂",
        "  空格键 — 快速返回蜂巢",
        "  ESC — 返回主菜单",
        "",
        "【花朵类型】",
        "  🌼 油菜花 · 🌻 向日葵 · 💜 薰衣草 · 🍀 三叶草",
        "",
        "↑↓ 选择  回车 确认",
    ]

    y = 400
    for line in instructions:
        color = BROWN if line.startswith("【") else GRAY
        text = FONT_SMALL.render(line, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - 160, y))
        y += 22


def draw_leaderboard(screen, entries, new_entry_index=-1):
    title = FONT_LARGE.render("🏆 排行榜", True, GOLD)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

    header = FONT_MEDIUM.render("排名    名字          分数    天数   日期", True, BROWN)
    screen.blit(header, (80, 90))

    pygame.draw.line(screen, BROWN, (80, 120), (SCREEN_WIDTH - 80, 120), 2)

    if not entries:
        empty_text = FONT_MEDIUM.render("暂无记录，快来挑战吧！", True, GRAY)
        screen.blit(empty_text, (SCREEN_WIDTH // 2 - empty_text.get_width() // 2, 200))
    else:
        y = 135
        for i, entry in enumerate(entries[:10]):
            if i == new_entry_index:
                bg_rect = pygame.Rect(70, y - 5, SCREEN_WIDTH - 140, 38)
                pygame.draw.rect(screen, (60, 60, 30), bg_rect)
                pygame.draw.rect(screen, GOLD, bg_rect, 2)

            medal = ""
            if i == 0:
                medal = "🥇"
            elif i == 1:
                medal = "🥈"
            elif i == 2:
                medal = "🥉"

            name = entry.get("name", "???")
            score = entry.get("score", 0)
            days = entry.get("days", 1)
            date = entry.get("date", "-")
            rank_title = entry.get("rank", "")

            rank_str = f"{medal}{i + 1}" if medal else f"  {i + 1}"
            text_color = WHITE if i == new_entry_index else BLACK

            line = f"{rank_str}.   {name:<10s}   {score:>5d}    {days:>2d}天   {date}"
            row_text = FONT_MEDIUM.render(line, True, text_color)
            screen.blit(row_text, (90, y))

            if rank_title:
                rank_tag = FONT_SMALL.render(rank_title, True, GOLD)
                screen.blit(rank_tag, (580, y + 4))

            y += 42

    hint = FONT_SMALL.render("按 ESC 返回主菜单", True, GRAY)
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))


def draw_name_input(screen, player_name, cursor_visible, final_score, day_count, rank):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    title = FONT_LARGE.render("🎉 新纪录！", True, GOLD)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    score_text = FONT_MEDIUM.render(f"得分: {final_score}  存活: {day_count}天  评级: {rank}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 170))

    prompt = FONT_MEDIUM.render("请输入你的名字:", True, WHITE)
    screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 240))

    input_w = 300
    input_h = 50
    input_x = SCREEN_WIDTH // 2 - input_w // 2
    input_y = 290
    pygame.draw.rect(screen, WHITE, (input_x - 2, input_y - 2, input_w + 4, input_h + 4))
    pygame.draw.rect(screen, BLACK, (input_x, input_y, input_w, input_h))

    display_name = player_name
    if cursor_visible:
        display_name += "|"
    name_surf = FONT_LARGE.render(display_name, True, WHITE)
    screen.blit(name_surf, (input_x + 10, input_y + 8))

    hint = FONT_SMALL.render("回车确认  (名字为空则记为「无名蜂」)", True, (200, 200, 200))
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 360))


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

    hint = FONT_SMALL.render("按 空格键 或 回车 继续", True, (200, 200, 200))
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50))


def draw_upgrade_panel(screen, upgrade, selected_index):
    from upgrade import SKILL_TYPES

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    panel_w = 500
    panel_h = 420
    panel_x = SCREEN_WIDTH // 2 - panel_w // 2
    panel_y = SCREEN_HEIGHT // 2 - panel_h // 2

    pygame.draw.rect(screen, (60, 50, 30), (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, GOLD, (panel_x, panel_y, panel_w, panel_h), 3)

    title = FONT_LARGE.render("🐝 升级面板", True, GOLD)
    screen.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, panel_y + 20))

    sp_text = FONT_MEDIUM.render(f"可用技能点: {upgrade.skill_points}", True, GOLD if upgrade.skill_points > 0 else GRAY)
    screen.blit(sp_text, (panel_x + panel_w // 2 - sp_text.get_width() // 2, panel_y + 75))

    level_text = FONT_MEDIUM.render(f"当前等级: Lv.{upgrade.level}", True, WHITE)
    screen.blit(level_text, (panel_x + 30, panel_y + 75))

    skill_keys = ["speed", "capacity", "stamina", "collect"]
    y = panel_y + 130

    for i, key in enumerate(skill_keys):
        skill = SKILL_TYPES[key]
        level = upgrade.skills[key]
        can_up = upgrade.can_upgrade(key)
        is_selected = i == selected_index

        bg_color = (100, 90, 60) if is_selected else (70, 60, 40)
        border_color = GOLD if is_selected else (80, 70, 50)

        pygame.draw.rect(screen, bg_color, (panel_x + 30, y, panel_w - 60, 60))
        pygame.draw.rect(screen, border_color, (panel_x + 30, y, panel_w - 60, 60), 2)

        icon_text = FONT_LARGE.render(skill["icon"], True, WHITE)
        screen.blit(icon_text, (panel_x + 45, y + 10))

        name_text = FONT_MEDIUM.render(skill["name"], True, WHITE)
        screen.blit(name_text, (panel_x + 95, y + 8))

        desc_text = FONT_SMALL.render(skill["desc"], True, GRAY)
        screen.blit(desc_text, (panel_x + 95, y + 35))

        lvl_text = FONT_MEDIUM.render(f"Lv.{level}/{skill['max']}", True, GOLD)
        screen.blit(lvl_text, (panel_x + panel_w - 150, y + 15))

        if can_up:
            plus_text = FONT_LARGE.render("+", True, GOLD)
            screen.blit(plus_text, (panel_x + panel_w - 70, y + 10))
        else:
            max_text = FONT_SMALL.render("已满级" if level >= skill["max"] else "无点数", True, GRAY)
            screen.blit(max_text, (panel_x + panel_w - 80, y + 22))

        y += 70

    hint = FONT_SMALL.render("↑↓ 选择  回车 加点  U/ESC 关闭", True, (200, 200, 200))
    screen.blit(hint, (panel_x + panel_w // 2 - hint.get_width() // 2, panel_y + panel_h - 35))


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
