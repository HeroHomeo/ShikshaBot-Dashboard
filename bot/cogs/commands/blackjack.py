import discord
from discord.ext import commands
import random
import asyncio
from utils.Tools import blacklist_check, ignore_check
from utils.cv2 import CV2, build_container
from discord.ui import LayoutView, TextDisplay, Separator

class CV2(LayoutView):
    def __init__(self, title, *sections):
        super().__init__(timeout=None)
        items = [TextDisplay(f"**{title}**")]
        for s in sections:
            if s:
                items.append(Separator(visible=True))
                items.append(TextDisplay(str(s)))
        self.add_item(build_container(*items))

class Card:
    suits = ["♣️", "♦️", "♥️", "♠️"]
    names = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    values = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11}

    def __init__(self, suit, name):
        self.suit = suit
        self.name = name
        self.value = self.values[name]
        self.down = False

    def __str__(self):
        if self.down:
            return "🎴"
        return f"`{self.name}{self.suit}`"

def calculate_hand(hand):
    total = sum(c.value for c in hand if not c.down)
    aces = sum(1 for c in hand if c.name == "A" and not c.down)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['bj', 'blackjacks'], help="Play a simple game of blackjack.", usage="blackjack")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def blackjack(self, ctx: commands.Context):
        deck = [Card(suit, name) for suit in Card.suits for name in Card.names]
        random.shuffle(deck)

        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        dealer_hand[1].down = True

        def get_embed(title, status=""):
            p_score = calculate_hand(player_hand)
            d_score = calculate_hand(dealer_hand)
            
            p_cards = " ".join(str(c) for c in player_hand)
            d_cards = " ".join(str(c) for c in dealer_hand)
            
            desc = f"**Your Hand ({p_score})**: {p_cards}\n**Dealer's Hand ({d_score})**: {d_cards}\n\n{status}"
            return CV2(title, desc)

        msg = await ctx.send(view=get_embed("🎰 Blackjack"))
        
        await msg.add_reaction("🇭") # Hit
        await msg.add_reaction("🇸") # Stand
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["🇭", "🇸"] and reaction.message.id == msg.id

        standing = False
        while True:
            if calculate_hand(player_hand) == 21:
                standing = True
                break
            elif calculate_hand(player_hand) > 21:
                break

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                await msg.remove_reaction(reaction.emoji, ctx.author)
            except asyncio.TimeoutError:
                await msg.delete()
                return

            if str(reaction.emoji) == "🇭":
                player_hand.append(deck.pop())
            elif str(reaction.emoji) == "🇸":
                standing = True
                break

            await msg.edit(view=get_embed("🎰 Blackjack - Your Turn"))

        dealer_hand[1].down = False
        
        if standing:
            while calculate_hand(dealer_hand) < 17:
                dealer_hand.append(deck.pop())

        p_score = calculate_hand(player_hand)
        d_score = calculate_hand(dealer_hand)

        if p_score > 21:
            title, status = "💥 BUST!", "**You busted! Dealer wins.**"
        elif d_score > 21:
            title, status = "🎉 YOU WIN!", "**Dealer busted! You win!**"
        elif p_score == 21 and len(player_hand) == 2:
            title, status = "🔥 BLACKJACK!", "**You hit Blackjack! You win!**"
        elif d_score == p_score:
            title, status = "🤝 PUSH!", "**It's a tie!**"
        elif p_score > d_score:
            title, status = "🎉 YOU WIN!", "**You beat the dealer!**"
        else:
            title, status = "😭 YOU LOSE!", "**Dealer wins!**"

        await msg.edit(view=get_embed(title, status))

async def setup(bot):
    pass