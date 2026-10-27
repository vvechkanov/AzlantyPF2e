# -*- coding: utf-8 -*-
"""«Туман плывёт» без видеомодели. Два листа: A (как нарисовано) и B (туман закрыл даль, правка Sol).
B вклеивается в A только внутри мягкой зоны; поверх едет облачная маска — где она, там виден B.
Края листа, передний план и защищённые места берутся из A пиксель в пиксель.
usage: fog.py <кадр> <A.png> <B.png> <alpha.png> <зона x0,y0,x1,y1> <порог> [защита x0,y0,x1,y1]   (координаты в долях листа)"""
import sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

shot, pa, pb, palpha, zone, thr = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], [float(x) for x in sys.argv[5].split(",")], float(sys.argv[6])
prot = [float(x) for x in sys.argv[7].split(",")] if len(sys.argv) > 7 else None
O = os.path.join(r"C:\Azlanti\Video\Session0\02__Жульничество\video", "shot" + shot); os.makedirs(O, exist_ok=True)
T, FPS = 12, 24

a = Image.open(pa).convert("RGB"); b = Image.open(pb).convert("RGB").resize(a.size, Image.LANCZOS)
w, h = a.size
m0 = Image.new("L", (w, h), 0); ImageDraw.Draw(m0).ellipse((int(w * zone[0]), int(h * zone[1]), int(w * zone[2]), int(h * zone[3])), fill=255)
m0 = m0.filter(ImageFilter.GaussianBlur(70))
if prot:
    p0 = Image.new("L", (w, h), 0); ImageDraw.Draw(p0).ellipse((int(w * prot[0]), int(h * prot[1]), int(w * prot[2]), int(h * prot[3])), fill=255)
    p0 = p0.filter(ImageFilter.GaussianBlur(25))
    m0 = Image.fromarray((np.asarray(m0).astype(np.float32) * (1 - np.asarray(p0).astype(np.float32) / 255)).astype(np.uint8))
Z = np.asarray(m0).astype(np.float32) / 255
An = np.asarray(a).astype(np.float32); Bn = np.asarray(b).astype(np.float32)
Bn = An * (1 - Z[..., None]) + Bn * Z[..., None]                     # B = A везде, кроме зоны тумана

alpha = Image.open(palpha).split()[-1].resize(a.size, Image.LANCZOS)
def onblack(arr):
    im = Image.fromarray(arr.astype(np.uint8)); sc = min(1920 / w, 1080 / h); sz = (round(w * sc), round(h * sc))
    bg = Image.new("RGB", (1920, 1080), (0, 0, 0)); bg.paste(im.resize(sz, Image.LANCZOS), ((1920 - sz[0]) // 2, (1080 - sz[1]) // 2), alpha.resize(sz, Image.LANCZOS)); return bg
A1 = onblack(An); B1 = onblack(Bn)
A1.save(os.path.join(O, "shot%s_A_открыто.png" % shot)); B1.save(os.path.join(O, "shot%s_B_туман_закрыл.png" % shot))
A = np.asarray(A1).astype(np.float32); B = np.asarray(B1).astype(np.float32); H, W = A.shape[:2]

rng = np.random.default_rng(7); nh, nw = H // 8, (2 * W) // 8
n = ndimage.gaussian_filter(rng.random((nh, nw)).astype(np.float32), (9, 22), mode=("reflect", "wrap")); n = (n - n.min()) / (n.max() - n.min())
out = os.path.join(O, "shot%s_туман_плывёт_12с.mp4" % shot)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
                      "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
N = T * FPS; cover = []
for i in range(N):
    tile = np.roll(n, -int(round(nw * i / N)), axis=1)[:, :W // 8 + 1]
    big = np.asarray(Image.fromarray((tile * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255
    m = np.clip((big - thr) / 0.24, 0, 1); m = m * m * (3 - 2 * m)
    cover.append(float(m.mean()))
    p.stdin.write((A * (1 - m[..., None]) + B * m[..., None]).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
# контрольные кадры
t = Image.new("RGB", (1920 * 2 + 20, 1080), "white"); t.paste(A1, (0, 0)); t.paste(B1, (1940, 0)); t.resize((1960, 548)).save("fog%s_AB.jpg" % shot, quality=85)
print("кадр %s: туман закрывает в среднем %.0f%% площади (от %.0f до %.0f), файл %s" % (shot, 100 * np.mean(cover), 100 * min(cover), 100 * max(cover), os.path.basename(out)))
