import imaplib
import email
from email.header import decode_header
import os
import re
import json
from bs4 import BeautifulSoup

def load_config(config_path="config.json"):
    """ Load email configuration from a JSON file. """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_directory, config_path)
    
    try:
        with open(config_file_path, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: {config_file_path} not found!")
        return None

def connect_to_email(config):
    """ Connect to the IMAP email server using the provided credentials. """
    mail = imaplib.IMAP4_SSL(config['email']['imap_server'])
    mail.login(config['email']['email_address'], config['email']['password'])
    return mail

def decode_email_header(header_value):
    """ Decode email header (e.g., Subject, From). """
    value, encoding = decode_header(header_value)[0]
    if isinstance(value, bytes):
        return value.decode(encoding if encoding else "utf-8")
    return value

def extract_body_from_multipart(msg):
    """ Extract body from a multipart email. """
    body = ""
    html_content = None
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type == "text/html" and html_content is None:
            html_content = part.get_payload(decode=True).decode("utf-8", errors="ignore")
        elif content_type == "text/plain":
            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
    
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        body = soup.get_text(separator="\n", strip=True)
    return body

def extract_body_from_non_multipart(msg):
    """ Extract body from a non-multipart email. """
    payload = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    if msg.get_content_type() == "text/html":
        soup = BeautifulSoup(payload, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    return payload

def clean_email_body(body):
    """ Clean the extracted email body (e.g., remove excessive whitespace). """
    return re.sub(r'\s+', ' ', body).strip()

def fetch_unread_emails(mail):
    """ Fetch unread emails from the inbox. """
    mail.select("inbox")
    status, messages = mail.search(None, 'UNSEEN')
    
    if status != "OK":
        print("No unread emails found!")
        return []

    email_ids = messages[0].split()
    emails = []

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")

        if status != "OK":
            print(f"Failed to fetch email ID {email_id}")
            continue
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # Decode headers
                subject = decode_email_header(msg["Subject"])
                sender = decode_email_header(msg.get("From"))

                # Initialize email body extraction
                body = ""

                if msg.is_multipart():
                    body = extract_body_from_multipart(msg)
                else:
                    body = extract_body_from_non_multipart(msg)
                
                # Clean up the extracted text
                body = clean_email_body(body)

                # Prepare the email data
                email_data = {
                    "subject": subject,
                    "sender": sender,
                    "body": body,
                    "date": msg.get("Date", "")
                }

                emails.append(email_data)

    return emails