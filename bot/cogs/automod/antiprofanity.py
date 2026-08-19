import discord
from discord.ext import commands
from db import aiosqlite_mock as aiosqlite
import asyncio
from datetime import datetime, timezone
from better_profanity import profanity

# Load the default wordlist
profanity.load_censor_words()

class AntiProfanity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_punishments = {}

    async def is_automod_enabled(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT enabled FROM automod WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            return result is not None and result[0] == 1

    async def is_anti_profanity_enabled(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT punishment FROM automod_punishments WHERE guild_id = ? AND event = 'Anti profanity'", (guild_id,))
            result = await cursor.fetchone()
            return result is not None

    async def get_anti_profanity_punishment(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT punishment FROM automod_punishments WHERE guild_id = ? AND event = 'Anti profanity'", (guild_id,))
            result = await cursor.fetchone()
            return result[0] if result else "Mute"

    async def get_ignored_channels(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT id FROM automod_ignored WHERE guild_id = ? AND type = 'channel'", (guild_id,))
            return [row[0] for row in await cursor.fetchall()]

    async def get_ignored_roles(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT id FROM automod_ignored WHERE guild_id = ? AND type = 'role'", (guild_id,))
            return [row[0] for row in await cursor.fetchall()]

    async def execute_punishment(self, user, guild, punishment, reason):
        if punishment == "Mute":
            mute_role = discord.utils.get(guild.roles, name="Muted")
            if not mute_role:
                try:
                    mute_role = await guild.create_role(name="Muted", reason="Automod: Mute role created")
                    for channel in guild.channels:
                        await channel.set_permissions(mute_role, send_messages=False, speak=False)
                except discord.Forbidden:
                    return
            try:
                await user.add_roles(mute_role, reason=reason)
            except discord.Forbidden:
                pass
        elif punishment == "Kick":
            try:
                await user.kick(reason=reason)
            except discord.Forbidden:
                pass
        elif punishment == "Ban":
            try:
                await user.ban(reason=reason)
            except discord.Forbidden:
                pass

    async def log_punishment(self, guild_id, user, punishment, reason, message):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT log_channel_id FROM automod WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            log_channel_id = result[0] if result else None

        if log_channel_id:
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
                embed = discord.Embed(title="Automod Action", color=discord.Color.red())
                embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
                embed.add_field(name="Action", value=punishment, inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Message", value=message.content, inline=False)
                embed.set_thumbnail(url=avatar_url)
                embed.timestamp=discord.utils.utcnow()
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Executes the on message command."""
        if message.author.bot or not message.guild:
            return

        guild = message.guild
        user = message.author
        channel = message.channel
        guild_id = guild.id

        if not await self.is_automod_enabled(guild_id) or not await self.is_anti_profanity_enabled(guild_id):
            return

        if user == guild.owner or user == self.bot.user:
            return

        ignored_channels = await self.get_ignored_channels(guild_id)
        if channel.id in ignored_channels:
            return

        ignored_roles = await self.get_ignored_roles(guild_id)
        if any(role.id in ignored_roles for role in user.roles):
            return

        # Check for profanity
        if profanity.contains_profanity(message.content):
            try:
                await message.delete()
            except discord.Forbidden:
                pass
            except discord.NotFound:
                pass
                
            punishment = await self.get_anti_profanity_punishment(guild_id)
            reason = "Automod: Used profanity"
            
            # Avoid duplicate punishments in rapid succession
            current_time = asyncio.get_event_loop().time()
            if user.id in self.recent_punishments and current_time - self.recent_punishments[user.id] < 10:
                return
                
            self.recent_punishments[user.id] = current_time
            await self.execute_punishment(user, guild, punishment, reason)
            await self.log_punishment(guild_id, user, punishment, reason, message)

async def setup(bot):
    await bot.add_cog(AntiProfanity(bot))
