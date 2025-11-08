import json
import os
import random
from actions import actions

DATA_FILE = "data.json"
MAX_RECENT = 5  # How many recent actions to remember per user

def load_data():
    """Load user data from JSON file, or return empty dict if file missing/corrupted."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    """Save user data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def select_action(user_id, data):
    """
    Select a new eco action for the user, avoiding recently done actions.
    Updates the user's recent actions list in-memory.
    """
    # Ensure the user has a recent_actions list
    user = data[user_id]
    if "recent_actions" not in user:
        user["recent_actions"] = []
    recent = user["recent_actions"]

    # Choose actions that are not in recent
    available_actions = [a for a in actions if a["task"] not in recent]

    # If all actions are recently done, allow any action
    if not available_actions:
        available_actions = actions

    # Pick a random action
    action = random.choice(available_actions)

    # Update recent_actions list
    recent.append(action["task"])
    if len(recent) > MAX_RECENT:
        recent.pop(0)  # keep only the last MAX_RECENT actions

    return action
