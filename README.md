# Sentient Event Tracker: Full Project Idea and Description

The core idea behind this build is to create a robust, modular Python-based agent (or bot) that automates the monitoring and notification of events, engagements, and contributions related to Sentient AGI an open-source artificial general intelligence (AGI) project focused on decentralized, community-driven AI development. Sentient AGI, as per its official site (sentient.xyz), emphasizes open-source tools like ROMA (a reasoning model), ODS (Open Deep Search), and other initiatives under the Sentient Foundation. The agent addresses challenges like X's (formerly Twitter) rate limits by using efficient API polling instead of real-time streaming, making it sustainable for long-term use.
The project started as a response to manual tracking frustrations (e.g., missing Spaces or Discord events due to rate limits) and evolved into a full-featured system. It's designed to be beginner-friendly, with a Git repository structure, separate modules for each platform, and a central orchestrator. Users interact primarily through a Telegram bot, which handles subscriptions, queries, and notifications keeping everything user-centric without needing direct code access. The agent runs locally or on a server (e.g., Heroku, AWS) and can be open-sourced to align with Sentient's ethos.
Key Features and Components

## Event Tracking Across Platforms:

X (Twitter) Spaces: Polls the Twitter API every 20 minutes for Spaces matching keywords like "@sentientAGI", "sentient", "ROMA", "ODS", "open source AGI", "AGI", "Sentient Foundation", "Open AGI Summit", "Sentient Eco", "Dobby API", "GRID". It filters for scheduled or live Spaces, stores new ones in a database to avoid duplicates, and sends notifications. If a Space is live, it triggers an immediate "ALERT" message.
Discord Events: Connects to the Sentient Discord server (via bot token and guild ID) and polls for scheduled events in channels like #announcements or #events. Filters by keywords in names/descriptions and notifies users with details like start time and link.
GitHub Contributions: Monitors specified repositories under organizations like "sentient-agi" and "sentient-engineering" (e.g., ROMA, Sentient-Agent-Framework, OpenDeepSearch). Polls every 20 minutes for new commits and pull requests (PRs) since the last check, stores them, and alerts subscribed users with details (repo, type, author, timestamp, URL).


## Notification and Reminder System:

Telegram Bot: Central hub for user interaction. Users subscribe with /subscribe, connect Google Calendar with /connect_calendar [id], and receive push notifications for events, live alerts, and contributions. Reminders are sent ~30 minutes before events (based on start_time checks), with optional auto-add to linked calendars.
Google Calendar Integration: Optional; uses service account credentials to insert events (title, start/end, link) into user-provided calendar IDs. Future expansion could include full OAuth for per-user auth.


## User Engagement Checks (Mini-Share Reports):

X Engagement: Command /check_x [username] fetches recent tweets (up to 100), filters for Sentient-related content via keywords, calculates average engagement rate (likes + retweets + replies per post), compares to previous checks for growth %, and reports back (e.g., "Current Rate: 5.2, Growth: 15%, Matching Posts: 8").
Discord Messages: Command /check_discord [username#discrim or id] scans recent messages (up to 100 per channel) in the Sentient server, counts them, computes growth from prior checks, and reports (e.g., "Recent Count: 42, Growth: 20%").
These provide "mini-share" insights, like a lightweight analytics dashboard, stored per user in the DB for historical tracking.


## Technical Architecture:

### Modular File Structure (Git repo: sentient-event-tracker):

main.py: Orchestrates everything. initializes DB, schedules polls, runs Telegram/Discord bots in threads.
database.py: SQLite DB for events, users, metrics (engagements), contributions. Handles CRUD to prevent duplicates.
utils.py: Shared keywords, GitHub repos/orgs, matching functions.
twitter_handler.py: Twitter API auth, Spaces polling, keyword filtering.
discord_handler.py: Discord bot setup, event polling.
telegram_handler.py: Telegram Application (v20+), command handlers (/start, /subscribe, checks), notifications.
calendar_handler.py: Google Calendar API integration.
github_handler.py: GitHub API polling for commits/PRs.
.env: Secure storage for API keys/tokens (Twitter, Discord, Telegram, Google, optional GitHub).


Polling and Scheduling: Uses schedule library for 20-minute cycles (rate-limit friendly). Polls detect new items, notify immediately.
Dependencies: Listed in requirements.txt (tweepy, discord.py, python-telegram-bot v20.8, etc.).
Error Handling: Try/except in polls for API errors (e.g., rate limits with backoff), DB integrity.


## Motivation and Benefits
This agent solves the pain of missing key Sentient AGI discussions (e.g., AMAs, summits) amid rate limits and scattered platforms. It fosters community engagement by providing timely reminders, growth insights (encouraging participation), and contribution alerts aligning with Sentient's open-source mission. For users, it's a hands-off tool: subscribe once, get updates forever. Cost: Near-zero (free APIs for basics), setup in a weekend.
