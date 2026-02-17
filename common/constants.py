import os

LLM_MODEL_NAME = "openai:gpt-5-mini"

# IMAP configuration (for newsletter source)
IMAP_HOST = os.environ.get("IMAP_HOST", "imap.fastmail.com")
IMAP_USER = os.environ.get("IMAP_USER", "")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD", "")
NEWSLETTER_DOMAIN = os.environ.get("NEWSLETTER_DOMAIN", "")
