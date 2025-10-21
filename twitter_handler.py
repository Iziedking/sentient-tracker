import tweepy
import os
from database import add_event
from dotenv import load_dotenv
from utils import matches_keywords, KEYWORDS

load_dotenv()

def get_twitter_client():
    auth = tweepy.OAuth1UserHandler(
        os.getenv('TWITTER_API_KEY'), os.getenv('TWITTER_API_SECRET'),
        os.getenv('TWITTER_ACCESS_TOKEN'), os.getenv('TWITTER_ACCESS_SECRET')
    )
    return tweepy.API(auth)

def poll_twitter_spaces(cursor, conn, notify_func):
    client = get_twitter_client()
    query = ' OR '.join(KEYWORDS) + ' filter:spaces'
    try:
        spaces = client.search_spaces(query=query, expansions=['creator_id'], space_fields=['id', 'title', 'scheduled_start', 'state', 'topic_ids'])
        for space in spaces.data or []:
            title = space.title or ''
            if matches_keywords(title) and space.state in ['scheduled', 'live']:
                space_id = space.id
                cursor.execute('SELECT id FROM events WHERE id=?', (space_id,))
                if not cursor.fetchone():
                    start_time = space.scheduled_start or 'Now'
                    link = f'https://twitter.com/i/spaces/{space_id}'
                    add_event(cursor, conn, space_id, 'X', start_time, title, '', link)
                    event = {'platform': 'X', 'title': title, 'start_time': start_time, 'link': link, 'state': space.state}
                    notify_func(event)
                    if space.state == 'live':
                        notify_func({'platform': 'X', 'title': 'Live Alert: ' + title, 'start_time': 'Now', 'link': link})
    except tweepy.TweepyException as e:
        print(f"Twitter error: {e}")