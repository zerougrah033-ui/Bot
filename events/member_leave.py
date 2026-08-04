import discord
from discord.ext import commands

from utils.logger import send_log


class MemberLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        embed = discord.Embed(
            title="🔴 Member Left",
            color=discord.Color.red()
        )

        embed.add_field(
            name="👤 Member",
            value=f"{member} (`{member.id}`)",
            inline=False
        )

        embed.add_field(
            name="👥 Members Left",
            value=str(member.guild.member_count),
            inline=False
        )

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        embed.set_footer(text="Discord Security Bot")

        await send_log(self.bot, embed)


async def setup(bot):
    await bot.add_cog(MemberLeave(bot))
