import json
import os
from datetime import datetime


LEADERBOARD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard.json")
MAX_ENTRIES = 10


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, IOError):
        pass
    return []


def save_leaderboard(entries):
    entries = sorted(entries, key=lambda e: e.get("score", 0), reverse=True)
    entries = entries[:MAX_ENTRIES]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    return entries


def add_entry(name, score, day_count, rank_title):
    entries = load_leaderboard()
    entry = {
        "name": name,
        "score": score,
        "days": day_count,
        "rank": rank_title,
        "date": datetime.now().strftime("%Y-%m-%d"),
    }
    entries.append(entry)
    entries = save_leaderboard(entries)
    position = next(i for i, e in enumerate(entries) if e is entry) if entry in entries else -1
    for i, e in enumerate(entries):
        if e["name"] == name and e["score"] == score and e["date"] == entry["date"]:
            position = i
            break
    return entries, position


def is_high_score(score):
    entries = load_leaderboard()
    if len(entries) < MAX_ENTRIES:
        return True
    return score > entries[-1].get("score", 0)
