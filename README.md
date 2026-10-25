# Toolnookz website

Static site for toolnookz.com, built from templates plus one small JSON file per app.

## Add or edit an app
Each app is one file in `src/data/apps/` (name, category, tagline, features, privacy facts, `status`, `play_url`).
Copy any file, change the fields, then run:

    pip install -r requirements.txt
    python build.py

The finished site is written to `docs/` (commit it). Set `play_url` once the app is live on Google Play.

## Privacy facts per app (`privacy` block)
The policy text is generated from these fields, so keep them true to the real app:
`data_entered`, `permissions` (notifications, camera, photos, files), `uses_clipboard`, `ads`, `premium`, `device_backup`, `export`.
Review each app's policy against the real app before publishing it.

## Placeholders to confirm
- `src/site.json`: `email` (support@toolnookz.com must exist) and `policy_date`.
- Replace the "Google Play" placeholder button with the official badge once an app is live.
