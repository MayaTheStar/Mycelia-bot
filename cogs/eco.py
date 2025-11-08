
from discord.ext import commands
import discord
import random
from datetime import date
from actions import actions
from encouragements import encouragements
from forest_visuals import get_forest_visual
from utils import load_data, save_data

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

class Eco(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ecoaction')
    async def ecoaction(self, ctx):
        """Assign a daily eco action and show forest progress."""
        user_id = str(ctx.author.id)
        data = load_data()
        today = str(date.today())

        if not actions:
            await ctx.send("🍁 No eco actions available right now.")
            return

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

        # Checks if action already completed today
        if user.get("last_log_date") == today:
            await ctx.send("You've already completed an eco-action today! 😊 Come back tomorrow 🌱")
            return

        # Checks if pending action exists
        if user.get("pending_action") and user.get("pending_action_date") == today:
            await ctx.send(
                f"🌎 You already have a pending action for today:\n"
                f"**{user['pending_action']['task']}**\n"
                "Complete it with `!log` to earn XP 🌱"
            )
            return

        # Assigns new action
        action = random.choice(actions)
        user["pending_action"] = action
        user["pending_action_date"] = today
        save_data(data)

        # Creates embed for action + forest preview
        forest_preview = get_forest_visual(user["xp"], user["streak"])
        level = get_level(user["xp"])
        embed = discord.Embed(
            title="🌎 Daily Eco Action",
            description=f"**{action['task']}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Level", value=level)
        embed.add_field(name="XP", value=user["xp"])
        embed.add_field(name="Streak", value=f"{user['streak']} days")
        embed.add_field(name="Actions completed", value=user["actions_completed"])
        embed.add_field(name="Your forest so far", value=forest_preview, inline=False)
        embed.set_footer(text="Complete your action with !log to earn XP and grow your forest 🌱")

        await ctx.send(embed=embed)

    @commands.command(name='log')
    async def log_action(self, ctx):
        """Log the pending eco action and update streak, XP, CO₂, and forest."""
        user_id = str(ctx.author.id)
        data = load_data()
        today = str(date.today())

        if user_id not in data:
            await ctx.send("❗You need to request an action first with `!ecoaction`")
            return

        user = data[user_id]
        action = user.get("pending_action")

        if not action:
            await ctx.send("❗You have no pending action! Use `!ecoaction` first.")
            return

        last_log = user.get("last_log_date")
        if last_log == today:
            await ctx.send("You already logged an action today 🌿 Come back tomorrow!")
            return

        # Updates streak
        if last_log:
            last_date = date.fromisoformat(last_log)
            days_since_last = (date.today() - last_date).days
            if days_since_last == 1:
                user["streak"] += 1
                streak_msg = "You're keeping the green energy alive! 🌞"
            elif 2 <= days_since_last <= 3:
                lost_days = days_since_last - 1
                user["streak"] = max(1, user["streak"] - lost_days)
                streak_msg = f"🌙 You rested a bit, but your forest still thrives! (Streak slightly reduced by {lost_days} 🌿)"
            elif days_since_last > 3:
                user["streak"] = 1
                streak_msg = "Welcome back, wanderer 🚣 Your forest missed you - a new streak begins! 🌱"
        else:
            user["streak"] = 1
            streak_msg = "Your eco-journey begins today! 🌱"

        # Applies action rewards
        task = action["task"]
        co2_saved = action["co2_saved"]
        user["co2_saved"] += co2_saved
        user["last_log_date"] = today
        user["actions_completed"] += 1
        user["xp"] += 2
        user["pending_action"] = None
        user["pending_action_date"] = None
        save_data(data)

        # Forest visual + level + encouragement
        forest_visual = get_forest_visual(user["xp"], user["streak"])
        level = get_level(user["xp"])
        encouragement = random.choice(encouragements)

        # Creates embed
        embed = discord.Embed(
            title="🌿 Eco Action Completed!",
            description=f"**{task}**\n\n💨 You helped reduce **{co2_saved:.2f} kg CO₂** today!\n"
                        f"Total saved so far: **{user['co2_saved']:.2f} kg CO₂** 🌍",
            color=discord.Color.green()
        )
        embed.add_field(name="XP Gained", value="+2 🌱", inline=True)
        embed.add_field(name="Streak", value=f"{user['streak']} days\n{streak_msg}", inline=False)
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="Your forest", value=forest_visual, inline=False)
        embed.set_footer(text=encouragement)

        await ctx.send(embed=embed)

    @commands.command(name='profile')
    async def profile(self, ctx):
        """Show user profile with stats and forest."""
        user_id = str(ctx.author.id)
        data = load_data()

        if user_id not in data:
            await ctx.send("You haven't started your eco journey yet 🌱 Use `!ecoaction` to begin!")
            return

        user = data[user_id]
        level = get_level(user["xp"])
        forest_visual = get_forest_visual(user["xp"], user["streak"])

        embed = discord.Embed(
            title=f"{ctx.author.name}'s Eco Profile 🌿",
            color=discord.Color.green()
        )
        embed.add_field(name="🌱 Level", value=level)
        embed.add_field(name="✨ XP", value=user['xp'])
        embed.add_field(name="✅ Actions Completed", value=user['actions_completed'])
        embed.add_field(name="🔥 Streak", value=f"{user['streak']} days")
        embed.add_field(name="🌳 Forest", value=forest_visual, inline=False)
        embed.set_footer(text="Keep completing actions to grow your forest 🌿")
        await ctx.send(embed=embed)

    @commands.command(name='forest')
    async def forest(self, ctx):
        """Show current forest visual with level and streak."""
        user_id = str(ctx.author.id)
        data = load_data()

        if user_id not in data:
            await ctx.send("You haven't started your eco journey yet 🌱 Try `!ecoaction` first!")
            return

        user = data[user_id]
        forest_visual = get_forest_visual(user["xp"], user["streak"])
        level = get_level(user["xp"])

        embed = discord.Embed(
            title=f"{ctx.author.name}'s Living Forest",
            description=f"{forest_visual}\n\nLevel: **{level}**\nStreak: **{user['streak']} days**\nXP: **{user['xp']}**",
            color=discord.Color.green()
        )
        embed.set_footer(text="*Tiny steps can make your forest bloom* 🪷")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Eco(bot))
