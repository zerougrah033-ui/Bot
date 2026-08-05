import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta

from utils.logger import send_log


class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="timeout",
        description="Timeout a member."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],
        reason: str = "No reason provided."
    ):

        # لا يمكنك معاقبة نفسك
        if member == interaction.user:
            await interaction.response.send_message(
                "❌ لا يمكنك عمل Timeout لنفسك.",
                ephemeral=True
            )
            return

        # لا يمكنك معاقبة البوت
        if member == self.bot.user:
            await interaction.response.send_message(
                "❌ لا يمكنك عمل Timeout للبوت.",
                ephemeral=True
            )
            return

        # لا يمكنك معاقبة مالك السيرفر
        if member == interaction.guild.owner:
            await interaction.response.send_message(
                "❌ لا يمكنك عمل Timeout لمالك السيرفر.",
                ephemeral=True
            )
            return

        # رتبة البوت
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ لا أستطيع عمل Timeout لهذا العضو لأن رتبته أعلى من رتبتي أو مساوية لها.",
                ephemeral=True
            )
            return

        # رتبة المنفذ
        if (
            member.top_role >= interaction.user.top_role
            and interaction.user != interaction.guild.owner
        ):
            await interaction.response.send_message(
                "❌ لا يمكنك معاقبة عضو رتبته أعلى من رتبتك أو مساوية لها.",
                ephemeral=True
            )
            return

        await member.timeout(
            timedelta(minutes=minutes),
            reason=reason
        )

        await interaction.response.send_message(
            f"✅ تم عمل Timeout لـ {member.mention} لمدة **{minutes}** دقيقة.",
            ephemeral=True
        )

        embed = discord.Embed(
            title="⏳ Member Timed Out",
            color=discord.Color.gold()
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
            name="⏱️ Duration",
            value=f"{minutes} minute(s)",
            inline=False
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        await send_log(self.bot, embed)

    @timeout.error
    async def timeout_error(self, interaction: discord.Interaction, error):
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
    await bot.add_cog(Timeout(bot))
