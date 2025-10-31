# Visual forest that grows with XP and streaks

def get_forest_visual(xp: int, streak: int) -> str:
    """
    Return a small visual forest representation based on XP and streak.
    """
    if xp < 10:
        return "🌱"
    elif xp < 25:
        return "🌱🌿"
    elif xp < 50:
        return "🌱🌿🌳"
    elif xp < 100:
        return "🌱🌿🌳🌲"
    else:
        trees = "🌱🌿🌳🌲🌼"
        bonus_trees = "🌳" * (streak // 5)
        return f"{trees}{bonus_trees}"
