from simplegmail import Gmail
from simplegmail.query import construct_query
import os

# Ensure the credentials file exists
CREDENTIALS_FILE = "client_secret.json"

if not os.path.exists(CREDENTIALS_FILE):
    print(
        f"Error: '{CREDENTIALS_FILE}' file is missing.\n"
        "Download it from Google Cloud Console after enabling the Gmail API.\n"
        "Refer to https://developers.google.com/gmail/api/quickstart/python for setup instructions."
    )
    exit()

# Initialize Gmail API
try:
    gmail = Gmail()  # Looks for 'client_secret.json' by default
except Exception as e:
    print(f"Error initializing Gmail API: {e}")
    exit()

# Construct query parameters
query_params = {
    "newer_than": (6, "year"),  # Emails newer than 6 years
    "older_than": (4, "year")   # Emails older than 4 years
}

# Fetch sent messages based on the constructed query
try:
    messages = gmail.get_sent_messages(query=construct_query(query_params))

    if not messages:
        print("No messages found for the specified criteria.")
    else:
        print(f"Found {len(messages)} messages.")
        for message in messages:
            print(f"To: {message.recipient}")
            print(f"From: {message.sender}")
            print(f"Subject: {message.subject}")
            print(f"Date: {message.date}")
            print(f"Preview: {message.snippet}")
            print("-" * 40)

            # Save email body to a file
            if message.plain:
                if len(message.plain) < 1000:
                    with open("email_samples.txt", "a", encoding="utf-8") as f:
                        f.write(f"Subject: {message.subject}\n")
                        f.write(f"Date: {message.date}\n")
                        f.write(f"Body:\n{message.plain}\n")
                        f.write("-" * 40 + "\n")
except Exception as e:
    print(f"An error occurred while fetching emails: {e}")
