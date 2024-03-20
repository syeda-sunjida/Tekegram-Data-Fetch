from telethon.sync import TelegramClient
import datetime
import pandas as pd
import os
import re
import pytz  # Import the pytz library

api_id = 20958493
api_hash = '6c6ef1995153c4596f203d2cfb018ab0'

# Initialize the client
client = TelegramClient('test', api_id, api_hash)

# Start the client
client.start()

# Define the DataFrame outside of the loop
df = pd.DataFrame()

# Fetch all dialogs
dialogs = client.get_dialogs()

# Calculate the date for 30 days ago
one_month_ago = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=30)  # Ensure the datetime is timezone-aware

# Your local time zone, for example, 'Asia/Dhaka' for Bangladesh
local_tz = pytz.timezone('Asia/Dhaka')

# Look for the group by name
for dialog in dialogs:
    if dialog.name == 'PriceAction Forex VIP':
        target_group = dialog
        break
else:
    target_group = None
    print("Group 'PriceAction Forex VIP' not found.")
    client.disconnect()
    exit()

# Assuming target_group is found and not None
if target_group:
    for message in client.iter_messages(target_group, offset_date=one_month_ago, reverse=True):
        if message.text:  # Ensure message has text content
            message_text_upper = message.text.upper()
            action_match = re.search(r"(BUY|SELL)\s*([\d.]+)", message.text, re.IGNORECASE)
            sl_match = re.search(r"SL\s*([\d.]+)", message.text, re.IGNORECASE)
            tp_match = re.search(r"TP\s*([\d.]+)", message.text, re.IGNORECASE)

            if action_match and sl_match and tp_match:
                # Convert message date to local time zone
                local_date = message.date.astimezone(local_tz)

                action = action_match.group(0)
                sl = sl_match.group(1)
                tp = tp_match.group(1)

                data = {
                    "group": target_group.name,
                    "sender": message.sender_id,
                    "text": message.text,
                    "date": local_date.strftime('%Y-%m-%d %H:%M:%S'),  # Format datetime in a string
                    "Action": action,
                    "SL": sl,
                    "TP": tp
                }
                temp_df = pd.DataFrame(data, index=[0])
                df = pd.concat([df, temp_df], ignore_index=True)

if 'date' in df.columns:
    # No need to adjust 'date' column timezone here, as it's already been converted to local timezone above

    home_dir = os.path.expanduser('~')
    excel_path = os.path.join(home_dir, "Detect_SS_datamonth_{}.xlsx".format(datetime.date.today()))

    df.to_excel(excel_path, index=False)
    print(f"Data exported to Excel at {excel_path}.")
else:
    print("No relevant messages were found or added to the DataFrame.")
    client.disconnect()
