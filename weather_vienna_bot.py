#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.


import logging
import json
import requests
import os

from dotenv import load_dotenv
from telegram import ForceReply, Update, User
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

from coordinates import Coordinates
from weather_forecast import WeatherForecast

load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define conversation state
CITY = range(1)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user: User = update.effective_user  # type: ignore
    if update.message is None:
        return
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Please write /weather to select a city and get current weather there",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    if update.message is None:
        return
    await update.message.reply_text(
        "Send /weather to select a city and get current weather there"
    )


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send current Vienna weather"""
    if update.message is None:
        return
    await update.message.reply_text(
        "Which city would you like to check the weather in?"
    )
    return CITY


async def return_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returns current weather for given city"""
    if not update.message or not update.message.text:
        return
    user_says = update.message.text
    city_coords: Coordinates | None = get_coords(user_says)

    if city_coords is None:
        await update.message.reply_text(
            "Sorry, I can't find this city. Please try again"
        )
        return CITY

    weather: WeatherForecast | None = get_weather(city_coords)
    await update.message.reply_text(weather.generate_report())
    return ConversationHandler.END


def get_coords(city: str):
    """Get coordinates for the selected city"""
    url_loc = f"https://geocoding-api.open-meteo.com/v1/search?name={city.strip()}&count=1&language=en&format=json"
    cities = json.loads(requests.get(url_loc, timeout=60).text)
    try:
        long = cities["results"][0]["longitude"]
        lat = cities["results"][0]["latitude"]
        loc = cities["results"][0]["name"]
        country = cities["results"][0]["country"]
    except Exception:
        return None
    return Coordinates(loc, country, lat, long)


def get_weather(coords: Coordinates) -> WeatherForecast:
    """Get weather for passed coordinates"""

    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords.lat}&longitude={coords.long}&current=temperature_2m,weather_code"
    weather = json.loads(requests.get(url, timeout=60).text)
    temp = round(weather["current"]["temperature_2m"])
    weather_code = weather["current"]["weather_code"]

    return WeatherForecast(coords, temp, weather_code)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler in case of unknown commands/messages"""
    if update.effective_chat is None:
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    if not update.message:
        return None
    await update.message.reply_text("Weather command cancelled :(")

    return ConversationHandler.END


def main() -> None:
    """Start the bot."""

    telegram_bot_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_bot_token:
        raise Exception("Missing telegram bot token")
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(telegram_bot_token)
        .build()
    )

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on starting weather conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("weather", weather_command)],
        states={
            CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, return_weather),
                CommandHandler("cancel", cancel),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # on unrecognizable command
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

# Steps:
# 2. Refactor coordinates finding + weather into separate method
# 3. persist location settting per user (for now in JSON)
# 4. read tokens (and other app configs) from .env file https://github.com/theskumar/python-dotenv


# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Types-of-Handlers#commandhandlers-with-arguments
