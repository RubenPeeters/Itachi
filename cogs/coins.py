import discord
import discord.ext.commands as commands
import json
import random
import dbl
import asyncio

def setup(bot):
    bot.add_cog(Coins(bot))

class Coins:
    def __init__(self, bot):
        self.bot = bot
        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQ1NzgzODYxNzYzMzQ4ODkwOCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTMyNTU4NzEyfQ.uxAky0vSEHTUG09KlZQvtQ7PuBRyZ36PM-_A1J3AZps"
        self.dblpy = dbl.Client(self.bot, self.token)

    async def on_guild_join(self, guild):
        self.add_guild_users(guild)

    async def on_member_join(self, member):
        with open('users.json', 'r') as f:
            users = json.load(f)
        self.update_data(users, member)
        with open('users.json', 'w') as f:
            json.dump(users, f)

    def update_data(self, users, user: discord.Member):
        try:
            if str(user.guild.id) not in users:
                users[str(user.guild.id)] = {}
            if str(user.id) not in users[str(user.guild.id)]:
                users[str(user.guild.id)][str(user.id)] = {"coins": 200}
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to get update data\n{}'.format(exc))

    def user_add_coins(self, users, user, coins: int):
        users[str(user.guild.id)][str(user.id)]['coins'] += coins
        with open('users.json', 'w') as f:
            json.dump(users, f)

    def user_remove_coins(self, users, user, coins: int):
        users[str(user.guild.id)][str(user.id)]['coins'] -= coins
        with open('users.json', 'w') as f:
            json.dump(users, f)

    def add_guild_users(self, guild):
        for member in guild.members:
            with open('users.json', 'r') as fp:
                users = json.load(fp)
            self.update_data(users, member)
            with open('users.json', 'w') as fp:
                json.dump(users, fp)

    def get_leaderboard(self, ctx: commands.Context):
        leaderboard = [["name0", 0], ["name1", 0], ["name2", 0]]
        with open('users.json', 'r') as f:
            users = json.load(f)
        try:
            for user in ctx.guild.members:
                self.update_data(users, user)
                if users[str(ctx.guild.id)][str(user.id)]['coins'] >= leaderboard[0][1]:
                    leaderboard[2] = leaderboard[1]
                    leaderboard[1] = leaderboard[0]
                    leaderboard[0] = [user.display_name, users[str(ctx.guild.id)][str(user.id)]['coins']]
                else:
                    if users[str(ctx.guild.id)][str(user.id)]['coins'] >= leaderboard[1][1]:
                        leaderboard[2] = leaderboard[1]
                        leaderboard[1] = [user.display_name, users[str(ctx.guild.id)][str(user.id)]['coins']]
                    else:
                        if users[str(ctx.guild.id)][str(user.id)]['coins'] >= leaderboard[2][1]:
                            leaderboard[2] = [user.display_name, users[str(ctx.guild.id)][str(user.id)]['coins']]
                        else:
                            pass
            with open('users.json', 'w') as f:
                json.dump(users, f)
            return leaderboard
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to get leaderboard\n{}'.format(exc))

    @commands.command()
    async def coins(self, ctx, member: discord.Member=None):
        embed = discord.Embed(color=0xA90000)
        user = ctx.message.author
        if member is not None:
            user = member
        with open('users.json', 'r') as fp:
            users = json.load(fp)
        self.update_data(users, member)
        with open('users.json', 'w') as fp:
            json.dump(users, fp)
        embed.add_field(name=":moneybag: Balance for {} ".format(user.display_name), value=" <:blobcoins:469600670761091075> " + str(users[str(user.guild.id)][str(user.id)]["coins"]))
        embed.set_footer(text="Coins can be used to play games against friends!")
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx: commands.Context):
        '''Leaderboard for coins in this server.'''
        embed = discord.Embed(color=0xA90000)
        leaderboard = self.get_leaderboard(ctx)
        text = ":first_place: " + leaderboard[0][0] + ": **" + str(
            leaderboard[0][1]) + "**:moneybag: \n" \
                                 ":second_place: " + leaderboard[1][0] + ": **" + str(
            leaderboard[1][1]) + "** :moneybag:\n" \
                                 ":third_place: " + leaderboard[2][0] + ": **" + str(
            leaderboard[2][1]) + "** :moneybag:\n"
        embed.add_field(name="Coin Leaderboard {}".format(ctx.guild.name), value=text)
        embed.set_footer(text="Win games against friend or gamble to earn more coins!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def gamble(self, ctx: commands.Context, amount: int):
        allowed = True
        with open('users.json', 'r') as fp:
            users = json.load(fp)
        if users[str(ctx.guild.id)][str(ctx.author.id)]['coins'] < amount:
            await ctx.send("You dont have sufficient funds for that! You currently have **{}** coins".format(users[str(ctx.guild.id)][str(ctx.author.id)]['coins']))
            allowed = False
        win = random.choice([0, 1])
        try:
            if allowed:
                if win == 0:
                    self.user_remove_coins(users, ctx.author, amount)
                    await ctx.send("You lost. Your new balance is {} <:blobsadlife:469612379106312192> ".format(users[str(ctx.guild.id)][str(ctx.author.id)]['coins']))
                if win == 1:
                    self.user_add_coins(users, ctx.author, amount)
                    await ctx.send("You won! Your new balance is {} <:blessfingergunsamused:468552080764960770>".format(users[str(ctx.guild.id)][str(ctx.author.id)]['coins']))
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to get gamble\n{}'.format(exc))

    @commands.command()
    @commands.is_owner()
    async def givec(self, ctx: commands.Context, amount: int, member: discord.Member=None):
        with open('users.json', 'r') as fp:
            users = json.load(fp)
        user = ctx.message.author
        if member is not None:
            user = member
        self.user_add_coins(users, user, amount)
        await ctx.send(f"{user}\'s new balance is {users[str(ctx.guild.id)][str(user.id)]['coins']}")

    @commands.command()
    @commands.is_owner()
    async def delc(self, ctx: commands.Context, amount: int, member: discord.Member = None):
        with open('users.json', 'r') as fp:
            users = json.load(fp)
        user = ctx.author
        if member is not None:
            user = member
        self.user_remove_coins(users, user, amount)
        await ctx.send(f"{user}\'s new balance is {users[str(ctx.guild.id)][str(user.id)]['coins']}")

    @commands.command(aliases=["relc"])
    @commands.is_owner()
    async def manual_reload_coins(self, ctx):
        member_count = 0
        with open('users.json', 'r') as fp:
            users = json.load(fp)
        for guild in self.bot.guilds:
            for member in guild.members:
                self.update_data(users, member)
                member_count += 1
        await ctx.send(f"Done. {member_count} members coins reset")
        with open('users.json', 'w') as fp:
            json.dump(users, fp)

    @commands.command()
    async def getvotes(self, ctx):
        await ctx.message.delete()
        with open('users.json', 'r') as fp:
            users = json.load(fp)
        votes = await self.dblpy.get_upvote_info(days=1, onlyids=True)
        for x in votes:
            for guild in self.bot.guilds:
                for member in guild.members:
                    if member.id == int(x["id"]):
                        try:
                            users[str(guild.id)][str(member.id)]['coins'] += 200
                            await ctx.send(f"{member} has voted in the last day and has gotten 200 coins.")
                        except:
                            await ctx.send(f"failed to give {member} coins, even though he/she has voted.")

        with open('users.json', 'w') as fp:
            json.dump(users, fp)
