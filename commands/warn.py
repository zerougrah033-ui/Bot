import discord
from discord.ext import commands
from discord import app_commands

from utils.logger import send_log
from database.database import add_warning, get_warnings


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="warn",
        description="Warn a member."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided."
    ):

        # لا يمكنك تحذير نفسك
        if member == interaction.user:
            await interaction.response.send_message(
                "❌ لا يمكنك تحذير نفسك.",
                ephemeral=True
            )
            return

        # لا يمكنك تحذير البوت
        if member == self.bot.user:
            await interaction.response.send_message(
                "❌ لا يمكنك تحذير البوت.",
                ephemeral=True
            )
            return

        # لا يمكنك تحذير مالك السيرفر
        if member == interaction.guild.owner:
            await interaction.response.send_message(
                "❌ لا يمكنك تحذير مالك السيرفر.",
                ephemeral=True
            )
            return

        # رتبة البوت
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ لا أستطيع تحذير هذا العضو لأن رتبته أعلى من رتبتي أو مساوية لها.",
                ephemeral=True
            )
            return

        # رتبة المنفذ
        if (
            member.top_role >= interaction.user.top_role
            and interaction.user != interaction.guild.owner
        ):
            await interaction.response.send_message(
                "❌ لا يمكنك تحذير عضو رتبته أعلى من رتبتك أو مساوية لها.",
                ephemeral=True
            )
            return

        # إضافة التحذير
        add_warning(interaction.guild.id, member.id)
        warns = get_warnings(interaction.guild.id, member.id)

        await interaction.response.send_message(
            f"✅ تم تحذير {member.mention}.\nعدد التحذيرات: **{warns}**",
            ephemeral=True
        )

        embed = discord.Embed(
            title="⚠️ Member Warned",
            color=discord.Color.yellow()
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
            name="📊 Total Warnings",
            value=str(warns),
            inline=False
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        await send_log(self.bot, embed)

    @warn.error
    async def warn_error(self, interaction: discord.Interaction, error):
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
    await bot.add_cog(Warn(bot))
