import zulip
import time
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from secrets.env
load_dotenv(dotenv_path="secrets.env")

EMAIL = os.getenv("EMAIL")
API_KEY = os.getenv("API_KEY")
ZULIP_SITE = os.getenv("ZULIP_SITE")

client = zulip.Client(email=EMAIL, api_key=API_KEY, site=ZULIP_SITE)

# Fetch all streams (channels)
def fetch_streams():
    response = client.get_streams()
    
    if response["result"] == "success":
        return [stream["name"] for stream in response["streams"]]
    else:
        print("Error:", response["msg"])
        return []

# Write stream names to CSV
def write_streams_to_csv(streams, filename="zulip_channels.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Channel Name"])  # Header row
        for stream in streams:
            writer.writerow([stream])  # Write each channel name

# Fetch streams and save to CSV
streams = fetch_streams()
write_streams_to_csv(streams)

print("Channels saved to zulip_channels.csv")
