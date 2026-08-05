import discord
from discord.ext import commands
from discord import app_commands

from utils.logger import send_log
from database.database import reset_warnings


class ResetWarnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="resetwarnings",
        description="Reset all warnings for a member."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def resetwarnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        reset_warnings(interaction.guild.id, member.id)

        await interaction.response.send_message(
            f"✅ تم تصفير جميع تحذيرات {member.mention}.",
            ephemeral=True
        )

        embed = discord.Embed(
            title="♻️ Warnings Reset",
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

        await send_log(self.bot, embed)

    @resetwarnings.error
    async def resetwarnings_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية استخدام هذا الأمر.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(ResetWarnings(bot))
