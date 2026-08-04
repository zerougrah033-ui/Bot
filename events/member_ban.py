import discord
from discord.ext import commands

from utils.logger import send_log


class MemberBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):

        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.dark_red()
        )

        embed.add_field(
            name="👤 User",
            value=f"{user} (`{user.id}`)",
            inline=False
        )

        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)

        embed.set_footer(text="Discord Security Bot")

        await send_log(self.bot, embed)


async def setup(bot):
    await bot.add_cog(MemberBan(bot))
