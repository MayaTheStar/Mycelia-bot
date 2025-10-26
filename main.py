# main.py 🌿Mycelia Bot v2
# Adds streaks, levels, and cozy encouragements

import discord
from discord.ext import commands
import os
import random
from datetime import date
from dotenv import load_dotenv
from actions import actions
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

# Cozy encouragement messages
encouragements = [
    "Keep growing strong! 🌱",
    "Tiny steps make a forest bloom 🌳",
    "You're making the world a little greener 🌍",
    "The earth smiles at your kindness 🌸",
    "Nature thanks you for your care 🌿",
    "Your small act creates big ripples 🌊",
    "Every action nurtures the planet 🌼"
]

# EVENTS
@bot.event
async def on_ready():
    print(f'🌿 Mycelia is online as {bot.user}!')
    await bot.change_presence(activity=discord.Game(name="👀 Fun Fact: My name comes from Mycelium! 🍄"))

# COMMANDS
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send("Haii there! I'm Mycelia, your cozy eco-companion 😊")

@bot.command(name='ecoaction')
async def ecoaction(ctx):
    if not actions:
        await ctx.send("🍁 No eco actions available right now.")
        return
    action = random.choice(actions)
    await ctx.send(f"🌎 Today's eco action:\n**{action}**")

@bot.command(name='log')
async def log_action(ctx):
    """Log an eco action and update streaks + XP."""
    user_id = str(ctx.author.id)
    data = load_data()
    today = str(date.today())

    # Create user entry if not found
    if user_id not in data:
        data[user_id] = {
            "xp": 0,
            "actions_completed": 0,
            "streak": 0,
            "last_log_date": None
        }

    user = data[user_id]
    last_log = user.get("last_log_date")

    # Prevent double logging in one day
    if last_log == today:
        await ctx.send("You already logged an action today 🌿 Come back tomorrow!")
        return

    # Streak logic with a grace period
    if last_log:
        last_date = date.fromisoformat(last_log)
        days_since_last = (date.today() - last_date).days

        if days_since_last == 1:
            # Logged yesterday --> normal streak continuation
            user["streak"] += 1
            streak_msg = "You're keeping the momentum going! 🌞"
        elif 2 <= days_since_last <= 3:
            # Grace period: missed 1-2 days --> streak continues
            user["streak"] += 1
            streak_msg = "🌛 You took a short rest, but your streak continues strong!"
        else:
            # Missed more than 2 days --> streak resets
            user["streak"] = 1
            streak_msg = "Welcome back! 🌿 Your new growth cycle begins today."
    else:
        # First-ever log
        user["streak"] = 1
        streak_msg = "Your eco-journey begins today! 🌱"

    # Update user stats
    user["last_log_date"] = today
    user["actions_completed"] += 1
    user["xp"] += 2

    save_data(data)

    # Determine current level
    level = get_level(user["xp"])

    # Random encouragement
    encouragement = random.choice(encouragements)

    # Send cozy message
    await ctx.send(
        f"+2 🌱 eco points!\n"
        f"{streak_msg}\n\n"
        f"You're on a **{user['streak']}-day streak** and have reached **{level}**!\n"
        f"Total actions completed: **{user['actions_completed']}** ✅\n\n"
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

# RUN BOT 🚀
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error starting bot: {e}")
