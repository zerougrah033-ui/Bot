import discord
from discord.ext import commands

from utils.logger import send_log


class MemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        embed = discord.Embed(
            title="🟢 Member Joined",
            color=discord.Color.green()
        )

        embed.add_field(
            name="👤 Member",
            value=f"{member.mention}\n`{member.id}`",
            inline=False
        )

        embed.add_field(
            name="📅 Account Created",
            value=discord.utils.format_dt(member.created_at, style="F"),
            inline=False
        )

        embed.add_field(
            name="👥 Members",
            value=str(member.guild.member_count),
            inline=False
        )

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        embed.set_footer(text="Discord Security Bot")

        await send_log(self.bot, embed)


async def setup(bot):
    await bot.add_cog(MemberJoin(bot))
