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

# Fetch messages from a specific stream
def fetch_messages(stream, topic=None, num_messages=1000):
    request = {
        "anchor": "newest",
        "num_before": num_messages,
        "num_after": 0,
        "narrow": [["stream", stream]],
    }
    if topic:
        request["narrow"].append(["topic", topic])

    response = client.get_messages(request)
    
    if response["result"] == "success":
        return response["messages"]
    else:
        print(f"Error fetching messages for stream '{stream}':", response["msg"])
        return []

# Convert timestamp to human-readable format
def convert_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Write messages to a CSV file
def write_to_csv(messages, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Sender", "Timestamp", "Message"])  # Write header row
        for msg in messages:
            timestamp = convert_timestamp(msg['timestamp'])
            writer.writerow([msg['sender_full_name'], timestamp, msg['content']])  # Write each message

# Read channel names and categories from the CSV file
def read_channels_from_csv(filename="clean_sorted_zulip_channels.csv"):
    channels = []
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            channels.append((row[0], row[1]))  # Tuple of (category, channel name)
    return channels

# Main function to fetch messages for all channels and save to separate CSV files
def main():
    channels = read_channels_from_csv()
    for category, channel in channels:
        print(f"Fetching messages for channel: {channel} in category: {category}")
        messages = fetch_messages(channel)
        if messages:
            filename = f"{category.replace(' ', '_')}_{channel.replace(' ', '_')}_messages.csv"
            write_to_csv(messages, filename)
            print(f"Messages saved to {filename}")
        else:
            print(f"No messages found for channel: {channel}")

if __name__ == "__main__":
    main()