import datetime as dt
from pytz import timezone  # pip install pytz
# from dotenv import load_dotenv  # pip install python-dotenv
import os
import asyncio
import discord  # pip install discord
from discord.ext import commands
# from discord.utils import get
from keep_alive import keep_alive
keep_alive()


# load_dotenv()
TOKEN = os.environ.get('TOKEN')

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())


@bot.event
async def schedule_renaming_vc():
    while True:
        wait_time = 600  # update every 10 min
        await asyncio.sleep(wait_time)

        # rename bummmer vc
        channel_id_bummmer= 1237131804662693999
        vc_bummmer = bot.get_channel(channel_id_bummmer)
        await vc_bummmer.edit(name=get_pst())

        # rename generous vc
        channel_id_generous= 1237132385846558750
        vc_generous = bot.get_channel(channel_id_generous)
        await vc_generous.edit(name=get_est())

        # rename brigitte vc
        channel_id_brigitte= 1237651048232128613
        vc_brigitte = bot.get_channel(channel_id_brigitte)
        await vc_brigitte.edit(name=get_cest_brigitte())

        # rename molder vc
        channel_id_molder= 1238114668128501800
        vc_molder = bot.get_channel(channel_id_molder)
        await vc_molder.edit(name=get_cst())

        # rename observer vc
        channel_id_observer= 1237135098533646477
        vc_observer = bot.get_channel(channel_id_observer)
        await vc_observer.edit(name=get_ist())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    # start the rename loop
    bot.loop.create_task(schedule_renaming_vc())



# bummmer: PST -> UTC-7
# 12:30 hrs behind(IST)
def get_pst():
    now_pst = dt.datetime.now(timezone("America/Los_Angeles")).strftime("%I:%M %p")
    # print(now_pst)  # 03:00 AM
    bummmer_user_id = 863907307267555328   # not sensative (publically available)
    user = bot.get_user(bummmer_user_id)
    return f"🕐{user}@{now_pst}"


# generous: Eastern Daylight Time -> UTC-4
# 9:30 hrs behind(IST)
def get_est():
    now_est = dt.datetime.now(timezone('America/New_York')).strftime("%I:%M %p")
    # print(now_est)  # 06:00 AM
    generous_user_id = 124272535490527232
    user = bot.get_user(generous_user_id)
    return f"🕐{user}@{now_est}"


# Brigitte
# 3:30 hrs behind (IST)
# CEST — Central European Summer Time -> UTC+02:00
def get_cest_brigitte():
    now_cest = dt.datetime.now(timezone("Europe/Paris")).strftime("%I:%M %p")
    # print(now_cest)  # 12:00 PM (noon)
    # brigitte_user_id = 1144537872704213024
    # user = bot.get_user(brigitte_user_id)
    return f"🕐Brigitte@{now_cest}"

# ObserverOfVoid
def get_ist():
    now_ist = dt.datetime.now(timezone("Asia/Kolkata")).strftime("%I:%M %p")
    # print(now_ist)  # 03:30 PM
    # observer_user_id = 835225393630806046 
    # user = bot.get_user(observer_user_id)
    return f"🕐Observer@{now_ist}"


# molder
# ahead of IST by 2:30 hrs
def get_cst():
    now_cst = dt.datetime.now(timezone("Asia/Shanghai")).strftime("%I:%M %p")
    # print(now_cst)  # 06:00 PM
    # molder_user_id = 835225393630806046 
    # user = bot.get_user(molder_user_id)
    return f"🕐molder@{now_cst}"


@bot.command()
async def createvc(ctx):
    # channel creation
    guild = ctx.guild
    # guild = bot.get_guild(os.environ.get('SERVER_ID'))  # alternatively
    # admin_role = get(guild.roles, name="Admin")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True),  # view_channel is an alias for read_messages
        # guild.me: discord.PermissionOverwrite(read_messages=True),
        # admin_role: discord.PermissionOverwrite(read_messages=True)
    }
    await guild.create_voice_channel(name='new-vc', overwrites=overwrites)

#  testing
@bot.command(aliases=['gm', 'morning'])
async def test(ctx):
    await ctx.send(f'test successful, {ctx.author.mention}!')

if __name__ == '__main__':
    bot.run(TOKEN)
