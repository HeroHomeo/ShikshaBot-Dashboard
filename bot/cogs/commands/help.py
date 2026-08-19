# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
# ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
# ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
# ║                                                                  ║
# ║           © 2026 Avinash aka Shroud.bean — All Rights Reserved    ║
# ║                                                                  ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import discord
from utils.emoji import ARROWRED, BOOST, CAST, GAMES, LEVEL_UP, LOADINGRED, LOCK, MESSAGE, MINECRAFT, MUSIC, NEW, PIN, SEED, STAR, SWORD, SYSTEM, THUNDER, TICKET, WIFI, ZAI, ZARROW, ZBAN, ZBOT, ZCIRCLE, ZCIRCLE_ALT1, ZCLOUD, ZCOUNTING, ZMODULE, ZPEOPLE, ZROCKET, ZSAFE, ZTADA, ZUNMUTE, ZWRENCH
from discord.ext import commands
from discord import app_commands, Interaction
from difflib import get_close_matches
from contextlib import suppress
from core import Context
from core.shikshabot import shikshabot
from core.Cog import Cog
from utils.Tools import getConfig
from itertools import chain
import json
from utils import help as vhelp
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
import asyncio
from utils.config import serverLink
from utils.Tools import *
from utils.cv2 import CV2, CV2Embed
from utils.config import *

color = 0xFF0000
client = shikshabot()

from utils.config import BotName

class HelpCommand(commands.HelpCommand):

  async def send_ignore_message(self, ctx, ignore_type: str):
    if ignore_type == "channel":
      await ctx.reply(f"This channel is ignored.", mention_author=False)
    elif ignore_type == "command":
      await ctx.reply(f"{ctx.author.mention} This Command, Channel, or You have been ignored here.", delete_after=6)
    elif ignore_type == "user":
      await ctx.reply(f"You are ignored.", mention_author=False)

  async def on_help_command_error(self, ctx, error):
    errors = [
      commands.CommandOnCooldown, commands.CommandNotFound,
      discord.HTTPException, commands.CommandInvokeError
    ]
    if not type(error) in errors:
      await self.context.reply(f"Unknown Error Occurred\n{error.original}",
                               mention_author=False)
    else:
      if type(error) == commands.CommandOnCooldown:
        return
    return await super().on_help_command_error(ctx, error)

  async def command_not_found(self, string: str) -> None:
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
        return

    if not check_ignore:
        await self.send_ignore_message(ctx, "command")
        return

    cmds = (str(cmd) for cmd in self.context.bot.walk_commands())
    matches = get_close_matches(string, cmds)

    embed = CV2Embed(
        title=f"{BotName} Helper",
        description=f">>> **Ops! Command not found with the name** `{string}`.",
        color=0xFF0000
    )

    await ctx.reply(view=embed, mention_author=True)

  async def send_bot_help(self, mapping):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    # Show loading message
    loading_embed = CV2(f"{LOADINGRED} Loading help Menu...")
    loading_msg = await ctx.reply(view=loading_embed)

    # Wait 1 second (faster loading)
    await asyncio.sleep(1)

    with suppress(discord.NotFound):
      await loading_msg.delete()

    data = await getConfig(self.context.guild.id)
    prefix = data["prefix"]

    embed = discord.Embed(
        title=f"{self.context.bot.user.name} Help Directory",
        description=(
            f"Browse through the categories below using the dropdown menu.\n"
            f"Need details on a specific command? Run `{prefix}help <command>`!"
        ),
        color=0xFF0000
    )
    if self.context.bot.user.display_avatar:
        embed.set_thumbnail(url=self.context.bot.user.display_avatar.url)
        embed.set_author(name=f"Command Categories", icon_url=self.context.bot.user.display_avatar.url)

    current_field_value = ""
    used_labels = set()

    # Use the curated dummy cogs for home page grouping instead of raw mapping
    for cog in self.context.bot.cogs.values():
        if hasattr(cog, "help_custom"):
            try:
                emoji, label, _ = cog.help_custom()
            except Exception:
                continue
            
            # Find the dummy command to get the string
            cmds = cog.get_commands()
            if not cmds or not cmds[0].short_doc:
                continue
                
            subcmds = [s.strip().replace("`", "") for s in cmds[0].short_doc.split(",")]
            # remove any newlines from the string and clean it up
            cleaned = []
            for s in subcmds:
                if '\n' in s:
                    cleaned.extend([x.strip() for x in s.split('\n') if x.strip()])
                elif s:
                    cleaned.append(s)
            
            if not cleaned:
                continue

            # Prevent duplicate labels
            original_label = label
            counter = 1
            while label in used_labels:
                label = f"{original_label} {counter}"
                counter += 1
            used_labels.add(label)

            command_strings = []
            for c in cleaned:
                if c.startswith(">"):
                    command_strings.append(f"`{prefix}{c[1:]}`")
                elif c.startswith("/"):
                    command_strings.append(f"`{c}`")
                else:
                    command_strings.append(f"`{prefix}{c}`")
            
            if command_strings:
                category_text = f"{emoji} **{label}**\n" + ", ".join(command_strings) + "\n\n"
                
                # Check if adding this would exceed the safe 5000 char limit (to leave room for footers, etc)
                if len(embed) + len(current_field_value) + len(category_text) > 5000:
                    break
                    
                # If adding this category exceeds field limit, start a new field
                if len(current_field_value) + len(category_text) > 1024:
                    if not current_field_value:
                        # Should never happen if categories are reasonably sized
                        current_field_value = category_text[:1021] + "..."
                        
                    embed.add_field(name="\u200b", value=current_field_value, inline=False)
                    current_field_value = category_text
                else:
                    current_field_value += category_text

    # Add the final field if there's leftover text
    if current_field_value:
        embed.add_field(name="\u200b", value=current_field_value, inline=False)
    
    embed.set_thumbnail(url=self.context.bot.user.display_avatar.url if self.context.bot.user.display_avatar else None)
    
    # We pass the embed as homeembed to the dropdown UI
    view = vhelp.View(mapping=mapping, ctx=self.context, homeembed=embed, ui=2)
    current_embed = view.current_embed
    await ctx.reply(embed=current_embed, view=view)

  async def send_command_help(self, command):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    description = command.help or 'No Information Provided...'
    
    embed = discord.Embed(
        title=f"Command: {command.name}",
        description=f"```yaml\n{description}\n```",
        color=0xFF0000
    )

    if command.aliases:
        alias_str = ", ".join(command.aliases)
        embed.add_field(name="🔗 Aliases", value=f"`{alias_str}`", inline=True)
    else:
        embed.add_field(name="🔗 Aliases", value="`None`", inline=True)

    usage_str = f"{self.context.prefix}{command.qualified_name} {command.signature}".strip()
    embed.add_field(name="🛠️ Usage", value=f"`{usage_str}`", inline=False)
    
    if self.context.bot.user.display_avatar:
        embed.set_thumbnail(url=self.context.bot.user.display_avatar.url)
        embed.set_author(name=f"{self.context.bot.user.name} Command Help", icon_url=self.context.bot.user.display_avatar.url)
    else:
        embed.set_author(name=f"Command Help")
        
    embed.set_footer(text="< > = required | [ ] = optional")

    await self.context.reply(embed=embed, mention_author=False)

  def get_command_signature(self, command: commands.Command) -> str:
    parent = command.full_parent_name
    if len(command.aliases) > 0:
      aliases = ' | '.join(command.aliases)
      fmt = f'[{command.name} | {aliases}]'
      if parent:
        fmt = f'{parent}'
      alias = f'[{command.name} | {aliases}]'
    else:
      alias = command.name if not parent else f'{parent} {command.name}'
    return f'{alias} {command.signature}'

  def common_command_formatting(self, embed_like, command):
    embed_like.title = self.get_command_signature(command)
    if command.description:
      embed_like.description = f'{command.description}\n\n{command.help}'
    else:
      embed_like.description = command.help or 'No help found...'

  async def send_group_help(self, group):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    entries = [
        (
            f"🛠️ `{self.context.prefix}{cmd.qualified_name}`",
            f"```yaml\n{cmd.short_doc if cmd.short_doc else 'No details provided.'}\n```"
        )
        for cmd in group.commands
      ]

    count = len(group.commands)

    embeds = FieldPagePaginator(
      entries=entries,
      title=f"Group Command: {group.qualified_name.title()} [{count} Subcommands]",
      description=f"Type `{self.context.prefix}help <subcommand>` for more details.",
      per_page=4
    ).get_pages()   
    
    paginator = Paginator(ctx, embeds)
    await paginator.paginate()

  async def send_cog_help(self, cog):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    entries = [(
      f"🛠️ `{self.context.prefix}{cmd.qualified_name}`",
      f"```yaml\n{cmd.short_doc if cmd.short_doc else 'No details provided.'}\n```",
    ) for cmd in cog.get_commands()]
    
    paginator = Paginator(source=FieldPagePaginator(
      entries=entries,
      title=f"Category: {cog.qualified_name.title()} ({len(cog.get_commands())} Commands)",
      description=f"Type `{self.context.prefix}help <command>` for detailed usage.\n",
      color=0xFF0000,
      per_page=4),
                          ctx=self.context)
    await paginator.paginate()


class Help(Cog, name="help"):

  def __init__(self, client: shikshabot):
    self._original_help_command = client.help_command
    attributes = {
      'name': "help",
      'aliases': ['h'],
      'cooldown': commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user),
      'help': 'Shows help about bot, a command, or a category'
    }
    client.help_command = HelpCommand(command_attrs=attributes)
    client.help_command.cog = self

  async def cog_unload(self):
    self.help_command = self._original_help_command