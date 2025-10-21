import discord
from discord.ext import commands
import os
from database import add_event
from dotenv import load_dotenv
from utils import matches_keywords

load_dotenv()

intents = discord.Intents.default()
intents.guild_scheduled_events = True

bot = commands.Bot(command_prefix='!', intents=intents)

def poll_discord_events(cursor, conn, notify_func):
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    guild = bot.get_guild(guild_id)
    if guild:
        for event in guild.scheduled_events:
            if matches_keywords(event.name or '') or matches_keywords(event.description or ''):
                event_id = str(event.id)
                cursor.execute('SELECT id FROM events WHERE id=?', (event_id,))
                if not cursor.fetchone():
                    start_time = str(event.start_time)
                    link = event.url if hasattr(event, 'url') else ''
                    add_event(cursor, conn, event_id, 'Discord', start_time, event.name, event.description, link)
                    notify_func({'platform': 'Discord', 'title': event.name, 'start_time': start_time, 'link': link})
    else:
        print("Guild not found.")

