# Арка 1 — TODO: портреты и арты

## Процесс генерации внешности и портрета (как мы работаем)
1) Нейронка открывает файл NPC/локации и читает контент.
2) Если в файле уже есть **описание внешности**, нейронка генерирует *своё* описание внешности **на основе** файла: можно придумывать новое, но **нельзя противоречить** тому, что уже написано.
3) Мы обсуждаем внешность и финализируем.
4) После финализации внешности нейронка генерирует портрет, используя **STYLE BLOCK** ниже **без изменений**.
5) Мы обсуждаем получившийся портрет/стиль и финализируем конкретную картинку.
6) После финализации портрета нейронка выдаёт итог: (а) финальное описание внешности, (б) портрет (ссылка/идентификатор). Дальше считаем портрет достаточным источником истины.

## Инструкция после генерации (ссылка на портрет)
- Я присылаю **ссылку** на финальный портрет.
- Нейронка:
  1) добавляет эту ссылку в соответствующий **NPC-файл**;
  2) синхронизирует/уточняет текстовое описание внешности в NPC-файле **в соответствии с портретом**;
  3) при необходимости отмечает, что портрет зафиксирован и является референсом.

## STYLE BLOCK (paste into prompts)
STYLE BLOCK (paste into prompts): • clean fantasy character illustration, not photorealistic, crisp linework and clear contour outlines • soft painterly shading with smooth color fills, high material clarity (leather, cloth, metal), no gritty texture • neutral studio-like soft lighting, balanced contrast, sharp readable silhouette, artbook-quality rendering • minimal pale background with subtle paper texture, heavily blurred / abstract, no environment details • character centered, either full-body or waist-up portrait, consistent professional RPG portrait style

Очередь на генерацию картинок для Арки 1 (Greenford): локации и NPC без портретов.

## Локации (арт окружения)
- Таверна: The Swordsman and the Jaguar
- Гостиница: Лесная жизнь (The Life and the Forest)
- Общий зал: Community Hall
- Школа: The Gikishika School
- Кузня: The Common Blacksmith
- Железная лавка: Jurelisma's Ironmonger
- Травница: The Wrinkled Lantern Herbalist
- Лесной двор: The Immaculate Logging Co.
- Охотничий дом: Serene Hunter

## NPC без портрета (имя + raw)
- **Гаррен Кинсуик.md** — raw: [[Гаррен Кинсуик]]
- **Освальд Меррик.md** — raw: [[Освальд Меррик]]
- **Курзаир.md** — raw: [[Курзаир]]
- **Варх Кет.md** — raw: [[Варх Кет]]
- **Иш Сарра.md** — raw: [[Иш Сарра]]
- **Лиш Тен.md** — raw: [[Лиш Тен]]
- **Сай Мор.md** — raw: [[Сай Мор]]
- **Керрен Тар-Крыло.md** — raw: [[Керрен Тар-Крыло]]
- **Марна Вельс.md** — raw: [[Марна Вельс]]
- **Риан Вельс.md** — raw: [[Риан Вельс]]
- **Эли Вельс.md** — raw: [[Эли Вельс]]
- **Ника Вельс.md** — raw: [[Ника Вельс]]

## Ссылки на ключевые страницы Арки 1
- Деревня: raw: [[Greenford__деревня]]
- Гостиница: raw: [[Лесная жизнь]]
- Сводка папки Greenford: `Golarion/Greenford/` (файла 00__SUMMARY.md не существует)

