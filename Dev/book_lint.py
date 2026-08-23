#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
book_lint.py — механическая проверка сцены/главы книги Тироса на запреты
из Assistant Guides/Книга__Project_Instructions.md.

Не оценивает качество прозы — это работа критика. Ловит то, что проверяется
без модели: следы игровой механики, оформление прямой речи, синтаксические
запреты, копирование эталонных сцен.

Калибровка: на эталонной главе С4 (45/50) линтер должен молчать. Если правило
срабатывает на С4 — правило неверное, а не глава.

Запуск:
    python3 Dev/book_lint.py Sessions/Session5/сцена_1.md
    python3 Dev/book_lint.py --no-ref --quiet Sessions/Session4/С4-архив.md
"""

import argparse
import os
import re
import sys
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REF = os.path.join(BASE, "Assistant Guides", "Автописатель_Книги", "05__Эталонные_сцены.md")

# Ритм эталонной главы С4
BENCH_AVG_SENT = 11.0
BENCH_SHORT_SHARE = 0.23
# 6 находок на 5090 слов эталонной главы С4
BENCH_DENSITY = 1.2

VERB_ENDINGS = (
    "ть", "ться", "л", "ла", "ло", "ли", "лся", "лась", "лись",
    "ет", "ёт", "ит", "ут", "ют", "ат", "ят", "ешь", "ишь", "ем", "им",
    "ал", "ил", "ел", "ыл", "ул", "ся", "сь", "шь", "ло", "ний",
)
VERB_FALSE = {
    "стол", "угол", "пол", "вол", "мел", "гол", "ствол", "котёл", "орёл",
    "узел", "вокзал", "канал", "металл", "финал", "сигнал", "провал", "зал",
    "лес", "нос", "пёс", "вес", "интерес", "лось", "гость", "кость",
    "весь", "часть", "смерть", "дверь", "мать", "дочь", "ночь", "речь",
    "путь", "жизнь", "боль", "соль", "роль", "цель", "тень", "день",
    "он", "она", "они", "всё", "это", "тоже", "здесь", "теперь", "очень",
}

MECHANICS = [
    (r"\bd\s?\d{1,3}\b", "кубик"),
    (r"\bк\d{1,3}\b", "кубик"),
    (r"хит[- ]?поинт|\bхиты\b", "HP"),
    (r"\bHP\b", "HP"),
    (r"\bAC\b|\bКД\b", "класс защиты"),
    (r"спасбр[оа]с", "спасбросок"),
    (r"броск\w* инициативы|инициатив\w+ (?:ещё |уже )?(?:не )?(?:дошла|дошёл|прошла|идёт|наступила)", "инициатива"),
    (r"провер[кио]\w* (?:навыка|атаки|умения)", "проверка навыка"),
    (r"крит(?:ический)? (?:успех|провал)\b", "термин правил"),
    (r"\bуровн(?:я|ем|е) \d+\b", "уровень персонажа"),
    (r"\bдейств(?:ие|ия) \d\b", "экономика действий"),
    (r"\bраунд\w* \d", "нумерация раундов"),
]

OOC = [
    (r"\bOOC\b|\bООС\b", "OOC-маркер"),
    (r"\(смех\)|\(смеются\)|\(нрзб\)|\(неразборчиво\)", "транскрипционная ремарка"),
    (r"\bГМ\b|\bгеймастер|\bмастер говорит\b", "мета-упоминание ГМа"),
]


def strip_meta(text):
    """Убирает заголовки, врезки, цитаты, разделители."""
    out = []
    for line in text.split("\n"):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(">") or s.startswith("---"):
            continue
        if s.startswith("**") and s.endswith("**"):
            continue
        out.append(s)
    return "\n".join(out)


def paragraphs(text):
    return [s for s in strip_meta(text).split("\n") if s.strip()]


def is_speech(par):
    """Реплика прямой речи: синтаксис прозы к ней не применяется."""
    return par.lstrip().startswith(("—", "–"))


def sentences_of(par):
    """Предложения абзаца, без слов автора внутри реплик."""
    par = re.sub(r"—[^.!?…]{0,80}—", " ", par)
    res = []
    for p in re.split(r"(?<=[.!?…])\s+", par):
        p = p.strip()
        if len(p) > 1 and not p.startswith(("—", "–")):
            res.append(p)
    return res


def split_sentences(text):
    sents = []
    for par in paragraphs(text):
        if is_speech(par):
            continue
        sents.extend(sentences_of(par))
    return sents


def words(s):
    return re.findall(r"[А-Яа-яЁёA-Za-z]+(?:-[А-Яа-яЁёA-Za-z]+)?", s)


def has_verb(sent):
    for w in words(sent):
        lw = w.lower()
        if lw in VERB_FALSE:
            continue
        if lw.endswith(VERB_ENDINGS):
            return True
    return False


def line_of(text, fragment):
    idx = text.find(fragment[:60])
    if idx < 0:
        return 0
    return text.count("\n", 0, idx) + 1


def ngrams(text, n=7):
    ws = [w.lower() for w in words(strip_meta(text))]
    return {" ".join(ws[i:i + n]) for i in range(max(0, len(ws) - n + 1))}


def runs(items, predicate, minlen):
    """Возвращает цепочки подряд идущих элементов, удовлетворяющих предикату."""
    out, run = [], []
    for it in items:
        if predicate(it):
            run.append(it)
        else:
            if len(run) >= minlen:
                out.append(run)
            run = []
    if len(run) >= minlen:
        out.append(run)
    return out


def check(text, ref_text=None):
    findings = []

    # HARD: следы механики и меты
    for pattern, label in MECHANICS + OOC:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            frag = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ").strip()
            findings.append(("HARD", text.count("\n", 0, m.start()) + 1,
                             f"следы механики/мета: {label}", frag))

    # HARD: прямая речь в кавычках вместо тире
    for i, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if re.match(r'^[«"].{10,}[»"][ ,]*—\s*(сказал|ответил|проговорил|спросил)', s):
            findings.append(("HARD", i, "прямая речь в кавычках — оформляется через тире", s[:90]))

    # HARD: копирование эталонов
    if ref_text:
        for frag in sorted(ngrams(text) & ngrams(ref_text))[:10]:
            findings.append(("HARD", line_of(text, frag),
                             "совпадение 7+ слов с эталонной сценой — эталон копировать нельзя", frag))

    # SOFT: синтаксис — только внутри абзацев прозы, реплики не трогаем
    for par in paragraphs(text):
        if is_speech(par):
            continue
        ss = sentences_of(par)

        for run in runs(ss, lambda s: len(words(s)) <= 4, 4):
            findings.append(("SOFT", line_of(text, run[0]),
                             f"цепочка из {len(run)} коротких предложений — фрагментация ради веса",
                             " ".join(run)[:120]))

        for run in runs(ss, lambda s: 1 <= len(words(s)) <= 6 and not has_verb(s), 2):
            findings.append(("SOFT", line_of(text, run[0]),
                             f"{len(run)} назывных предложения подряд", " ".join(run)[:110]))

        for s in ss:
            if len(words(s)) <= 8 and re.search(r"[а-яё]{3,}\s+—\s+[а-яё]{3,}", s) and not has_verb(s):
                findings.append(("SOFT", line_of(text, s), "тире вместо глагола", s[:90]))

        for i in range(len(ss) - 1):
            a, b = ss[i].strip(), ss[i + 1].strip()
            if a.startswith(("Не ", "Не«")) and b.startswith(("Не ", "Не«")):
                findings.append(("SOFT", line_of(text, a),
                                 "разбор слова через отрицание альтернатив", f"{a} {b}"[:110]))

    return findings, split_sentences(text)


def report(path, findings, sents, quiet=False):
    ws = sum(len(words(s)) for s in sents)
    n = len(sents) or 1
    avg = ws / n
    short = sum(1 for s in sents if len(words(s)) <= 4) / n

    hard = [f for f in findings if f[0] == "HARD"]
    soft = [f for f in findings if f[0] == "SOFT"]

    print(f"\n=== {os.path.basename(path)} ===")
    print(f"слов: {ws}   предложений: {n}   ср. длина: {avg:.1f} (эталон С4: {BENCH_AVG_SENT})")
    print(f"доля предложений ≤4 слов: {short:.0%} (эталон С4: {BENCH_SHORT_SHARE:.0%})")
    if avg < BENCH_AVG_SENT - 2.5:
        print("  ⚠ текст рубленее эталона — вероятна фрагментация")
    if short > BENCH_SHORT_SHARE + 0.12:
        print("  ⚠ много коротких предложений — проверить назывные цепочки")

    density = len(findings) / max(ws, 1) * 1000
    print(f"находок на 1000 слов: {density:.1f} (эталон С4: {BENCH_DENSITY})")
    if density > BENCH_DENSITY * 2:
        print("  ⚠ плотность вдвое выше эталонной — текст стоит посмотреть глазами")

    for level, group in (("HARD", hard), ("SOFT", soft)):
        if not group:
            continue
        print(f"\n[{level}] {len(group)}")
        seen = Counter()
        for _lvl, line, rule, frag in group:
            seen[rule] += 1
            if quiet and seen[rule] > 6:
                continue
            print(f"  строка {line:>4}  {rule}")
            print(f"              «{frag}»")
        if quiet:
            for rule, cnt in seen.items():
                if cnt > 6:
                    print(f"  … и ещё {cnt - 6} того же типа: {rule}")

    if not findings:
        print("\nчисто.")
    return 1 if hard else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--ref", default=DEFAULT_REF)
    ap.add_argument("--no-ref", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    ref_text = None
    if not args.no_ref and os.path.exists(args.ref):
        ref_text = open(args.ref, encoding="utf-8").read()

    rc = 0
    for path in args.files:
        text = open(path, encoding="utf-8").read()
        findings, sents = check(text, ref_text)
        rc |= report(path, findings, sents, quiet=args.quiet)
    return rc


if __name__ == "__main__":
    sys.exit(main())
