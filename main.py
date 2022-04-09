# -----------
#   Imports
# -----------
from cmath import nan
from unicodedata import name
import os
import logging
from discord.utils import get
import discord # Import Discord
from discord.ext import commands # Import commands for the bot
from keep_alive import keep_alive
import datetime
# --------------
#   Initialize
# --------------
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
activity = discord.Activity(type=discord.ActivityType.listening, name="!sb") # Set up the bot's activity
bot = commands.Bot(command_prefix='!sb ', intents=intents, activity=activity, status=discord.Status.online) # Initialize Bot Commands
bot.remove_command('help') # Remove the default command
# ----------
#   Logger
# ----------
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
    reaction_added = reaction.emoji # Get the reaction that was added
    print(f"Getting the Reaction that was added... {reaction_added}")
    # if reaction_added != '❌' or reaction_added != '✅': return print("Stopping Function...") # Stop the function if it's not a reaction we're monitoring
    print("Reaction is either a ❌ or a ✅, proceeding...")
    author = str(reaction.message.author) # Get the author of the message that was reacted to
    users = await reaction.users().flatten()
    mentions = ''
    for i in users: 
        if i.name == 'Sesh Time': continue
        mentions += f'{i.mention} '
    for embed in reaction.message.embeds: message = embed.to_dict() # Convert the Embeds into a dictionary
    title = message['title'] # Get the Title
    try: description = message['description'] # Get the Description
    except: description = '' # Set description to an empty string if not added
    date = message['fields'][0]['value'] # Get the Date
    time = message['fields'][1]['value'] # Get the Time 
    min_players = int(message['fields'][2]['value']) # Get the Min. Players
    group_size = int(message['fields'][3]['value']) # Get the Group Size
    game_master = discord.utils.get(reaction.message.guild.roles, name='Game Master') # Grab the Game Master role
    player_active = discord.utils.get(reaction.message.guild.roles, name='Player (Active)') # Grab the Player (Active) role
    if 'Sesh Time' in author: # Only do something if the author was the scheduler bot
        reactions = reaction.message.reactions # Get all the reactions on the message
        try: attendCount = int(get(reactions, emoji='✅').count) - 1 # Get the number of players who will attend minus the bot
        except: pass
        try: absentCount = int(get(reactions, emoji='❌').count) - 1 # Get the number of players who will be absent minus the bot
        except: pass
        # Handle Changes
        if reaction_added == '❌': # Handle Absences
            if absentCount > group_size - min_players:
                await reaction.message.channel.send( # Send a message saying the session is cancelled due to too many players not being able to make it
                    content = f'{mentions} \n {player_active.mention} {game_master.mention} \n *SESSION CANCELLED* -- **{title}** is *CANCELLED* which was scheduled for **{date}** at **{time}** due to too many players not being able to make it.', 
                    allowed_mentions = discord.AllowedMentions(roles=True)
                )
        elif reaction_added == '✅': # Handle Attendees
            if attendCount >= min_players: # Handle 
                await reaction.message.channel.send(
                    content = f'{mentions} \n {player_active.mention} {game_master.mention} \n *SESSION CONFIRMED* -- **{title}** is *CONFIRMED* for **{date}** at **{time}**! {description}', 
                    allowed_mentions = discord.AllowedMentions(roles=True)
                )
# On Reaction Removed
@bot.event
async def on_reaction_remove(reaction, user):
    reaction_removed = reaction.emoji # Get the reaction that was removed
    print(f"Getting the Reaction that was removed... {reaction_removed}")
    # if reaction_removed != '❌' or reaction_removed != '✅': return print("Stopping Function...") # Stop the function if it's not a reaction we're monitoring
    print("Reaction is either a ❌ or a ✅, proceeding...")
    author = str(reaction.message.author) # Get the author of the message that was reacted to
    users = await reaction.users().flatten()
    mentions = ''
    for i in users: 
        if i.name == 'Sesh Time': continue
        mentions += f'{i}.mention '
    for embed in reaction.message.embeds: message = embed.to_dict() # Convert the Embeds into a dictionary
    title = message['title'] # Get the Title
    date = message['fields'][0]['value'] # Get the Date
    time = message['fields'][1]['value'] # Get the Time 
    min_players = int(message['fields'][2]['value']) # Get the Min. Players
    group_size = int(message['fields'][3]['value']) # Get the Group Size
    game_master = discord.utils.get(reaction.message.guild.roles, name='Game Master')
    player_active = discord.utils.get(reaction.message.guild.roles, name='Player (Active)')
    if 'Sesh Time' in author: # Only do something if the author was the scheduler bot
        reactions = reaction.message.reactions # Get all the reactions on the message
        # See if there's an Attend reaction
        try: attendCount = int(get(reactions, emoji='✅').count) - 1 # Get the number of players who will attend minus the bot
        except: pass
        # See if there's an Absent reaction
        try: absentCount = int(get(reactions, emoji='❌').count) - 1 # Get the number of players who will be absent minus the bot
        except: pass

        if reaction_removed == '❌':
            if absentCount == group_size - min_players + 1:
                await reaction.message.channel.send( # Send a message saying the session is cancelled due to too many players not being able to make it
                    content = f'{mentions} \n {player_active.mention} {game_master.mention} \n *SESSION UNCANCELLED* -- **{title}** is has been *UNCANCELLED*. Please reconsider your attendance for **{date}** at **{time}** and react with the appropriate Reaction.', 
                    allowed_mentions = discord.AllowedMentions(roles=True)
                )
        elif reaction_removed == '✅':
            if attendCount == min_players - 1:
                await reaction.message.channel.send(
                    content = f'{mentions} \n {player_active.mention} {game_master.mention} \n *SESSION UNCONFIRMED* -- **{title}** has been *UNCONFIRMED*. Only {min_players - attendCount} more player needed to confirm the session!', 
                    allowed_mentions = discord.AllowedMentions(roles=True)
                )
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
        value='View the open-source code: https://github.com/mikitz/discord-Sesh Time',
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
    try: description = params[3] # Get the Description
    except: description='No description...' 
    try: min_players = params[4] # Get the Min. Players
    except: min_players = ''
    try: group_size = params[5] # Get the Group Size
    except: group_size = 4
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
        name='Group Size',
        value=group_size,
        inline=False
    )
    embed.add_field(
        name='RSVP',
        value='React with a ✅ to confirm attendance or with a ❌ to confirm absence.',
        inline=False
    )
    player_active = discord.utils.get(ctx.guild.roles, name='Player (Active)') # Grab the Player (Active) role
    message = await ctx.send(
        content = player_active.mention, # Mention the active players that a new Session has been scheduled
        embed = embed # Add the embed to the message
    )
    await message.add_reaction("✅")
    await message.add_reaction("❌")
# -----------------
#   Start the Bot
# -----------------
keep_alive() # Start the HTTP server to that it runs 24/7
bot.run(os.getenv("TOKEN")) # Start the bot