import discord
from discord.ext import commands
import numpy
import asyncio
import json
import chess
import chess.svg
import cairosvg



def setup(bot):
    bot.add_cog(Fun(bot))


class Fun:
    def __init__(self, bot):
        self.bot = bot
        self.c4 = []

    @commands.command(name='connect4', aliases=['c4'])
    async def connect_four(self, ctx):
        """Play a game of Connect Four."""
        if ctx.channel.id in self.c4:
            return await ctx.send('There is already a Connect Four game in this channel. Please wait for it to finish.')

        joiner = discord.Embed(description=f'{ctx.author.display_name} wants to play Connect Four!\n\n'
                                           f'React with ☑ to join!')
        joiner.set_footer(text='This will be valid for 5 minutes.')
        joiner.set_thumbnail(url='https://i.imgur.com/BF6KD1E.png')

        msg = await ctx.send(embed=joiner)
        try:
            await msg.add_reaction('☑')
        except discord.HTTPException:
            pass

        try:
            user = await self.c4join_loop(ctx)
        except asyncio.TimeoutError:
            return await ctx.send(f'{ctx.author.mention}. No one joined within 5 minutes, please try again!',
                                  delete_after=30)
        finally:
            await msg.delete()

        self.c4.append(ctx.channel.id)
        c4 = ConnectFour(ctx.author, user)

        embed = c4.generate_board()
        board = await ctx.send(embed=embed)

        self.bot.loop.create_task(c4.play_loop(ctx, board))




    async def c4join_loop(self, ctx: commands.Context):
        def check(r, u):
            if u == ctx.me:
                return False
            return str(r) == '☑'

        while True:
            react, user = await self.bot.wait_for('reaction_add', check=check, timeout=300)

            return user


class ConnectFour:
    __slots__ = ('FIELD', 'board', 'new', 'numbers', 'end', 'player_one', 'player_two', 'top', 'turn', 'winner',
                 'amount', 'loser')

    ROWS = 6
    COLS = 7

    def __init__(self, one: discord.Member, two: discord.Member):
        self.FIELD = [['⚫' for _ in range(7)] for _ in range(6)]
        self.board = None
        self.winner = None
        self.loser = None
        self.new = False
        self.numbers = [f'{n}\u20E3' for n in range(1, 8)]
        self.end = False
        self.top = 5
        self.player_one = (one, '🔴')
        self.player_two = (two, '🔵')

        self.turn = 0

    def is_valid(self, c):
        return self.FIELD[self.top][c] == '⚫'

    def next_open(self, c):
        for r in range(self.ROWS):
            if self.FIELD[r][c] == '⚫':
                return r

    def make_move(self, r, c, player):
        self.FIELD[r][c] = player[1]

    def check_win(self, player):
        for c in range(self.COLS - 3):
            for r in range(self.ROWS):
                if self.FIELD[r][c] == player[1] and \
                        self.FIELD[r][c + 1] == player[1] and \
                        self.FIELD[r][c + 2] == player[1] and \
                        self.FIELD[r][c + 3] == player[1]:
                    return True

        for c in range(self.COLS):
            for r in range(self.ROWS - 3):
                if self.FIELD[r][c] == player[1] and \
                        self.FIELD[r + 1][c] == player[1] and \
                        self.FIELD[r + 2][c] == player[1] and \
                        self.FIELD[r + 3][c] == player[1]:
                    return True

        for c in range(self.COLS - 3):
            for r in range(self.ROWS - 3):
                if self.FIELD[r][c] == player[1] and \
                        self.FIELD[r + 1][c + 1] == player[1] and \
                        self.FIELD[r + 2][c + 2] == player[1] and \
                        self.FIELD[r + 3][c + 3] == player[1]:
                    return True

        for c in range(self.COLS - 3):
            for r in range(3, self.ROWS):
                if self.FIELD[r][c] == player[1] and \
                        self.FIELD[r - 1][c + 1] == player[1] and \
                        self.FIELD[r - 2][c + 2] == player[1] and \
                        self.FIELD[r - 3][c + 3] == player[1]:
                    return True

    def generate_field(self):
        fields = []

        for _ in self.FIELD:
            line = ''.join(str(e) for e in _)
            fields.append(line)

        fields.append(''.join(self.numbers))
        fields = numpy.flip(fields, 0) # flip the array vertically

        field = '\n'.join(line for line in fields)
        return field

    def generate_board(self):
        field = self.generate_field()
        embed = discord.Embed(description=field, colour=0x36393E)
        embed.set_footer(text='Enter your number to make a move.')

        if self.current_player() == 0:
            embed.add_field(name='\u200b', value=f'{self.player_one[1]} = {self.player_one[0].display_name} <---\n'
                                                 f'{self.player_two[1]} = {self.player_two[0].display_name}')
            embed.set_thumbnail(url=self.player_one[0].avatar_url)
        else:
            embed.add_field(name='\u200b', value=f'{self.player_one[1]} = {self.player_one[0].display_name}\n'
                                                 f'{self.player_two[1]} = {self.player_two[0].display_name} <---')
            embed.set_thumbnail(url=self.player_two[0].avatar_url)

        return embed

    def generate_winner(self, winner):
        field = self.generate_field()
        embed = discord.Embed(title=f'{winner[0].display_name} Wins!', description=field, colour=0x36393E)

        if winner == self.player_one:
            embed.add_field(name='\u200b',
                            value=f'{self.player_one[1]} = **{self.player_one[0].display_name}** (Wins)\n'
                                  f'{self.player_two[1]} = {self.player_two[0].display_name}'
                                  f'\n\n'
                                  f'**{winner[0].display_name}** won the game in **{self.turn}** turns')
            embed.set_thumbnail(url=winner[0].avatar_url)
            self.winner = self.player_one[0]
            self.loser = self.player_two[0]
        else:
            embed.add_field(name='\u200b', value=f'{self.player_one[1]} = {self.player_one[0].display_name}\n'
                                                 f'{self.player_two[1]} = **{self.player_two[0].display_name}** (Wins)'
                                                 f'\n\n'
                                                 f'**{winner[0].display_name}** won the game in **{self.turn}** turns.')
            embed.set_thumbnail(url=winner[0].avatar_url)
            self.winner = self.player_two[0]
            self.loser = self.player_one[0]
        return embed

    def generate_draw(self):
        field = self.generate_field()
        embed = discord.Embed(title=f'Draw!', description=field, colour=0x36393E)

        embed.add_field(name='\u200b', value=f'{self.player_one[1]} = {self.player_one[0].display_name}\n'
                                             f'{self.player_two[1]} = {self.player_two[0].display_name}'
                                             f'\n\n'
                                             f'**The game has ended in a Draw!**')
        embed.set_thumbnail(url='https://i.imgur.com/BF6KD1E.png')

        return embed

    def current_player(self):
        return self.turn % 2


    async def play_loop(self, ctx, board):
        self.board = board
        cog = ctx.bot.get_cog('Fun')

        def check(msg):
            if self.current_player() == 0:
                return self.player_one[0] == msg.author
            else:
                return self.player_two[0] == msg.author

        while True:
            if self.current_player() == 0:
                player = self.player_one
                opposite = self.player_two
            else:
                player = self.player_two
                opposite = self.player_one

            try:
                message = await ctx.bot.wait_for('message', check=check, timeout=180)
            except asyncio.TimeoutError:
                cog.c4.remove(ctx.channel.id)

                await self.board.delete()
                await ctx.send(embed=self.generate_winner(opposite))
                return await ctx.send(f'{player[0].mention} has taken too long to move.'
                                      f' {opposite[0].mention} wins by default.')

            if any(n == message.content for n in ['quit', 'end', 'die', 'ff', 'surrender']):
                cog.c4.remove(ctx.channel.id)
                await self.board.delete()
                await ctx.send(embed=self.generate_winner(opposite))
                return await ctx.send(f'{player[0].mention} has quit the game. {opposite[0].mention} wins by default.')

            try:
                move = int(message.content)
            except ValueError:
                continue
            if move < 1 or move > 7:
                continue

            try:
                await message.delete()
            except discord.HTTPException:
                pass

            # Align with the board. Index 0
            move -= 1

            if not self.is_valid(move):
                await ctx.send('Invalid move!')
                continue

            self.turn += 1

            if self.turn == 42:
                cog.c4.remove(ctx.channel.id)
                if not self.check_win(player):
                    await self.board.delete()
                    return await ctx.send(embed=self.generate_draw())

            row = self.next_open(move)
            self.make_move(row, move, player)

            if not await self.is_current_fresh(ctx.channel, 6):
                await self.board.delete()
                self.new = True

            if self.check_win(player):
                cog.c4.remove(ctx.channel.id)

                if self.new:
                    return await ctx.send(embed=self.generate_winner(player))
                return await self.board.edit(embed=self.generate_winner(player))
            if self.new:
                self.board = await ctx.send(embed=self.generate_board())
                self.new = False
            else:
                await self.board.edit(embed=self.generate_board())

    async def is_current_fresh(self, chan, limit):
        try:
            async for m in chan.history(limit=limit):
                if m.id == self.board.id:
                    return True
        except (discord.HTTPException, AttributeError):
            return False
        return False



