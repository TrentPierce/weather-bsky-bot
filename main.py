# main.py
import os
import time
import requests
from deep_translator import LibreTranslateTranslator
from atproto import Client
import schedule

# Load config from environment variables
BLSKY_HANDLE = os.environ['BLSKY_HANDLE']
BLSKY_APP_PASSWORD = os.environ['BLSKY_APP_PASSWORD']

# Keep track of seen alert IDs
seen_ids = set()

# Set up translation
translator = LibreTranslateTranslator(source='en', target='es')

# Set up Bluesky client
client = Client()
client.login(BLSKY_HANDLE, BLSKY_APP_PASSWORD)

def fetch_and_post_alerts():
    print("Checking for new alerts...")
    try:
        response = requests.get("https://api.weather.gov/alerts/active")
        alerts = response.json().get("features", [])

        for alert in alerts:
            alert_id = alert.get('id')
            properties = alert.get('properties', {})

            if alert_id in seen_ids:
                continue

            headline = properties.get('headline', '')
            description = properties.get('description', '')
            area = properties.get('areaDesc', '')

            if not headline or not description:
                continue

            translated_headline = translator.translate(headline)
            translated_description = translator.translate(description[:800])
            
            post_text = f"\ud83c\udf0a Alerta meteorol\u00f3gica para {area}:\n\n{translated_headline}\n\n{translated_description}"

            # Post to Bluesky
            client.send_post(text=post_text)
            print(f"Posted alert: {translated_headline}")

            seen_ids.add(alert_id)
            time.sleep(2)  # small delay to avoid spamming

    except Exception as e:
        print(f"Error: {e}")

# Schedule to run every 10 minutes
schedule.every(10).minutes.do(fetch_and_post_alerts)

print("Weather alert bot is running...")
fetch_and_post_alerts()

while True:
    schedule.run_pending()
    time.sleep(30)
