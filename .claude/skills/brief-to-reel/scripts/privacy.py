#!/usr/bin/env python3
"""Blur faces for privacy (for example kids in the background).

plan["blur_faces"]:
  "all"            blur every face
  "others"         keep the biggest face (usually the person talking), blur everyone else
  {"faces": [2]}   blur only the people picked from the face sheet (Face 1, Face 2...)

To let the person pick, make the sheet first:
  privacy.py VIDEO_OR_CLIP OUT_DIR       -> OUT_DIR/faces.jpg + faces.json (one entry per person)
then set "blur_faces": {"faces": [...], "sheet": "OUT_DIR/faces.json"}.

Uses OpenCV's YuNet face detector and SFace face matcher (models/, downloaded from
Hugging Face on first use).
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "..", "models")
URLS = {
    "face_yunet.onnx": "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx",
    "face_sface.onnx": "https://huggingface.co/opencv/face_recognition_sface/resolve/main/face_recognition_sface_2021dec.onnx",
}
MATCH = 0.36  # SFace cosine similarity: same person above this


def model(name):
    p = os.path.join(MODELS, name)
    if not os.path.exists(p):
        os.makedirs(MODELS, exist_ok=True)
        subprocess.run(["curl", "-sSfL", "-m", "120", "-o", p, URLS[name]], check=True)
    return p


def frames(video, W, H, fps=None):
    vf = ["-vf", f"fps={fps}"] if fps else []
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", video, *vf, "-f", "rawvideo",
                            "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    size = W * H * 3
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
    dec.wait()


def probe_size(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", video], capture_output=True, text=True)
    w, h = (int(x) for x in r.stdout.strip().split(",")[:2])
    return w, h


class Faces:
    def __init__(self, W, H):
        import cv2
        self.cv2 = cv2
        self.dw, self.dh = W // 2, H // 2  # detect at half size: plenty for faces, twice as fast
        self.det = cv2.FaceDetectorYN.create(model("face_yunet.onnx"), "", (self.dw, self.dh), 0.6)
        self.rec = None

    def detect(self, frame):
        small = self.cv2.resize(frame, (self.dw, self.dh))
        _, faces = self.det.detect(small)
        return small, ([] if faces is None else list(faces))

    def embed(self, small, face):
        if self.rec is None:
            self.rec = self.cv2.FaceRecognizerSF.create(model("face_sface.onnx"), "")
        f = self.rec.feature(self.rec.alignCrop(small, face))[0]
        return f / (np.linalg.norm(f) + 1e-9)


def face_sheet(video, out_dir):
    """Find the different people in a video; save a numbered sheet to pick from."""
    import cv2
    W, H = probe_size(video)
    fd = Faces(W, H)
    people = []  # {"emb": mean embedding, "count", "thumb"}
    for frame in frames(video, W, H, fps=2):
        small, faces = fd.detect(frame)
        for f in faces:
            e = fd.embed(small, f)
            best = max(people, key=lambda p: float(p["emb"] @ e), default=None)
            if best is not None and float(best["emb"] @ e) > MATCH:
                best["emb"] = best["emb"] * best["count"] + e
                best["emb"] /= np.linalg.norm(best["emb"])
                best["count"] += 1
            else:
                x, y, w, h = (int(v) for v in f[:4])
                pad = int(0.3 * max(w, h))
                crop = small[max(0, y - pad):y + h + pad, max(0, x - pad):x + w + pad]
                people.append({"emb": e, "count": 1, "thumb": cv2.resize(crop, (220, 220))})
    people = [p for p in people if p["count"] >= 2] or people  # ignore one-off false detections
    os.makedirs(out_dir, exist_ok=True)
    tiles = []
    for i, p in enumerate(people, 1):
        t = p["thumb"].copy()
        cv2.rectangle(t, (0, 180), (220, 220), (255, 255, 255), -1)
        cv2.putText(t, f"Face {i}", (50, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (20, 20, 20), 2)
        tiles.append(t)
    if tiles:
        cv2.imwrite(os.path.join(out_dir, "faces.jpg"), np.hstack(tiles))
    json.dump([{"face": i, "embedding": p["emb"].tolist(), "seen": p["count"]} for i, p in enumerate(people, 1)],
              open(os.path.join(out_dir, "faces.json"), "w"))
    return len(people)


def blur_faces(video, out, W, H, fps, mode="all", every=2):
    import cv2
    fd = Faces(W, H)
    targets = None
    if isinstance(mode, dict):
        sheet = json.load(open(mode["sheet"]))
        targets = [np.array(p["embedding"]) for p in sheet if p["face"] in mode.get("faces", [])]
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-i", video, "-map", "0:v", "-map", "1:a?",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "copy", out], stdin=subprocess.PIPE)
    boxes = []
    for n, frame in enumerate(frames(video, W, H)):
        if n % every == 0:
            small, faces = fd.detect(frame)
            if targets is not None:
                faces = [f for f in faces if max(float(t @ fd.embed(small, f)) for t in targets) > MATCH] \
                    if targets else []
            found = [tuple(int(v * 2) for v in f[:4]) for f in faces]
            if mode == "others" and found:
                found.remove(max(found, key=lambda b: b[2] * b[3]))
            boxes = found
        for x, y, w, h in boxes:
            pad = int(0.35 * max(w, h))  # cover hair and chin too
            x0, y0 = max(0, x - pad), max(0, y - pad)
            x1, y1 = min(W, x + w + pad), min(H, y + h + pad)
            if x1 > x0 and y1 > y0:
                roi = frame[y0:y1, x0:x1]
                small_roi = cv2.resize(roi, (max(1, (x1 - x0) // 18), max(1, (y1 - y0) // 18)))
                frame[y0:y1, x0:x1] = cv2.GaussianBlur(
                    cv2.resize(small_roi, (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST), (0, 0), 6)
        enc.stdin.write(frame.tobytes())
    enc.stdin.close()
    enc.wait()
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    print(f"{face_sheet(sys.argv[1], sys.argv[2])} people found; sheet in {sys.argv[2]}/faces.jpg")
