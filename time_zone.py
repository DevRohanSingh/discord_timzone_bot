import datetime as dt
import json
from pytz import timezone  # pip install pytz
# from dotenv import load_dotenv  # pip install python-dotenv
import os
import asyncio
import discord  # pip install discord
from discord.ext import commands
from discord.ext.commands import has_permissions
# from discord.utils import get
from keep_alive import keep_alive
keep_alive()


# load_dotenv()
TOKEN = os.environ.get('TOKEN')

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

# Load channel data from JSON
def load_channel_data():
    with open('channels.json') as f:
        return json.load(f)

# Save channel data to JSON
def save_channel_data(channel_data):
    with open('channels.json', 'w') as f:
        json.dump(channel_data, f, indent=4)


async def rename_channels():
    await bot.wait_until_ready()
    while not bot.is_closed():
        channel_data = load_channel_data()
        for person, data in channel_data.items():
            channel_id = data['channel_id']
            timezone_name = data['timezone']
            channel = bot.get_channel(int(channel_id))
            await channel.edit(name=await get_time_in_timezone(timezone_name, person))
        await asyncio.sleep(600)  # Update every 10 minutes


async def get_time_in_timezone(timezone_name, person):
    now_time = dt.datetime.now(timezone(timezone_name)).strftime("%I:%M %p")
    return f"🕐{person}@{now_time}"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    # start the rename channels loop
    bot.loop.create_task(rename_channels())


@bot.command()
@has_permissions(administrator=True)
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


@bot.command()
@has_permissions(administrator=True)
async def add_channel_data(ctx, person, channel_id, timezone):
    """
    Add channel data to channels.json if the channel_id is not already present.

    Usage: /add_channel_data <person> <channel_id> <timezone>
    """
    channel_data = load_channel_data()
    for existing_person, data in channel_data.items():
        if data['channel_id'] == channel_id:
            await ctx.send(f"The channel ID {channel_id} is already associated with {existing_person}.")
            return

    channel_data[person] = {
        "channel_id": channel_id,
        "timezone": timezone
    }

    save_channel_data(channel_data)
    await ctx.send(f"Channel data added for {person}.")

@bot.command()
@has_permissions(administrator=True)
async def update_channel_data(ctx, person, channel_id, timezone):
    """
    Update channel data in channels.json.

    Usage: /update_channel_data <person> <channel_id> <timezone>
    """
    channel_data = load_channel_data()
    if person not in channel_data:
        await ctx.send(f"{person} does not exist in the data. Use /add_channel_data instead.")
        return

    channel_data[person] = {
        "channel_id": channel_id,
        "timezone": timezone
    }

    save_channel_data(channel_data)
    await ctx.send(f"Channel data updated for {person}.")

@bot.command()
@has_permissions(administrator=True)
async def remove_channel_data(ctx, person):
    """
    Remove channel data from channels.json.

    Usage: /remove_channel_data <person>
    """
    channel_data = load_channel_data()
    if person not in channel_data:
        await ctx.send(f"{person} does not exist in the data.")
        return

    del channel_data[person]
    save_channel_data(channel_data)
    await ctx.send(f"Channel data removed for {person}.")


@bot.command()
async def reset_time(ctx):
    """
    Reset the time (rename the channel).
    """
    channel_data = load_channel_data()
    for person, data in channel_data.items():
        channel_id = data['channel_id']
        timezone_name = data['timezone']
        channel = bot.get_channel(int(channel_id))
        await channel.edit(name=await get_time_in_timezone(timezone_name, person))
    await ctx.send("Time reset for all channels.")
    
    
@bot.command()
@has_permissions(administrator=True)
async def test(ctx, msg):
    await ctx.send(f'{msg}, {ctx.author.mention}!')


if __name__ == '__main__':
    bot.run(TOKEN)
