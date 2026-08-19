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
from utils.emoji import SWORD
from discord.ext import commands


class _moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
Moderation commands"""  
    def help_custom(self):
		      emoji = f'{SWORD} '
		      label = "Moderation Commands"
		      description = "Show you Commands of Moderation"
		      return emoji, label, description

    @commands.group()
    async def __Moderation__(self, ctx: commands.Context):
        """`audit` , `warn` , `clearwarns` , `ban` , `clone` , `snipe` , `hide` , `hideall` , `kick` , `lock` , `mute` , `unmute` , `nick` , `nuke` , `role` , `roleicon` , `role all` , `role bots` , `role create` , `role delete` , `role humans` , `role rename` , `role temp` , `role unverified` , `slowmode` , `lockall` , `unlockall` , `steal` , `unban` , `unbanall` , `unhide` , `unhideall` , `unlock` , `unslowmode` , `removerole all` , `removerole bots` , `removerole humans` , `removerole unverified` , `clear` , `clear all` , `clear bots` , `clear contains` , `clear embeds` , `clear files` , `clear images` , `clear mentions` , `clear reactions` , `clear user` , `purgebots` , `purgeuser` , `deleteemoji` , `deletesticker` , `enlarge` , `topcheck` , `topcheck enable` , `topcheck disable` , `prefix` , `give`"""