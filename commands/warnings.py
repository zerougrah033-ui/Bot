import discord
from discord.ext import commands
from discord import app_commands

from database.database import get_warnings


class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="warnings",
        description="View a member's warnings."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        warns = get_warnings(interaction.guild.id, member.id)

        embed = discord.Embed(
            title="⚠️ Warnings",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="👤 Member",
            value=f"{member.mention}\n`{member.id}`",
            inline=False
        )

        embed.add_field(
            name="📊 Total Warnings",
            value=str(warns),
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    @warnings.error
    async def warnings_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية استخدام هذا الأمر.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Warnings(bot))
