"""Merge cleaned chunks of a session into ПС{N}_transcript.md.

Usage:
    python merge.py N
where N is session number. Reads chunks from
  C:\\DND\\Азланти\\Cессии\\Сессия-N\\chunks\\cleaned\\000K_clean.md
and writes to
  C:\\DND\\sync\\Sync\\Obsidian\\PF2e\\Кампейны\\Азланти\\Sessions\\SessionN\\ПС{N}_transcript.md

Handles:
- Strips YAML frontmatter from any chunk
- Strips UNCERTAINTIES blocks at chunk ends
- Dedups overlaps on chunk-to-chunk boundaries via session-specific MARKERS
- Applies normalization replacements (WhisperX -> canon)

Session-specific MARKERS need to be configured for each session — see SESSION_MARKERS dict.
For a new session not in dict, the script falls back to gluing chunks with '---' separators.
"""
import re
import sys
from pathlib import Path


# Per-session overlap markers: for chunk[i+1], marker_text is where new content starts.
# Anything BEFORE the marker in chunk[i+1] is overlap with chunk[i] and is dropped.
# Key = chunk index (1-based) where dedup is applied (i.e., MARKERS[2] applies to chunk 0002).
SESSION_MARKERS = {
    8: {
        2: "### Визит Микаэля к Борису Вальку",
        3: "**Егорушка (Гельдала, IC — голос духа):** Ты опозорил меня",
        4: "### Путь к Абсалому: выезд из леса",
        5: "Подождите. Я не подскажу вам точный путь",
        6: "### Дорога в Абсалом — разговор партии о Пятом Крестовом Походе",
        7: "### Интерьер Приюта — хозяин Харвин и стена памяти",
        8: "### Прощание с мемориалом",
        9: None,  # whole post-session OOC, keep all
    },
    7: {
        2: "### Ход Калигни-авангарда (Раунд 3)",
        3: "### Ход Бель — массовое исцеление эманацией",
        4: "### Боёвка — ход Среднего Гуманоида (Ши'Ранна Тенеслух)",
        5: "**Сеня (Анканто/Микаэль):** Протыкается его сердце, а в руке, которая дёрнется в спазме",
        6: "### Раунд 7 — ход Калигни-убийцы: Курзаир падает без сознания",
        7: "### Микаэль возвращается к жизни",
        8: "### Условия сделки: отчёты раз в три месяца",
        9: None,
        10: None,
        11: None,
    },
    # Add new sessions here as you process them.
}


# WhisperX → canon replacements. Applied to merged text in order.
# Order matters: more specific forms must come BEFORE less specific.
REPL = [
    # Абсалом
    ("Псаломе", "Абсаломе"),
    ("Псалому", "Абсалому"),
    ("Псалома", "Абсалома"),
    ("Псалом", "Абсалом"),
    ("про псалом", "про Абсалом"),
    # Гельдала
    ("Гильдалой", "Гельдалой"),
    ("Гильдалу", "Гельдалу"),
    ("Гильдале", "Гельдале"),
    ("Гильдалы", "Гельдалы"),
    ("Гильдала", "Гельдала"),
    ("Гедалой", "Гельдалой"),
    ("Гедалу", "Гельдалу"),
    ("Гедале", "Гельдале"),
    ("Гедала", "Гельдала"),
    # Абадар
    ("Аббадару", "Абадару"),
    ("Аббадаром", "Абадаром"),
    ("Аббадара", "Абадара"),
    ("Аббадар", "Абадар"),
    # Ароден
    ("Аарадану", "Ародену"),
    ("Аарадана", "Ародена"),
    ("Аарадан", "Ароден"),
    ("Арадану", "Ародену"),
    ("Арадана", "Ародена"),
    ("Арадан", "Ароден"),
    # Арканамириум
    ("Аркариуму", "Арканамириуму"),
    ("Аркариума", "Арканамириума"),
    ("Аркариум", "Арканамириум"),
    ("Арканомириуму", "Арканамириуму"),
    ("Арканомириума", "Арканамириума"),
    ("Арканомириум", "Арканамириум"),
    ("Арканариуму", "Арканамириуму"),
    ("Арканариума", "Арканамириума"),
    ("Арканариум", "Арканамириум"),
    ("Оркнариум", "Арканамириум"),
    # Иомедай
    ("Амидай", "Иомедай"),
    ("Амедай", "Иомедай"),
    ("Айодай", "Иомедай"),
    ("Айодан", "Иомедай"),
    # Галфри
    ("Голдфри", "Галфри"),
    ("Голдфры", "Галфри"),
    # Дескари
    ("Доскари", "Дескари"),
    ("Эскарри", "Дескари"),
    # Мендев
    ("Миндева", "Мендева"),
    ("Миндеве", "Мендеве"),
    ("Миндевом", "Мендевом"),
    ("Миндев", "Мендев"),
    # Анканто
    ("Анкантой", "Анканто"),
    ("Анканта", "Анканто"),
    # Ферасма
    ("форазмы", "Ферасмы"),
    ("форазмой", "Ферасмой"),
    ("Ферасм)", "Ферасма)"),
    # Прочее
    ("Псекира", "секира"),  # Только Торина оружие, не имя
    ("Ургатуа", "Уртагоа"),
    ("Саквротский", "Сакворотский"),
    ("Саквротского", "Сакворотского"),
    ("Саквротскому", "Сакворотскому"),
    ("Альдрик", "Алдрик"),
    ("Хайден Кайдан", "Кайдан"),
    # NPC, специфичные С8+
    ("Дом Ормуз", "Дом Ормус"),
    ("Дома Ормуз", "Дома Ормус"),
    ("Дому Ормуз", "Дому Ормус"),
    ("Дом Сени Грации", "Дом Сени и Грации"),
    # Унгвинор — сын Гельдалы (не путать с другим Ангвинором, если такой есть)
    # Если в сессии явно про сына — добавь раскомментировать:
    # ("Ангвинор", "Унгвинор"),
]


def read_clean(path):
    """Read a cleaned chunk, strip frontmatter and UNCERTAINTIES."""
    t = path.read_text(encoding='utf-8')
    # strip YAML frontmatter (e.g., chunk 0008 in С8 had one)
    t = re.sub(r'^---\nchunk:.*?\n---\n+', '', t, flags=re.DOTALL)
    # strip UNCERTAINTIES section (at end of chunk)
    t = re.sub(r'\n+# UNCERTAINTIES.*$', '', t, flags=re.DOTALL)
    return t.strip()


def merge_session(N):
    chunks_dir = Path(f"C:/DND/Азланти/Cессии/Сессия-{N}/chunks/cleaned")
    out_path = Path(f"C:/DND/sync/Sync/Obsidian/PF2e/Кампейны/Азланти/Sessions/Session{N}/ПС{N}_transcript.md")

    chunk_files = sorted(chunks_dir.glob("0*_clean.md"))
    if not chunk_files:
        raise FileNotFoundError(f"No cleaned chunks in {chunks_dir}")

    chunks = [read_clean(p) for p in chunk_files]
    K = len(chunks)

    markers = SESSION_MARKERS.get(N, {})

    out = [f"# Сессия {N} — Транскрипт\n"]
    out.append(chunks[0])

    warnings = []
    for i in range(1, K):
        chunk_idx = i + 1  # 1-based chunk number
        marker = markers.get(chunk_idx, None)
        text = chunks[i]
        if marker:
            idx = text.find(marker)
            if idx < 0:
                warnings.append(f"WARN: marker not found in chunk {chunk_idx}: {marker[:60]!r}")
                out.append("\n\n---\n\n" + text)
            else:
                # rewind to the nearest preceding "### " heading, if close
                head = text.rfind("\n### ", 0, idx)
                if head >= 0 and (idx - head) < 200:
                    out.append("\n\n" + text[head+1:])
                else:
                    out.append("\n\n" + text[idx:])
        else:
            # no marker (e.g., post-session OOC) — keep whole chunk with separator
            out.append("\n\n---\n\n" + text)

    merged = "\n".join(out)

    # Apply normalization
    for old, new in REPL:
        merged = merged.replace(old, new)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(merged, encoding='utf-8')

    lines = merged.count("\n") + 1
    chars = len(merged)
    return out_path, lines, chars, warnings


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python merge.py <session_number>\n")
        sys.exit(1)
    N = int(sys.argv[1])
    out, lines, chars, warns = merge_session(N)
    # Use ASCII-safe encoding for stdout (Windows console default is cp1252)
    safe = lambda s: s.encode('ascii', 'replace').decode('ascii')
    print(f"OK: wrote session {N} transcript")
    print(f"Path: {safe(str(out))}")
    print(f"Size: {chars} chars / {lines} lines")
    for w in warns:
        print(safe(w))
