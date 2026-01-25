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
- **Гаррен Кинсуик.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%93%D0%B0%D1%80%D1%80%D0%B5%D0%BD%20%D0%9A%D0%B8%D0%BD%D1%81%D1%83%D0%B8%D0%BA.md)
- **Освальд Меррик.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%9E%D1%81%D0%B2%D0%B0%D0%BB%D1%8C%D0%B4%20%D0%9C%D0%B5%D1%80%D1%80%D0%B8%D0%BA.md)
- **Курзаир.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%9A%D1%83%D1%80%D0%B7%D0%B0%D0%B8%D1%80.md)
- **Варх Кет.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%92%D0%B0%D1%80%D1%85%20%D0%9A%D0%B5%D1%82.md)
- **Иш Сарра.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%98%D1%88%20%D0%A1%D0%B0%D1%80%D1%80%D0%B0.md)
- **Лиш Тен.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%9B%D0%B8%D1%88%20%D0%A2%D0%B5%D0%BD.md)
- **Сай Мор.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%A1%D0%B0%D0%B9%20%D0%9C%D0%BE%D1%80.md)
- **Керрен Тар-Крыло.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%9A%D0%B5%D1%80%D1%80%D0%B5%D0%BD%20%D0%A2%D0%B0%D1%80-%D0%9A%D1%80%D1%8B%D0%BB%D0%BE.md)
- **Марна Вельс.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%9C%D0%B0%D1%80%D0%BD%D0%B0%20%D0%92%D0%B5%D0%BB%D1%8C%D1%81.md)
- **Риан Вельс.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%A0%D0%B8%D0%B0%D0%BD%20%D0%92%D0%B5%D0%BB%D1%8C%D1%81.md)
- **Эли Вельс.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%AD%D0%BB%D0%B8%20%D0%92%D0%B5%D0%BB%D1%8C%D1%81.md)
- **Ника Вельс.md** — raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/NPC/%D0%9D%D0%B8%D0%BA%D0%B0%20%D0%92%D0%B5%D0%BB%D1%8C%D1%81.md)

## Ссылки на ключевые страницы Арки 1
- Деревня: raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/Golarion/Greenford/Greenford__%D0%B4%D0%B5%D1%80%D0%B5%D0%B2%D0%BD%D1%8F.md)
- Гостиница: raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/Golarion/Greenford/%D0%9B%D0%B5%D1%81%D0%BD%D0%B0%D1%8F%20%D0%B6%D0%B8%D0%B7%D0%BD%D1%8C.md)
- Сводка папки Greenford: raw: [RAW](https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/Golarion/Greenford/00__SUMMARY.md)

