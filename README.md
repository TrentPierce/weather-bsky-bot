# Bluesky Weather Alert Translator Bot

This bot fetches weather alerts from the National Weather Service, translates them to Spanish, and posts them on a Bluesky account every 10 minutes.

## Setup

1. Clone this repo
2. Create a `.env` file (or set environment variables in Render)
3. Push to GitHub and connect to [Render](https://render.com)

## Required Environment Variables

- `BLSKY_HANDLE` = your Bluesky handle (e.g. `botname.bsky.social`)
- `BLSKY_APP_PASSWORD` = app password (create here: https://bsky.app/settings/app-passwords)

## Deployment

1. Create a new **Background Worker** service in Render
2. Point it at your GitHub repo
3. Add your environment variables
4. Done!
