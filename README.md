# Discord Scheduler Bot
This is a self-hosted Discord bot that handles scheduling. Built with the intention to handle scheduling and RSVPs for D&amp;D 5e sessions on the 3 servers for the 3 campaigns I run.

## Features
This Discord bot will 
  1. Automatically confirm a session once the MINIMUM NUMBER OF PLAYERS have RSVPed
  2. Automatically unconfirm a session if the MINIMUM NUMBER OF PLAYERS threshold was met, but becomes unmet by a player removing the reaction
  3. Automatically cancel a session based on GROUP SIZE and MINIMUM NUMBER OF PLAYERS
  4. Automatically uncancel a session if if the number of absent players is equal to `GROUP SIZE - MINIMUM NUMBER OF PLAYERS + 1`
### Create a New Session
The `!sb event` takes in 6 varaiables that must all be included and separated by a comma.
```
!sb event NAME, DATE, TIME, DESCRIPTION, MINIMUM NUMBER OF PLAYERS, GROUP SIZE
```