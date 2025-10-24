# main.py 🌿 Mycelia Bot v2
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

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ----------------------------
# 🌿 Helper Functions
# ----------------------------

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

# ----------------------------
# 🌱 EVENTS
# ----------------------------

@bot.event
async def on_ready():
    print(f'🌿 Mycelia is online as {bot.user}!')

# ----------------------------
# 🌸 COMMANDS
# ----------------------------

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send("Haii there! I'm Mycelia, your cozy eco-companion. 🌱✨")

@bot.command(name='ecoaction')
async def ecoaction(ctx):
    if not actions:
        await ctx.send("No eco actions available right now. 🌿")
        return
    action = random.choice(actions)
    await ctx.send(f"🌎 Today's eco action:\n**{action}**")

@bot.command(name='log')
async def log_action(ctx):
    user_id = str(ctx.author.id)
    data = load_data()

    today = str(date.today())

    if user_id not in data:
        data[user_id] = {
            "xp": 0,
            "actions_completed": 0,
            "streak": 0,
            "last_log_date": None
        }

    user = data[user_id]
    last_log = user.get("last_log_date")

    # Check if user already logged today
    if last_log == today:
        await ctx.send("You already logged an action today 🌿 Come back tomorrow!")
        return

    # Streak logic
    if last_log:
        last_date = date.fromisoformat(last_log)
        if (date.today() - last_date).days == 1:
            user["streak"] += 1
        else:
            user["streak"] = 1
    else:
        user["streak"] = 1

    user["last_log_date"] = today
    user["actions_completed"] += 1
    user["xp"] += 2

    save_data(data)

    level = get_level(user["xp"])
    await ctx.send(
        f"+2 🌱 eco points!\n"
        f"You're on a **{user['streak']}-day streak** and have reached **{level}**!\n"
        f"Total actions: {user['actions_completed']} ✅"
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

# ----------------------------
# 🚀 RUN BOT
# ----------------------------

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error starting bot: {e}")
