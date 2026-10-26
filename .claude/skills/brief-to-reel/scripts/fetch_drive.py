#!/usr/bin/env python3
"""Download clips from a Google Drive share link (folder or single file).

The link must be shared as "Anyone with the link". Needs network access to
drive.google.com and drive.usercontent.google.com.

Usage: fetch_drive.py LINK OUT_DIR
"""
import os
import sys

import gdown


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    link, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if "/folders/" in link:
        files = gdown.download_folder(url=link, output=out, quiet=False)
    else:
        f = gdown.download(url=link, output=out + os.sep, quiet=False, fuzzy=True)
        files = [f] if f else []
    if not files:
        raise SystemExit("Nothing downloaded. Check the link is shared as 'Anyone with the link'.")
    for f in files:
        print(f)


if __name__ == "__main__":
    main()
