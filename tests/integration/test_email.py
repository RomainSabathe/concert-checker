import pytest

from concert_checker.common.constants import IMAP_PASSWORD, IMAP_TO_ADDRESSES, IMAP_USER
from concert_checker.tools.email import fetch_unread_emails

_missing_creds = not IMAP_USER or not IMAP_PASSWORD or not IMAP_TO_ADDRESSES


@pytest.mark.integration
@pytest.mark.skipif(_missing_creds, reason="IMAP credentials not set")
def test_fetch_unread_emails():
    """Fetch unread emails for all IMAP_TO_ADDRESSES and validate the results.

    Prerequisites:
      - IMAP_USER, IMAP_PASSWORD, IMAP_TO_ADDRESSES env vars (or .env) are set
      - At least one *unread* email addressed to one of IMAP_TO_ADDRESSES exists

    Side effect: fetched emails are marked as read.
    """
    emails = fetch_unread_emails()

    assert len(emails) > 0, (
        f"No unread emails found for {IMAP_TO_ADDRESSES}. "
        "Send a test email to one of those addresses first."
    )

    for email in emails:
        assert email.subject, "subject should not be empty"
        assert email.from_addr, "from_addr should not be empty"
        assert email.date, "date should not be empty"
        assert email.body, "body should not be empty"
