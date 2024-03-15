## Weather bot for Telegram

#### *Can be found as @WeatherViennaBot*

This is a small personal project to explore basic API usage and Python in general.   
Starting as a small bot that only gives the current weather in Vienna (hence the name), it can now get the current weather of any city or town.

## List of commands

- `/start`

    Executed on starting the bot - greets the user and informs them of `/weather` command

- `/weather`

    Starts the weather conversation.  
    Prompts the user for a city: returns the weather report if the city is found, otherwise reprompts

- `/cancel`

    Gets the user out of the `/weather` conversation if needed

- `/help`

    If the user is stuck, provides an instruction how to get the weather report via `/weather`
