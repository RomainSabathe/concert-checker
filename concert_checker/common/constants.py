import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

LLM_MODEL_NAME = "openai:gpt-5-mini"

# IMAP configuration (for email source)
IMAP_HOST = os.environ.get("IMAP_HOST", "imap.fastmail.com")
IMAP_USER = os.environ.get("IMAP_USER", "")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD", "")
IMAP_TO_ADDRESSES = [
    a.strip()
    for a in os.environ.get("IMAP_TO_ADDRESSES", "").split(",")
    if a.strip()
]
IMAP_MAILBOXES = [
    m.strip()
    for m in os.environ.get("IMAP_MAILBOXES", "INBOX").split(",")
    if m.strip()
]
