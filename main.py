import os
import time
import logging
import datetime
import requests
from PIL import Image
from io import BytesIO
from deep_translator import MyMemoryTranslator
from atproto import Client
from atproto import models

bsky_identifier = os.getenv("BLSKY_HANDLE")
bsky_password = os.getenv("BLSKY_APP_PASSWORD")

client = Client()
client.login(bsky_identifier, bsky_password)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

translator = MyMemoryTranslator(source='en-US', target='es-MX')
seen_ids = set()

def fetch_and_post_alerts():
    logging.info("Checking for new alerts...")
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

            raw_text = f"🌊 Alerta meteorológica para {area}:\n\n{translated_headline}\n\n{translated_description}"
            post_text = raw_text[:280] + "…" if len(raw_text) > 300 else raw_text


            client.send_post(text=post_text)
            logging.info(f"✅ Posted alert: {translated_headline}")

            seen_ids.add(alert_id)
            time.sleep(2)

    except Exception as e:
        logging.error(f"❌ Error: {e}")

def post_day1_outlook():
    logging.info("Fetching the latest SPC Day 1 Outlook...")

    outlook_url = "https://www.spc.noaa.gov/products/outlook/day1otlk.gif"
    caption_en = "\U0001F300 Latest Day 1 Severe Weather Outlook from @NWSSPC\n#weather #SPC"
    caption_es = translator.translate("Latest Day 1 Severe Weather Outlook from @NWSSPC")
    caption = f"\U0001F300 {caption_es}\n#clima #SPC"

    try:
        response = requests.get(outlook_url)
        response.raise_for_status()

        img_bytes = BytesIO(response.content)
        image = Image.open(img_bytes)
        image.save("day1_outlook.gif")

        with open("day1_outlook.gif", "rb") as f:
            response = client.com.atproto.repo.upload_blob(f)
            image_blob = response.blob


        client.app.bsky.feed.post(models.AppBskyFeedPost(
            text=caption,
            embed=models.AppBskyEmbedImages.Main(images=[
                models.AppBskyEmbedImages.Image(
                    image=image_blob,
                    alt="SPC Day 1 Convective Outlook"
                )
            ])
        ))

        logging.info("Posted Day 1 SPC Outlook to Bluesky.")
    except Exception as e:
        logging.error(f"Failed to fetch or post SPC outlook: {e}")

def main():
    logging.info("Bot started and running...")
    last_post_date = None

    while True:
        logging.info("Heartbeat - bot is alive and checking...")
        now = datetime.datetime.utcnow()

        fetch_and_post_alerts()

        if last_post_date != now.date() and now.hour >= 12:
            post_day1_outlook()
            last_post_date = now.date()

        time.sleep(300)

if __name__ == "__main__":
    main()
