import discord
from discord.ext import commands
from discord import app_commands

from utils.logger import send_log


class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="clear",
        description="Delete messages from a channel."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100]
    ):

        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(
            f"✅ تم حذف **{len(deleted)}** رسالة.",
            ephemeral=True
        )

        embed = discord.Embed(
            title="🗑️ Messages Cleared",
            color=discord.Color.red()
        )

        embed.add_field(
            name="👮 Moderator",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="📍 Channel",
            value=interaction.channel.mention,
            inline=False
        )

        embed.add_field(
            name="🧹 Messages Deleted",
            value=str(len(deleted)),
            inline=False
        )

        await send_log(self.bot, embed)

    @clear.error
    async def clear_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية استخدام هذا الأمر.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ حدث خطأ أثناء تنفيذ الأمر.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Clear(bot))
