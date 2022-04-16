# -----------
#   Imports
# -----------
from cmath import nan
from unicodedata import name
import os
import logging
from discord.utils import get
import discord # Import Discord
from discord.ext import commands, tasks # Import commands for the bot
from keep_alive import keep_alive
import datetime
# from datetime import datetime
from dateutil.parser import parse
from replit import db
from dateutil.tz import gettz
import pytz
tzinfos = {"CST": gettz("America/Chicago")}
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
# -------------
#   Functions
# -------------
def index_of(iterable, element_name, condition):
    for idx, element in enumerate(iterable):
        if iterable[idx][element_name] == condition:
            return idx
    return None
# Function to delete all events that already passed
async def delete_non_applicable_events():
    for guild in bot.guilds:
        guild = str(guild.name)
        if guild in db.keys():
            indecies_to_delete = []
            messages = db[guild]
            print("**********")
            print(f"{guild} Messages:", messages)
            for idx, element in enumerate(messages):
                dt = element['datetime']
                datetime_object = parse(dt, tzinfos=tzinfos)
                print("Datetime:", datetime_object)
                print("Datetime:", dt)
                new_time = datetime_object + datetime.timedelta(days=1) # Add 6 days to the event time
                print("Delete Message Date:", new_time)
                timezone = element['timezone']
                if timezone == 'CST':
                    local_time = datetime.datetime.now(pytz.timezone('US/Central')) # Get local time and convert it to the timezone of the event
                elif timezone == 'KST':
                    local_time = datetime.datetime.now(pytz.timezone('Asia/South Korea')) # Get local time and convert it to the timezone of the event
                print("Current Time:", local_time)
                if local_time >= new_time:
                    print(f"Deleting Message at index {idx}...")
                    indecies_to_delete.append(idx) # Append this index to a list of those that need to be deleted
                else:
                    print(f"Message at index {idx} still being monitored...")
            # Delete those that need to be deleted
            if indecies_to_delete:
                for idx in indecies_to_delete:
                    del messages[idx]
                db[guild] = messages
            print(f"'{guild}' Messages:", db[guild])
        else:
            print(f'Guild "{guild}" has no table.')
# Function to determine if the event should be cancelled or uncancelled
async def adjust_event_status_on_reaction_add(reaction, user):
    reaction_added = reaction.emoji # Get the reaction that was added
    guild = reaction.message.guild
    print(f"Getting the Reaction that was added... {reaction_added} (Guild: {guild})")
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
            if "Game Master" in str(user.roles):
                await reaction.message.channel.send( # Send a message saying the session is cancelled due to too many players not being able to make it
                    content = f'{mentions} \n {player_active.mention} {game_master.mention} \n *SESSION CANCELLED* -- **{title}** is *CANCELLED* which was scheduled for **{date}** at **{time}** by the Gamemaster.', 
                    allowed_mentions = discord.AllowedMentions(roles=True)
                )
                update_event_value(reaction.message.channel, reaction.message.id, 'status', 'cancelled')
                update_event_value(reaction.message.channel, reaction.message.id, 'messaged', True)
            elif absentCount > group_size - min_players:
                await reaction.message.channel.send( # Send a message saying the session is cancelled due to too many players not being able to make it
                    content = f'{mentions} \n {player_active.mention} {game_master.mention} \n *SESSION CANCELLED* -- **{title}** is *CANCELLED* which was scheduled for **{date}** at **{time}** due to too many players not being able to make it.', 
                    allowed_mentions = discord.AllowedMentions(roles=True)
                )
                update_event_value(reaction.message.channel, reaction.message.id, 'status', 'cancelled')
                update_event_value(reaction.message.channel, reaction.message.id, 'messaged', True)
        elif reaction_added == '✅': # Handle Attendees
            if attendCount >= min_players: # Handle 
                await reaction.message.channel.send(
                    content = f'{mentions} \n {player_active.mention} {game_master.mention} \n *SESSION CONFIRMED* -- **{title}** is *CONFIRMED* for **{date}** at **{time}**! {description}', 
                    allowed_mentions = discord.AllowedMentions(roles=True)
                )
                update_event_value(reaction.message.channel, reaction.message.id, 'status', 'confirmed')
                update_event_value(reaction.message.channel, reaction.message.id, 'messaged', True)
# Function to determine if an event should be confirmed or unconfirmed
async def adjust_event_status_on_reaction_remove(reaction, user):
    reaction_removed = reaction.emoji # Get the reaction that was removed
    guild = reaction.message.guild
    print(f"Getting the Reaction that was removed... {reaction_removed} (Guild: {guild})")
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
                update_event_value(reaction.message.channel, reaction.message.id, 'status', 'pending')
                update_event_value(reaction.message.channel, reaction.message.id, 'messaged', True)
        elif reaction_removed == '✅':
            if attendCount == min_players - 1:
                await reaction.message.channel.send(
                    content = f'{mentions} \n {player_active.mention} {game_master.mention} \n *SESSION UNCONFIRMED* -- **{title}** has been *UNCONFIRMED*. Only {min_players - attendCount} more player needed to confirm the session!', 
                    allowed_mentions = discord.AllowedMentions(roles=True)
                )
                update_event_value(reaction.message.channel, reaction.message.id, 'status', 'pending')
                update_event_value(reaction.message.channel, reaction.message.id, 'messaged', True)
# Function to update the status of an event
async def update_event_value(context, message_id, value, string):
    message = await context.fetch_message(message_id)
    guild = str(message.guild)
    msg_index = index_of(db[guild], 'id', message.id)
    db[guild][msg_index][value] = string
# Function to update a specific message in the Database
async def update_message(context, message_id):
    message = await context.fetch_message(message_id)
    guild = str(message.guild)
    msg_index = index_of(db[guild], 'id', message.id)
    db_msg = db[guild][msg_index]
    print("update_message ~~ DB Message:", db_msg)
    reactions = message.reactions
    attendees = []
    absentees = []
    
    for reaction in reactions: # Loop through all the reactions on this message
        users = await reaction.users().flatten() # Get a list of users who have reacted with this emoji
        emoj = reaction.emoji # Get the emoji
        for user in users: # Loop through the users
            if emoj == '✅': attendees.append(user.name) # Append user to Attendees list if they have confirmed attendance
            elif emoj == '❌': absentees.append(user.name) # Apppend user to the Absentees list if they have confirmed absence
                
    message_object = {
        "id": message_id,
        "channel": {
            "name": message.channel.name,
            "id": message.channel.id
        },
        "author": {
            "name": message.author.name,
            "id": message.author.id
        },
        "datetime": db_msg['datetime'],
        "timezone": db_msg['timezone'],
        "attendees": attendees,
        "absentees": absentees,
        "status": 'pending',
        "title": db_msg['title'],
        "date": db_msg['date'],
        "time": db_msg['time'],
        "min_players": db_msg['min_players']
    }
    db[guild][msg_index] = message_object
    print("update_message ~~ Updated Message Object:", message_object)
# ------------------------
#   Bot Command Fuctions
# ------------------------
# On start up
@bot.event
async def on_ready():
    print("-------------------------")
    print("Scheduler Bot is running.")
    print("-------------------------")
    # print("Keys:", db.keys())
    # for key in db.keys():
    #     print(f'Deleting Key for Server "{key}"')
    #     del db[key]
# Function that runs when a reaction is added
@bot.event
async def on_resume():
    await delete_non_applicable_events()
    await auto_cancel_event()
    await monitor_changes()
    print("-------------------")
    print("Sesh Time is Ready.")
    print("-------------------")
# Function that runs when a reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    await adjust_event_status_on_reaction_add(reaction, user)
    await update_message(reaction.message.channel, reaction.message.id)       
# Function that runs when a reaction is removed
@bot.event
async def on_reaction_remove(reaction, user):
    await adjust_event_status_on_reaction_remove(reaction, user)
    await update_message(reaction.message.channel, reaction.message.id)
# Function to spit out a help message
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
# Function to give the user info about the bot
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
# Function to create a new event
@bot.command()
async def event(ctx, *args): # !sb event
    args_string = ' '.join(args)
    params = args_string.split(", ")
    guild = str(ctx.message.guild)
    name = params[0]
    date = params[1]
    time = params[2]
    timezone = params[3]
    dt = date + " " + time + " " + timezone
    try: description = params[4] # Get the Description
    except: description='No description...' 
    try: min_players = params[5] # Get the Min. Players
    except: min_players = ''
    try: group_size = params[6] # Get the Group Size
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
        value=f"{time} {timezone}",
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
    # ==============
    # Database Stuff
    # ==============
    message_id = message.id # Get the ID
    command_message_id = ctx.message.id # Get the ID for the message that was used to schedule the new event
    command_msg = await ctx.channel.fetch_message(command_message_id) # Get the Command message object so it can be deleted
    await command_msg.delete() # Delete the Command message
    message_object = {
        "id": message.id,
        "channel": {
            "name": message.channel.name,
            "id": message.channel.id
        },
        "author": {
            "name": message.author.name,
            "id": message.author.id
        },
        "datetime": dt,
        "timezone": timezone,
        "attendees": [],
        "absentees": [],
        "title": name,
        "date": date,
        "time": time,
        "min_players": min_players,
        "group_size": group_size
    }
	# Adding Data
    if guild in db.keys():
        msgs = db[guild]
        msgs.append(message_object)
        db[guild] = msgs
    else:
        db[guild] = [message_object]
    # ===============
    #  Add Reactions
    # ===============
    await message.add_reaction("✅")
    await message.add_reaction("❌")
# --------------------
#   Looped Functions
# --------------------
# Function to auto cancel sessions that don't have enough player reserved
@tasks.loop(minutes=5)
async def auto_cancel_event():
    print("------------------")
    print("Auto-cancelling...")
    print("------------------")
    for guild in bot.guilds:
        dic_guild = guild
        guild = str(guild.name)
        if guild in db.keys():
            messages = db[guild]
            for idx, message in enumerate(messages):
                channel = discord.utils.get(dic_guild.channels, name=message['channel']['name'])
                channel_message = await channel.fetch_message(message['id'])
                title = message['title']
                date = message['date']
                time = message['time']
                dt = message['datetime']
                datetime_object = parse(dt, tzinfos=tzinfos) 
                timezone = message['timezone']
                if timezone == 'CST':
                    local_time = datetime.datetime.now(pytz.timezone('US/Central')) # Get local time and convert it to the timezone of the event
                elif timezone == 'KST':
                    local_time = datetime.datetime.now(pytz.timezone('Asia/South Korea')) # Get local time and convert it to the timezone of the event
                if local_time - datetime.timedelta(hours=24) <= local_time:
                    if len(message['attendees']) <= message['min_players']:
                        game_master = discord.utils.get(channel.guild.roles, name='Game Master')
                        player_active = discord.utils.get(channel.guild.roles, name='Player (Active)')
                        await channel_message.channel.send( # Send a message saying the session is cancelled due to not enough players RSVPing within 24 hours
                            content = f'{player_active.mention} {game_master.mention} \n *SESSION CANCELLED* -- **{title}**, scheduled for {date} at {time}, has been *CANCELLED* due to not having enough players confirm attendance before 24 hours prior to session start.', 
                            allowed_mentions = discord.AllowedMentions(roles=True)
                        )
                    print(f'Auto-cancelling event {title}...')
auto_cancel_event.start()
# Function to monitor changes the messages
@tasks.loop(minutes=5)
async def monitor_changes():
    print("-----------------")
    print("Making Changes...")
    print("-----------------")
    await delete_non_applicable_events()
    for guild in bot.guilds:
        dic_guild = guild
        guild = str(guild.name)
        if guild in db.keys():
            messages = db[guild]
            for idx, message in enumerate(messages):
                # Message from the Channel
                channel = discord.utils.get(dic_guild.channels, name=message['channel']['name'])
                channel_message = await channel.fetch_message(message['id'])
                game_master = discord.utils.get(channel.guild.roles, name='Game Master')
                player_active = discord.utils.get(channel.guild.roles, name='Player (Active)')
                reactions = await channel_message.reactions
                mentions = ''
                attendees = []
                absentees = []
                for reaction in reactions: # Loop through all the reactions on this message
                    users = await reaction.users().flatten() # Get a list of users who have reacted with this emoji
                    emoj = reaction.emoji # Get the emoji
                    for user in users: # Loop through the users
                        if user.name == 'Sesh Time': continue
                        if emoj == '✅': attendees.append(user.name) # Append user to Attendees list if they have confirmed attendance
                        elif emoj == '❌': absentees.append(user.name) # Apppend user to the Absentees list if they have confirmed absence
                        mentions += f'{user.name}.mention '
                # Message from Database
                title = message['title'] # Get the Title
                date = message['date'] # Get the Date
                time = message['time'] # Get the Time 
                db_attendees = message['attendees']
                db_absentees = message['absentees']
                # Logic
                if len(db_absentees) != len(absentees):
                    print('Absentees != Absentees')
                elif len(db_attendees) != len(attendees):
                    print('Attendees != Attendees')
                
monitor_changes.start()
# -----------------
#   Start the Bot
# -----------------
keep_alive() # Start the HTTP server to that it runs 24/7
bot.run(os.getenv("TOKEN")) # Start the bot