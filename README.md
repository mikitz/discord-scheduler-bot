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
The `!sb event` takes in 6 varaiables that must all be included and separated by a comma.
```
!sb event NAME, DATE, TIME, DESCRIPTION, MINIMUM NUMBER OF PLAYERS, GROUP SIZE
```