import discord
import discord.ext.commands as commands
import json
from .utils import checks
import os

def setup(bot):
    bot.add_cog(exp(bot))

def get_xp(user_id: int):
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
            return users[str(user_id)]['xp']
    except Exception as e:
        exc = "{}: {}".format(type(e).__name__, e)
        print('Failed to get exp\n{}'.format(exc))

    else:
        return 0
def get_leaderboard():
    leaderboard = [["name0", 0], ["name1", 0], ["name2", 0]]
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
            for x in users:
                if users[str(x)]['xp'] >= leaderboard[0][1]:
                    leaderboard[2] = leaderboard[1]
                    leaderboard[1] = leaderboard[0]
                    leaderboard[0] = [x, users[str(x)]['xp']]
                else:
                    if users[str(x)]['xp'] >= leaderboard[1][1]:
                        leaderboard[2] = leaderboard[1]
                        leaderboard[1] = [x, users[str(x)]['xp']]
                    else:
                        if users[str(x)]['xp'] >= leaderboard[2][1]:
                            leaderboard[2] = [x, users[str(x)]['xp']]
                        else:
                            pass
            return leaderboard
    except Exception as e:
        exc = "{}: {}".format(type(e).__name__, e)
        print('Failed to get leaderboard\n{}'.format(exc))


def get_lvl(user_id: int):
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
            return users[str(user_id)]['level']
    except Exception as e:
        exc = "{}: {}".format(type(e).__name__, e)
        print('Failed to get exp\n{}'.format(exc))

    else:
        return 0

class exp:
    def __init__(self, bot):
        self.bot = bot
        self.errorchannelid = 467672989232529418


    async def on_message(self, message):
        if checks.is_exp_enabled():
            with open('users.json', 'r') as fp:
                users = json.load(fp)
            await self.update_data(users, message.author)
            await self.user_add_xp(users, message.author, 5)
            await self.level_up(users, message.author, message.channel)

            with open('users.json', 'w') as fp:
                json.dump(users, fp)


    async def on_member_join(self, member):
        if checks.is_exp_enabled():
            with open('users.json', 'r') as f:
                users = json.load(f)
            await self.update_data(users, member)
            with open('users.json', 'w') as f:
                json.dump(users, f)

    async def update_data(self, users, user):
        if str(user.id) not in users:
            users[str(user.id)] = {}
            users[str(user.id)]['xp'] = 0
            users[str(user.id)]['level'] = 1

    async def user_add_xp(self, users, user, xp: int):
        users[str(user.id)]['xp'] += xp


    async def level_up(self, users, user, channel):
        for x in self.bot.guilds:
            for chan in x.channels:
                if chan.id == self.errorchannelid:
                    errorchannel = chan
        xp = users[str(user.id)]['xp']
        lvl_start = users[str(user.id)]['level']
        lvl_end = int(xp ** (1 / 4))
        if lvl_start < lvl_end:
            users[str(user.id)]['level'] = lvl_end
            if lvl_end == 10:
                try:
                    role1 = discord.utils.get(user.guild.roles, name='Casual')
                    role2 = discord.utils.get(user.guild.roles, name='New')
                    await user.add_roles(role1)
                    await user.remove_roles(role2)
                except Exception as e:
                    exc = "{}: {}".format(type(e).__name__, e)
                    await errorchannel.send(
                        'Failed to level up\n{}\n{}'.format(exc))
                    print('Failed to assign \'Casual\' role \n{}'.format(exc))

    @checks.is_exp_enabled()
    @commands.group(invoke_without_command= True)
    async def exp(self, ctx: commands.Context):
        '''Show the experience and level for the user that sends it'''
        try:
            await ctx.send("{} has {} XP and is level {}".format(ctx.message.author.mention,
                                                                get_xp(ctx.message.author.id),
                                                                get_lvl(ctx.message.author.id)))
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            await self.errorchannel.send(
                'Failed to send exp\n{}\n{}'.format(exc, ctx.guild.name))
            print('Failed to send exp\n{}'.format(exc))

    @exp.command()
    async def leaderboard(self, ctx: commands.Context):
        '''Global leaderboard for exp'''
        embed = discord.Embed(color=0xA90000)
        leaderboard = get_leaderboard()
        text = ":first_place: " + self.bot.get_user(int(leaderboard[0][0])).name + ": " + str(leaderboard[0][1]) + " XP\n" \
        ":second_place: " + self.bot.get_user(int(leaderboard[1][0])).name + ": " + str(leaderboard[1][1]) + " XP\n" \
        ":third_place: "  + self.bot.get_user(int(leaderboard[2][0])).name + ": " + str(leaderboard[2][1]) + " XP\n"
        embed.add_field(name="Global Leaderboard Itachi", value=text)
        embed.set_footer(text="Be active in servers I'm in to gain more XP!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)