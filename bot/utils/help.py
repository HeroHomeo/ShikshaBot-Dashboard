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
from utils.Tools import *
from utils.cv2 import build_container
from utils.emoji import REWIND, PREVIOUS, NEXT, FORWARD, DELETE, HOME
from discord.ui import LayoutView, TextDisplay, Separator, ActionRow


class Dropdown(discord.ui.Select):

    def __init__(self, ctx, options, placeholder="Choose a Category for Help"):
        super().__init__(placeholder=placeholder,
                         min_values=1,
                         max_values=1,
                         options=options)
        self.invoker = ctx.author

    async def callback(self, interaction: discord.Interaction):
        if self.invoker == interaction.user:
            index = self.view.find_index_from_select(self.values[0])
            if not index:
                index = 0
            await self.view.set_page(index, interaction)
        else:
            await interaction.response.send_message(
                "You must run this command to interact with it.", ephemeral=True)


class View(discord.ui.View):
    def __init__(self, mapping: dict, ctx, homeembed, ui: int):
        super().__init__(timeout=None)
        self.mapping = mapping
        self.ctx = ctx
        self.index = 0
        self.current_page = 0
        self.ui = ui

        self.options, self.pages, self.total_pages = self.gen_pages(homeembed)
        self.pages[0]['footer'] = f"• Help page 1/{self.total_pages} | Requested by: {self.ctx.author.display_name}"
        self.current_embed = self._rebuild()

    def _rebuild(self):
        self.clear_items()
        page = self.pages[self.index]
        page['footer'] = f"• Help page {self.index + 1}/{self.total_pages} | Requested by: {self.ctx.author.display_name}"

        embed = discord.Embed(
            title=page.get('title', ''),
            description=page.get('description', ''),
            color=0xFF0000
        )
        if page.get('thumbnail'):
            embed.set_thumbnail(url=page['thumbnail'])
        for name, value in page.get('fields', []):
            if name and value:
                embed.add_field(name=name, value=value, inline=False)
        if page.get('footer'):
            embed.set_footer(text=page['footer'])

        # Build buttons
        is_first = self.index == 0
        is_last = self.index >= len(self.pages) - 1

        # Build buttons (they will go on the last row)
        is_first = self.index == 0
        is_last = self.index >= len(self.pages) - 1

        homeB = discord.ui.Button(label="", emoji=HOME, style=discord.ButtonStyle.secondary, disabled=is_first)
        backB = discord.ui.Button(label="", emoji=PREVIOUS, style=discord.ButtonStyle.secondary, disabled=is_first)
        quitB = discord.ui.Button(label="", emoji=DELETE, style=discord.ButtonStyle.danger)
        nextB = discord.ui.Button(label="", emoji=NEXT, style=discord.ButtonStyle.secondary, disabled=is_last)
        lastB = discord.ui.Button(label="", emoji=FORWARD, style=discord.ButtonStyle.secondary, disabled=is_last)

        homeB.callback = self._home_cb
        backB.callback = self._back_cb
        quitB.callback = self._quit_cb
        nextB.callback = self._next_cb
        lastB.callback = self._last_cb
        
        button_row = 1

        # Add dropdowns first
        if self.ui == 0:
            d = Dropdown(ctx=self.ctx, options=self.options, placeholder="Select a command group.")
            d.row = 0
            self.add_item(d)
            button_row = 1
        elif self.ui == 2:
            mid = len(self.options) // 2
            o1, o2 = self.options[:mid], self.options[mid:]
            if o1:
                d1 = Dropdown(ctx=self.ctx, options=o1, placeholder="Main Commands")
                d1.row = 0
                self.add_item(d1)
            if o2:
                d2 = Dropdown(ctx=self.ctx, options=o2, placeholder="Extra Commands")
                d2.row = 1
                self.add_item(d2)
            button_row = 2
        elif self.ui == 3:
            d = Dropdown(ctx=self.ctx, options=self.options, placeholder="Select a command group.")
            d.row = 0
            self.add_item(d)
            button_row = 1

        # Add buttons
        homeB.row = button_row
        backB.row = button_row
        quitB.row = button_row
        nextB.row = button_row
        lastB.row = button_row
        
        self.add_item(homeB)
        self.add_item(backB)
        self.add_item(quitB)
        self.add_item(nextB)
        self.add_item(lastB)

        return embed

    async def _check(self, interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You must run this command to interact with it.", ephemeral=True)
            return False
        return True

    async def _home_cb(self, interaction):
        if await self._check(interaction):
            await self.set_page(0, interaction)

    async def _back_cb(self, interaction):
        if await self._check(interaction):
            await self.set_page(self.index - 1 if self.index > 0 else len(self.pages) - 1, interaction)

    async def _quit_cb(self, interaction):
        if await self._check(interaction):
            await interaction.response.defer()
            await interaction.delete_original_response()

    async def _next_cb(self, interaction):
        if await self._check(interaction):
            await self.set_page(self.index + 1 if self.index < len(self.pages) - 1 else 0, interaction)

    async def _last_cb(self, interaction):
        if await self._check(interaction):
            await self.set_page(len(self.pages) - 1, interaction)

    def find_index_from_select(self, value):
        i = 0
        used_labels = set()
        for cog in self.get_cogs():
            if cog.__class__.__name__ == "Roleplay":
                continue
            if "help_custom" in dir(cog):
                _, label, _ = cog.help_custom()
                original_label = label
                counter = 1
                while label in used_labels:
                    label = f"{original_label} {counter}"
                    counter += 1
                used_labels.add(label)
                if label == value or value.startswith(original_label + " "):
                    return i + 1
                i += 1
        return 0

    def get_cogs(self):
        return list(self.mapping.keys())

    def gen_pages(self, homeembed):
        options, pages = [], []
        total_pages = 0
        used_labels = set()

        options.append(discord.SelectOption(label="Home", emoji=HOME))

        avatar_url = self.ctx.bot.user.display_avatar.url if self.ctx.bot.user.display_avatar else None

        if hasattr(homeembed, '_title'):
            home_page = {
                'title': homeembed._title or '',
                'description': homeembed._description or '',
                'fields': list(homeembed._fields) if hasattr(homeembed, '_fields') else [],
                'footer': None,
                'thumbnail': avatar_url
            }
        else:
            home_page = {
                'title': getattr(homeembed, 'title', '') or '',
                'description': getattr(homeembed, 'description', '') or '',
                'fields': [(f.name, f.value) for f in homeembed.fields] if hasattr(homeembed, 'fields') and homeembed.fields else [],
                'footer': homeembed.footer.text if hasattr(homeembed, 'footer') and homeembed.footer else None,
                'thumbnail': avatar_url
            }

        pages.append(home_page)
        total_pages += 1
        used_labels.add("Home")

        for cog in self.get_cogs():
            if cog.__class__.__name__ == "Roleplay":
                continue
            if "help_custom" in dir(cog):
                emoji, label, description = cog.help_custom()
                original_label = label
                counter = 1
                while label in used_labels:
                    label = f"{original_label} {counter}"
                    counter += 1
                used_labels.add(label)
                
                options.append(discord.SelectOption(label=label, emoji=emoji.strip() if isinstance(emoji, str) else emoji))

                cmd_list = []
                for command in cog.get_commands():
                    # Handle custom shikshabot dummy commands like __Ticket__
                    if command.name.startswith("__") and command.name.endswith("__"):
                        if command.short_doc:
                            # Parse things like "`>vanityroles setup` , `>vanityroles reset `"
                            subcmds = [s.strip() for s in command.short_doc.split(",")]
                            for subcmd in subcmds:
                                if subcmd: 
                                    # Extract the raw command name (strip backticks and prefix)
                                    raw_cmd_name = subcmd.replace("`", "").strip()
                                    if raw_cmd_name.startswith(self.ctx.prefix):
                                        raw_cmd_name = raw_cmd_name[len(self.ctx.prefix):]
                                    elif raw_cmd_name.startswith("/"):
                                        raw_cmd_name = raw_cmd_name[1:]
                                        
                                    # Try to find the real command in the bot
                                    real_subcmd = self.ctx.bot.get_command(raw_cmd_name)
                                    if real_subcmd:
                                        help_text = real_subcmd.short_doc or real_subcmd.description or "No description available."
                                        cmd_list.append(f"{subcmd} - {help_text}")
                                    else:
                                        cmd_list.append(f"{subcmd} - No description available.")
                        else:
                            cmd_list.append(f"`{self.ctx.prefix}{command.name}` - No description available.")
                    else:
                        help_text = command.short_doc or command.description or "No description available."
                        cmd_list.append(f"`{self.ctx.prefix}{command.name}` - {help_text}")

                desc = "\n".join(cmd_list) if cmd_list else "No commands available."
                
                pages.append({
                    'title': f"Help Menu",
                    'description': f"{emoji} **{original_label}**\n{desc}",
                    'fields': [],
                    'footer': None,
                    'thumbnail': avatar_url
                })
                total_pages += 1

        return options, pages, total_pages

    async def set_page(self, page, interaction):
        self.index = page
        self.current_page = page
        embed = self._rebuild()
        await interaction.response.edit_message(embed=embed, view=self)