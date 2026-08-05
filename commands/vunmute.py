import discord
from discord.ext import commands
from discord import app_commands

from utils.logger import send_log


class VUnmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="vunmute",
        description="Unmute a member in voice."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def vunmute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided."
    ):

        if member.voice is None:
            await interaction.response.send_message(
                "❌ هذا العضو ليس في روم صوتي.",
                ephemeral=True
            )
            return

        if member == self.bot.user:
            await interaction.response.send_message(
                "❌ لا يمكنك استخدام الأمر على البوت.",
                ephemeral=True
            )
            return

        if member == interaction.guild.owner:
            await interaction.response.send_message(
                "❌ لا يمكنك استخدام الأمر على مالك السيرفر.",
                ephemeral=True
            )
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ لا أستطيع فك الكتم عن هذا العضو لأن رتبته أعلى من رتبتي أو مساوية لها.",
                ephemeral=True
            )
            return

        if (
            member.top_role >= interaction.user.top_role
            and interaction.user != interaction.guild.owner
        ):
            await interaction.response.send_message(
                "❌ لا يمكنك استخدام الأمر على عضو رتبته أعلى من رتبتك أو مساوية لها.",
                ephemeral=True
            )
            return

        await member.edit(mute=False, reason=reason)

        await interaction.response.send_message(
            f"🔊 تم فك الكتم عن {member.mention}.",
            ephemeral=True
        )

        embed = discord.Embed(
            title="🔊 Voice Unmute",
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

    @vunmute.error
    async def vunmute_error(self, interaction: discord.Interaction, error):
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
    await bot.add_cog(VUnmute(bot))
