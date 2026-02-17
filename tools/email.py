import email
import imaplib
from email.header import decode_header

import html2text

from common.constants import IMAP_HOST, IMAP_PASSWORD, IMAP_USER
from common.dataclasses import EmailContent


def _decode_header_value(value: str) -> str:
    """Decode a MIME-encoded email header into a plain string."""
    parts = decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def _extract_body(msg: email.message.Message) -> str:
    """Extract the body from an email message.

    Prefers text/plain, falls back to text/html converted to markdown.
    """
    text_body = None
    html_body = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain" and text_body is None:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                text_body = payload.decode(charset, errors="replace")
            elif content_type == "text/html" and html_body is None:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                html_body = payload.decode(charset, errors="replace")
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset() or "utf-8"
        decoded = payload.decode(charset, errors="replace")
        if content_type == "text/plain":
            text_body = decoded
        elif content_type == "text/html":
            html_body = decoded

    if text_body:
        return text_body

    if html_body:
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = True
        converter.body_width = 0  # Don't wrap lines
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
        imap.login(IMAP_USER, IMAP_PASSWORD)
        imap.select("INBOX")

        status, message_ids = imap.search(None, "UNSEEN", f'TO "{to_address}"')
        if status != "OK" or not message_ids[0]:
            return results

        for msg_id in message_ids[0].split():
            status, msg_data = imap.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            results.append(
                EmailContent(
                    subject=_decode_header_value(msg.get("Subject", "")),
                    from_addr=msg.get("From", ""),
                    to_addr=msg.get("To", ""),
                    date=msg.get("Date", ""),
                    body=_extract_body(msg),
                )
            )

            # Mark as seen
            imap.store(msg_id, "+FLAGS", "\\Seen")

    return results
