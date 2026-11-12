# Sentri

Retail computer-vision project aimed at entrance, aisle, and checkout camera feeds, including optional RTSP input.

**Current status:** this repository is a scaffold. The tracked files are:

- `README.md` (this file)
- `.env.example` (one empty variable, `RTSP_URL`)
- `.gitignore`
- `demo-videos/.gitkeep`

There is no application code, package manifest, Dockerfile, CI workflow, or committed demo video. `demo-videos/` exists so the directory is in git. It does not contain `entrance.mp4`, `aisle.mp4`, or `checkout.mp4`. `.gitignore` ignores `*.mp4`, `*.mov`, and `*.avi` under that folder, so clips added locally are not committed unless that rule changes.

Do not describe this repository as a running detection platform. On `main`, before this README, the only commit is the initial scaffold (2026-04-17). No frontend, API, detector, WebSocket server, or alert path is in the tree.

## Intended scope

Not implemented. The README this file replaces described:

- Demo clips in `demo-videos/`: `entrance.mp4`, `aisle.mp4`, `checkout.mp4`
- An optional live stream via `RTSP_URL` in `.env`

That README listed Node.js, Python, and Docker Desktop as prerequisites. Nothing in the tree invokes them. Next.js, FastAPI, OpenCV, WebSockets, and PostgreSQL are not named by any file here, and there is no code that uses them. Anything said about those tools outside this repository is not verifiable from this tree.

## Demo

There is no runnable app. The tree has no deployment workflow, Dockerfile, or Pages config.

The clip paths from the previous README are not in git:

```
demo-videos/entrance.mp4
demo-videos/aisle.mp4
demo-videos/checkout.mp4
```

`.env.example` is only:

```
RTSP_URL=
```

The previous README showed this shape for a live camera:

```
RTSP_URL=rtsp://user:pass@host:554/stream
```

No file in the repository reads `RTSP_URL`.

## Features

Nothing in this repository is a shipped feature. There is no detection, tracking, alerting, dashboard, API, or video ingest.

## Stack

**Named in the README this file replaces, and unused by the tree:**

- Node.js 20.9+
- Python 3.11 or 3.12
- Git
- Docker Desktop

There is no `package.json`, `requirements.txt`, `pyproject.toml`, or `Dockerfile`.

## Architecture

There is no ingest path, model, API, dashboard, or event store in this repository.

## How to run

There is no run command. Cloning the repo and copying the env file does not start a service:

```bash
git clone https://github.com/Harry0052/sentri.git
cd sentri
cp .env.example .env
```

`demo-videos/` can hold local files. `*.mp4`, `*.mov`, and `*.avi` there stay untracked.

## Repository metadata

GitHub settings for this repo are not changed by this file. At the time of writing they are:

- **Description:** unset
- **Website:** unset
- **Topics:** none

A description that matches the tree is: scaffold for a retail computer-vision project on entrance, aisle, and checkout camera feeds (RTSP). No application code yet.

Topics such as `computer-vision`, `opencv`, `python`, and `nextjs` do not match the current files. There is no website to attach.
