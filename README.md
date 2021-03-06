# Discord Scheduler Bot
This is a self-hosted Discord bot that handles scheduling. Built with the intention to handle scheduling and RSVPs for D&amp;D 5e sessions on the 3 servers for the 3 campaigns I run. The status of a session (confirmed/unconfirmed/cancelled/uncancelled) is sent to the players and the GM via user mentions and 2 roles that I have manually added into the code: Player (Active) & Game Master.

## Definitions
- MINIMUM NUMBER OF PLAYERS = The minimum number of players required in order to run a session
- ATTENDING PLAYERS = The users who reacted to the message with a ✅
- ABSENT PLAYERS = The users who reacted to the message with a ❌
- GROUP SIZE = This is maximum number of players that could attend any given session
- TIMEZONE = The timezone that you give to this Session, which is defined on lines 20 and 21 in `main.py` by **YOU**. 

## Features
This Discord bot will 
  1. Automatically confirm a session if the `ATTENDING PLAYERS >= MINIMUM NUMBER OF PLAYERS`. 
  2. Automatically unconfirm a session if the `ATTENDING PLAYERS >= MINIMUM NUMBER OF PLAYERS` was true, but becomes false due to a player removing the reaction.
  3. Automatically cancel a session if `ABSENT PLAYERS > GROUP SIZE - MINIMUM NUMBER OF PLAYERS`.
  4. Automatically uncancel a session if `ABSENT PLAYERS = GROUP SIZE - MINIMUM NUMBER OF PLAYERS + 1`.
  5. Automatically cancels a session if a user with the `game_master_role_name` confirms absence.
  6. Automatcailly delete sessions that have a date prior to the current date.
  7. Automatically reminds those who have not RSVPed every day to do so until 24 hours before the Session is scheduled to start

### Create a New Session
- ⚠️ The only supported date format is `MM-DD-YYYY`.
- ⚠️ The only supported time format is `4pm` or `4am`. Change the number to whatever.
```
!sb event NAME, DATE, TIME, TIMEZONE, DESCRIPTION, MINIMUM NUMBER OF PLAYERS, GROUP SIZE
```
The `!sb event` takes in 7 variaables that must all be included and separated by a comma. Each variable is a string, so feel free to put whatever you want in it **EXCEPT for commas**.

#### Examples
- ⚠️ The only supported date format is `MM-DD-YYYY`.
- ⚠️ The only supported time format is `4pm` or `4am`. Change the number to whatever.
1. `!sb event Session 54, 3-22-2022, 4pm, MST, Will the party escape the evil mage's lair?, 3, 4`
    - NAME = Session 54
    - DATE = 3-22-2022
    - TIME = 4pm 
    - TIMEZONE = MST
    - DESCRIPTION = Will the party escape the evil mage's lair?
    - MINIMUM NUMBER OF PLAYERS = 3
    - GROUP SIZE = 4
    - ![Session 54 Image](https://i.imgur.com/1WNO9MW.jpg)
2. `!sb event The Orcus Fight (Session 38), 3-22-2022, 7pm, CST, Can the party defeat Orcus to save the world? Find out soon!, 2, 6`
    - NAME = The Orcus Fight (Session 38)
    - DATE = 3-22-2022
    - TIME = 7pm
    - TIMEZONE = CST
    - DESCRIPTION = Can the party defeat Orcus to save the world? Find out soon!
    - MINIMUM NUMBER OF PLAYERS = 2
    - GROUP SIZE = 6
    - ![Session 38 Image](https://i.imgur.com/vfI3kQ1.jpg)
3. `!sb event You Will Die! (Session 12), 3-22-2022, 2pm, KST, , 3, 5`
    - NAME = You will Die! (Session 12)
    - DATE = 3-22-2022
    - TIME = 2pm 
    - TIMEZONE = KST
    - DESCRIPTION = None
    - MINIMUM NUMBER OF PLAYERS = 3 
    - GROUP SIZE = 5
    - ![Session 12 Image](https://i.imgur.com/ILk21Cf.jpg)

## How to Run
If you have any questions while setting it up, just message me on [Reddit](https://www.reddit.com/message/compose/?to=Mikitz) and I'll do my best to help out. If that first link doesn't work, just head to my [Reddit Profile](https://www.reddit.com/user/Mikitz).
### Step #1: Creating a Repl
1. Go to [replit.com](https://replit.com/~) and create an account or sign in
2. Create a new Repl by clicking the ➕ in the upper-right corner
3. In the upper-right corner of the popup, click the `Import from GitHub` button.
4. Copy and paste `https://github.com/mikitz/discord-scheduler-bot` into the *GitHub URL* field.
5. Hit the white on blue `+ Import from GitHub` button
### Step #2: Create a Discord bot on your Discord account
1. Watch this [YouTube video](https://youtu.be/SPTfmiYiuok?t=120) from *00:02:00 to 00:03:02* to do so.
2. Go change line 24 in `main.py` to whatever name you gave it.
### Step #3: Invie the Bot to your Server
1. Go to [Discord.com](https://discord.com/developers/applications/961225387269029928/oauth2/url-generator)
2. Check `bot`
3. Check `Administrator`
4. Navigate to the URL at the bottom of the page
5. Select a server that you own and add it
### Step #4: Modify the Code in `main.py`
1. Open `main.py` and find the section that is between the lines that have numerous ⚠️ emoji on them (lines 19 - 30):
    - **⚠️ I have not tested this with any timezone other than the Chicago and Seoul timezones.**
    - **⚠️ You must change the below 5 variables that are marked with a ❗, else the bot will *NOT* work on your server(s).**
    - **⚠️ The remaining 4 can be unchanged if you wish.** 
    - **⚠️ Make sure to only change text inside double quotes ("") or numbers after the equals (=) sign.**
    - You can find your timezone(s) in [timezones.txt](https://github.com/mikitz/discord-scheduler-bot/blob/main/timezones.txt) by searching for a major city near the city you live in.
    - "CST" and "KST" are the names of those respective timezones. They could be anything you want, but remember this timezone will be displayed to all users on the server.
    ```
    # ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
    # Set these to whatever you need
    tzinfos = {"CST": gettz("America/Chicago"), "KST": gettz("Asia/Seoul")} # ❗ Add the timezones you'll be using. If you need more copy "CST": gettz("America/Chicago") and separate additional timezones with a comma.
    timezones = {"CST": "America/Chicago", "KST": "Asia/Seoul"} # ❗ Add the timezones again; make sure they're the same as the above. If you need more than 2, ensure you copy "CST": "America/Chicago" and separate any addtions with a comma
    game_master_role_name = "Game Master" # ❗ Enter the role name of your GM.
    player_role_name = "Player (Active)" # ❗ Enter the role name of the players.
    bot_name = "Sesh Time" # ❗ This must be the same as the name you gave it on the Discord site in Step #3.
    looping_interval = 60 # Frequency, in minutes, of checking messages for changes, updating, and deletion.
    reminders_channel_name = "reminders" # The name of the channel where the reminders will be sent.
    RSVP_deadline = 24 # The number of hours before a session when RSVPs are due, otherwise the session will be cancelled.
    remind_interval = 48 # How frequently the bot will remind players who have not RSVPed yet in hours.
    # ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
    ```
2. Hit `Ctrl+S` to save.
### Step #5: Copy your Discord Token
1. Watch this [YouTube video](https://youtu.be/SPTfmiYiuok?t=182) from *00:03:02 to 00:03:10* to copy the token.
2. Click on the 🔒 icon on the left side of the window to open *Secrets (Environment Variables)* on Replit
3. Set the `key` as "TOKEN"
4. Set the `value` as the Discord token you copied in Step 6.1
5. Click the `Add new secret` button
### Step #6: Ensure the Bot stays up forever
1. Run the bot by clicking ` Run` on Replit.
2. Copy the URL you see in the upper-right corner, just above the text *Hello, I am alive!*
3. Watch this [YouTube video](https://youtu.be/SPTfmiYiuok?t=3794) from *01:03:14 to 01:05:20* for the rest.
### Step #7: Run the Bot
1. Run the bot and forget about it (Unless it goes down for whatever reason)    
    - The bot *should* start up again on its own if it goes offline due to the Uptime you set up.
    - The bot is able to monitor all the events, even ones that were edited while offline.