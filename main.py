import schedule
import time
import os
from dotenv import load_dotenv
from database import init_db
from twitter_handler import poll_twitter_spaces
from discord_handler import poll_discord_events, bot as discord_bot
from telegram_handler import updater, dispatcher, notify_users
from calendar_handler import add_to_calendar
from github_handler import poll_github_contributions
import threading

load_dotenv()

conn, cursor = init_db()

# Pass DB 
dispatcher.bot_data['conn'] = conn
dispatcher.bot_data['cursor'] = cursor

def notify_wrapper(event):
    notify_users(event, cursor, add_to_calendar)

# Polling jobs
def run_polls():
    poll_twitter_spaces(cursor, conn, notify_wrapper)
    poll_discord_events(cursor, conn, notify_wrapper)
    poll_github_contributions(cursor, conn, notify_wrapper)
    

# Schedule polls
schedule.every(15).minutes.do(run_polls)

# Run Telegram and Discord bots 
def run_telegram():
    updater.start_polling()
    updater.idle()

def run_discord():
    discord_bot.run(os.getenv('DISCORD_TOKEN'))

threading.Thread(target=run_telegram).start()
threading.Thread(target=run_discord).start()


while True:
    schedule.run_pending()
    time.sleep(1)