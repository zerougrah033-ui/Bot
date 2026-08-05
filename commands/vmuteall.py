import discord
from discord.ext import commands
from discord import app_commands

from utils.logger import send_log


class VMuteAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="vmuteall",
        description="Mute everyone in your current voice channel."
    )
    @app_commands.checks.has_permissions(mute_members=True)
    async def vmuteall(self, interaction: discord.Interaction):

        # التأكد أن المنفذ داخل روم صوتي
        if interaction.user.voice is None:
            await interaction.response.send_message(
                "❌ يجب أن تكون داخل روم صوتي.",
                ephemeral=True
            )
            return

        channel = interaction.user.voice.channel
        muted = 0

        for member in channel.members:

            if member.bot:
                continue

            if member == interaction.user:
                continue

            if member == interaction.guild.owner:
                continue

            if member.top_role >= interaction.guild.me.top_role:
                continue

            if (
                member.top_role >= interaction.user.top_role
                and interaction.user != interaction.guild.owner
            ):
                continue

            try:
                await member.edit(mute=True)
                muted += 1
            except discord.Forbidden:
                pass

        await interaction.response.send_message(
            f"🔇 تم كتم **{muted}** عضو في {channel.mention}.",
            ephemeral=True
        )

        embed = discord.Embed(
            title="🔇 Voice Mute All",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="👮 Moderator",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="🎤 Voice Channel",
            value=channel.mention,
            inline=False
        )

        embed.add_field(
            name="👥 Members Muted",
            value=str(muted),
            inline=False
        )

        await send_log(self.bot, embed)

    @vmuteall.error
    async def vmuteall_error(self, interaction: discord.Interaction, error):
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
    await bot.add_cog(VMuteAll(bot))
