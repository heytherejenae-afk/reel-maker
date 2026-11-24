"""Where is the speaker looking at the camera? facing.py talk.mp4 model.onnx -> prints t yaw (0 = straight on)."""
import cv2, sys, json
cap = cv2.VideoCapture(sys.argv[1]); det = None; out = []; i = 0
fps = cap.get(cv2.CAP_PROP_FPS)
while True:
    ok, f = cap.read()
    if not ok: break
    if i % 3 == 0:
        f = cv2.resize(f, (f.shape[1] // 3, f.shape[0] // 3))
        if det is None: det = cv2.FaceDetectorYN.create(sys.argv[2], '', (f.shape[1], f.shape[0]), 0.6)
        det.setInputSize((f.shape[1], f.shape[0])); _, faces = det.detect(f)
        yaw = None
        if faces is not None and len(faces):
            a = max(faces, key=lambda x: x[2] * x[3])
            rx, ry, lx, ly, nx, ny = a[4:10]
            ed = ((lx - rx) ** 2 + (ly - ry) ** 2) ** .5
            yaw = round(float((nx - (rx + lx) / 2) / max(ed, 1)), 3)
        out.append([round(i / fps, 2), yaw])
    i += 1
json.dump(out, open(sys.argv[3], 'w'))
