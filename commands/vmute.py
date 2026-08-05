import discord
from discord.ext import commands
from discord import app_commands

from utils.logger import send_log


class VMute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="vmute",
        description="Mute a member in voice."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def vmute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided."
    ):

        # التأكد أن العضو داخل روم صوتي
        if member.voice is None:
            await interaction.response.send_message(
                "❌ هذا العضو ليس في روم صوتي.",
                ephemeral=True
            )
            return

        # لا يمكنك استخدامه على نفسك
        if member == interaction.user:
            await interaction.response.send_message(
                "❌ لا يمكنك كتم نفسك.",
                ephemeral=True
            )
            return

        # لا يمكنك استخدامه على البوت
        if member == self.bot.user:
            await interaction.response.send_message(
                "❌ لا يمكنك كتم البوت.",
                ephemeral=True
            )
            return

        # لا يمكنك استخدامه على مالك السيرفر
        if member == interaction.guild.owner:
            await interaction.response.send_message(
                "❌ لا يمكنك كتم مالك السيرفر.",
                ephemeral=True
            )
            return

        # التحقق من رتبة البوت
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ لا أستطيع كتم هذا العضو لأن رتبته أعلى من رتبتي أو مساوية لها.",
                ephemeral=True
            )
            return

        # التحقق من رتبة المنفذ
        if (
            member.top_role >= interaction.user.top_role
            and interaction.user != interaction.guild.owner
        ):
            await interaction.response.send_message(
                "❌ لا يمكنك كتم عضو رتبته أعلى من رتبتك أو مساوية لها.",
                ephemeral=True
            )
            return

        await member.edit(mute=True, reason=reason)

        await interaction.response.send_message(
            f"🔇 تم كتم {member.mention}.",
            ephemeral=True
        )

        embed = discord.Embed(
            title="🔇 Voice Mute",
            color=discord.Color.blue()
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

    @vmute.error
    async def vmute_error(self, interaction: discord.Interaction, error):
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
    await bot.add_cog(VMute(bot))
