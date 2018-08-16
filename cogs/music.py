'''Copyright © 2018 F4stZ4p

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
"""
Please understand Music bots are complex, and that even this basic example can be daunting to a beginner.
For this reason it's highly advised you familiarize yourself with discord.py, python and asyncio, BEFORE
you attempt to write a music bot.
This example makes use of: Python 3.6
For a more basic voice example please read:
    https://github.com/Rapptz/discord.py/blob/rewrite/examples/basic_voice.py
This is a very basic playlist example, which allows per guild playback of unique queues.
The commands implement very basic logic for basic usage. But allow for expansion. It would be advisable to implement
your own permissions and usage logic for commands.
e.g You might like to implement a vote before skipping the song or only allow admins to stop the player.
Music bots require lots of work, and tuning. Goodluck.
If you find any bugs feel free to ping me on discord. @Eviee#0666 / @F4stZ4p#2061
"""
import discord
from discord.ext import commands

import asyncio
import itertools, datetime
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL
from discord.ext.commands.cooldowns import BucketType

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin -preset ultrafast',
    'options': '-vn -threads 1'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')

        if self.title is None:
            self.title = "No title available"

        self.web_url = data.get('webpage_url')
        self.thumbnail = data.get('thumbnail')

        if self.thumbnail is None:
            self.thumbnail = "http://ppc.tools/wp-content/themes/ppctools/img/no-thumbnail.jpg"

        self.duration = data.get('duration')

        if self.duration is None:
            self.duration = 0

        self.uploader = data.get('uploader')

        if self.uploader is None:
            self.uploader = "Unknown uploader"

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send(f':notes: Added to queue: **{data["title"]}**')

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = (
    'bot', '_guild', '_ctxs', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume', 'buttons', 'music',
    'music_controller', 'restmode')

    def __init__(self, ctx):

        self.buttons = {'⏯': 'rp',
                        '⏭': 'skip',
                        '➕': 'vol_up',
                        '➖': 'vol_down',
                        '🖼': 'thumbnail',
                        '⏹': 'stop',
                        'ℹ': 'queue',
                        '❔': 'tutorial'}

        self.bot = ctx.bot
        self._guild = ctx.guild
        self._ctxs = ctx
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None
        self.volume = .5
        self.current = None
        self.music_controller = None

        ctx.bot.loop.create_task(self.player_loop())

    async def buttons_controller(self, guild, current, source, channel, context):
        vc = guild.voice_client
        vctwo = context.voice_client

        for react in self.buttons:
            await current.add_reaction(str(react))

        def check(r, u):
            if not current:
                return False
            elif str(r) not in self.buttons.keys():
                return False
            elif u.id == self.bot.user.id or r.message.id != current.id:
                return False
            elif u not in vc.channel.members:
                return False
            return True

        while current:
            if vc is None:
                return False

            react, user = await self.bot.wait_for('reaction_add', check=check)
            control = self.buttons.get(str(react))

            if control == 'rp':
                if vc.is_paused():
                    vc.resume()
                else:
                    vc.pause()

            if control == 'skip':
                vc.stop()

            if control == 'stop':
                await channel.send('**:notes: Ok, goodbye!**', delete_after=5)
                await self._cog.cleanup(guild)

                try:
                    self.music_controller.cancel()
                except:
                    pass

            if control == 'vol_up':
                player = self._cog.get_player(context)
                if vctwo.source:
                    if not vctwo.source.volume > 100 or player.volume > 100:
                        vctwo.source.volume += 5
                        player.volume += 5

            if control == 'vol_down':
                player = self._cog.get_player(context)
                if vctwo.source:
                    if not vctwo.source.volume < 10 or player.volume < 10:
                        vctwo.source.volume -= 5
                        player.volume -= 5

            if control == 'thumbnail':
                await channel.send(embed=discord.Embed(color=0xA90000).set_image(url=source.thumbnail).set_footer(
                    text=f"Requested by {source.requester} | Video: {source.title}",
                    icon_url=source.requester.avatar_url), delete_after=10)

            if control == 'tutorial':
                await channel.send(embed=discord.Embed(color=0xA90000).add_field(name="Cheat sheet:",
                                                                                 value="⏯ - Resume or pause player\n⏭ - Skip song\n➕ - Volume up\n➖ - Volume down\n🖼 - Get song thumbnail\n⏹ - Stop music session\nℹ - Player queue\n❔ - Shows you how to use Music Controller"),
                                   delete_after=10)

            if control == 'queue':
                await self._cog.queue_info(context)

            if control == 'lyrics':
                await self._cog.search_lyrics(context, source.uploader, source.title)

            try:
                await current.remove_reaction(react, user)
            except discord.HTTPException:
                pass

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with timeout(3500):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f':notes: There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source
            try:
                self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            except Exception:
                continue
            embednps = discord.Embed(color=0xA90000)
            embednps.add_field(name=":notepad_spiral: Song title:", value=f"```fix\n{source.title}```", inline=False)
            embednps.add_field(name=":trumpet: Requested by:", value=f"**{source.requester}**", inline=True)
            embednps.add_field(name=":link: Song URL:", value=f"**[URL]({source.web_url})**", inline=True)
            embednps.add_field(name=":spy: Uploader:", value=f"**{source.uploader}**", inline=True)
            embednps.add_field(name=":alarm_clock: Song duration:",
                               value=f"**{datetime.timedelta(seconds=source.duration)}**", inline=True)
            embednps.set_thumbnail(url=f"{source.thumbnail}")
            self.np = await self._channel.send(embed=embednps)

            self.music_controller = self.bot.loop.create_task(
                self.buttons_controller(self._guild, self.np, source, self._channel, self._ctxs))
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
                self.music_controller.cancel()
            except Exception:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music:
    """Music related commands."""

    __slots__ = ('bot', 'players', 'musictwo', 'music_controller')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(':notes: This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send(":notes: Please join voice channel or specify one with command!")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='connect', aliases=['join'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel = None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send(":notes: Please join voice channel or specify one with command!")

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(
                    f'<:naokoyoutube:447656968937537546> Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(
                    f'<:naokoyoutube:447656968937537546> Connecting to channel: <{channel}> timed out.')

        await ctx.send(f":notes: Connected to channel: **{channel}**", delete_after=20)

    @commands.command(name='play', aliases=['sing'])
    @commands.cooldown(1.0, 15.0, commands.BucketType.guild)
    async def play_(self, ctx, *, search: str):
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        elif ctx.author not in ctx.guild.voice_client.channel.members:
            return await ctx.send(":notes: Please join my voice channel to execute this command.", delete_after=20)

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)
        await player.queue.put(source)

    @commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
    @commands.cooldown(1.0, 15.0, commands.BucketType.guild)
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                ":notes: I am not connected to voice or playing anything. Join or specify one with command join.",
                delete_after=20)

        elif ctx.author not in ctx.guild.voice_client.channel.members:
            return await ctx.send(":notes: Please join my voice channel to execute this command.", delete_after=20)

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send(
                ":notes: I am not connected to voice or playing anything. Join or specify one with command join.",
                delete_after=20)

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        embednp = discord.Embed(color=0xA90000)
        embednp.add_field(name=":notepad_spiral: Song title:", value=f"```fix\n{vc.source.title}```", inline=False)
        embednp.add_field(name=":trumpet: Requested by:", value=f"**{vc.source.requester}**", inline=True)
        embednp.add_field(name=":link: Song URL:", value=f"**[URL]({vc.source.web_url})**", inline=True)
        embednp.add_field(name=":spy: Uploader:", value=f"**{vc.source.uploader}**", inline=True)
        embednp.add_field(name=":alarm_clock: Song duration:",
                          value=f"**{datetime.timedelta(seconds=vc.source.duration)}**", inline=True)
        embednp.set_thumbnail(url=f"{vc.source.thumbnail}")
        player.np = await ctx.send(embed=embednp)
        self.music_controller = self.bot.loop.create_task(
            MusicPlayer(ctx).buttons_controller(ctx.guild, player.np, vc.source, ctx.channel, ctx))

    async def queue_info(self, ctx):
        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('**:notes: There are currently no more queued songs.**')

        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'Queue - Next {len(upcoming)}', description=fmt, color=0xA90000)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))
