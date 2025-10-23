import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv
from actions import actions
from utils import load_data, save_data

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🌿 Mycelia is online as {bot.user}!')

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send("Haii there! I'm Mycelia, your eco companion.🪴")

@bot.command(name='ecoaction')
async def ecoaction(ctx):
    action = random.choice(actions)
    await ctx.send(f"🌱 Today's eco action:\n**{action}**")

@bot.command(name='log')
async def log_action(ctx):
    user_id = str(ctx.author.id)
    data = load_data()

    # If user doesn’t exist yet, create an entry
    if user_id not in data:
        data[user_id] = {"xp": 0, "actions_completed": 0}

    # Update their stats
    data[user_id]["xp"] += 2
    data[user_id]["actions_completed"] += 1

    save_data(data)

    await ctx.send(f"+2 🌱 eco points! You've completed {data[user_id]['actions_completed']} actions total!")

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error starting bot: {e}")
        