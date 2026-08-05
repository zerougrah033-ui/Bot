import discord
from discord.ext import commands
from discord import app_commands

from utils.logger import send_log


class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="kick",
        description="Kick a member from the server."
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided."
    ):

        # لا يمكن طرد نفسك
        if member == interaction.user:
            await interaction.response.send_message(
                "❌ لا يمكنك طرد نفسك.",
                ephemeral=True
            )
            return

        # لا يمكن طرد البوت
        if member == self.bot.user:
            await interaction.response.send_message(
                "❌ لا يمكنك طرد البوت.",
                ephemeral=True
            )
            return

        # لا يمكن طرد مالك السيرفر
        if member == interaction.guild.owner:
            await interaction.response.send_message(
                "❌ لا يمكنك طرد مالك السيرفر.",
                ephemeral=True
            )
            return

        # رتبة البوت
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ لا أستطيع طرد هذا العضو لأن رتبته أعلى من رتبتي أو مساوية لها.",
                ephemeral=True
            )
            return

        # رتبة المنفذ
        if (
            member.top_role >= interaction.user.top_role
            and interaction.user != interaction.guild.owner
        ):
            await interaction.response.send_message(
                "❌ لا يمكنك طرد عضو رتبته أعلى من رتبتك أو مساوية لها.",
                ephemeral=True
            )
            return

        await member.kick(reason=reason)

        await interaction.response.send_message(
            f"✅ تم طرد {member.mention}.",
            ephemeral=True
        )

        embed = discord.Embed(
            title="👢 Member Kicked",
            color=discord.Color.orange()
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

    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error):
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
    await bot.add_cog(Kick(bot))
