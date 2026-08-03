from discord.ext import commands


class Ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("=" * 40)
        print(f"Logged in as: {self.bot.user}")
        print(f"Servers: {len(self.bot.guilds)}")
        print("Ready Event Loaded ✅")
        print("=" * 40)


async def setup(bot):
    await bot.add_cog(Ready(bot))
