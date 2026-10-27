# -*- coding: utf-8 -*-
"""Принять дубль озвучки, не разрезая. Whisper расшифровывает его со временем каждого слова, скрипт сам находит,
какие кадры раскадровки в нём прочитаны, ставит тайм-коды по кадрам и сверяет текст.
Запуск питоном, где есть whisper:  C:\\AI-assistant\\navia-align\\venv\\Scripts\\python.exe add_take.py <номер> <файл.mp3>"""
import sys, os, re, io, json, shutil, difflib, subprocess
import whisper, torch

A = r"C:\Azlanti\Video\Session0\02__Жульничество\audio"
T = os.path.join(A, "_дубли_2026-10-11"); os.makedirs(T, exist_ok=True)
MD = r"C:\DND\sync\Sync\Obsidian\PF2e\Кампейны\Азланти\Sessions\Session0\Видео\02__Жульничество__раскадровка.md"
num, src = int(sys.argv[1]), sys.argv[2]

order = ["0c"] + [str(i) for i in range(1, 53)]
md = io.open(MD, encoding="utf-8").read()
PAT = r"### Кадр %s ·.*?\*\*\[ТЕКСТ[^\]]*\]\*\*\s*\n(.*?)(?=\n\n---|\n### |\n## |\Z)"
def text(fid):
    m = re.search(PAT % re.escape(fid), md, re.S)
    if not m and fid == "0c":
        m = re.search(r"\*\*\[ТЕКСТ поверх интро\]\*\*\s*\n(.*?)(?=\n\n---|\n### |\n## )", md, re.S)
    return " ".join(m.group(1).split()) if m else ""
norm = lambda s: re.findall(r"[а-яa-z0-9]+", s.lower().replace("ё", "е"))
exp, owner = [], []
for fid in order:
    for w in norm(text(fid)):
        exp.append(w); owner.append(fid)

cache = os.path.join(T, "расшифровка_%02d.json" % num)
if os.path.exists(cache) and "--fresh" not in sys.argv:
    r = json.load(io.open(cache, encoding="utf-8"))
else:
    model = whisper.load_model("medium")
    r = model.transcribe(src, language="ru", word_timestamps=True, fp16=torch.cuda.is_available(), verbose=False,
                         initial_prompt="Тирос, Хартвик, Анканто, Микаэль, Бель, Абсалом, Кьонин, Саренрэй, Тарвен, Варен, Гринфорд, Делюг.")
    json.dump(r, io.open(cache, "w", encoding="utf-8"), ensure_ascii=False)
if "--text" in sys.argv:
    for seg in r["segments"]: print("%6.1f %s" % (seg["start"], seg["text"]))
act = []
for seg in r["segments"]:
    for w in seg.get("words", []):
        for t in norm(w["word"]):
            act.append((t, w["start"], w["end"]))
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", src],
                           capture_output=True, text=True).stdout.strip())

sm = difflib.SequenceMatcher(None, exp, [a[0] for a in act], autojunk=False)
m2a = {}
for b in sm.get_matching_blocks():
    for k in range(b.size): m2a[b.a + k] = b.b + k
hit = {}
for i, fid in enumerate(owner):
    hit.setdefault(fid, [0, 0]); hit[fid][1] += 1
    if i in m2a: hit[fid][0] += 1
cov = [fid for fid in order if hit[fid][1] and hit[fid][0] / hit[fid][1] >= 0.5]
if not cov: sys.exit("не нашёл в записи ни одного кадра раскадровки: " + r["text"][:200])
ids = order[order.index(cov[0]): order.index(cov[-1]) + 1]

starts = []
for fid in ids:                                           # первое слово кадра в записи
    idx = [i for i, o in enumerate(owner) if o == fid]
    first = next((m2a[i] for i in idx if i in m2a), None)
    k = idx.index(next(i for i in idx if i in m2a)) if first is not None else 0
    a = max(first - k, 0) if first is not None else None       # если первые k слов Whisper услышал иначе — отступить на k слов
    if a is not None and starts and a <= starts[-1]: a = first
    starts.append(a)
edges = [0.0]
for a in starts[1:]:
    if a is None: edges.append(edges[-1]); continue
    edges.append((act[a - 1][2] + act[a][1]) / 2 if a > 0 else 0.0)
edges.append(dur)
tc = lambda x: "%d:%04.1f" % (int(x // 60), x % 60)

dst = os.path.join(T, "дубль%02d_кадры_%s-%s.mp3" % (num, ids[0], ids[-1]))
shutil.copy2(src, dst)
jp = os.path.join(A, "_дубли.json")
data = json.load(io.open(jp, encoding="utf-8")) if os.path.exists(jp) else {}
for v in data.values():
    if v and not v[0][0].startswith(("часть", "дубль 1", "старая")) and "· " in v[0][0] and "10.2026" not in v[0][0]:
        pass
print("ФАЙЛ %s\n  %.1f с, кадры %s–%s, %d слов распознано, %.2f сл/с" % (os.path.basename(dst), dur, ids[0], ids[-1], len(act), len(act) / dur))
for k, fid in enumerate(ids):
    a, b = edges[k], edges[k + 1]
    data[fid] = [["запись 11.10 · дубль %d · %s–%s" % (num, tc(a), tc(b)), round(b - a, 1)]]
    said = [w[0] for w in act if a <= (w[1] + w[2]) / 2 < b]; want = norm(text(fid))
    miss = [w for w in want if w not in said]; extra = [w for w in said if w not in want]
    note = "" if len(miss) + len(extra) <= 1 else "   ≠ в тексте: «%s» / в записи: «%s»" % (" ".join(miss[:6]), " ".join(extra[:6]))
    print("  кадр %-3s %s–%s %5.1f с%s" % (fid, tc(a), tc(b), b - a, note))
with io.open(jp, "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=1)
