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
from discord.ext import commands
from discord.ui import LayoutView, TextDisplay, Separator, MediaGallery
import random
import aiohttp
from discord import app_commands
import io
from PIL import Image
from utils.Tools import blacklist_check, ignore_check
from utils.cv2 import CV2, build_container

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giphy_api_key = "y3KcqQTdiS0RYcpNJrWn8hFGglKqX4is"

    async def fetch_giphy(self, query):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.giphy.com/v1/gifs/search?api_key={self.giphy_api_key}&q={query}&limit=30&rating=pg") as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data['data']:
                    return random.choice(data['data'])['images']['original']['url']
                else:
                    return None

    def random_emoji(self):
        return random.choice(["😂", "🤣", "😆", "😳", "🥴", "🙃", "😜"])

    async def action_command(self, ctx, user: discord.Member, action: str):
        gif_url = await self.fetch_giphy(action)
        if not gif_url:
            await ctx.send(view=CV2("😒 Error", "GIPHY API is sleeping. Try later!"))
            return
        view = LayoutView(timeout=None)
        gallery = MediaGallery()
        gallery.add_item(media=gif_url)
        view.add_item(build_container(
            TextDisplay(f"**{ctx.author.mention} {action}s {user.mention} {self.random_emoji()}**"),
            gallery
        ))
        await ctx.send(view=view)

    async def meter_command(self, ctx, title, user, text):
        await ctx.send(view=CV2(title, text))

    @commands.command(name="shipp")
    @blacklist_check()
    @ignore_check()
    async def shipp(self, ctx, user1: discord.Member, user2: discord.Member):
        """
Executes the shipp command."""
        percentage = random.randint(0, 100)
        await ctx.send(view=CV2(f"{self.random_emoji()} Ship Result", f"**{user1.mention} x {user2.mention} = {percentage}% Love**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def hug(self, ctx, user: discord.Member):
        """
Executes the hug command."""
        await self.action_command(ctx, user, "hug")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def kiss(self, ctx, user: discord.Member):
        """
Executes the kiss command."""
        await self.action_command(ctx, user, "kiss")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def pat(self, ctx, user: discord.Member):
        """
Executes the pat command."""
        await self.action_command(ctx, user, "pat")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def slap(self, ctx, user: discord.Member):
        """
Executes the slap command."""
        await self.action_command(ctx, user, "slap")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def tickle(self, ctx, user: discord.Member):
        """
Executes the tickle command."""
        await self.action_command(ctx, user, "tickle")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def coinflip(self, ctx):
        """
Executes the coinflip command."""
        result = random.choice(["Heads", "Tails"])
        await ctx.send(view=CV2("🪙 Coin Flip", f"**Result: {result}**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def dice(self, ctx):
        """
Executes the dice command."""
        result = random.randint(1, 6)
        await ctx.send(view=CV2("🎲 Dice Roll", f"**You rolled a {result}!**"))

    @commands.command(name="8ball")
    @blacklist_check()
    @ignore_check()
    async def eight_ball(self, ctx, *, question: str):
        """
Executes the eight ball command."""
        responses = ["It is certain.", "Without a doubt.", "You may rely on it.",
                     "Ask again later.", "Better not tell you now.",
                     "Don't count on it.", "My sources say no.", "Very doubtful."]
        await ctx.send(view=CV2("🎱 Magic 8Ball", f"**Q:** {question}\n**A:** {random.choice(responses)}"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def roast(self, ctx, user: discord.Member):
        """
Executes the roast command."""
        roasts = [
            f"{user.mention} you're the reason shampoo has instructions!",
            f"{user.mention} you have something on your chin... no, the third one down!",
            f"{user.mention} your secrets are safe with me. I never even listen when you tell me them."
        ]
        await ctx.send(view=CV2("🔥 Roast Time", random.choice(roasts)))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def iq(self, ctx, user: discord.Member = None):
        """
Executes the iq command."""
        user = user or ctx.author
        await ctx.send(view=CV2("🧠 IQ Test", f"**{user.mention} has an IQ of {random.randint(50, 200)}!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def dumb(self, ctx, user: discord.Member = None):
        """
Executes the dumb command."""
        user = user or ctx.author
        await ctx.send(view=CV2("🤪 Dumbness Test", f"**{user.mention} is {random.randint(0, 100)}% dumb!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def simprate(self, ctx, user: discord.Member = None):
        """
Executes the simprate command."""
        user = user or ctx.author
        await ctx.send(view=CV2("😳 Simp Rate", f"**{user.mention} is {random.randint(0, 100)}% simp!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def toxic(self, ctx, user: discord.Member = None):
        """
Executes the toxic command."""
        user = user or ctx.author
        await ctx.send(view=CV2("☠️ Toxic Meter", f"**{user.mention} is {random.randint(0, 100)}% toxic!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def intelligence(self, ctx, user: discord.Member = None):
        """
Executes the intelligence command."""
        user = user or ctx.author
        await ctx.send(view=CV2("🧠 Intelligence Meter", f"**{user.mention} has {random.randint(0, 200)} IQ Points!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def genius(self, ctx, user: discord.Member = None):
        """
Executes the genius command."""
        user = user or ctx.author
        await ctx.send(view=CV2("🤓 Genius Rate", f"**{user.mention} is {random.randint(0, 100)}% genius!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def brainrate(self, ctx, user: discord.Member = None):
        """
Executes the brainrate command."""
        user = user or ctx.author
        await ctx.send(view=CV2("🧠 Brain Power", f"**{user.mention} is using {random.randint(0, 100)}% of their brain!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def howhot(self, ctx, user: discord.Member = None):
        """
Executes the howhot command."""
        user = user or ctx.author
        await ctx.send(view=CV2("🔥 Hotness Meter", f"**{user.mention} is {random.randint(0, 100)}% hot!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def cute(self, ctx, user: discord.Member = None):
        """Executes the cute command."""
        user = user or ctx.author
        await ctx.send(view=CV2("✨ Cuteness Meter", f"**{user.mention} is {random.randint(0, 100)}% cute!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def tharki(self, ctx, user: discord.Member = None):
        """Executes the tharki command."""
        user = user or ctx.author
        await ctx.send(view=CV2("🥵 Tharki Meter", f"**{user.mention} is {random.randint(0, 100)}% tharki!**"))

    @commands.command(aliases=["howgay"])
    @blacklist_check()
    @ignore_check()
    async def gay(self, ctx, user: discord.Member = None):
        """Executes the gay command."""
        user = user or ctx.author
        
        try:
            # Download user avatar
            avatar_bytes = await user.display_avatar.replace(size=256, format='png').read()
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
            
            # Create rainbow gradient horizontally
            # Red, Orange, Yellow, Green, Blue, Indigo, Violet
            colors = [(255, 0, 0, 120), (255, 127, 0, 120), (255, 255, 0, 120), 
                      (0, 255, 0, 120), (0, 0, 255, 120), (75, 0, 130, 120), (148, 0, 211, 120)]
            
            # Create a 1x7 pixel image with rainbow colors to create horizontal stripes
            rainbow = Image.new('RGBA', (1, 7))
            rainbow.putdata(colors)
            
            # Resize the rainbow gradient to match avatar size using LANCZOS to smooth the gradient
            rainbow = rainbow.resize(avatar.size, Image.Resampling.LANCZOS)
            
            # Apply the rainbow overlay
            final_img = Image.alpha_composite(avatar, rainbow)
            
            # Save to buffer
            buffer = io.BytesIO()
            final_img.save(buffer, format="PNG")
            buffer.seek(0)
            
            file = discord.File(buffer, filename="gay.png")
            
            # Send embed
            embed = discord.Embed(
                title="🏳️‍🌈 Gay Rate", 
                description=f"**{user.mention} is {random.randint(0, 100)}% gay!**", 
                color=0xFF0000
            )
            embed.set_image(url="attachment://gay.png")
            await ctx.send(embed=embed, file=file)
            
        except Exception as e:
            print(f"Gay command error: {e}")
            await ctx.send(view=CV2("🏳️‍🌈 Gay Rate", f"**{user.mention} is {random.randint(0, 100)}% gay!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def lesbian(self, ctx, user: discord.Member = None):
        """Executes the lesbian command."""
        user = user or ctx.author
        await ctx.send(view=CV2("🏳️‍🌈 Lesbian Rate", f"**{user.mention} is {random.randint(0, 100)}% lesbian!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def chutiya(self, ctx, user: discord.Member = None):
        """Executes the chutiya command."""
        user = user or ctx.author
        await ctx.send(view=CV2("🤡 Chutiya Rate", f"**{user.mention} is {random.randint(0, 100)}% chutiya!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def horny(self, ctx, user: discord.Member = None):
        """Executes the horny command."""
        user = user or ctx.author
        await ctx.send(view=CV2("💦 Horny Meter", f"**{user.mention} is {random.randint(0, 100)}% horny!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def chat(self, ctx, *, message: str = None):
        """Executes the chat command."""
        await ctx.send(view=CV2("🤖 AI Chat", "**To use the AI Chat, simply mention me or reply to my messages!**"))

async def setup(bot):
    await bot.add_cog(Fun(bot))