import schedule
import time
import os
import asyncio  # Added for async run
from dotenv import load_dotenv
from database import init_db
from twitter_handler import poll_twitter_spaces
from discord_handler import poll_discord_events, bot as discord_bot
from telegram_handler import application, notify_users  # Changed from updater/dispatcher
from calendar_handler import add_to_calendar
from github_handler import poll_github_contributions
import threading

load_dotenv()

conn, cursor = init_db()


application.bot_data['conn'] = conn
application.bot_data['cursor'] = cursor

def notify_wrapper(event):
    notify_users(event, cursor, add_to_calendar)


def run_polls():
    poll_twitter_spaces(cursor, conn, notify_wrapper)
    poll_discord_events(cursor, conn, notify_wrapper)
    poll_github_contributions(cursor, conn, notify_wrapper)


schedule.every(15).minutes.do(run_polls)


async def run_telegram_polling():
    async with application:
        await application.start()
        await application.updater.start_polling()  # Or application.run_polling() directly
        await application.updater.stop()
        await application.stop()

def run_telegram():
    asyncio.run(run_telegram_polling())


def run_discord():
    discord_bot.run(os.getenv('DISCORD_TOKEN'))

threading.Thread(target=run_telegram).start()
threading.Thread(target=run_discord).start()

while True:
    schedule.run_pending()
    time.sleep(1)