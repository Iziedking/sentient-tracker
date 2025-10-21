import requests
import datetime
import os
from dotenv import load_dotenv
from utils import GITHUB_ORGS, MONITORED_REPOS
from database import add_contribution

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def poll_github_contributions(cursor, conn, notify_func):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    since = (datetime.datetime.now() - datetime.timedelta(minutes=20)).isoformat()
    for org in GITHUB_ORGS:
        for repo in MONITORED_REPOS:

            # Poll commits
            url = f'https://api.github.com/repos/{org}/{repo}/commits?since={since}'
            try:
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                commits = resp.json()
                for commit in commits:
                    sha = commit['sha']
                    cursor.execute('SELECT id FROM contributions WHERE id=?', (sha,))
                    if not cursor.fetchone():
                        timestamp = commit['commit']['author']['date']
                        author = commit['commit']['author']['name']
                        url = commit['html_url']
                        add_contribution(cursor, conn, sha, f'{org}/{repo}', 'commit', timestamp, author, url)
                        notify_func({'contrib': True, 'repo': f'{org}/{repo}', 'type': 'commit', 'timestamp': timestamp, 'author': author, 'url': url})
            except requests.RequestException as e:
                print(f"GitHub error for {repo}: {e}")

          
            url = f'https://api.github.com/repos/{org}/{repo}/pulls?state=open&sort=updated&direction=desc'
            try:
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                prs = resp.json()
                for pr in prs:
                    pr_id = str(pr['id'])
                    cursor.execute('SELECT id FROM contributions WHERE id=?', (pr_id,))
                    if not cursor.fetchone() and pr['updated_at'] > since:
                        timestamp = pr['updated_at']
                        author = pr['user']['login']
                        url = pr['html_url']
                        add_contribution(cursor, conn, pr_id, f'{org}/{repo}', 'PR', timestamp, author, url)
                        notify_func({'contrib': True, 'repo': f'{org}/{repo}', 'type': 'PR', 'timestamp': timestamp, 'author': author, 'url': url})
            except requests.RequestException as e:
                print(f"GitHub error for {repo}: {e}")