
from discord.ext import commands
import discord

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hello')
    async def hello(self, ctx):
        """Greet the user."""
        await ctx.send("Haii there! I'm Mycelia, your cozy eco-companion 😊")

    @commands.command(name='about')
    async def about(self, ctx):
        """Show bot commands."""
        embed = discord.Embed(
            title="🌿 Mycelia Bot Commands",
            description="Here's how to grow your forest and earn eco-points!",
            color=discord.Color.green()
        )
        embed.add_field(name="`!hello`", value="Say hi to Mycelia!", inline=False)
        embed.add_field(name="`!ecoaction`", value="Get a daily eco action 🌱", inline=False)
        embed.add_field(name="`!log`", value="Log your completed action and earn XP", inline=False)
        embed.add_field(name="`!profile`", value="View your eco stats", inline=False)
        embed.add_field(name="`!forest`", value="See your forest growth 🌳", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
