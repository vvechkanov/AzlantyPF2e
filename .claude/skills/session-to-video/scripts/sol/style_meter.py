# -*- coding: utf-8 -*-
"""Стилевой измеритель кадра: насколько он «набросок на бумаге», а насколько «картинка».
Три числа по области листа (без белого поля):
  paper  — доля листа, оставшаяся голой бумагой (цвет близок к тону пергамента)
  ink    — доля пикселей с резким перепадом яркости (плотность штриха и деталей)
  colour — средняя насыщенность закрашенной (не бумажной) части
usage: style_meter.py <папка-эталон> <папка-или-список n_*.txt>"""
import sys, glob, os
import numpy as np
from PIL import Image
from scipy import ndimage

def measure(path):
    im = Image.open(path).convert("RGB"); im.thumbnail((640, 640))
    rgb = np.asarray(im).astype(np.float32)
    white = (rgb.min(2) >= 242) & ((rgb.max(2) - rgb.min(2)) <= 10)
    lab, _ = ndimage.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); edge = edge[edge != 0]
    sheet = ~np.isin(lab, edge)
    sheet = ndimage.binary_erosion(sheet, iterations=6)          # без рваной кромки
    if sheet.mean() < 0.2: sheet = np.ones(sheet.shape, bool)
    hsv = np.asarray(im.convert("HSV")).astype(np.float32) / 255
    # тон бумаги = самый частый светлый цвет листа
    lum = rgb.mean(2)
    light = sheet & (lum > np.percentile(lum[sheet], 60))
    tone = np.median(rgb[light], axis=0)
    dist = np.sqrt(((rgb - tone) ** 2).sum(2))
    paper = (dist < 26) & sheet
    g = ndimage.gaussian_filter(lum, 0.8)
    grad = np.hypot(ndimage.sobel(g, 0), ndimage.sobel(g, 1))
    ink = (grad > 60) & sheet
    painted = sheet & ~paper
    colour = hsv[..., 1][painted].mean() if painted.sum() > 50 else 0.0
    return paper.sum() / sheet.sum(), ink.sum() / sheet.sum(), float(colour)

def files(arg):
    if os.path.isdir(arg):
        ns = sorted(glob.glob(os.path.join(arg, "n_*.txt")))
        if ns:
            return [os.path.join(arg, open(n, encoding="utf-8").read().strip()) for n in ns]
        return [p for p in sorted(glob.glob(os.path.join(arg, "shot*.*"))) if p.lower().endswith((".png", ".jpg")) and "upscayl" not in p]
    return [arg]

if __name__ == "__main__":
    ref = [(os.path.basename(p), measure(p)) for p in files(sys.argv[1])]
    R = np.array([m for _, m in ref])
    lo, hi = np.percentile(R, 10, axis=0), np.percentile(R, 90, axis=0)
    print("ЭТАЛОН (%d кадров)  бумага %.2f [%.2f..%.2f]   штрих %.3f [%.3f..%.3f]   цвет %.2f [%.2f..%.2f]" % (
        len(R), np.median(R[:, 0]), lo[0], hi[0], np.median(R[:, 1]), lo[1], hi[1], np.median(R[:, 2]), lo[2], hi[2]))
    rows = []
    for p in files(sys.argv[2]):
        if not os.path.exists(p): continue
        pa, ik, co = measure(p)
        flags = []
        if pa < R[:, 0].min(): flags.append("мало бумаги")
        if ik > R[:, 1].max(): flags.append("слишком плотный штрих")
        if co > R[:, 2].max(): flags.append("слишком цветной")
        # индекс «картинности»: 0 — как самый пустой кадр эталона, 1 — как самый плотный
        z = np.mean([(R[:, 0].max() - pa) / (np.ptp(R[:, 0]) + 1e-6), (ik - R[:, 1].min()) / (np.ptp(R[:, 1]) + 1e-6), (co - R[:, 2].min()) / (np.ptp(R[:, 2]) + 1e-6)])
        rows.append((z, os.path.basename(p), pa, ik, co, ", ".join(flags)))
    for z, n, pa, ik, co, fl in sorted(rows, reverse=True):
        print("%.2f  %-40s бумага %.2f  штрих %.3f  цвет %.2f  %s" % (z, n[:40], pa, ik, co, fl))
    print("\nэталон по индексу:", " ".join("%s=%.2f" % (n[:18], np.mean([(R[:, 0].max() - m[0]) / (np.ptp(R[:, 0]) + 1e-6), (m[1] - R[:, 1].min()) / (np.ptp(R[:, 1]) + 1e-6), (m[2] - R[:, 2].min()) / (np.ptp(R[:, 2]) + 1e-6)])) for n, m in sorted(ref, key=lambda x: -x[1][1])[:6]))
