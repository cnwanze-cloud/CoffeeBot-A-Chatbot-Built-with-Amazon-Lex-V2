"""
Command-line client for CoffeeBot (Amazon Lex V2).

Configuration is read from environment variables so no IDs or credentials
are stored in the code:

    AWS_REGION      Region your bot is in (default: us-east-1)
    LEX_BOT_ID      Bot ID from the Lex console (bot overview page)
    LEX_ALIAS_ID    Alias ID (e.g. your dev alias, or TSTALIASID for the draft)
    LEX_LOCALE_ID   Locale (default: en_US)

AWS credentials come from `aws configure` or the standard AWS environment
variables. Never put access keys in this file.

Usage (Windows Command Prompt):
    set AWS_REGION=us-east-1
    set LEX_BOT_ID=your-bot-id
    set LEX_ALIAS_ID=your-alias-id
    python client\\chat.py
"""

import os
import sys
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError

REGION = os.environ.get("AWS_REGION", "us-east-1")
LOCALE_ID = os.environ.get("LEX_LOCALE_ID", "en_US")
BOT_ID = os.environ.get("LEX_BOT_ID")
ALIAS_ID = os.environ.get("LEX_ALIAS_ID")


def check_config():
    """Exit with a helpful message if required settings are missing."""
    missing = [
        name
        for name, value in (("LEX_BOT_ID", BOT_ID), ("LEX_ALIAS_ID", ALIAS_ID))
        if not value
    ]
    if missing:
        print("Missing environment variable(s): " + ", ".join(missing))
        print("Set them first, for example:")
        print("  set LEX_BOT_ID=your-bot-id")
        print("  set LEX_ALIAS_ID=your-alias-id")
        sys.exit(1)


def main():
    check_config()

    client = boto3.client("lexv2-runtime", region_name=REGION)
    session_id = str(uuid.uuid4())  # same ID keeps the conversation going

    print("CoffeeBot ready. Type 'quit' to exit.")
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if text.lower() == "quit":
            break
        if not text:
            continue

        try:
            response = client.recognize_text(
                botId=BOT_ID,
                botAliasId=ALIAS_ID,
                localeId=LOCALE_ID,
                sessionId=session_id,
                text=text,
            )
        except ClientError as err:
            print("Lex error:", err.response["Error"]["Message"])
            continue
        except BotoCoreError as err:
            print("AWS client error:", err)
            continue

        for msg in response.get("messages", []):
            print("Bot:", msg["content"])


if __name__ == "__main__":
    main()
