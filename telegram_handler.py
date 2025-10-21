from telegram import Bot
from telegram.ext import Updater, CommandHandler
import os
import datetime
import asyncio
from twitter_handler import get_twitter_client
from discord_handler import bot as discord_bot
from database import add_metric, get_last_metric, add_user, get_users  # Added get_users
from utils import matches_keywords, KEYWORDS
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = Bot(TELEGRAM_TOKEN)
updater = Updater(TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher


def subscribe(update, context):
    telegram_id = update.message.chat_id
    add_user(context.bot_data['cursor'], context.bot_data['conn'], telegram_id)
    update.message.reply_text('Subscribed to Sentient event reminders!')

dispatcher.add_handler(CommandHandler('subscribe', subscribe))


def connect_calendar(update, context):
    if len(context.args) == 1:
        calendar_id = context.args[0]
        telegram_id = update.message.chat_id
        add_user(context.bot_data['cursor'], context.bot_data['conn'], telegram_id, calendar_id)
        update.message.reply_text('Google Calendar connected!')
    else:
        update.message.reply_text('Usage: /connect_calendar your_calendar_id@group.calendar.google.com')

dispatcher.add_handler(CommandHandler('connect_calendar', connect_calendar))


def send_notification(telegram_id, message):
    bot.send_message(chat_id=telegram_id, text=message)

def check_x(update, context):
    if len(context.args) != 1:
        update.message.reply_text('Usage: /check_x username')
        return
    username = context.args[0].lstrip('@')
    telegram_id = update.message.chat_id
    try:
        client = get_twitter_client()
        user = client.get_user(username=username)
        tweets = client.get_users_tweets(user.data.id, max_results=100, tweet_fields=['public_metrics'])
        matching_tweets = [t for t in tweets.data or [] if matches_keywords(t.text)]
        if not matching_tweets:
            update.message.reply_text(f'No Sentient-related posts found for @{username}')
            return
        total_engagement = sum(t.public_metrics['like_count'] + t.public_metrics['retweet_count'] + t.public_metrics['reply_count'] for t in matching_tweets)
        rate = total_engagement / len(matching_tweets)
        now = datetime.datetime.now().isoformat()
        last_rate, _ = get_last_metric(context.bot_data['cursor'], telegram_id, 'X', username) or (0, 0)
        growth = ((rate - last_rate) / last_rate * 100) if last_rate > 0 else 0
        add_metric(context.bot_data['cursor'], context.bot_data['conn'], telegram_id, 'X', username, now, rate)
        report = f"@{username} Sentient Engagement Report:\n- Current Rate: {rate:.2f}\n- Growth: {growth:.2f}%\n- Matching Posts: {len(matching_tweets)}"
        update.message.reply_text(report)
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

dispatcher.add_handler(CommandHandler('check_x', check_x))

def check_discord(update, context):
    if len(context.args) != 1:
        update.message.reply_text('Usage: /check_discord username#discriminator or user_id')
        return
    user_input = context.args[0]
    telegram_id = update.message.chat_id
    guild = discord_bot.get_guild(int(os.getenv('DISCORD_GUILD_ID')))
    if not guild:
        update.message.reply_text('Server not found.')
        return
    try:
        if '#' in user_input:
            member = guild.get_member_named(user_input)
        else:
            member = guild.get_member(int(user_input))
        if not member:
            update.message.reply_text('User not found.')
            return
        count = 0
        for channel in guild.text_channels:

            future = asyncio.run_coroutine_threadsafe(channel.history(limit=100), discord_bot.loop)
            history = future.result()
            for msg in history:
                if msg.author.id == member.id:
                    count += 1
        now = datetime.datetime.now().isoformat()
        _, last_count = get_last_metric(context.bot_data['cursor'], telegram_id, 'Discord', str(member.id)) or (0, 0)
        growth = ((count - last_count) / last_count * 100) if last_count > 0 else 0
        add_metric(context.bot_data['cursor'], context.bot_data['conn'], telegram_id, 'Discord', str(member.id), now, 0, count)
        report = f"{member.name} Discord Message Report:\n- Recent Count: {count}\n- Growth: {growth:.2f}%"
        update.message.reply_text(report)
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

dispatcher.add_handler(CommandHandler('check_discord', check_discord))

def notify_users(event, cursor, add_to_calendar_func):
    for telegram_id, calendar_id in get_users(cursor):
        if 'contrib' in event:
            message = f"New {event['type']} in {event['repo']}: {event['author']} at {event['timestamp']}. URL: {event['url']}"
        else:
            message = f"Upcoming {event['platform']} event: {event['title']} starts at {event['start_time']}. Link: {event['link']}"
            if event.get('state') == 'live':
                message = "ALERT: " + message
        send_notification(telegram_id, message)
        if calendar_id and 'contrib' not in event:
            add_to_calendar_func(event, calendar_id)