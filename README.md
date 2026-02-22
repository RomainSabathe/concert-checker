To do:

- ~DB with parsed concert information~
- ~Store artist url, songkick url, etc.~
- Async, so we can fetch from muliple sources/artists at the same time
- ~Url content hashing to avoid parsing the same content multiple times~
- Image parsing on artist's webpage
- Skill/reflection traces when parsing certain common websites (e.g. songkick,
  bandsintown)
- ~Add source for when an event has been added? (e.g. "added from songkick")~
  - In practice, we have the "source_url" field.
- ~Email source.~

## Email source setup

1. **Cloudflare Email Routing**: set up a catch-all rule on your domain that
   forwards all emails to your Fastmail inbox.
2. **Fastmail app password**: generate one in Fastmail → Settings → Privacy &
   Security → App Passwords (IMAP access).
3. **Environment variables** (see `.env.example`):
   ```bash
   IMAP_USER=you@fastmail.com
   IMAP_PASSWORD=<app-specific-password>
   EMAIL_DOMAIN=yourdomain.com
   ```
4. **Subscribe** to artist newsletters using `artist-slug@yourdomain.com`
   (e.g. `men-i-trust@yourdomain.com` for "Men I Trust").
5. The source picks up unread emails on each run and marks them as read.
