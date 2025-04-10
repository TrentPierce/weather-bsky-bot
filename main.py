import os
import time
import requests
from deep_translator import MyMemoryTranslator
from atproto import Client
import schedule

# Load config from environment variables
BLSKY_HANDLE = os.environ['BLSKY_HANDLE']
BLSKY_APP_PASSWORD = os.environ['BLSKY_APP_PASSWORD']

# Keep track of seen alert IDs
seen_ids = set()

# Set up translation (English to Spanish)
translator = MyMemoryTranslator(source='en', target='es')

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

            # Translate headline and part of description
            translated_headline = translator.translate(headline)
            translated_description = translator.translate(description[:800])  # NWS descriptions can be long

            post_text = f"🌊 Alerta meteorológica para {area}:\n\n{translated_headline}\n\n{translated_description}"

            # Post to Bluesky
            client.send_post(text=post_text)
            print(f"✅ Posted alert: {translated_headline}")

            seen_ids.add(alert_id)
            time.sleep(2)  # avoid spamming

    except Exception as e:
        print(f"❌ Error: {e}")

# Schedule to run every 10 minutes
schedule.every(10).minutes.do(fetch_and_post_alerts)

print("✅ Weather alert bot is running...")
fetch_and_post_alerts()

# Keep the schedule running and host a fake server
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Weather bot is running!')

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

# Start the fake server in a background thread
threading.Thread(target=run_server, daemon=True).start()

# Keep bot running with schedule
while True:
    schedule.run_pending()
    time.sleep(30)
