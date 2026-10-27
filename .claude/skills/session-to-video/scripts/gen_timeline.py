# -*- coding: utf-8 -*-
"""Таймлайн ролика 2 для импорта в DaVinci Resolve (File > Import > Timeline).
Кадры ложатся на V1 длиной ровно по озвучке, девять файлов голоса — подряд на A1.
Длину кадра можно переопределить в _длины.txt (строка «кадр секунды»), потом перезапустить скрипт.
Пишет: Жульничество_vN.xml (FCP7 XML) и Жульничество_маркеры.edl (запасной путь: только маркеры на границах кадров)."""
import json, io, os, re, glob, subprocess, sys
from urllib.parse import quote
from xml.sax.saxutils import escape

P = r"C:\Azlanti\Video\Session0\02__Жульничество"; C1 = r"C:\Azlanti\Video\Session0\01__Хартвик"
A = os.path.join(P, "audio"); OUT = os.path.join(P, "timeline"); FPS = 24
LEAD = {"0a": 1.5, "0b": 1.5}          # интро до начала голоса
TAIL = 2.0                              # хвост после последнего слова
# паузы после каждого файла голоса, с: 3|4 тот же разговор; 7|8, 19|20, 25|26 смена сцены; 26|27 титр «Запись третья»; дальше смены сцен
GAPS = [0.5, 1.0, 1.0, 1.0, 1.5, 1.0, 1.0, 1.0]
H = 6                                   # половина перекрёстного наплыва, кадров (наплыв = 12 кадров)
NO_DISSOLVE_INTO = {"1", "13", "52"}    # в эти кадры — встык, как в раскадровке

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", p],
                                capture_output=True, text=True).stdout.strip())
sec = lambda t: int(t.split(":")[0]) * 60 + float(t.split(":")[1])
order = ["0c"] + [str(i) for i in range(1, 53)]
d = json.load(io.open(os.path.join(A, "_дубли.json"), encoding="utf-8"))
voices = sorted(glob.glob(os.path.join(A, "голос_*.mp3")))
vdur = [dur(v) for v in voices]
lead = sum(LEAD.values())
vstart = [lead + sum(vdur[:k]) + sum(GAPS[:k]) for k in range(len(voices))]            # начало каждого файла голоса на таймлайне, с

# начало каждого кадра на таймлайне
start = {"0a": 0.0, "0b": LEAD["0a"]}
for fid in order:
    m = re.match(r"голос (\d+) · ([\d:.]+)–", d[fid][0][0]); k = int(m.group(1)) - 1
    start[fid] = vstart[k] + sec(m.group(2))
seq = ["0a", "0b"] + order
end_total = vstart[-1] + vdur[-1] + TAIL
bounds = [start[f] for f in seq] + [end_total]
# ручные правки длин: сдвигают всё, что правее (голос при этом остаётся на месте — правьте осознанно)
ov = os.path.join(OUT, "_длины.txt"); shift = 0.0
if os.path.exists(ov):
    over = dict(l.split()[:2] for l in io.open(ov, encoding="utf-8") if l.strip() and not l.startswith("#"))
    nb = [bounds[0]]
    for i, f in enumerate(seq):
        L = float(over[f]) if f in over else bounds[i + 1] - bounds[i]; nb.append(nb[-1] + L)
    bounds = nb
fr = [round(b * FPS) for b in bounds]

def pic(fid):
    if fid in ("0a", "0b", "0c"):
        loc = glob.glob(os.path.join(P, "shot0%s_*.png" % fid))            # вырезанная копия без белого поля
        return loc[0] if loc else glob.glob(os.path.join(C1, "shot0%s_*" % fid))[0]
    n = int(fid)
    v = glob.glob(os.path.join(P, "video", "shot%02d" % n, "*туман_плывёт_24с.mp4"))
    if v: return v[0]
    if n == 43: return os.path.join(C1, "video", "shot03_river_CLIP.mp4")
    if n == 39: return os.path.join(P, "shot39_varen.png") if os.path.exists(os.path.join(P, "shot39_varen.png")) else os.path.join(C1, "shot05_varen.jpg")
    return glob.glob(os.path.join(P, "shot%02d_*.png" % n))[0]
url = lambda p: "file://localhost/" + quote(p.replace("\\", "/"), safe="/:")
rate = "<rate><timebase>%d</timebase><ntsc>FALSE</ntsc></rate>" % FPS
X = ['<?xml version="1.0" encoding="UTF-8"?>', '<!DOCTYPE xmeml>', '<xmeml version="5">', '<sequence id="seq1">',
     '<name>Жульничество</name>', '<duration>%d</duration>' % fr[-1], rate,
     '<timecode>%s<string>01:00:00:00</string><frame>%d</frame><displayformat>NDF</displayformat></timecode>' % (rate, 3600 * FPS),
     '<media><video><format><samplecharacteristics>%s<width>1920</width><height>1080</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format><track>' % rate]
rows = [(f, fr[i] / FPS, (fr[i + 1] - fr[i]) / FPS, os.path.basename(pic(f))) for i, f in enumerate(seq)]
STILL_IN = 240
def vtrack(h):
    """клипы V1; h > 0 — с перекрёстными наплывами по 2h кадров на склейках"""
    n = len(seq); info = []
    for i, f in enumerate(seq):
        p = pic(f); isvid = p.lower().endswith(".mp4")
        info.append((p, isvid, round(dur(p) * FPS) if isvid else 24 * 3600, fr[i + 1] - fr[i]))
    cut = [h > 0 and seq[i + 1] not in NO_DISSOLVE_INTO for i in range(n - 1)]      # наплыв на склейке i|i+1
    for i, (p, isvid, src, ln) in enumerate(info):                                  # у видео может не хватить запаса
        if isvid and src < ln + 2 * h:
            if i < n - 1: cut[i] = False
            if src < ln + h and i > 0: cut[i - 1] = False
    out = []
    for i, (p, isvid, src, ln) in enumerate(info):
        head = i > 0 and cut[i - 1]; tail = i < n - 1 and cut[i]
        base = STILL_IN if not isvid else (h if head else 0)
        ln2 = min(ln, src) if isvid else ln
        cin = base - (h if head else 0); cout = base + ln2 + (h if tail else 0)
        out.append('<clipitem id="v%d"><name>%s</name><duration>%d</duration>%s<start>%d</start><end>%d</end><in>%d</in><out>%d</out>'
                   '<file id="vf%d"><name>%s</name><pathurl>%s</pathurl>%s<duration>%d</duration><media><video><samplecharacteristics><width>1920</width><height>1080</height></samplecharacteristics></video></media></file>'
                   '%s</clipitem>' % (i, escape("кадр %s · %s" % (seq[i], os.path.basename(p))), src, rate, -1 if head else fr[i], -1 if tail else fr[i] + ln2, cin, cout,
                                      i, escape(os.path.basename(p)), url(p), rate, src, "" if isvid else "<stillframe>TRUE</stillframe>"))
        if tail:
            c = fr[i + 1]
            out.append('<transitionitem><start>%d</start><end>%d</end><alignment>center</alignment>%s<effect><name>Cross Dissolve</name><effectid>Cross Dissolve</effectid>'
                       '<effectcategory>Dissolve</effectcategory><effecttype>transition</effecttype><mediatype>video</mediatype></effect></transitionitem>' % (c - h, c + h, rate))
    return out, sum(cut)
X.append("@@VIDEO@@")
X.append('</track></video><audio><format><samplecharacteristics><depth>16</depth><samplerate>44100</samplerate></samplecharacteristics></format><track>')
for k, v in enumerate(voices):
    a = round(vstart[k] * FPS); n = round(vdur[k] * FPS)
    X.append('<clipitem id="a%d"><name>%s</name><duration>%d</duration>%s<start>%d</start><end>%d</end><in>0</in><out>%d</out>'
             '<file id="af%d"><name>%s</name><pathurl>%s</pathurl>%s<duration>%d</duration><media><audio><samplecharacteristics><depth>16</depth><samplerate>44100</samplerate></samplecharacteristics><channelcount>1</channelcount></audio></media></file>'
             '<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>'
             % (k, escape(os.path.basename(v)), n, rate, a, a + n, n, k, escape(os.path.basename(v)), url(v), rate, n))
bed = os.path.join(A, "_music", "подложка_v1.wav")
if os.path.exists(bed):                                                  # музыка одним файлом на A2
    n = round(dur(bed) * FPS)
    X.append('</track><track><clipitem id="m0"><name>%s</name><duration>%d</duration>%s<start>0</start><end>%d</end><in>0</in><out>%d</out>'
             '<file id="mf0"><name>%s</name><pathurl>%s</pathurl>%s<duration>%d</duration><media><audio><samplecharacteristics><depth>24</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>2</channelcount></audio></media></file>'
             '<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>'
             % (escape(os.path.basename(bed)), n, rate, n, n, escape(os.path.basename(bed)), url(bed), rate, n))
X.append('</track></audio></media></sequence></xmeml>')
ver = int(sys.argv[1]) if len(sys.argv) > 1 else 1
xml = os.path.join(OUT, "Жульничество_v%d_с_наплывами.xml" % ver)
for name, h in ((xml, H), (os.path.join(OUT, "Жульничество_v%d_встык.xml" % ver), 0)):
    vt, nd = vtrack(h)
    io.open(name, "w", encoding="utf-8", newline="\n").write("\n".join(X).replace("@@VIDEO@@", "\n".join(vt)) + "\n")
    print(os.path.basename(name), "| наплывов:", nd)

# --- запасной путь №2: Lua-скрипт для самого Resolve (в бесплатной 21.1 Lua остался). Ничего не читает с диска, пути вшиты.
def lq(p): return '"' + p.replace("\\", "/") + '"'
uniq = []
for f in seq:
    if pic(f) not in uniq: uniq.append(pic(f))
L = ["-- Жульничество: собрать таймлайн. Запуск в Resolve: Workspace > Console > Lua, вставить весь текст и Enter.",
     "local pm = resolve:GetProjectManager(); local proj = pm:GetCurrentProject(); local mp = proj:GetMediaPool()",
     "local paths = {" + ", ".join(lq(p) for p in uniq + voices + ([bed] if os.path.exists(bed) else [])) + "}",
     "local items = mp:ImportMedia(paths)",
     "local byname = {}",
     "for _, it in ipairs(items or {}) do byname[it:GetClipProperty('File Name')] = it end",
     "local tl = mp:CreateEmptyTimeline('Жульничество')",
     "proj:SetCurrentTimeline(tl)",
     "local T0 = tl:GetStartFrame()",
     "local function put(name, rec, len, kind, track)",
     "  local it = byname[name]; if not it then print('нет в пуле: ' .. name); return end",
     "  mp:AppendToTimeline({{mediaPoolItem = it, startFrame = 0, endFrame = len - 1, recordFrame = T0 + rec, trackIndex = track, mediaType = kind}})",
     "end"]
for i, f in enumerate(seq):
    L.append("put(%s, %d, %d, 1, 1)   -- кадр %s" % (lq(os.path.basename(pic(f))), fr[i], fr[i + 1] - fr[i], f))
for k, v in enumerate(voices):
    L.append("put(%s, %d, %d, 2, 1)" % (lq(os.path.basename(v)), round(vstart[k] * FPS), round(vdur[k] * FPS)))
if os.path.exists(bed):
    L.append("put(%s, 0, %d, 2, 2)" % (lq(os.path.basename(bed)), round(dur(bed) * FPS)))
for i, f in enumerate(seq):
    L.append("tl:AddMarker(%d, 'Blue', 'Кадр %s', '', 1)" % (fr[i], f))
L.append("print('готово: кадров %d, голос %d файлов')" % (len(seq), len(voices)))
io.open(os.path.join(OUT, "Жульничество_собрать.lua"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")

def tc(f): f += 3600 * FPS; return "%02d:%02d:%02d:%02d" % (f // (3600 * FPS), f // (60 * FPS) % 60, f // FPS % 60, f % FPS)
E = ["TITLE: Жульничество", "FCM: NON-DROP FRAME", ""]
for i, f in enumerate(seq):
    E += ["%03d  001      V     C        %s %s %s %s  " % (i + 1, tc(fr[i]), tc(fr[i] + 1), tc(fr[i]), tc(fr[i] + 1)),
          " |C:ResolveColorBlue |M:Кадр %s |D:1" % f, ""]
io.open(os.path.join(OUT, "Жульничество_маркеры.edl"), "w", encoding="utf-8", newline="\r\n").write("\n".join(E))
T = ["кадр  начало   длина   файл"] + ["%-4s  %d:%05.2f  %5.2f   %s" % (f, int(s // 60), s % 60, L, n) for f, s, L, n in rows]
io.open(os.path.join(OUT, "Жульничество_длины.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(T) + "\n")
print(os.path.basename(xml), "| кадров %d | длина %d:%04.1f | голос с %.1f с" % (len(seq), int(fr[-1] / FPS // 60), fr[-1] / FPS % 60, lead))
print("самые короткие:", sorted((round(L, 1), f) for f, s, L, n in rows)[:4], "| самые длинные:", sorted((round(L, 1), f) for f, s, L, n in rows)[-4:])
miss = [n for f, s, L, n in rows if not os.path.exists(pic(f))]; print("нет файлов:", miss)
