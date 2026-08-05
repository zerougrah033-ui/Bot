import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta

from utils.logger import send_log


class Untimeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="untimeout",
        description="Remove timeout from a member."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def untimeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided."
    ):

        # لا يمكنك إزالة التايم أوت عن نفسك
        if member == interaction.user:
            await interaction.response.send_message(
                "❌ لا يمكنك استخدام هذا الأمر على نفسك.",
                ephemeral=True
            )
            return

        # لا يمكنك إزالة التايم أوت عن البوت
        if member == self.bot.user:
            await interaction.response.send_message(
                "❌ لا يمكنك استخدام هذا الأمر على البوت.",
                ephemeral=True
            )
            return

        # لا يمكنك استخدامه على مالك السيرفر
        if member == interaction.guild.owner:
            await interaction.response.send_message(
                "❌ لا يمكنك استخدام هذا الأمر على مالك السيرفر.",
                ephemeral=True
            )
            return

        # رتبة البوت
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ لا أستطيع إزالة الـ Timeout عن هذا العضو لأن رتبته أعلى من رتبتي أو مساوية لها.",
                ephemeral=True
            )
            return

        # رتبة المنفذ
        if (
            member.top_role >= interaction.user.top_role
            and interaction.user != interaction.guild.owner
        ):
            await interaction.response.send_message(
                "❌ لا يمكنك استخدام الأمر على عضو رتبته أعلى من رتبتك أو مساوية لها.",
                ephemeral=True
            )
            return

        await member.timeout(
            None,
            reason=reason
        )

        await interaction.response.send_message(
            f"✅ تمت إزالة الـ Timeout عن {member.mention}.",
            ephemeral=True
        )

        embed = discord.Embed(
            title="✅ Timeout Removed",
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
            name="📝 Reason",
            value=reason,
            inline=False
        )

        await send_log(self.bot, embed)

    @untimeout.error
    async def untimeout_error(self, interaction: discord.Interaction, error):
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
    await bot.add_cog(Untimeout(bot))
