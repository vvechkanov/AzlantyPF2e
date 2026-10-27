# -*- coding: utf-8 -*-
"""Убирает чисто-белое поле вокруг листа пергамента: белое, связанное с краями кадра, -> прозрачное (и чёрное под альфой).
usage: cut_white.py src.png dst.png   -> печатает долю вырезанного"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

def cut(src, dst, thr=242, spread=10):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    # «белый-белый»: все каналы высокие и почти равны (пергамент тёплый, у него B заметно ниже R)
    white = (a.min(axis=2) >= thr) & ((a.max(axis=2) - a.min(axis=2)) <= spread)
    lab, n = ndimage.label(white)
    edge = np.unique(np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]]))
    edge = edge[edge != 0]
    bg = np.isin(lab, edge)
    # съесть светлую кайму на границе листа и чуть смягчить край
    bg = ndimage.binary_dilation(bg, iterations=2)
    alpha = Image.fromarray(((~bg) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    al = np.asarray(alpha).astype(np.float32) / 255.0
    rgb = (np.asarray(im).astype(np.float32) * al[..., None]).astype(np.uint8)   # под прозрачным — чёрное
    out = Image.fromarray(np.dstack([rgb, np.asarray(alpha)]), "RGBA")
    out.save(dst, optimize=True)
    return float(bg.mean())

if __name__ == "__main__":
    print(round(cut(sys.argv[1], sys.argv[2]) * 100, 1))
