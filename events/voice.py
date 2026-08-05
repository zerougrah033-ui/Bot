import discord
from discord.ext import commands


class VoiceEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        # إذا خرج العضو من الروم وكان عليه Server Mute
        if before.channel is not None and after.channel is None:
            if before.mute:
                try:
                    await member.edit(
                        mute=False,
                        reason="Auto unmute after leaving voice channel"
                    )
                    print(f"Auto unmuted: {member}")
                except discord.Forbidden:
                    print("Missing Permissions")
                except discord.HTTPException as e:
                    print(f"Error: {e}")


async def setup(bot):
    await bot.add_cog(VoiceEvents(bot))
