# main.py 🌿Mycelia Bot v2
# Adds streaks, levels, and cozy encouragements

import discord
from discord.ext import commands
import os
import random
from datetime import date
from dotenv import load_dotenv
from actions import actions
from encouragements import encouragements
from forest_visuals import get_forest_visual
from utils import load_data, save_data

# Load environment variables (token)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    raise ValueError("🚨 No DISCORD_TOKEN found in your .env file!")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Helper function for levels
def get_level(xp: int) -> str:
    """Return a level name based on XP."""
    if xp < 10:
        return "Seedling 🌱"
    elif xp < 25:
        return "Sprout 🌿"
    elif xp < 50:
        return "Sapling 🌳"
    elif xp < 100:
        return "Forest Guardian 🌲"
    else:
        return "Ancient Tree 🌼"

# EVENTS
@bot.event
async def on_ready():
    print(f'🌿 Mycelia is online as {bot.user}!')
    # Set bot's status as a custom bio line
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,  # or listening, etc.
            name="👀 Fun Fact: My name comes from Mycelium! 🍄"
        )
    )

# COMMANDS
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send("Haii there! I'm Mycelia, your cozy eco-companion 😊")

@bot.command(name='ecoaction')
async def ecoaction(ctx):
    """Assign a daily eco action to the user and give a mini progress preview."""
    user_id = str(ctx.author.id)
    data = load_data()
    today = str(date.today())

    if not actions:
        await ctx.send("🍁 No eco actions available right now.")
        return

    # Ensure user has a data entry
    if user_id not in data:
        data[user_id] = {
            "xp": 0,
            "actions_completed": 0,
            "streak": 0,
            "last_log_date": None,
            "co2_saved": 0.0,
            "pending_action": None,
            "pending_action_date": None
        }

    user = data[user_id]

    # Prevent overwriting a pending action
    if user.get("pending_action") and user.get("pending_action_date") == today:
        await ctx.send(
            f"🌎 You already have a pending action for today:\n"
            f"**{user['pending_action']['task']}**\n"
            "Complete it with `!log` to earn XP 🌱"
        )
        return

    # Pick a random action and save it as pending
    action = random.choice(actions)
    user["pending_action"] = action
    user["pending_action_date"] = today
    save_data(data)

    # Mini forest preview
    forest_preview = get_forest_visual(user["xp"], user["streak"])
    level = get_level(user["xp"])

    await ctx.send(
        f"🌎 Your eco action for today:\n**{action['task']}**\n\n"
        f"📊 Current progress:\n"
        f"- Level: **{level}**\n"
        f"- XP: **{user['xp']}**\n"
        f"- Streak: **{user['streak']} days**\n"
        f"- Actions completed: **{user['actions_completed']}**\n\n"
        f"🌲 Your forest so far:\n{forest_preview}\n\n"
        f"When you complete this action, log it with `!log` to earn XP and grow your forest 🌱"
    )

@bot.command(name='log')
async def log_action(ctx):
    """Log the pending eco action and update streaks, XP, and CO₂ saved."""
    user_id = str(ctx.author.id)
    data = load_data()
    today = str(date.today())

    # Check if user exists
    if user_id not in data:
        await ctx.send("❗ You need to request an action first with `!ecoaction`!")
        return

    user = data[user_id]
    action = user.get("pending_action")

    # Ensure there is a pending action
    if not action:
        await ctx.send("❗ You have no pending action! Use `!ecoaction` first 🌿")
        return

    # Prevent double logging
    last_log = user.get("last_log_date")
    if last_log == today:
        await ctx.send("You already logged an action today 🌿 Come back tomorrow!")
        return

    # Streak logic
    if last_log:
        last_date = date.fromisoformat(last_log)
        days_since_last = (date.today() - last_date).days

        if days_since_last == 1:
            user["streak"] += 1
            streak_msg = "You're keeping the momentum going! 🌞"
        elif 2 <= days_since_last <= 3:
            user["streak"] += 1
            streak_msg = "🌛 You took a short rest, but your streak continues strong!"
        else:
            user["streak"] = 1
            streak_msg = "Welcome back! 🌿 Your new growth cycle begins today."
    else:
        user["streak"] = 1
        streak_msg = "Your eco-journey begins today! 🌱"

    # Apply action effects
    task = action["task"]
    co2_saved = action["co2_saved"]
    user["co2_saved"] += co2_saved
    user["last_log_date"] = today
    user["actions_completed"] += 1
    user["xp"] += 2

    # Clear pending action
    user["pending_action"] = None
    user["pending_action_date"] = None

    # Save data
    save_data(data)

    forest_visual = get_forest_visual(user["xp"], user["streak"])
    level = get_level(user["xp"])
    encouragement = random.choice(encouragements)

    await ctx.send(
        f"🌿 You completed an eco action!\n"
        f"**{task}**\n\n"
        f"💨 You helped reduce **{co2_saved:.2f} kg CO₂** today!\n"
        f"Total saved so far: **{user['co2_saved']:.2f} kg CO₂** 🌍\n\n"
        f"+2 🌱 eco-points!\n"
        f"{streak_msg}\n\n"
        f"You're on a **{user['streak']}-day streak** and are now a **{level}**!\n\n"
        f"🌲 Your forest now looks like this:\n{forest_visual}\n\n"
        f"{encouragement}"
    )

@bot.command(name='profile')
async def profile(ctx):
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id not in data:
        await ctx.send("You haven't logged any eco actions yet! Use !ecoaction to start 🌱")
        return

    user = data[user_id]
    level = get_level(user["xp"])

    embed = discord.Embed(
        title=f"{ctx.author.name}'s Eco Profile 🌿",
        color=discord.Color.green()
    )
    embed.add_field(name="🌱 Level", value=level, inline=False)
    embed.add_field(name="✨ XP", value=user['xp'])
    embed.add_field(name="✅ Actions", value=user['actions_completed'])
    embed.add_field(name="🔥 Streak", value=f"{user['streak']} days")
    await ctx.send(embed=embed)

@bot.command(name='forest')
async def forest(ctx):
    """Show your current forest growth 🌳"""
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id not in data:
        await ctx.send("You haven't started your eco journey yet 🌱 Try `!log` first!")
        return

    user = data[user_id]
    forest_visual = get_forest_visual(user["xp"], user["streak"])
    level = get_level(user["xp"])

    embed = discord.Embed(
        title=f"{ctx.author.name}'s Living Forest 🌲",
        description=f"{forest_visual}\n\nLevel: **{level}**\n"
                    f"Streak: **{user['streak']} days**\n"
                    f"XP: **{user['xp']}**",
        color=discord.Color.green()
    )

    embed.set_footer(text="Tiny steps make your forest bloom 🌿")
    await ctx.send(embed=embed)

# RUN BOT 🚀
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error starting bot: {e}")
