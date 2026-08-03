import discord
from discord.ext import commands

from utils.logger import send_log


class MessageDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):

        if message.author.bot:
            return

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red()
        )

        embed.add_field(
            name="👤 Author",
            value=f"{message.author} (`{message.author.id}`)",
            inline=False
        )

        embed.add_field(
            name="📍 Channel",
            value=message.channel.mention,
            inline=False
        )

        embed.add_field(
            name="💬 Message",
            value=message.content if message.content else "*No Text*",
            inline=False
        )

        embed.set_footer(text="Discord Security Bot")

        await send_log(self.bot, embed)


async def setup(bot):
    await bot.add_cog(MessageDelete(bot))
