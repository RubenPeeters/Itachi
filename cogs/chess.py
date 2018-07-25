import chess
import chess.svg
import discord
from discord.ext import commands
import numpy
import asyncio
import json
import cairosvg



def setup(bot):
    bot.add_cog(ChessCog(bot))


class ChessCog:
    def __init__(self, bot):
        self.bot = bot
        self.chess = []

    @commands.command(name="chess", aliases=['yikes'])
    async def _chess(self, ctx):
        """Play a game of Chess."""
        if ctx.channel.id in self.chess:
            return await ctx.send(
                'There is already a Chess game in this channel. Please wait for it to finish.')

        joiner = discord.Embed(description=f'{ctx.author.display_name} wants to play Chess!\n\n'
                                           f'React with ☑ to join!')
        joiner.set_footer(text='This will be valid for 5 minutes.')
        joiner.set_thumbnail(url='https://vignette.wikia.nocookie.net/mlp/images/0/00/PonyMaker_Chess.png/revision/latest?cb=20120407173351')

        msg = await ctx.send(embed=joiner)
        try:
            await msg.add_reaction('☑')
        except discord.HTTPException:
            pass

        try:
            # Can reuse the connect four loop
            user = await self.chessjoin_loop(ctx)
        except asyncio.TimeoutError:
            return await ctx.send(f'{ctx.author.mention}. No one joined within 5 minutes, please try again!',
                                  delete_after=30)
        finally:
            await msg.delete()

        self.chess.append(ctx.channel.id)
        _chess = Chess(ctx.author, user, ctx)

        embed = _chess.generate_board()
        board_message = await ctx.send(embed=embed, file=_chess.get_board())

        self.bot.loop.create_task(_chess.play_loop(ctx, board_message))

    async def chessjoin_loop(self, ctx: commands.Context):
        def check(r, u):
            if u == ctx.me:
                return False
            return str(r) == '☑'

        while True:
            react, user = await self.bot.wait_for('reaction_add', check=check, timeout=300)

            return user


class Chess:
    __slots__ = ('board', 'new', 'player_one', 'player_two', 'turn', 'board_message', 'channel', 'lastmove', 'analyze', 'flipped')

    def __init__(self, one: discord.Member, two: discord.Member, ctx):
        self.board = chess.Board()
        self.board_message = None
        self.player_one = (one, "<:whitepawn:469994694076530730> WHITE")
        self.player_two = (two, "<:blackpawn:469994682940653588> BLACK")
        self.turn = 0
        self.analyze = None
        self.flipped = False
        self.new = False
        self.channel = ctx.channel.id
        self.lastmove = None

    def get_board(self):
        svg_data = chess.svg.board(self.board, lastmove=self.lastmove, style="""
text {
    fill: #5B80FF;
    font-weight: bold;
}
""", flipped=self.flipped)
        png_string = "board" + str(self.channel) + ".png"
        cairosvg.svg2png(bytestring=svg_data, write_to=png_string)
        file = discord.File(open(png_string, "rb"), "board.png")
        return file


    def current_player(self):
        return self.turn % 2

    def generate_board(self):
        embed = discord.Embed(colour=0x36393E)
        embed.set_image(url="attachment://board.png")
        embed.set_footer(text='Enter your move like this: e2e4. \n'
                              'This moves the piece on e2 to e4.')

        if self.current_player() == 0:
            embed.add_field(name='\u200b', value=f'{self.player_one[1]} = {self.player_one[0].display_name} <---\n'
                                                 f'{self.player_two[1]} = {self.player_two[0].display_name}')
            embed.set_thumbnail(url=self.player_one[0].avatar_url)
        else:
            embed.add_field(name='\u200b', value=f'{self.player_one[1]} = {self.player_one[0].display_name}\n'
                                                 f'{self.player_two[1]} = {self.player_two[0].display_name} <---')
            embed.set_thumbnail(url=self.player_two[0].avatar_url)

        return embed

    async def play_loop(self, ctx, board):
        self.board_message = board
        cog = ctx.bot.get_cog('ChessCog')

        def check(msg):
            if self.current_player() == 0:
                return self.player_one[0] == msg.author
            else:
                return self.player_two[0] == msg.author

        while True:
            if self.current_player() == 0:
                self.flipped = True
                player = self.player_one
                opposite = self.player_two
            else:
                self.flipped = False
                player = self.player_two
                opposite = self.player_one

            try:
                message = await ctx.bot.wait_for('message', check=check, timeout=180)
            except asyncio.TimeoutError:
                cog.chess.remove(ctx.channel.id)

                await self.board_message.delete()
                await ctx.send(embed=self.generate_winner(opposite), file=self.get_board())
                return await ctx.send(f'{player[0].mention} has taken too long to move.'
                                      f' {opposite[0].mention} wins by default.')

            if any(n == message.content for n in ['quit', 'end', 'die', 'ff', 'surrender']):
                cog.chess.remove(ctx.channel.id)
                await self.board_message.delete()
                await ctx.send(embed=self.generate_winner(opposite), file=self.get_board())
                return await ctx.send(f'{player[0].mention} has quit the game. {opposite[0].mention} wins by default.')
            try:
                move_str = str(message.content)
                move = chess.Move.from_uci(move_str)
            except ValueError:
                continue
            try:
                await message.delete()
            except discord.HTTPException:
                pass
            if not move in self.board.legal_moves:
                await ctx.send("That is not a legal move!")
                continue
            self.turn += 1
            await self.make_move(move)
            await self.board_message.delete()

            if self.board.is_checkmate():
                cog.chess.remove(ctx.channel.id)
                return await ctx.send(embed=self.generate_winner(player), file=self.get_board())
            if self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.is_seventyfive_moves() \
                    or self.board.is_fivefold_repetition():
                cog.chess.remove(ctx.channel.id)
                return await ctx.send(embed=self.generate_draw(player), file=self.get_board())
            self.board_message = await ctx.send(embed=self.generate_board(), file=self.get_board())


    async def make_move(self, move):
        self.board.push(move)
        self.lastmove = move

    def generate_draw(self):
        embed = discord.Embed(title=f'Draw!', colour=0x36393E)
        embed.set_image(url="attachment://board.png")

        embed.add_field(name='\u200b', value=f'{self.player_one[1]} = {self.player_one[0].display_name}\n'
                                             f'{self.player_two[1]} = {self.player_two[0].display_name}'
                                             f'\n\n'
                                             f'**The game has ended in a Draw!**')
        embed.set_thumbnail(url='https://vignette.wikia.nocookie.net/mlp/images/0/00/PonyMaker_Chess.png/revision/latest?cb=20120407173351')

        return embed

    def generate_winner(self, winner):
        embed = discord.Embed(title=f'{winner[0].display_name} Wins!', colour=0x36393E)
        embed.set_image(url="attachment://board.png")

        if winner == self.player_one:
            embed.add_field(name='\u200b',
                            value=f'{self.player_one[1]} = **{self.player_one[0].display_name}** (Wins)\n'
                                  f'{self.player_two[1]} = {self.player_two[0].display_name}'
                                  f'\n\n'
                                  f'**{winner[0].display_name}** won the game in **{self.turn}** turns')
            embed.set_thumbnail(url=winner[0].avatar_url)
        else:
            embed.add_field(name='\u200b', value=f'{self.player_one[1]} = {self.player_one[0].display_name}\n'
                                                 f'{self.player_two[1]} = **{self.player_two[0].display_name}** (Wins)'
                                                 f'\n\n'
                                                 f'**{winner[0].display_name}** won the game in **{self.turn}** turns.')
            embed.set_thumbnail(url=winner[0].avatar_url)
        return embed




