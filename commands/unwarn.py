import discord
from discord.ext import commands
from discord import app_commands

from utils.logger import send_log
from database.database import remove_warning, get_warnings


class Unwarn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="unwarn",
        description="Remove one warning from a member."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unwarn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided."
    ):

        if member == self.bot.user:
            await interaction.response.send_message(
                "❌ لا يمكنك استخدام الأمر على البوت.",
                ephemeral=True
            )
            return

        remove_warning(interaction.guild.id, member.id)
        warns = get_warnings(interaction.guild.id, member.id)

        await interaction.response.send_message(
            f"✅ تمت إزالة تحذير من {member.mention}.\nالتحذيرات الحالية: **{warns}**",
            ephemeral=True
        )

        embed = discord.Embed(
            title="➖ Warning Removed",
            color=discord.Color.green()
        )

        embed.add_field(
            name="👤 Member",
            value=f"{member} (`{member.id}`)",
            inline=False
        )

        embed.add_field(
            name="👮 Moderator",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="📊 Remaining Warnings",
            value=str(warns),
            inline=False
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        await send_log(self.bot, embed)

    @unwarn.error
    async def unwarn_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية استخدام هذا الأمر.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Unwarn(bot))
