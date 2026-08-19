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
from utils.emoji import ARROWRED, ZMODULE
from discord.utils import *
from core import shikshabot, Cog
from utils.Tools import *
from utils.config import BotName, serverLink
from discord.ext import commands
from discord.ui import Button, View

class Autorole(Cog):
    def __init__(self, bot: shikshabot):
       self.bot = bot


    @commands.Cog.listener(name="on_guild_join")
    async def send_msg_to_adder(self, guild: discord.Guild):
        """Executes the send msg to adder command."""
        async for entry in guild.audit_logs(limit=3):
            if entry.action == discord.AuditLogAction.bot_add:
                embed = discord.Embed(
                   description=f"{ZMODULE} **Thanks for adding me.**\n\n{ARROWRED} My default prefix is `>`\n{ARROWRED}> Use the `>help` command to see a list of commands",
                    color=0xFF0000
               )
                embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar else entry.user.default_avatar.url)
                embed.set_author(name=f"{guild.name}", icon_url=guild.me.display_avatar.url)
               
                async def support_callback(interaction: discord.Interaction):
                    await interaction.response.send_message(
                        "If you really want to support me, then send some real dough! 💸",
                        file=discord.File('assets/qr_code.png'),
                        ephemeral=True
                    )

                website_button = Button(label='Website', style=discord.ButtonStyle.link, url='https://.vercel.app')
                support_button = Button(label='Support', style=discord.ButtonStyle.success)
                support_button.callback = support_callback
                
                view = View()
                view.add_item(support_button)
                #view.add_item(website_button)
                if guild.icon:
                    embed.set_author(name=guild.name, icon_url=guild.icon.url)
                try:
                    await entry.user.send(embed=embed, view=view)
                except Exception as e:
                    print(e)
