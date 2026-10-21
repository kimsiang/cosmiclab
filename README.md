# Cosmic Lab

Landing page for **Cosmic Lab** — a one-day online masterclass where Malaysian Form 4–6 students analyse real muon-detector data with Python. Live at [cosmiclab.my](https://cosmiclab.my).

## Files

| Path | Purpose |
|---|---|
| `index.html` | Single-file landing page: trilingual (EN / BM / 中文), ice-blue theme, Tally registration embed, AI chat widget |
| `api/chat.php` | PHP proxy between the chat widget and the Claude API — grounding prompt, per-IP rate limit, trilingual fallbacks, mbstring polyfill |
| `claude_config.sample.php` | Template for the API key file |
| `setup_guide.html` | Six-page install guide for the AI assistant on cPanel |

## Deploying the AI assistant (Shinjiru / cPanel)

1. Upload `index.html` to `public_html`.
2. Upload `api/chat.php` to `public_html/api/`.
3. Rename `claude_config.sample.php` to `claude_config.php`, add your key, and upload it **one level above** `public_html` so it is never web-accessible.

`claude_config.php` is listed in `.gitignore` — never commit a real API key to this repo.

## Notes

- The chat widget calls `api/chat.php` on the same origin, so it needs PHP hosting. On a static host (e.g. Netlify) the page works but the assistant shows its fallback message.
- The Tally form (`vGLP7g`) only loads on a live domain; it appears blank when opened as a local file.
