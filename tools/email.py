import imaplib
from email import message_from_bytes
from email.header import decode_header
from email.message import Message
from typing import cast

import html2text

from common.constants import IMAP_HOST, IMAP_PASSWORD, IMAP_USER
from common.dataclasses import EmailContent


def _decode_header_value(value: str) -> str:
    """Decode a MIME-encoded email header into a plain string."""
    parts = decode_header(value)
    decoded: list[str] = []
    for raw_part, charset in parts:
        part = cast(str | bytes, raw_part)
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def _extract_body(msg: Message) -> str:
    """Extract the body from an email message.

    Prefers text/plain, falls back to text/html converted to markdown.
    """
    text_body: str | None = None
    html_body: str | None = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain" and text_body is None:
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    charset = part.get_content_charset() or "utf-8"
                    text_body = payload.decode(charset, errors="replace")
            elif content_type == "text/html" and html_body is None:
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    charset = part.get_content_charset() or "utf-8"
                    html_body = payload.decode(charset, errors="replace")
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            charset = msg.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if content_type == "text/plain":
                text_body = text
            elif content_type == "text/html":
                html_body = text

    if text_body:
        return text_body

    if html_body:
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = True
        converter.body_width = 0
        return converter.handle(html_body)

    return ""


def fetch_unread_emails(to_address: str) -> list[EmailContent]:
    """Fetch unread emails addressed to `to_address` from the configured IMAP server.

    Connects via IMAP SSL, searches for UNSEEN messages matching the TO address,
    parses them, and marks them as seen.

    Returns a list of EmailContent with the extracted body text.
    """
    results: list[EmailContent] = []

    with imaplib.IMAP4_SSL(IMAP_HOST) as imap:
        _ = imap.login(IMAP_USER, IMAP_PASSWORD)
        _ = imap.select("INBOX")

        status, message_ids = imap.search(None, "UNSEEN", f'TO "{to_address}"')
        ids_bytes = cast(bytes, message_ids[0])
        if status != "OK" or not ids_bytes:
            return results

        for msg_id_bytes in ids_bytes.split():
            msg_id = msg_id_bytes.decode()
            status, msg_data = imap.fetch(msg_id, "(RFC822)")
            if status != "OK" or not msg_data:
                continue

            first = msg_data[0]
            if not isinstance(first, tuple):
                continue

            raw_bytes: bytes = first[1]
            msg = message_from_bytes(raw_bytes)

            results.append(
                EmailContent(
                    subject=_decode_header_value(msg.get("Subject", "")),
                    from_addr=msg.get("From", ""),
                    to_addr=msg.get("To", ""),
                    date=msg.get("Date", ""),
                    body=_extract_body(msg),
                )
            )

            _ = imap.store(msg_id, "+FLAGS", "\\Seen")

    return results
