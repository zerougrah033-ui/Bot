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
    # لا يمكن حظر نفسك
if member == interaction.user:
    await interaction.response.send_message(
        "❌ لا يمكنك حظر نفسك.",
        ephemeral=True
    )
    return

# لا يمكن حظر البوت
if member == self.bot.user:
    await interaction.response.send_message(
        "❌ لا يمكنك حظر البوت.",
        ephemeral=True
    )
    return

# لا يمكن حظر مالك السيرفر
if member == interaction.guild.owner:
    await interaction.response.send_message(
        "❌ لا يمكنك حظر مالك السيرفر.",
        ephemeral=True
    )
    return

# التأكد أن رتبة البوت أعلى من رتبة العضو
if member.top_role >= interaction.guild.me.top_role:
    await interaction.response.send_message(
        "❌ لا أستطيع حظر هذا العضو لأن رتبته أعلى من رتبتي أو مساوية لها.",
        ephemeral=True
    )
    return

# التأكد أن رتبة المنفذ أعلى من رتبة العضو
if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
    await interaction.response.send_message(
        "❌ لا يمكنك حظر عضو رتبته أعلى من رتبتك أو مساوية لها.",
        ephemeral=True
    )
    return
    await bot.add_cog(Ban(bot))
