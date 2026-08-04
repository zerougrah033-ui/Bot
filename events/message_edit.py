import discord
from discord.ext import commands

from utils.logger import send_log


class MessageEdit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):

        # تجاهل رسائل البوتات
        if before.author.bot:
            return

        # إذا ما تغير المحتوى لا ترسل لوق
        if before.content == after.content:
            return

        embed = discord.Embed(
            title="📝 Message Edited",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="👤 Author",
            value=f"{before.author} (`{before.author.id}`)",
            inline=False
        )

        embed.add_field(
            name="📍 Channel",
            value=before.channel.mention,
            inline=False
        )

        embed.add_field(
            name="📄 Before",
            value=before.content if before.content else "*No Text*",
            inline=False
        )

        embed.add_field(
            name="✏️ After",
            value=after.content if after.content else "*No Text*",
            inline=False
        )

        embed.set_footer(text="Discord Security Bot")

        await send_log(self.bot, embed)


async def setup(bot):
    await bot.add_cog(MessageEdit(bot))
