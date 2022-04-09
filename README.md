# Discord Scheduler Bot
This is a self-hosted Discord bot that handles scheduling. Built with the intention to handle scheduling and RSVPs for D&amp;D 5e sessions on the 3 servers for the 3 campaigns I run. The status of a session (confirmed/unconfirmed/cancelled/uncancelled) is sent to the players and the GM via user mentions and 2 roles that I have manually added into the code: Player (Active) & Game Master.

## Definitions
- MINIMUM NUMBER OF PLAYERS = The minimum number of players required in order to run a session
- ATTENDING PLAYERS = The users who reacted to the emssage with a ✅
- ABSENT PLAYERS = The users who reacted to the message with a ❌
- GROUP SIZE = This is maximum number of players that could attend any given session

## Features
This Discord bot will 
  1. Automatically confirm a session if the `ATTENDING PLAYERS >= MINIMUM NUMBER OF PLAYERS`. 
  2. Automatically unconfirm a session if the `ATTENDING PLAYERS >= MINIMUM NUMBER OF PLAYERS` was true, but becomes false due to a player removing the reaction.
  3. Automatically cancel a session if `ABSENT PLAYERS > GROUP SIZE - MINIMUM NUMBER OF PLAYERS`.
  4. Automatically uncancel a session if `ABSENT PLAYERS = GROUP SIZE - MINIMUM NUMBER OF PLAYERS + 1`.

**IMPORTANT:** This Discord bot does NOT have a calendar built in, nor does it track time. We leave that up to the players and the GM. This means that a player could cancel/uncancel/confirm/unconfirm an old session simply by altering their reactions to those messages.

### Create a New Session
```
!sb event NAME, DATE, TIME, DESCRIPTION, MINIMUM NUMBER OF PLAYERS, GROUP SIZE
```
The `!sb event` takes in 6 variaables that must all be included and separated by a comma. Each variable is a string, so feel free to put whatever you want in it.

#### Examples
1. !sb event Session 54, 2022/3/12, 4pm MST, Will the party escape the evil mage's lair?, 3, 4
    - NAME = Session 54
    - DATE = 2022/3/12
    - TIME = 4pm MST
    - DESCRIPTION = Will the party escape the evil mage's lair?
    - MINIMUM NUMBER OF PLAYERS = 3
    - GROUP SIZE = 4
2. !sb event The Orcus Fight (Session 38), 3/28, 1900 CST, Can the party defeat Orcus to save the world? Find out soon!, 2, 6
    - NAME = The Orcus Fight (Session 38)
    - DATE = 3/28
    - TIME = 1900 CST
    - DESCRIPTION = Can the party defeat Orcus to save the world? Find out soon!
    - MINIMUM NUMBER OF PLAYERS = 2
    - GROUP SIZE = 6
3. !sb event You Will Die! (Session 12), March 16th, 2pm GMT+1, , 3, 5
    - NAME = You will Die! (Session 12)
    - DATE = March 16th
    - TIME = 2pm GMT+1
    - DESCRIPTION = null
    - MINIMUM NUMBER OF PLAYERS = 3 
    - GROUP SIZE = 5