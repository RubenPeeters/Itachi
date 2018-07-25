import discord
import discord.ext.commands as commands
import random
import asyncio
from .utils import checks
from .utils.paginator import HelpPaginator, CannotPaginate
import requests
import io
from cogs.utils.fortunes import fortunes
from cogs.utils.lists import *
import aiohttp



def setup(bot):
    bot.add_cog(miscellaneous(bot))

class miscellaneous:
    def __init__(self, bot):
        self.bot = bot
        bot.remove_command("help")

    async def fetch_img(self, session, url):
        async with session.get(url) as response:
            assert response.status == 200
            return await response.read()

    def url_to_bytes(self, url):
        data = requests.get(url)
        content = io.BytesIO(data.content)
        filename = url.rsplit("/", 1)[-1]
        return {"content": content, "filename": filename}

    async def get_feedbackchannel(self):
        for x in self.bot.guilds:
            if x.id == 457833113771442201:
                feedback_channel = discord.utils.get(x.channels, id=468338554532134922)
        return feedback_channel

    @commands.command(name="8ball", aliases=["eight ball", "eightball", "8-ball"], pass_context = "True")
    @checks.is_misc_enabled()
    async def eight_ball(self,ctx):
        '''Responds to yes or no questions'''
        possible_responses = [
            "That is a resounding no",
            "It is not looking likely",
            "Too hard to tell",
            "It is quite possible",
            "Definitely",
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes - definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy, try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",


        ]
        await ctx.send(random.choice(possible_responses) + ", " + ctx.message.author.mention)

    @commands.command(name='help')
    async def _help(self, ctx, *, command: str = None):
        """Shows help about a command or the bot"""
        if command is None:
            p = await HelpPaginator.from_bot(ctx)
        else:
            entity = self.bot.get_cog(command) or self.bot.get_command(command)

            if entity is None:
                clean = command.replace('@', '@\u200b')
                return await ctx.send(f'Command or category "{clean}" not found.')
            elif isinstance(entity, commands.Command):
                p = await HelpPaginator.from_command(ctx, entity)
            else:
                p = await HelpPaginator.from_cog(ctx, entity)

        await p.paginate()


    @commands.command()
    @checks.is_misc_enabled()
    async def donger(self, ctx, choice: str, *, amount: int =1):
        '''Send a specified donger'''
        try:
            await ctx.message.delete()
        except:
            await ctx.message.add_reaction('\N{CROSS MARK}')

        dict = {"shrug": "¯\\_(ツ)_/¯",
                "flip": "(╯°□°）╯︵ ┻━┻",
                "unflip": "┬─┬﻿ノ( ゜-゜ノ)",
                "lenny": "( ͡° ͜ʖ ͡°)",
                "fite": "(ง’̀-‘́)ง"}
        await ctx.send((dict[choice]) * amount)

    @commands.command()
    @checks.is_misc_enabled()
    async def flip(self, ctx, user : discord.Member=None):
        """Flips a coin... or a user.
        Defaults to coin.
        """
        if user != None:
            msg = ""
            if user.id == self.bot.user.id:
                user = ctx.message.author
                msg = "Nice try. You think this is funny? How about *this* instead:\n\n"
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            return await ctx.send(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            return await ctx.send("*flips a coin and... " + random.choice(["HEADS!*", "TAILS!*"]))

    @commands.command()
    @checks.is_misc_enabled()
    async def choose(self, ctx,*choices):
        """Chooses between multiple choices.
        To denote multiple choices, you should use double quotes.
        """
        if len(choices) < 2:
            await ctx.send('Not enough choices to pick from.')
        else:
            await ctx.send(random.choice(choices))

    @commands.command()
    @checks.is_misc_enabled()
    async def feedback(self, ctx, command: str, *, feedback: str):
        """Allows you to send feedback about a command or in general about the bot
        Usage: [p]feedback {topic} {actual feedback}"""

        for x in self.bot.guilds:
            for chan in x.channels:
                if chan.id == 468338554532134922:
                    feedback_channel = chan

        await feedback_channel.send("**{}**\n"
                                        "**{}**: {}\n"
                                        "__**{}**__: \n"
                                        "{}".format(ctx.author.display_name, ctx.guild.name, ctx.guild.id, command,
                                                    feedback))
        await ctx.send("Your feedback was sent to the owner!\n"
                 "Thanks for helping to improve the bot <:blobpats:464514305610743828>")

    @commands.command()
    async def invite(self, ctx):
        await ctx.send("With this link you can invite me to your server. <https://discordapp.com/api/oauth2/authorize?client_id=457838617633488908&scope=bot&permissions=473052286>.")

    @commands.command()
    async def vote(self, ctx):
        await ctx.send("You can vote for me here. https://discordbots.org/bot/457838617633488908.\n"
                       "Votes are very much appreciated.")

    @commands.command(aliases=['pat'])
    async def headpat(self, ctx, member: discord.Member):
        """Posts a random headpat from headp.at"""
        embed = discord.Embed(color=0xA90000, title="**Good pat, yes.**",description=f"{ctx.author.mention} pats {member.mention}")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://headp.at/js/pats.json") as resp:
                pat = random.choice(await resp.json())
        file = self.url_to_bytes("http://headp.at/pats/{}".format(pat))
        embed.set_image(url="attachment://file.png")
        embed.set_footer(icon_url=self.bot.user.avatar_url, text="headp.at")
        await ctx.send(embed=embed, file=discord.File(file["content"], "file.png"))

    @commands.command(aliases=["doggo"])
    async def dog(self, ctx):
        """Posts a random dog"""
        embed = discord.Embed(color=0xA90000, title="**DOG <a:owo:464531597702725632>**")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as resp:
                pat = await resp.json()
        embed.set_image(url=pat["message"])
        embed.set_footer(icon_url=self.bot.user.avatar_url, text="dog.ceo")
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def hug(self, ctx, user: discord.Member = None):
        """Hug your senpai/waifu!"""
        if user is None:
            await ctx.send("Mention your waifu/senpai!")


    @commands.command(aliases=["cate"])
    async def cat(self, ctx):
        """Posts a random cat"""
        embed = discord.Embed(color=0xA90000, title="**CAT <:meow0w0:468426081796358155>**")
        url = "https://cataas.com/cat"
        async with aiohttp.ClientSession() as session:
            img = await self.fetch_img(session, url)
            with open("img.png", "wb") as f:
                f.write(img)
        file = discord.File(open("img.png", "rb"), "img.png")
        embed.set_image(url="attachment://img.png")
        embed.set_footer(icon_url=self.bot.user.avatar_url, text="cataas.com")
        await session.close()
        await ctx.send(embed=embed, file=file)

    @commands.command(aliases=["rev"])
    async def reverse(self, ctx, *, msg: str):
        """ffuts esreveR"""
        await ctx.send(msg[::-1])

    @commands.command()
    async def intellect(self, ctx, *, msg:str):
        """Me, an intellectual"""
        await ctx.channel.trigger_typing()
        intellectify = ""
        for char in msg:
            intellectify += random.choice([char.upper(), char.lower()])
        await ctx.send(intellectify)

    @commands.command()
    async def fight(self, ctx, user: str = None, *, weapon: str = None):
        """Fight someone with something"""
        if user is None or user.lower() == ctx.author.mention or user == ctx.author.name.lower() or ctx.guild is not None and ctx.author.nick is not None and user == ctx.author.nick.lower():
            await ctx.send("{} fought themself but only ended up in a mental hospital!".format(ctx.author.mention))
            return
        if weapon is None:
            await ctx.send(
                "{0} tried to fight {1} with nothing so {1} beat the breaks off of them!".format(ctx.author.mention,
                                                                                                 user))
            return
        await ctx.send("{} used **{}** on **{}** {}".format(ctx.author.mention, weapon, user,
                                                            random.choice(fight_results).replace("%user%",
                                                                                                 user).replace(
                                                                "%attacker%", ctx.author.mention)))

    @commands.command()
    async def fortune(self, ctx):
        """Get your fortune read, not as authentic as a fortune cookie."""
        await ctx.send("```{}```".format(random.choice(fortunes)))

    @commands.command()
    async def insult(self, ctx, *, user: str):
        """Insult those ass wipes"""
        await ctx.send("{} {}".format(user, random.choice(insults)))