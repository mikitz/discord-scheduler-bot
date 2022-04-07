# -----------
#   Imports
# -----------
from cmath import nan
from unicodedata import name
import os
import logging
import json
from discord.utils import get
from dotenv import load_dotenv
import discord # Import Discord
from discord.ext import commands # Import commands for the bot
# --------------
#   Initialize
# --------------
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix='!sb ', intents=intents) # Initialize Bot Commands
bot.remove_command('help')
load_dotenv()
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# ------------------------
#   Bot Command Fuctions
# ------------------------

# On start up
@bot.event
async def on_ready():
    print("-------------------------")
    print("Scheduler Bot is running.")
    print("-------------------------")

# On Reaction Added
@bot.event
async def on_reaction_add(reaction, user):
    print("--------------")
    print("Reaction Added")
    print("--------------")
    author = str(reaction.message.author) # Get the author of the message that was reacted to
    for embed in reaction.message.embeds: 
        message = embed.to_dict() # Convert the Embeds into a dictionary
    title = message['title'] # Get the Title
    try:
        description = message['description'] # Get the Description
    except:
        description = ''
    date = message['fields'][0]['value'] # Get the Date
    time = message['fields'][1]['value'] # Get the Time 
    min_players = int(message['fields'][2]['value']) # Get the Min. Players
    game_master = discord.utils.get(reaction.message.guild.roles, name='Game Master')
    player_active = discord.utils.get(reaction.message.guild.roles, name='Player (Active)')
    if 'scheduler-bot' in author: # Only do something if the author was the scheduler bot
        reactions = reaction.message.reactions # Get all the reactions on the message
        attendCount = int(get(reactions, emoji='✅').count) - 1 # Get the number of players who will attend minus the bot
        absentCount = int(get(reactions, emoji='❌').count) - 1 # Get the number of players who will be absent minus the bot
        if attendCount >= min_players: # Mention everyone that the session is confirmed
            await reaction.message.channel.send(content=f'{player_active.mention} {game_master.mention} *SESSION CONFIRMED* -- **{title}** is *CONFIRMED* for **{date}** at **{time}**! {description}', allowed_mentions=discord.AllowedMentions(roles=True))

# On Reaction Removed
@bot.event
async def on_reaction_remove(reaction, user):
    print("----------------")
    print("Reaction Removed")
    print("----------------")
    author = str(reaction.message.author) # Get the author of the message that was reacted to
    for embed in reaction.message.embeds: 
        message = embed.to_dict() # Convert the Embeds into a dictionary
    title = message['title'] # Get the Title
    try:
        description = message['description'] # Get the Description
    except:
        description = ''
    date = message['fields'][0]['value'] # Get the Date
    time = message['fields'][1]['value'] # Get the Time 
    min_players = int(message['fields'][2]['value']) # Get the Min. Players
    game_master = discord.utils.get(reaction.message.guild.roles, name='Game Master')
    player_active = discord.utils.get(reaction.message.guild.roles, name='Player (Active)')
    if 'scheduler-bot' in author: # Only do something if the author was the scheduler bot
        reactions = reaction.message.reactions # Get all the reactions on the message
        attendCount = int(get(reactions, emoji='✅').count) - 1 # Get the number of players who will attend minus the bot
        absentCount = int(get(reactions, emoji='❌').count) - 1 # Get the number of players who will be absent minus the bot
        print("Min. Players:", min_players)
        print("Attend Count:", attendCount)
        if attendCount == min_players - 1:
            await reaction.message.channel.send(content=f'{player_active.mention} {game_master.mention} *SESSION UNCONFIRMED* -- **{title}** has been *UNCONFIRMED*. Only {min_players - attendCount} more player needed to confirm the session!', allowed_mentions=discord.AllowedMentions(roles=True))

# Help Command
@bot.command()
async def help(ctx): #!sb help
    embed = discord.Embed(
        title='Schedule Bot',
        description='Welcome to the help section of Scheduler Bot. See below for a list of commands and their description.',
        color=discord.Colour.green()
    )
    embed.add_field(
        name='Help',
        value="`!sb help` provides a list of all commands.",
        inline=False
    )
    embed.add_field(
        name='Info',
        value="`!sb info` provides information about where the bot's open source code is stored and how to donate to the author.",
        inline=False
    )
    embed.add_field(
        name='Create a New Event',
        value='`!sb event` creates a new event using the followwing syntax: `!sb event NAME, DATE, TIME, DESCRIPTION, MINIMUM NUMBER OF PLAYERS`. DESCRIPTION is optional',
        inline=False
    )
    await ctx.send(embed=embed)

# Info Command
@bot.command()
async def info(ctx): # !sb info
    embed = discord.Embed(
        title='Schedule Bot',
        description='Schedule Bot Info',
        color=discord.Colour.green()
    )
    embed.set_thumbnail(url='https://avatars.githubusercontent.com/u/17684097?s=400&u=badb2a3839ce5cb4e5c3f75dc3172c1f2786412b&v=4')
    embed.add_field(
        name='Ko-fi',
        value='Buy Mikitz some avocadoes: https://ko-fi.com/mikitz',
        inline=False
    )
    embed.add_field(
        name='GitHub',
        value='View the open-source code: https://github.com/mikitz/discord-scheduler-bot',
        inline=False
    )
    await ctx.send(embed=embed)

# New Event Command
@bot.command()
async def event(ctx, *args): # !sb event
    args_string = ' '.join(args)
    params = args_string.split(", ")
    name = params[0]
    date = params[1]
    time = params[2]
    try:
        description = params[3]
    except:
        description='No description...' 
    try:
        min_players = params[4]
    except:
        min_players = ''
    embed = discord.Embed(
        title=name,
        description=f'{description}',
        color=discord.Colour.blue()
    )
    embed.add_field(
        name='Date',
        value=date,
        inline=False
    )
    embed.add_field(
        name='Time',
        value=time,
        inline=False
    )
    embed.add_field(
        name='Min. Players',
        value=min_players,
        inline=False
    )
    embed.add_field(
        name='RSVP',
        value='React with a ✅ to confirm attendance or with a ❌ to confirm absence.',
        inline=False
    )
    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")
# -----------------
#   Start the Bot
# -----------------
bot.run(os.getenv("TOKEN")) # Start the bot