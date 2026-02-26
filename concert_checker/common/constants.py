import os

from dotenv import load_dotenv

load_dotenv()

LLM_MODEL_NAME = "openai:gpt-5-mini"
LLM_MODEL_NAME = "openrouter:nvidia/nemotron-3-nano-30b-a3b"

# IMAP configuration (for email source)
IMAP_HOST = os.environ.get("IMAP_HOST", "imap.fastmail.com")
IMAP_USER = os.environ.get("IMAP_USER", "")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD", "")
IMAP_TO_ADDRESSES = [
    a.strip() for a in os.environ.get("IMAP_TO_ADDRESSES", "").split(",") if a.strip()
]
IMAP_MAILBOXES = [
    m.strip() for m in os.environ.get("IMAP_MAILBOXES", "INBOX").split(",") if m.strip()
]
