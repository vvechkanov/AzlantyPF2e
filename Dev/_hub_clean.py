# -*- coding: utf-8 -*-
# Снятие сессионных пометок (С9/С10) с рёбер и нод хаба. Точные замены.
p = r"C:\DND\sync\Sync\Obsidian\PF2e\Кампейны\Азланти\00__HUB.d2"

REPL = [
 ('Sources.Plates -> Pathfinders: "залог 1000 зм\\n(С9: на неделю)" {class: thread-plates}',
  'Sources.Plates -> Pathfinders: "путь к эксперту" {class: thread-plates}'),
 ('Sources.Plates -> KessaVara: "центральное слово\\n(С9: Зарта прочла)" {class: thread-plates}',
  'Sources.Plates -> KessaVara: "центральное слово" {class: thread-plates}'),
 ('Pathfinders -> Sarel: "Зарта знает\\n(С9: вбросила имя Бель)" {class: thread-plates}',
  'Pathfinders -> Sarel: "Зарта знает" {class: thread-plates}'),
 ('Sources.Kiran_statue -> Iroriarum: "Йсия знала Аширу;\\n(С9: дала Лисенга)" {class: thread-statue}',
  'Sources.Kiran_statue -> Iroriarum: "Йсия знала Аширу" {class: thread-statue}'),
 ('Sources.Kiran_statue -> Library: "архивы Forae Logos\\n(С9: цель — Лисенг)" {class: thread-statue}',
  'Sources.Kiran_statue -> Library: "архивы Forae Logos" {class: thread-statue}'),
 ('Iroriarum -> Library: "Йсия → Лисенг\\n(С9: ключевая зацепка)" {class: thread-statue}',
  'Iroriarum -> Library: "Йсия → Лисенг" {class: thread-statue}'),
 ('# === НИТЬ ПОПАДАНЧЕСТВА БЕЛЬ × ПРОИЗНОШЕНИЕ (С9) ===',
  '# === НИТЬ ПОПАДАНЧЕСТВА БЕЛЬ × ПРОИЗНОШЕНИЕ ==='),
 ('Sources.Bell -> Sarel: "одинаковое произношение\\n(С9: Зарта услышала;\\nБель не его ученица)" {class: thread-plates-hidden}',
  'Sources.Bell -> Sarel: "одинаковое произношение\\n(Бель не его ученица)" {class: thread-plates-hidden}'),
 ('\\n«Сегодня другой человек» (Йсия)\\n[цель Кирана на С10]"',
  '\\n«Сегодня другой человек» (Йсия)"'),
 ('Kiran_statue_src -> Library.Liseng: "цель Кирана на С10\\n(направила Йсия)" {class: thread-statue}',
  'Kiran_statue_src -> Library.Liseng: "направила Йсия" {class: thread-statue}'),
 ('Plates_src: "Пластины Азланти\\n(С9: переданы Зарте\\nна неделю, залог 1000 зм)" {',
  'Plates_src: "Пластины Азланти" {'),
 ('Bell_src: "Бель — попаданка\\n(С9: произнесла азланти\\nкак Сарел Тейваниэль)" {',
  'Bell_src: "Бель — попаданка" {'),
 ('Plates_src -> GrandLodge.Zarta: "С9: приняты на неделю,\\nгипотеза Кесса Вара" {class: thread-plates}',
  'Plates_src -> GrandLodge.Zarta: "гипотеза Кесса Вара" {class: thread-plates}'),
 ('Bell_src -> Sarel_ext: "одинаковое произношение\\n(С9: загадка,\\nБель не его ученица)" {class: thread-plates-hidden}',
  'Bell_src -> Sarel_ext: "одинаковое произношение\\n(загадка, Бель не его ученица)" {class: thread-plates-hidden}'),
 ('Bell_src -> GrandLodge.Zarta: "С9: стычка по азланти,\\nправо вечерних визитов" {class: thread-plates}',
  'Bell_src -> GrandLodge.Zarta: "стычка по азланти,\\nправо вечерних визитов" {class: thread-plates}'),
 ('\\n(лев 25 зм)\\n[С9: 3 гнола за 12 зм запланированы]"',
  '\\n(лев 25 зм)"'),
 ('Healer: "💊 Целитель арены\\n1.5–5 зм/мес\\n[С9: Илрик предложил Бель]" {',
  'Healer: "💊 Целитель арены\\n1.5–5 зм/мес" {'),
 ('Kiran_statue_src -> Iroriarum.Yisia: "С9: зацепка от Йсии\\n(зеркальное лицо,\\n«мастер мастеров»)" {class: thread-statue}',
  'Kiran_statue_src -> Iroriarum.Yisia: "зацепка от Йсии\\n(зеркальное лицо,\\n«мастер мастеров»)" {class: thread-statue}'),
 ('Iroriarum.Yisia -> Liseng_ext: "С9: главная наводка\\n(Лисенг 10 лет назад\\nбыл нездорово увлечён)" {class: thread-statue}',
  'Iroriarum.Yisia -> Liseng_ext: "главная наводка\\n(Лисенг 10 лет назад\\nбыл нездорово увлечён)" {class: thread-statue}'),
 ('Iroriarum.Yisia -> Ashira_src: "С9: передала послание\\n(«сталь + вода»)"',
  'Iroriarum.Yisia -> Ashira_src: "передала послание\\n(«сталь + вода»)"'),
 ("Bell_src -> Kiran_src: \"С9: версия 'Ашира сама\\nспрятала, инициатическое\\nиспытание'\"",
  "Bell_src -> Kiran_src: \"версия 'Ашира сама\\nспрятала, инициатическое\\nиспытание'\""),
]

data = open(p, 'rb').read().decode('utf-8')
misses = []
for old, new in REPL:
    if data.count(old) == 0:
        misses.append(old[:60])
    else:
        data = data.replace(old, new)

if misses:
    print("MISS", len(misses))
    for m in misses:
        print(" -", m)
else:
    open(p, 'wb').write(data.encode('utf-8'))
    print("OK applied", len(REPL))
