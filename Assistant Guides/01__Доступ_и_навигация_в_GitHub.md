# 01 — Доступ и навигация в GitHub (для ассистента)

Обновлено: 2026-01-11

GitHub используется **только для ассистента** как read-only источник текста.
Obsidian — основное место для человека.

## Что читать первым
1) `AZL__00_ACCESS.md` (в Project Files) — даёт ссылку на индекс.
2) `AZL_ASSISTANT_INDEX.md` (в GitHub) — *bootloader*: очень короткий, стабильный.
3) Root `00__SUMMARY.md` (в GitHub) — навигация по дереву.

## RAW-ссылки
Ассистент должен читать **raw**, а не `blob`:
- ✅ `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>/<file>.md`
- ❌ `https://github.com/<owner>/<repo>/blob/<branch>/<path>/<file>.md`

> [!important]- Про токены
> Не использовать ссылки вида `...?token=...`. Для публичного чтения токены не нужны.

## Index vs Root Summary — в двух строках
- **AZL_ASSISTANT_INDEX.md** — короткий “загрузчик”: ссылка на root summary + codes + 5–10 глобальных якорей.
- **Root 00__SUMMARY.md** — реальная карта дерева: подпапки/файлы “на уровень вниз” с описаниями и ссылками.

## Как ассистент “ходит по дереву”
1) Открыть индекс → перейти в root summary.
2) В root summary найти нужную ветку → открыть её summary.
3) В summary ветки открыть целевой файл по raw-ссылке.

## Если нет ссылок в Summary
Есть резервный путь: GitHub Contents API (листинг папки) и `download_url`.
Но **цель проекта** — чтобы summary сами содержали raw-ссылки на перечисленные файлы.
