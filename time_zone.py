import datetime as dt
from pytz import timezone  # pip install pytz
# from dotenv import load_dotenv  # pip install python-dotenv
import os
import asyncio
import discord  # pip install discord
from discord.ext import commands
from discord.ext.commands import has_permissions
# from discord.utils import get
from keep_alive import keep_alive
# pip install SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column, String
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base


keep_alive()


# load_dotenv()
TOKEN = os.environ.get('TOKEN')

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

# SQLAlchemy setup
Base = declarative_base()
class ChannelData(Base):
    __tablename__ = 'channel_data'
    
    person = Column("person", String)
    channel_id = Column("channel_id", String, primary_key=True)
    timezone = Column("timezone", String)
    
    def __init__(self, person, channel_id, timezone):
        self.person = person
        self.channel_id = channel_id
        self.timezone = timezone
        
    def __repr__(self):
        return f"<Person: '{self.person}', Channel_id: '{self.channel_id}'"

engine = create_engine('sqlite:///channel_data.db', echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

# Load channel data from SQLite database
def load_channel_data():
    session = Session()
    return session.query(ChannelData).all()

# # Save channel data to SQLite database
# def save_channel_data(channel_data):
#     session = Session()
#     session.bulk_save_objects(channel_data)
#     session.commit()

@bot.command()
@has_permissions(administrator=True)
async def reset_time(ctx):
    """
    Reset the time (rename the channel).
    """
    channel_data = load_channel_data()
    for data in channel_data:
        channel = bot.get_channel(int(data.channel_id))
        await channel.edit(name=await get_time_in_timezone(data.timezone, data.person))
    await ctx.send("Time reset for all channels.")

async def rename_channels():
    await bot.wait_until_ready()
    while not bot.is_closed():
        channel_data = load_channel_data()
        for data in channel_data:
            channel = bot.get_channel(int(data.channel_id))
            await channel.edit(name=await get_time_in_timezone(data.timezone, data.person))
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
@commands.has_permissions(administrator=True)
async def add_channel_data(ctx, person, channel_id, timezone):
    """
    Add channel data to SQLite database.
    """
    session = Session()
    channel_data = ChannelData(person=person, channel_id=channel_id, timezone=timezone)
    session.add(channel_data)
    session.commit()
    await ctx.send(f"Channel data added for {person}.")

@bot.command()
@commands.has_permissions(administrator=True)
async def update_channel_data(ctx, person, channel_id, timezone):
    """
    Update channel data in SQLite database.
    """
    session = Session()
    channel_data = session.query(ChannelData).filter_by(person=person).first()
    if channel_data:
        channel_data.channel_id = channel_id
        channel_data.timezone = timezone
        session.commit()
        await ctx.send(f"Channel data updated for {person}.")
    else:
        await ctx.send(f"{person} does not exist in the data. Use /add_channel_data instead.")

@bot.command()
@commands.has_permissions(administrator=True)
async def remove_channel_data(ctx, person):
    """
    Remove channel data from SQLite database.
    """
    session = Session()
    channel_data = session.query(ChannelData).filter_by(person=person).first()
    if channel_data:
        session.delete(channel_data)
        session.commit()
        await ctx.send(f"Channel data removed for {person}.")
    else:
        await ctx.send(f"{person} does not exist in the data.")
    
    
@bot.command()
@has_permissions(administrator=True)
async def test(ctx):
    channel_data = load_channel_data()
    await ctx.send(f'{channel_data}, {ctx.author.mention}!')


if __name__ == '__main__':
    bot.run(TOKEN)
