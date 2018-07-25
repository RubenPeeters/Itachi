import requests
import aiohttp
from bs4 import BeautifulSoup
import copy
import discord
import discord.ext.commands as commands
from .utils import checks


def setup(bot):
    bot.add_cog(lookup(bot))


class lookup:
    def __init__(self, bot):
        self.bot = bot
        self.errorchannelid = 467672989232529418

# The link you want to lookup
    @commands.group(invoke_without_command=True)
    @checks.is_lookup_enabled()
    async def opgg(self, ctx, server: str, *, player: str):
        '''Look up a player on opgg'''
        for x in self.bot.guilds:
            for chan in x.channels:
                if chan.id == self.errorchannelid:
                    errorchannel = chan
        http = "http://"
        original = ".op.gg/summoner/userName="
        link = http + server + original + player
        # The HTML text from the given link
        try:
            async with aiohttp.ClientSession() as session:
                html = await self.fetch(session, link)
        except:
            embed = discord.Embed(title="{}".format(ctx.message.content))
            embed.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
            embed.description = "Sorry, but this is not an existing server and/or player."
            await ctx.send(embed=embed)
        else:
            # Create a BeautifulSoup object
            try:
                soup = BeautifulSoup(html, "html.parser")

                res = soup.find_all('meta')
                srcs = [img['src'] for img in soup.find_all('img', class_='ProfileImage')]
            except:
                embed = discord.Embed(title="{}".format(ctx.message.content))
                embed.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
                embed.description = "Sorry, but bs4 didn't work"
                await ctx.send(embed=embed)

            # Current format srcs[0]: //opgg-static.akamaized.net/images/profile_icons/profileIcon3103.jpg

            image_link = "https:" + srcs[0]

            # Current format of infostring: 'name / rank / W L winrate / Most played champions'

            infostring = res[3].get('content')
            splitinfostring = infostring.split("/")

            # Current format of splitinfostring: ['name', 'rank', ' W L winrate ', ' Most played champions (5)']

            player_name = str(copy.deepcopy(splitinfostring[0]))
            player_rank = str(copy.deepcopy(splitinfostring[1]))
            player_winrate = str(copy.deepcopy(splitinfostring[2]))
            player_most_played = str(copy.deepcopy(splitinfostring[3]))
            player_most_played_split = player_most_played.split(',')

            embed = discord.Embed(title="OP.GG Lookup for {}".format(player_name), color=0xA90000)
            embed.set_thumbnail(url="{}".format(image_link))
            embed.add_field(name="__Rank__ ", value="{}".format(player_rank))
            embed.add_field(name="__Winrate__ ", value="{}".format(player_winrate))
            try:
                champs = ""
                for f in player_most_played_split:
                    champs = champs + f.strip() + "\n"
                embed.add_field(name="__Most played champions__", value="{}".format(champs), inline=False)
            except Exception as e:
                exc = "{}: {}".format(type(e).__name__, e)
                await errorchannel.send(
                    'Failed to send opgg\n{}\n{}'.format(exc, ctx.guild.name))
                print('Failed to send opgg\n{}'.format(exc))
            await ctx.send(embed=embed)

    @opgg.command()
    @checks.is_lookup_enabled()
    async def champion(self, ctx, role: str, *, champion: str):
        '''Display an opgg champion link'''

        http = "http://www.op.gg/champion/"
        rest = "/statistics/"
        link = http + champion + rest + role
        # The HTML text from the given link
        try:
            async with aiohttp.ClientSession() as session:
                html = await self.fetch(session, link)
        except:
            embed = discord.Embed(title="{}".format(ctx.message.content), color=0xA90000)
            embed.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
            embed.description = "Sorry, but this is not an existing champion and/or role."
            await ctx.send(embed=embed)
        else:
            await ctx.send(link)


    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

