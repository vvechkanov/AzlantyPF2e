# -*- coding: utf-8 -*-
"""
Сборка монтажного листа для видео-пересказа.

Читает раскадровку (markdown), подтягивает кадры и озвучку из папки проекта,
собирает одностраничный HTML со встроенными картинками — его публикуем Artifact'ом.

Запуск:
    python build_board.py --session 0
    python build_board.py --md "путь/раскадровка.md" --assets "C:\Azlanti\Video\Session0" --out board.html

Требуется: Pillow, ffprobe в PATH.
"""
import argparse, base64, glob, html, io, json, os, re, subprocess, sys

try:
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
except ImportError:
    sys.exit("нужен Pillow: pip install pillow")

VAULT = r"C:\DND\sync\Sync\Obsidian\PF2e\Кампейны\Азланти"
PROJECTS = r"C:\Azlanti\Video"


# ---------------------------------------------------------------- вспомогательное

def dur(path):
    """длительность аудио в секундах"""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True).stdout.strip()
        return float(out)
    except Exception:
        return 0.0


def still(video, at=4):
    """кадр из видеоклипа во временный png"""
    out = os.path.abspath("_still_%s.png" % os.path.basename(video).replace(".", "_"))
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(at), "-i", video,
                    "-frames:v", "1", out, "-y"])
    return out if os.path.exists(out) else None


def b64(path, width=680):
    """картинка в data-uri, ужатая по ширине"""
    if not path or not os.path.exists(path):
        return None
    im = Image.open(path).convert("RGB")
    im.thumbnail((width, width), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=72, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def esc(t):
    t = html.escape(t)
    t = re.sub(r'`([^`]+)`', r'<code class="k">\1</code>', t)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)


# ---------------------------------------------------------------- сбор ассетов

def collect_assets(assets_dir):
    """кадр -> путь к картинке, кадр -> [(файл озвучки, секунды)]"""
    pics, auds = {}, {}

    for f in sorted(glob.glob(os.path.join(assets_dir, "shot*"))):
        if os.path.isdir(f):
            continue
        m = re.match(r'shot(00[abc]|\d+)', os.path.basename(f))
        if not m:
            continue
        key = m.group(1).lstrip("0") or "0" if m.group(1).isdigit() else m.group(1)
        if f.lower().endswith(".mp4"):
            s = still(f)
            if s:
                pics.setdefault(key, s)
        else:
            pics.setdefault(key, f)

    vdir = os.path.join(assets_dir, "video")
    if os.path.isdir(vdir):
        for f in sorted(glob.glob(os.path.join(vdir, "shot*.mp4"))):
            m = re.match(r'shot(\d+)', os.path.basename(f))
            if m:
                key = str(int(m.group(1)))
                if key not in pics:
                    s = still(f)
                    if s:
                        pics[key] = s

    adir = os.path.join(assets_dir, "audio")
    for f in sorted(glob.glob(os.path.join(adir, "*.mp3"))):
        b = os.path.basename(f)
        if b.startswith("_"):
            continue
        if b.startswith("intro"):
            key = "0c"
        else:
            m = re.match(r'shot(\d+)', b)
            if not m:
                continue
            key = str(int(m.group(1)))
        auds.setdefault(key, []).append((b, round(dur(f), 1)))

    # интро в раскадровке нумеруется 0a/0b/0c, файлы — 00a/00b/00c
    for a, b in (("00a", "0a"), ("00b", "0b"), ("00c", "0c")):
        if a in pics and b not in pics:
            pics[b] = pics[a]
    return pics, auds


# ---------------------------------------------------------------- разбор раскадровки

def parse_board(md_text):
    """[(название части, [кадры])], кадр = dict"""
    body = md_text.split("## ИНТРО", 1)
    if len(body) < 2:
        sys.exit("в раскадровке не найден раздел '## ИНТРО'")
    body = "## ИНТРО" + body[1]
    body = re.split(r'\n## Сборка', body)[0]

    parts = []
    for chunk in re.split(r'\n## ', body):
        chunk = chunk.lstrip("# ").strip()
        if not chunk:
            continue
        title = chunk.split("\n", 1)[0].strip()
        rest = chunk.split("\n", 1)[1] if "\n" in chunk else ""
        m = re.match(r'(.+?)\s*\(([^)]+)\)\s*$', title)
        name = (m.group(1) if m else title).replace("ЧАСТЬ ", "Часть ").rstrip(".")
        if "ИНТРО" in name.upper():
            name = "Интро"

        blocks = re.split(r'\n### ', rest)
        note = blocks[0].strip()
        note = " ".join(l.strip("> ").strip() for l in note.split("\n") if l.strip()) \
            if note and not note.startswith("[") else ""

        shots = []
        for b in blocks[1:]:
            lines = b.split("\n")
            hm = re.match(r'Кадр\s+(\S+)\s*·\s*~?([\d,]+)\s*с(?:\s*—\s*(.+))?', lines[0])
            if not hm:
                continue
            shot = {"num": hm.group(1), "plan": hm.group(2), "badge": hm.group(3),
                    "rows": [], "say": [], "hints": []}
            mode = None
            for ln in lines[1:]:
                t = ln.strip()
                if not t:
                    continue
                if t.startswith(">"):
                    shot["hints"].append(t.lstrip("> ").strip()); continue
                tm = re.match(r'\*\*\[([^\]]+)\]\*\*\s*(.*)', t)
                if tm:
                    tag, txt = tm.group(1), tm.group(2).strip()
                    if tag.startswith("ТЕКСТ"):
                        mode = "say"; continue
                    if tag == "ЗВУК" or tag.startswith("АРТ") or tag == "КЛИП":
                        mode = None; continue
                    mode = None
                    if txt:
                        shot["rows"].append((tag, txt))
                    continue
                if mode == "say":
                    shot["say"].append(t)
            shots.append(shot)
        parts.append((name, note, shots))
    return parts


# ---------------------------------------------------------------- рендер html

CSS = """
:root{--ground:#EDEBE4;--panel:#FFF;--sunk:#E4E1D7;--edge:#D7D2C4;--ink:#23262B;
--muted:#6B7079;--amber:#A9761E;--amber-soft:#F0E4CB;--teal:#3F6F74;
--shadow:0 1px 2px rgba(35,38,43,.06),0 8px 24px -12px rgba(35,38,43,.18)}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--ground:#14161A;
--panel:#1B1F25;--sunk:#181B21;--edge:#2B313A;--ink:#D9D5CB;--muted:#878D97;
--amber:#D9A44A;--amber-soft:#2A2318;--teal:#7EA5AA;
--shadow:0 1px 2px rgba(0,0,0,.4),0 10px 28px -14px rgba(0,0,0,.7)}}
:root[data-theme="dark"]{--ground:#14161A;--panel:#1B1F25;--sunk:#181B21;--edge:#2B313A;
--ink:#D9D5CB;--muted:#878D97;--amber:#D9A44A;--amber-soft:#2A2318;--teal:#7EA5AA;
--shadow:0 1px 2px rgba(0,0,0,.4),0 10px 28px -14px rgba(0,0,0,.7)}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
font-family:"Source Serif 4",Georgia,serif;font-size:17px;line-height:1.6}
.wrap{max-width:920px;margin:0 auto;padding:0 20px 96px}
header{padding:56px 0 28px}
.eyebrow{font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.22em;
text-transform:uppercase;color:var(--amber);margin:0 0 14px}
h1{font-family:Archivo,system-ui,sans-serif;font-weight:700;font-size:clamp(34px,6vw,52px);
line-height:1.03;letter-spacing:-.02em;margin:0 0 10px;text-wrap:balance}
.sub{color:var(--muted);margin:0;max-width:60ch}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(128px,1fr));gap:1px;
background:var(--edge);border:1px solid var(--edge);border-radius:10px;overflow:hidden;margin:30px 0 10px}
.fact{background:var(--panel);padding:14px 16px}
.fact dt{font-family:"JetBrains Mono",monospace;font-size:10px;letter-spacing:.16em;
text-transform:uppercase;color:var(--muted);margin:0 0 6px}
.fact dd{margin:0;font-family:Archivo,sans-serif;font-weight:600;font-size:21px;
font-variant-numeric:tabular-nums}
nav{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--ground) 92%,transparent);
backdrop-filter:blur(8px);border-bottom:1px solid var(--edge);margin:26px -20px 0;
padding:10px 20px;display:flex;gap:6px;overflow-x:auto}
nav a{font-family:"JetBrains Mono",monospace;font-size:11px;color:var(--muted);
text-decoration:none;white-space:nowrap;padding:5px 9px;border-radius:6px;border:1px solid transparent}
nav a:hover,nav a:focus-visible{color:var(--ink);border-color:var(--edge);background:var(--panel);outline:none}
.part{margin-top:52px}
.part-head{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;padding-bottom:10px;
border-bottom:2px solid var(--ink)}
.part-head h2{font-family:Archivo,sans-serif;font-weight:700;font-size:23px;margin:0}
.part-head .range{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--amber);
font-variant-numeric:tabular-nums;margin-left:auto}
.note{color:var(--muted);font-size:15px;margin:14px 0 0;border-left:2px solid var(--edge);padding-left:14px}
.shot{display:grid;grid-template-columns:74px 1fr;gap:20px;padding:22px 0;border-bottom:1px solid var(--edge)}
.rail{font-family:"JetBrains Mono",monospace;font-variant-numeric:tabular-nums}
.num{font-family:Archivo,sans-serif;font-weight:700;font-size:26px;line-height:1}
.dur{font-size:12px;color:var(--muted);margin-top:5px}
.rows{display:flex;flex-direction:column;gap:11px;min-width:0}
.row{display:grid;grid-template-columns:82px 1fr;gap:12px;align-items:start}
.tag{font-family:"JetBrains Mono",monospace;font-size:10px;font-weight:700;letter-spacing:.1em;
text-transform:uppercase;color:var(--muted);padding-top:5px;text-align:right}
.tag.cam{color:var(--teal)}.tag.snd{color:#8A6BAF}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]) .tag.snd{color:#B49BD6}}
:root[data-theme="dark"] .tag.snd{color:#B49BD6}
.row p{margin:0;font-size:15.5px;line-height:1.55}
.row .tech{color:var(--muted)}
.frame{margin:0 0 12px;border:1px solid var(--edge);border-radius:8px;overflow:hidden;
background:var(--sunk);line-height:0}
.frame img{width:100%;height:auto;display:block}
.say{background:var(--panel);border:1px solid var(--edge);border-left:3px solid var(--amber);
border-radius:0 8px 8px 0;padding:13px 16px;box-shadow:var(--shadow)}
.say p{margin:0;font-size:17px;line-height:1.62}
.say p+p{margin-top:11px}
.say .beat{font-family:"JetBrains Mono",monospace;font-size:10px;letter-spacing:.1em;
text-transform:uppercase;color:var(--teal);display:block;margin-bottom:3px}
.files{display:flex;flex-direction:column;gap:3px}
.files span{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--muted);
font-variant-numeric:tabular-nums}
.files b{color:var(--ink);font-weight:500}
.miss{font-family:"JetBrains Mono",monospace;font-size:11px;color:var(--amber)}
.hint{font-size:14px;color:var(--muted);font-style:italic;margin:0}
.badge{display:inline-block;font-family:"JetBrains Mono",monospace;font-size:9px;font-weight:700;
letter-spacing:.12em;text-transform:uppercase;color:var(--amber);background:var(--amber-soft);
border-radius:4px;padding:2px 6px;margin-top:7px}
code.k{font-family:"JetBrains Mono",monospace;font-size:12.5px;background:var(--sunk);
border:1px solid var(--edge);border-radius:4px;padding:1px 5px}
@media(max-width:640px){.shot{grid-template-columns:1fr;gap:10px}
.rail{display:flex;align-items:baseline;gap:10px}.dur{margin-top:0}
.row{grid-template-columns:1fr;gap:3px}.tag{text-align:left;padding-top:0}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

HEAD = ('<title>{title}</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Archivo:wght@600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600'
        '&family=JetBrains+Mono:wght@400;500;700&display=swap">\n<style>{css}</style>\n')


def build(parts, pics, auds, title, subtitle):
    out, navs, total = [], [], 0.0
    tagcls = {"КАМЕРА": "cam", "СИНХРОН": "cam", "СКОРОСТЬ": "cam", "ВХОД": "cam",
              "ПЕРЕХОД": "cam"}

    for i, (name, note, shots) in enumerate(parts):
        pid = "p%d" % i
        short = name.replace("Часть ", "")
        navs.append('<a href="#%s">%s</a>' % (pid, esc(short)))
        blocks, part_time = [], 0.0

        for s in shots:
            key = str(int(s["num"])) if s["num"].isdigit() else s["num"]
            files = auds.get(key, [])
            fact = round(sum(d for _, d in files), 1)
            part_time += fact
            total += fact
            img = b64(pics.get(key))

            h = ['<div class="shot"><div class="rail"><div class="num">%s</div>'
                 '<div class="dur">%s с</div>%s</div><div class="rows">'
                 % (esc(s["num"]), ("%.0f" % fact) if fact else s["plan"],
                    ('<div class="badge">%s</div>' % esc(s["badge"].lower())) if s["badge"] else "")]
            h.append('<div class="frame"><img src="%s" alt="кадр %s"></div>' % (img, esc(s["num"]))
                     if img else '<p class="miss">арта нет</p>')
            for tag, txt in s["rows"]:
                cls = tagcls.get(tag.split()[0], "")
                h.append('<div class="row"><span class="tag %s">%s</span>'
                         '<p class="%s">%s</p></div>'
                         % (cls, esc(tag.capitalize()), "tech" if cls else "", esc(txt)))
            if s["say"]:
                paras = []
                for line in s["say"]:
                    bm = re.match(r'\*([^*]+)\*\s*—\s*(.*)', line)
                    paras.append('<p><span class="beat">%s</span>%s</p>'
                                 % (esc(bm.group(1)), esc(bm.group(2))) if bm
                                 else '<p>%s</p>' % esc(line))
                h.append('<div class="row"><span class="tag">Текст</span>'
                         '<div class="say">%s</div></div>' % "".join(paras))
            h.append('<div class="row"><span class="tag snd">Звук</span>%s</div>'
                     % ('<div class="files">%s</div>'
                        % "".join('<span><b>%s</b> · %.1f с</span>' % (n, d) for n, d in files)
                        if files else '<p class="miss">не записан</p>'))
            for hint in s["hints"]:
                h.append('<p class="hint">%s</p>' % esc(hint))
            h.append('</div></div>')
            blocks.append("".join(h))

        mm, ss = divmod(int(part_time), 60)
        out.append('<section class="part" id="%s"><div class="part-head"><h2>%s</h2>'
                   '<span class="range">%d:%02d</span></div>%s%s</section>'
                   % (pid, esc(name), mm, ss,
                      ('<p class="note">%s</p>' % esc(note)) if note else "", "".join(blocks)))

    n_shots = sum(len(p[2]) for p in parts)
    n_art = sum(1 for p in parts for s in p[2]
                if (str(int(s["num"])) if s["num"].isdigit() else s["num"]) in pics)
    n_vo = len(auds)
    mm, ss = divmod(int(total), 60)
    header = ('<header><p class="eyebrow">Орден Азланти · реестр аномалий</p>'
              '<h1>%s</h1><p class="sub">%s</p><dl class="facts">'
              '<div class="fact"><dt>Хронометраж</dt><dd>%d:%02d</dd></div>'
              '<div class="fact"><dt>Кадров</dt><dd>%d</dd></div>'
              '<div class="fact"><dt>Артов</dt><dd>%d</dd></div>'
              '<div class="fact"><dt>Озвучено</dt><dd>%d</dd></div>'
              '<div class="fact"><dt>Формат</dt><dd>1080p</dd></div></dl></header>'
              % (esc(title), esc(subtitle), mm, ss, n_shots, n_art, n_vo))

    return (HEAD.format(title=esc(title), css=CSS) + '<div class="wrap">\n' + header
            + '<nav>%s</nav>' % "".join(navs) + "\n".join(out) + "\n</div>\n"), total


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", type=int, help="номер сессии, задаёт пути по умолчанию")
    ap.add_argument("--md", help="путь к раскадровке")
    ap.add_argument("--assets", help="папка проекта с кадрами и озвучкой")
    ap.add_argument("--out", default="board.html")
    ap.add_argument("--title", default=None)
    ap.add_argument("--subtitle",
                    default="Монтажный лист: кадр, движение камеры, текст и файлы озвучки. "
                            "Хронометраж — по факту записи.")
    a = ap.parse_args()

    if a.session is not None:
        a.md = a.md or os.path.join(VAULT, "Sessions", "Session%d" % a.session,
                                    "Пересказ-видео__раскадровка.md")
        a.assets = a.assets or os.path.join(PROJECTS, "Session%d" % a.session)
        a.title = a.title or "Запись %d" % (a.session + 1)
    if not (a.md and a.assets):
        sys.exit("нужны --session или пара --md/--assets")

    md = open(a.md, encoding="utf-8").read()
    parts = parse_board(md)
    pics, auds = collect_assets(a.assets)
    html_text, total = build(parts, pics, auds, a.title or "Монтажный лист", a.subtitle)
    open(a.out, "w", encoding="utf-8", newline="\n").write(html_text)

    mm, ss = divmod(int(total), 60)
    print("%s — %.1f MB, хронометраж %d:%02d, кадров с артом %d, кадров с озвучкой %d"
          % (a.out, os.path.getsize(a.out) / 1e6, mm, ss, len(pics), len(auds)))
    for f in glob.glob("_still_*.png"):
        os.remove(f)


if __name__ == "__main__":
    main()
