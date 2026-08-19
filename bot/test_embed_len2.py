import os
import sys

# Mocking enough of discord.py and the bot to load the cogs
import discord
from discord.ext import commands

class DummyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=">", intents=discord.Intents.default())

async def main():
    bot = DummyBot()
    # Load all cogs in shikshabot
    cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs', 'shikshabot')
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.shikshabot.{filename[:-3]}')
            except Exception as e:
                pass

    total_len = 0
    categories = 0
    for cog in bot.cogs.values():
        if hasattr(cog, "help_custom"):
            try:
                emoji, label, _ = cog.help_custom()
            except Exception:
                continue
            
            cmds = cog.get_commands()
            if not cmds or not cmds[0].short_doc:
                continue
                
            subcmds = [s.strip().replace("`", "") for s in cmds[0].short_doc.split(",")]
            cleaned = []
            for s in subcmds:
                if '\n' in s:
                    cleaned.extend([x.strip() for x in s.split('\n') if x.strip()])
                elif s:
                    cleaned.append(s)
            
            if not cleaned:
                continue

            command_strings = [c for c in cleaned]
            if command_strings:
                category_text = f"{emoji} **{label}**\n" + ", ".join(command_strings) + "\n\n"
                total_len += len(category_text)
                categories += 1
                
    print(f"Total categories: {categories}")
    print(f"Total length: {total_len}")

import asyncio
asyncio.run(main())
