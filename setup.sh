#!/bin/bash
# Reel maker: one-time setup for a Claude Code cloud environment.
# Paste this whole file into the environment's "Setup script" box.
# It runs once, then Claude keeps a snapshot, so later reels start fast.

# Video tools (usually already there)
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg) || true
fc-list | grep -qi "color emoji" || apt-get install -y -qq fonts-noto-color-emoji || true

# Speech-to-text, Google Drive download, person cut-out, face blur
pip install -q --break-system-packages faster-whisper gdown ai-edge-litert opencv-python-headless \
  || pip install -q faster-whisper gdown ai-edge-litert opencv-python-headless || true

# Browser used to draw titles and overlays (usually already there)
node -e "require('playwright')" 2>/dev/null \
  || (npm install -g playwright && npx playwright install --with-deps chromium) || true

# Download the speech model now so each reel starts faster (needs huggingface.co allowed)
python3 -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')" || true

exit 0
