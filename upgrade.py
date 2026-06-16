SKILL_TYPES = {
    "speed": {"name": "移动速度", "icon": "⚡", "desc": "每级+10% 移动速度", "max": 10},
    "capacity": {"name": "携带容量", "icon": "🎒", "desc": "每级+20% 花蜜/花粉容量", "max": 10},
    "stamina": {"name": "体力上限", "icon": "❤️", "desc": "每级+15% 体力上限", "max": 10},
    "collect": {"name": "采集速度", "icon": "🌼", "desc": "每级-10% 采集耗时", "max": 10},
}


class UpgradeSystem:
    def __init__(self):
        self.level = 1
        self.exp = 0
        self.skill_points = 0
        self.skills = {
            "speed": 0,
            "capacity": 0,
            "stamina": 0,
            "collect": 0,
        }

    def exp_for_next_level(self):
        return 50 + (self.level - 1) * 30

    def add_exp(self, nectar, pollen):
        exp_gained = int(nectar * 0.8 + pollen * 1.5)
        self.exp += exp_gained
        leveled_up = False
        while self.exp >= self.exp_for_next_level():
            self.exp -= self.exp_for_next_level()
            self.level += 1
            self.skill_points += 1
            leveled_up = True
        return exp_gained, leveled_up

    def get_speed_mult(self):
        return 1.0 + self.skills["speed"] * 0.1

    def get_capacity_mult(self):
        return 1.0 + self.skills["capacity"] * 0.2

    def get_stamina_mult(self):
        return 1.0 + self.skills["stamina"] * 0.15

    def get_collect_speed_mult(self):
        return 1.0 / (1.0 + self.skills["collect"] * 0.1)

    def can_upgrade(self, skill_key):
        return (
            self.skill_points > 0
            and skill_key in self.skills
            and self.skills[skill_key] < SKILL_TYPES[skill_key]["max"]
        )

    def upgrade(self, skill_key):
        if self.can_upgrade(skill_key):
            self.skills[skill_key] += 1
            self.skill_points -= 1
            return True
        return False

    def reset(self):
        self.level = 1
        self.exp = 0
        self.skill_points = 0
        for k in self.skills:
            self.skills[k] = 0
