import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# To load cogs
initial_extensions = ["cogs.general", "cogs.eco"]
for ext in initial_extensions:
    bot.load_extension(ext)

@bot.event
async def on_ready():
    print(f'🌿 Mycelia is online as {bot.user}!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="👀 Fun Fact: My name comes from Mycelium! 🍄"))

# 🚀 RUN BOT
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error starting bot: {e}")
