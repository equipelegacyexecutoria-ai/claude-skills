"""Mede rosto (largura, centro, olhos) num vídeo, a cada N quadros, opcionalmente só numa faixa y."""
import sys, cv2, json
from pathlib import Path
MOD = str(Path.home()/".claude/skills/reels-novela-clailton/models/face_detection_yunet_2023mar.onnx")
vid, passo = sys.argv[1], int(sys.argv[2]); y0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
ate = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
cap = cv2.VideoCapture(vid); i = 0; det = None; out = []
while i <= ate:
    ok, fr = cap.read()
    if not ok: break
    if i % passo == 0:
        sub = fr[y0:]
        h, w = sub.shape[:2]
        if det is None: det = cv2.FaceDetectorYN.create(MOD, "", (w, h), 0.6, 0.3, 5000)
        det.setInputSize((w, h)); _, f = det.detect(sub)
        if f is not None and len(f):
            f = max(f, key=lambda r: r[2]*r[3])
            ex = (f[4]+f[6])/2; ey = (f[5]+f[7])/2 + y0
            out.append(dict(q=i, larg=round(float(f[2])), cx=round(float(f[0]+f[2]/2)), olhos_y=round(float(ey)), olhos_x=round(float(ex))))
    i += 1
print(json.dumps(out))
