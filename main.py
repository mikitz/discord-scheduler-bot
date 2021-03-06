# -----------
#   Imports
# -----------
from cmath import nan
from distutils.log import error
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
# ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
# Set these to whatever you need
tzinfos = {"CST": gettz("America/Chicago"), "KST": gettz("Asia/Seoul")} # Add the timezones you'll be using.
timezones = {"CST": "America/Chicago", "KST": "Asia/Seoul"} # Add the timezones again; make sure they're the same as the above.
game_master_role_name = "Game Master" # Enter the role name of your GM.
player_role_name = "Player (Active)" # Enter the role name of the players.
bot_name = "Sesh Time" # This must be the same as the name you gave it on the Discord site in Step #2.
looping_interval = 60 # Frequency, in minutes, of checking messages for changes, updating, and deletion.
reminders_channel_name = "reminders" # The name of the channel where the reminders will be sent.
RSVP_deadline = 24 # The number of hours before a session when RSVPs are due, otherwise the session will be cancelled.
remind_interval = 60 # How frequently the bot will remind players who have not RSVPed yet in hours.
# ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
# --------------
#   Initialize
# --------------
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
activity = discord.Activity(type=discord.ActivityType.listening, name="!sb") # Set up the bot's activity
bot = commands.Bot(command_prefix='!sb ', intents=intents, activity=activity, status=discord.Status.online) # Initialize Bot Commands
bot.remove_command('help') # Remove the default command
hours_counter = 0
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
    print("----------------------")
    print("Deleting Old Events...")
    print("----------------------")
    for guild in bot.guilds:
        guild = str(guild.name)
        if guild in db.keys():
            print(f"*** Inspecting events for Server {guild}... ***")
            indecies_to_delete = []
            messages = db[guild]
            for idx, element in enumerate(messages):
                dt = element['datetime']
                datetime_object = parse(dt, tzinfos=tzinfos)
                new_time = datetime_object + datetime.timedelta(days=1) # Add 6 days to the event time
                tz = element['timezone']
                print("Timezone:", tz)
                local_time = datetime.datetime.now(pytz.timezone(timezones.get(tz))) # Get local time and convert it to the timezone of the event
                if local_time >= new_time:
                    print(f"Deleting Message at index {idx}...")
                    indecies_to_delete.append(idx) # Append this index to a list of those that need to be deleted
            # Delete those that need to be deleted
            if indecies_to_delete:
                for idx in indecies_to_delete:
                    del messages[idx]
                db[guild] = messages
            else:
                print(f"No old events deleted in Server {guild}")
        else:
            print(f"No events found in Server {guild}.")
# ------------------------
#   Bot Command Fuctions
# ------------------------
# On start up
@bot.event
async def on_ready():
    print("----------------------------------------------------")
    print(f"{bot_name} is running with the the below...")
    print("----------------------------------------------------")
    # db['Seafaring Shenanigans'][0]['guild_id'] = 733495705468928061 # Add the missing Guild ID
    # print("Keys:", db.keys()) # Uncomment this to delete all data from the Database
    # for key in db.keys():
    #     print(f'Deleting Key for Server "{key}"')
    #     del db[key]
        # for message in db[key]:
            # print("\nMessage:", message)
    print("Bot Name:", bot_name)
    print("Timezones:", timezones)
    print("Game Master Role Name:", game_master_role_name)
    print("Player Role Name:", player_role_name)
    print("Looping Interval:", looping_interval, "minute(s)")
    print("Reminders Channel:", reminders_channel_name)
    print("Remind Interval:", remind_interval, "hour(s)")
# Function that runs when a reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    if user.name == bot_name: return # Don't do anything if it's Sesh Time reacting
    message_id = reaction.message.id
    channel_id = reaction.message.channel.id
    guild_id = reaction.message.guild.id
    await send_message_based_on_reactions(message_id, channel_id, guild_id)   
# Function that runs when a reaction is removed
@bot.event
async def on_reaction_remove(reaction, user):
    if user.name == bot_name: return # Don't do anything if it's Sesh Time reacting
    message_id = reaction.message.id
    channel_id = reaction.message.channel.id
    guild_id = reaction.message.guild.id
    await send_message_based_on_reactions(message_id, channel_id, guild_id)
# Function to spit out a help message
@bot.command()
async def help(ctx): #!sb help
    embed = discord.Embed(
        title='Sesh Time',
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
        value='`!sb event` creates a new event using the followwing syntax: `!sb event NAME, DATE, TIME, TIMEZONE, DESCRIPTION, MINIMUM NUMBER OF PLAYERS, GROUP SIZE`. \n *DESCRIPTION is optional*',
        inline=False
    )
    await ctx.send(embed=embed)
# Function to give the user info about the bot
@bot.command()
async def info(ctx): # !sb info
    embed = discord.Embed(
        title='Sesh Time',
        description='Sesh Time Info',
        color=discord.Colour.green()
    )
    embed.set_thumbnail(url='https://avatars.githubusercontent.com/u/17684097?s=400&u=badb2a3839ce5cb4e5c3f75dc3172c1f2786412b&v=4')
    embed.add_field(
        name='Ko-fi',
        value="Buy Mikitz some avocadoes because he doesn't drink coffee 😂: https://ko-fi.com/mikitz",
        inline=False
    )
    embed.add_field(
        name='GitHub',
        value='View the open-source code: https://github.com/mikitz/discord-scheduler-bot',
        inline=False
    )
    await ctx.send(embed=embed)
# New Event Command
# Function to create a new event
@bot.command()
async def event(ctx, *args): # !sb event
    print("------------------")
    print("New Event Added...")
    print("------------------")
    args_string = ' '.join(args)
    params = args_string.split(", ")
    guild = str(ctx.message.guild)
    guild_id = ctx.message.guild.id
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
    player_active = discord.utils.get(ctx.guild.roles, name=player_role_name) # Grab the Player (Active) role
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
        "group_size": group_size,
        "guild_id": guild_id,
        "description": description
    }
	# Adding Data
    if guild in db.keys():
        msgs = db[guild]
        msgs.append(message_object)
        db[guild] = msgs
        print(f"Data added to Server {guild}:", message_object)
    else:
        db[guild] = [message_object]
        print(f"Data added to Server {guild}:", message_object)
    # ===============
    #  Add Reactions
    # ===============
    await message.add_reaction("✅")
    await message.add_reaction("❌")
# --------------------
#   Looped Functions
# --------------------
# Function to auto cancel sessions that don't have enough player reserved
@tasks.loop(minutes=looping_interval)
async def auto_cancel_event():
    await delete_non_applicable_events()
    print("------------------")
    print("Auto-cancelling...")
    print("------------------")
    to_delete_messages = []
    for guild in bot.guilds:
        dic_guild = guild
        guild = str(guild.name)
        if guild in db.keys():
            print(f"*** Inspecting messages for Server {guild}... ***")
            messages = db[guild]
            for idx, message in enumerate(messages):
                channel = discord.utils.get(dic_guild.channels, name=message['channel']['name'])
                try: 
                    channel_message = await channel.fetch_message(message['id'])
                except discord.HTTPException as e:
                    print("Message ID:", message['id'])
                    print("Error:", e.text)
                    continue # Go to the next message
                title = message['title']
                date = message['date']
                time = message['time']
                dt = message['datetime']
                datetime_object = parse(dt, tzinfos=tzinfos) 
                tz = message['timezone']
                local_time = datetime.datetime.now(pytz.timezone(timezones.get(tz))) # Get local time and convert it to the timezone of the event
                if datetime_object - datetime.timedelta(hours=RSVP_deadline) <= local_time:
                    if len(message['attendees']) <= int(message['min_players']):
                        game_master = discord.utils.get(channel.guild.roles, name=game_master_role_name)
                        player_active = discord.utils.get(channel.guild.roles, name=player_role_name)
                        await channel_message.channel.send( # Send a message saying the session is cancelled due to not enough players RSVPing within 24 hours
                            content = f'{player_active.mention} {game_master.mention} \n *SESSION CANCELLED* -- **{title}**, scheduled for {date} at {time}, has been *CANCELLED* due to not having enough players confirm attendance before 24 hours prior to session start.', 
                            allowed_mentions = discord.AllowedMentions(roles=True)
                        )
                    print(f'Auto-cancelling and deleting event {title}...')
                    to_delete_messages.append(idx)
                else:
                    print(f"No auto-cancels performed for Server {guild}.")
        else:
            print(f"No messages found for Server {guild}.")
    for msg in to_delete_messages:
        msg = int(msg)
        del db[guild][msg]
    print("-----------------")
    print("Making Changes...")
    print("-----------------")
    for guild in bot.guilds:
        dic_guild = guild
        guild = str(guild.name)
        if guild in db.keys():
            print(f"*** Making Changes for Server {guild}... ***")
            messages = db[guild]
            if len(messages) > 0:
                for idx, message in enumerate(messages):
                    print("Message:", message)
                    message_id = message['id']
                    channel_id = message['channel']['id']
                    guild_id = message['guild_id']
                    await send_message_based_on_reactions(message_id, channel_id, guild_id) 
            else: 
                print(f"No changes made for Server {guild}")
        else:
            print(f"No messages found for Server {guild}")
auto_cancel_event.start()
@tasks.loop(hours=remind_interval)
async def remind_non_RSVPed_players():
    print("--------------------")
    print("Reminding Players...")
    print("--------------------")
    for gld in bot.guilds: # Loop through each guild
        guild = bot.get_guild(gld.id) # Get the Guild object from the Guild ID
        player_active_role = discord.utils.get(guild.roles, name=player_role_name) # Get the Users who are players
        players = player_active_role.members
        guild_name = str(guild.name)
        if guild_name in db.keys():
            print(f"*** Inspecting messages for Reminding for Server {guild}... ***")
            messages = db[guild_name]
            for idx, message in enumerate(messages):
                non_RSVPed_players = []
                channel = discord.utils.get(guild.channels, name=message['channel']['name']) # Get the channel where the message is
                try:    
                    msg = await channel.fetch_message(message['id']) # Get the message
                except discord.HTTPException as e:
                    print("~~~ERROR~~~")
                    print("Message ID:", message['id'])
                    print("Error:", e.text)
                    continue # Go to the next message
                reactions = msg.reactions
                dt = message['datetime']
                datetime_object = parse(dt, tzinfos=tzinfos) 
                tz = message['timezone']
                local_time = datetime.datetime.now(pytz.timezone(timezones.get(tz))) # Get local time and convert it to the timezone of the event
                for player in players:
                    player_name = player.name
                    for reaction in reactions:
                        users = await reaction.users().flatten()
                        print("Non-RSVPed Players (BEFORE):", non_RSVPed_players)
                        if player_name in str(non_RSVPed_players): continue # Skip this player b/c they'are already going to be reminded for this Session
                        if len(users) <= 1 and local_time <= datetime_object - datetime.timedelta(hours=RSVP_deadline):
                            non_RSVPed_players.append({ # Add the player to the to-be reminded list
                                "user_id": player.id,
                                "user_name": player_name,
                                "message_id": message['id'], 
                                "channel_id": message['channel']['id'], 
                                "guild_id": message['guild_id'],
                                "title": message['title'],
                                "time": message['time'],
                                "timzone": message['timezone'],
                                "date": message['date']
                            })
                            continue # Skip to the next user
                        for user in users:
                            user_name = user.name
                            if user_name == bot_name: continue # Skip the bot
                            if user_name == player_name or user_name in non_RSVPed_players: continue # Skip b/c this player has already reacted
                            if local_time <= datetime_object - datetime.timedelta(hours=RSVP_deadline): # Only remind the player if the sessioni is more than 24 hours away
                                non_RSVPed_players.append({
                                    "user_id": player.id,
                                    "user_name": player_name,
                                    "message_id": message['id'], 
                                    "channel_id": message['channel']['id'], 
                                    "guild_id": message['guild_id'],
                                    "title": message['title'],
                                    "time": message['time'],
                                    "timzone": message['timezone'],
                                    "date": message['date']
                                })
                if len(non_RSVPed_players) > 0:
                    print("Non-RSVPed Players (AFTER):", non_RSVPed_players)
                    mentions = ''
                    for player in non_RSVPed_players:
                        user = await bot.fetch_user(player['user_id'])
                        mentions += f"{user.mention} "
                    guild = bot.get_guild(message['guild_id']) # Get the Guild object from the Guild ID
                    channel = guild.get_channel(message['channel']['id']) # Get the Channel object from the Guild object
                    message = await channel.fetch_message(message['id']) # Get the Message object from the Channel object
                    link = message.jump_url # Grab the URL that allows the user to jump to the specified message
                    # Pull Message from Database
                    msg_index = index_of(db[str(guild)], 'id', message.id) # Get the Index of this Message by its ID
                    db_msg = db[str(guild)][msg_index] # Pull this Message's data from the Database
                    # Remind the User
                    channel = discord.utils.get(guild.channels, name=reminders_channel_name)
                    await channel.send(f"{mentions}, this is a friendly reminder that you have yet to RSVP for **{db_msg['title']}** scheduled for **{db_msg['date']}** at **{db_msg['time']} {db_msg['timezone']}**, which can be found here: {link}")
        else:
            print(f"------No Reminders sent for Server {guild}")
remind_non_RSVPed_players.start()
# ===========================================
#       Rewrite with Minimal Functions
# ===========================================
async def send_message_based_on_reactions(message_id, channel_id, guild_id):
    # Variables
    guild = bot.get_guild(guild_id) # Get the Guild object from the Guild ID
    channel = guild.get_channel(channel_id) # Get the Channel object from the Guild object
    try:
        message = await channel.fetch_message(message_id) # Get the Message object from the Channel object
    except Exception as e:
        print("~~~ERROR~~~")
        print("Error:", e)
        return # End the function b/c the channel doesn't exist
    reactions = message.reactions # Get the Reactions object from the Message object
    # Pull Message from Database
    msg_index = index_of(db[str(guild)], 'id', message.id) # Get the Index of this Message by its ID
    db_msg = db[str(guild)][msg_index] # Pull this Message's data from the Database
    # Get other data from the Database for this message
    group_size = int(db_msg['group_size']) # Get the Group Size integer from the Stored Message data
    min_players = int(db_msg['min_players']) # Get the Min. Players integer from the Stored Message data
    title = db_msg['title'] # Get the Title string from the stored Message data
    date = db_msg['date'] # Get the Date string from the stored Message data
    time = db_msg['time'] # Get the Time string from the stored Message data
    dt = db_msg['datetime'] # Get the DateTime object from the stored Message data
    timezone = db_msg['timezone'] # Get the Timezone string from the stored Message data
    # Get stored Reaction counts from the Database
    db_msg_attendees = len(db_msg['attendees']) # Get the number of stored Attendees
    db_msg_absentees = len(db_msg['absentees']) # Get the number of stored Absentees
    # Get the current Reaction counts
    attendees = [] # Create an empty list to store the users who confirm attendance
    absentees = [] # Create an empty list to store the users who confirm absence
    game_master = False # Set up Game Master for looping through the reactions and seeing if the user is a GM
    for reaction in reactions: # Loop through all the reactions on this message
        users = await reaction.users().flatten() # Get a list of users who have reacted with this emoji
        emoj = reaction.emoji # Get the emoji
        for user in users: # Loop through the users
            if emoj == '✅': attendees.append(user.name) # Append user to Attendees list if they have confirmed attendance
            elif emoj == '❌': 
                absentees.append(user.name) # Apppend user to the Absentees list if they have confirmed absence
                if game_master_role_name in str(user.roles): 
                    game_master = True
    message_attendees = len(attendees) # Get the number of current Attendees less the Bot
    message_absentees = len(absentees) # Get the number of current Absentees less the Bot
    # Attendees
    print("DB Attendees:", db_msg_attendees)
    print("Message Attendees:", message_attendees)
    # Absentees
    print("DB Absentees:", db_msg_absentees)
    print("Message Absentees:", message_absentees)
    
    if db_msg_absentees == message_absentees and db_msg_attendees == message_attendees: return # If they are the same, return b/c nothing needs to be done
    # Get Discord Roles
    game_master_role = discord.utils.get(guild.roles, name=game_master_role_name)
    player_active_role = discord.utils.get(guild.roles, name=player_role_name)
    print("Player (Active):", player_active_role)
    print("Gamemaster Role:", game_master_role)
    # Determine what message to send based on Reaction counts of the message
    status = 'pending' # Set up Status in case none of the below is met
    # Cancel Session
    if game_master: # Cancel the Session b/c the GM has stated they cannot make it
        await message.channel.send( # Send a message saying the session is cancelled due to too many players not being able to make it
            content = f'{player_active_role.mention} {game_master_role.mention} \n *SESSION CANCELLED* -- **{title}** is *CANCELLED* which was scheduled for **{date}** at **{time}** by the Gamemaster.', 
            allowed_mentions = discord.AllowedMentions(roles=True)
        )
        status = 'cancelled'
    # Cancel Session
    elif message_absentees > group_size - min_players: # Cnacel the session because the number of players who have not reacted is lower than the minimum player requirement
        await message.channel.send( # Send a message saying the session is cancelled due to too many players not being able to make it
            content = f'{player_active_role.mention} {game_master_role.mention} \n *SESSION CANCELLED* -- **{title}** is *CANCELLED* which was scheduled for **{date}** at **{time}** due to too many players not being able to make it.', 
            allowed_mentions = discord.AllowedMentions(roles=True)
        )
        status = 'cancelled'
    # Session is a go!
    elif message_attendees >= min_players: # Confirm the Session because the number of players who confirmed attendance is equal to or greater than the minimum required
        await message.channel.send(
            content = f'{player_active_role.mention} {game_master_role.mention} \n *SESSION CONFIRMED* -- **{title}** is *CONFIRMED* for **{date}** at **{time}**!', 
            allowed_mentions = discord.AllowedMentions(roles=True)
        )
        status = 'confirmed'
    # Uncancel the Session
    elif message_absentees == group_size - min_players + 1:
        await message.channel.send( # Send a message saying the session is cancelled due to too many players not being able to make it
            content = f'{player_active_role.mention} {game_master_role.mention} \n *SESSION UNCANCELLED* -- **{title}** is has been *UNCANCELLED*. Please reconsider your attendance for **{date}** at **{time}** and react with the appropriate Reaction.', 
            allowed_mentions = discord.AllowedMentions(roles=True)
        )
        status = 'pending'
    # Unconfirm the Session
    elif message_attendees == min_players - 1:
        await message.channel.send(
            content = f'{player_active_role.mention} {game_master_role.mention} \n *SESSION UNCONFIRMED* -- **{title}** has been *UNCONFIRMED*. Only {min_players - message_attendees} more player needed to confirm the session!', 
            allowed_mentions = discord.AllowedMentions(roles=True)
        )
        status = 'pending'
    # --------------------------------------------
    # Finally update the Database for this message
    # --------------------------------------------
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
        "datetime": dt,
        "timezone": timezone,
        "attendees": attendees,
        "absentees": absentees,
        "status": status,
        "title": title,
        "date": date,
        "time": time,
        "min_players": min_players,
        "group_size": group_size,
        "guild_id": guild_id
    }
    db[str(guild)][msg_index] = message_object
# -----------------
#   Start the Bot
# -----------------
try:
    keep_alive() # Start the HTTP server so that it runs 24/7
    bot.run(os.getenv("TOKEN")) # Start the bot
except discord.HTTPException as e:
    print("\n\n\n BLOCKED BY HTTP EXCEPTION \n RESTARTING IN 10 SECONDS \n")
    # print("Message:", e.text)
    print("Status:", e.status)
    print("Code:", e.code)
    print("\n")
    os.system("python restart.py")
    os.system("kill 1")