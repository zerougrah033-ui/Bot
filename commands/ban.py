import discord
from discord.ext import commands
from discord import app_commands

from utils.logger import send_log


class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ban",
        description="Ban a member from the server."
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided."
    ):

        await member.ban(reason=reason)

        await interaction.response.send_message(
            f"✅ {member.mention} has been banned.",
            ephemeral=True
        )

        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.red()
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
            name="📝 Reason",
            value=reason,
            inline=False
        )

        await send_log(self.bot, embed)


    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error):

        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Ban(bot))
