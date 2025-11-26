# Troubleshooting Guide

A quick reference for the most common issues observed while developing or demoing Z-GPT.

## Backend

### `ModuleNotFoundError: transformers`
- Install missing dependencies via `pip install -r requirements.txt`.
- If running inside Docker, rebuild the backend image: `docker compose build backend`.

### Chat endpoint returns HTTP 500
- Check the structured log entry (includes `request_id`).
- Confirm `CHAT_MODEL` is set and reachable; the default requires internet to download weights.
- Ensure `IMAGE_ENABLED=false` locally if hardware cannot load Stable Diffusion.

### Streaming endpoint disconnects immediately
- SSE requires HTTP/1.1. When testing behind nginx or a cloud proxy, disable response buffering for `text/event-stream`.
- Some corporate networks strip keep-alive connections. Retest on a different network or force the UI to use the sync `/chat/` fallback by setting `forceSync`.

### Database locked / stale data
- During local dev run `rm data/zgpt.db` (or the path from `DB_URL`) to start fresh.
- For tests, the fixtures automatically drop and recreate tables; ensure `DB_URL=sqlite:///./test.db` to isolate from prod data.

## Frontend

### `npm install` fails on legacy peer deps
- The project already pins `--legacy-peer-deps`. Run `npm install --legacy-peer-deps` or upgrade to Node 20+.

### Jest cannot find `scrollIntoView`
- JSDOM does not implement `scrollIntoView`. The component already guards the call, but if you add new refs, mock the method: `Element.prototype.scrollIntoView = jest.fn();`.

### Offline banner stuck
- The banner reflects `navigator.onLine`. Browser devtools can spoof offline state; disable the override or reload the page.

## Deployment

### Docker compose keeps restarting
- Verify `.env` exists and contains valid `CHAT_MODEL` / `DB_URL` entries.
- Use `docker compose logs backend` to see the FastAPI trace (missing GPU drivers, etc.).

### Scaling beyond one replica
- Stick a reverse proxy (nginx, Traefik, ALB) in front of multiple backend pods and enable sticky sessions or store rate-limit counters in Redis.
- Ensure the proxy forwards `Accept: text/event-stream` headers unmodified for SSE endpoints.
