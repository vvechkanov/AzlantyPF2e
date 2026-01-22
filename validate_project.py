#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Валидатор проекта AzlantyPF2e
Проверяет, что все SUMMARY файлы содержат корректные ссылки на все файлы в соответствующих директориях
"""

import os
import re
import urllib.parse
import urllib.request
import urllib.error
import sys
import argparse
from pathlib import Path

# Глобальный флаг: проверять доступность raw URL (сетевые запросы).
# По умолчанию выключено: это медленно и может флапать из-за сети/лимитов.
CHECK_URLS = False

# Устанавливаем кодировку для Windows
if sys.platform == 'win32':
    import codecs
    import locale
    # Получаем системную локаль и устанавливаем UTF-8
    try:
        locale.setlocale(locale.LC_ALL, 'Russian_Russia.UTF8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF8')
        except locale.Error:
            pass
    
    # Перенаправляем stdout/stderr в UTF-8
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

def check_url_accessibility(url):
    """Проверяет доступность URL в сети"""
    try:
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status == 200
    except urllib.error.HTTPError as e:
        return False
    except urllib.error.URLError as e:
        return False
    except Exception as e:
        return False

def list_markdown_files(base_path):
    md_files = []
    for root, _, files in os.walk(base_path):
        for name in files:
            if name.endswith('.md'):
                md_files.append(os.path.join(root, name))
    return md_files

def strip_obisidian_links_and_code(text):
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]*`', '', text)
    text = re.sub(r'\[\[[^\]]+\]\]', '', text)
    return text

def build_note_basename_index(base_path):
    """Index markdown files by their basename (without .md)."""
    idx = {}
    for fp in list_markdown_files(base_path):
        name = os.path.splitext(os.path.basename(fp))[0]
        idx.setdefault(name, []).append(fp)
    return idx

def parse_glossary_entries(glossary_path):
    if not os.path.exists(glossary_path):
        return []

    with open(glossary_path, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = []
    for line in content.splitlines():
        if not line.lstrip().startswith('- **'):
            continue

        m_term = re.search(r'-\s*\*\*([^*]+)\*\*', line)
        if not m_term:
            continue
        term = m_term.group(1).strip()

        aliases = []
        m_alias = re.search(r'\*\(([^)]+)\)\*', line)
        if m_alias:
            aliases = [a.strip() for a in m_alias.group(1).split(',') if a.strip()]

        m_local = re.search(r'local:\s*\[\[([^\]|]+)', line)
        target = m_local.group(1).strip() if m_local else None

        tokens = [term] + aliases
        entries.append({
            'term': term,
            'aliases': aliases,
            'tokens': tokens,
            'target': target,
        })

    return entries

def parse_npc_names(npc_dir):
    names = []
    if not os.path.isdir(npc_dir):
        return names

    for name in os.listdir(npc_dir):
        if not name.endswith('.md'):
            continue
        if name.startswith('00__SUMMARY'):
            continue
        if name in ('00__TEMPLATE.md', '00__NPC_без_портретов.md'):
            continue
        names.append(os.path.splitext(name)[0])
    return sorted(names)

def find_unlinked_token_occurrences(file_path, tokens):
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_lines = f.read().splitlines()

    matches = []
    for idx, line in enumerate(raw_lines, start=1):
        if not tokens:
            continue
        stripped_line = line.strip()

        # Не требуем ссылок в raw-строках (там URL и служебные индексы)
        if 'raw:' in stripped_line.lower():
            continue
        # И не требуем ссылок в markdown-raw ссылках (иначе токены ловятся внутри URL)
        if 'raw.githubusercontent.com' in stripped_line.lower():
            continue
        if stripped_line.startswith('```'):
            continue

        # Не требуем ссылок внутри заголовков (там обычно естественные названия)
        if stripped_line.startswith('#'):
            continue

        # Не требуем ссылок в строках-якорях/тегах (#tag), где это мешает поиску.
        if '#' in stripped_line and stripped_line.lstrip().startswith('-'):
            # типичный формат anchors: "- #tag1 #tag2"
            continue

        # Не требуем ссылок внутри HTML-кусков (Obsidian wikilinks там нестабильны)
        if '<' in stripped_line and '>' in stripped_line:
            continue

        stripped = strip_obisidian_links_and_code(line)
        for token in tokens:
            if not token:
                continue

            # Границы токена: чтобы не ловить подстроки внутри других слов.
            # Учитываем кириллицу и латиницу.
            token_re = re.compile(
                r'(?<![0-9A-Za-zА-Яа-яЁё_])' + re.escape(token) + r'(?![0-9A-Za-zА-Яа-яЁё_])'
            )
            if token_re.search(stripped):
                matches.append((idx, token, stripped_line))
    return matches

def validate_crosslinks(base_path):
    errors = []
    warnings = []

    npc_dir = os.path.join(base_path, 'NPC')
    glossary_path = os.path.join(base_path, 'Glossary', '00__GLOSSARY.md')

    npc_names = parse_npc_names(npc_dir)
    glossary_entries = parse_glossary_entries(glossary_path)
    note_index = build_note_basename_index(base_path)

    # Список каноничных страниц глоссария, внутри которых не требуем ссылок на сам термин
    glossary_target_paths = set()
    for e in glossary_entries:
        target = e.get('target')
        if not target:
            continue
        for fp in note_index.get(target, []):
            glossary_target_paths.add(os.path.normpath(fp))

    md_files = list_markdown_files(base_path)

    max_reports = 200
    report_count = 0

    for fp in md_files:
        rel = os.path.relpath(fp, base_path)
        if rel.startswith('NPC' + os.sep):
            continue
        if rel.startswith('Glossary' + os.sep):
            continue

        norm_fp = os.path.normpath(fp)

        for line_no, token, line in find_unlinked_token_occurrences(fp, npc_names):
            errors.append(f"NPC без obsidian-ссылки '{token}' в {rel}:{line_no}: {line}")
            report_count += 1
            if report_count >= max_reports:
                errors.append(f"(дальше не показываем, лимит {max_reports} совпадений)")
                return errors, warnings

        for entry in glossary_entries:
            target = entry.get('target')
            tokens = entry.get('tokens') or []
            if not target:
                continue

            # Не требуем, чтобы термин сам себя линковал внутри своей каноничной страницы
            if norm_fp in glossary_target_paths:
                continue

            for line_no, token, line in find_unlinked_token_occurrences(fp, tokens):
                errors.append(
                    f"Glossary без obsidian-ссылки '{token}' (target '{target}') в {rel}:{line_no}: {line}"
                )
                report_count += 1
                if report_count >= max_reports:
                    errors.append(f"(дальше не показываем, лимит {max_reports} совпадений)")
                    return errors, warnings

    return errors, warnings

def should_skip_crosslink_line(stripped_line):
    if stripped_line.startswith('```'):
        return True
    if stripped_line.startswith('#'):
        return True
    if 'raw:' in stripped_line.lower():
        return True
    if 'raw.githubusercontent.com' in stripped_line.lower():
        return True
    if '#' in stripped_line and stripped_line.lstrip().startswith('-'):
        return True
    if '<' in stripped_line and '>' in stripped_line:
        return True
    return False

def autofix_crosslinks_in_line(line, npc_names, glossary_entries):
    stripped_line = line.strip()
    if should_skip_crosslink_line(stripped_line):
        return line

    # Никогда не трогаем строки с обратными кавычками: там часто имена файлов и raw-индексы,
    # и автофикс ломает `Имя файла.md`.
    if '`' in line:
        return line

    if '[[`' in line:
        return line

    updated = line

    npc_tokens = sorted([n for n in npc_names if n], key=len, reverse=True)
    for token in npc_tokens:
        token_re = re.compile(
            r'(?<!\[\[)(?<![0-9A-Za-zА-Яа-яЁё_])' + re.escape(token) + r'(?![0-9A-Za-zА-Яа-яЁё_])(?!\]\])'
        )
        updated = token_re.sub(f'[[{token}]]', updated)

    glossary_items = []
    for entry in glossary_entries:
        target = entry.get('target')
        if not target:
            continue
        for t in entry.get('tokens') or []:
            if t:
                glossary_items.append((t, target))

    glossary_items.sort(key=lambda x: len(x[0]), reverse=True)
    for token, target in glossary_items:
        token_re = re.compile(
            r'(?<!\[\[)(?<![0-9A-Za-zА-Яа-яЁё_])' + re.escape(token) + r'(?![0-9A-Za-zА-Яа-яЁё_])(?!\]\])'
        )
        if token == target:
            repl = f'[[{target}]]'
        else:
            repl = f'[[{target}|{token}]]'
        updated = token_re.sub(repl, updated)

    return updated

def autofix_crosslinks(base_path):
    errors = []
    npc_dir = os.path.join(base_path, 'NPC')
    glossary_path = os.path.join(base_path, 'Glossary', '00__GLOSSARY.md')

    npc_names = parse_npc_names(npc_dir)
    glossary_entries = parse_glossary_entries(glossary_path)

    md_files = list_markdown_files(base_path)
    for fp in md_files:
        rel = os.path.relpath(fp, base_path)
        if rel.startswith('Glossary' + os.sep):
            continue
        if os.path.basename(fp) == '00__GLOSSARY.md':
            continue

        try:
            with open(fp, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines(True)
        except UnicodeDecodeError:
            continue

        in_fence = False
        changed = False
        out_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('```'):
                in_fence = not in_fence
                out_lines.append(line)
                continue
            if in_fence:
                out_lines.append(line)
                continue

            new_line = autofix_crosslinks_in_line(line, npc_names, glossary_entries)
            if new_line != line:
                changed = True
            out_lines.append(new_line)

        if changed:
            with open(fp, 'w', encoding='utf-8', newline='') as f:
                f.writelines(out_lines)

    return errors

def get_files_in_directory(directory_path):
    """Возвращает список .md файлов в директории, исключая SUMMARY файлы"""
    files = []
    if os.path.exists(directory_path):
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path) and item.endswith('.md') and not item.startswith('00__SUMMARY'):
                files.append(item)
    return sorted(files)

def extract_links_from_summary(summary_path):
    """Извлекает ссылки на файлы из SUMMARY файла"""
    if not os.path.exists(summary_path):
        return []
    
    with open(summary_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем строки вида - `filename.md` — description (с пробелом после дефиса)
    links = []
    pattern = r'-\s*`([^`]*\.md)`'
    matches = re.findall(pattern, content)
    
    for match in matches:
        links.append(match)
    
    return links

def generate_raw_url(base_path, relative_path):
    """Генерирует raw URL для GitHub"""
    # Преобразуем путь в URL-формат, заменяя \ на /
    github_base = "https://raw.githubusercontent.com/vvechkanov/AzlantyPF2e/master/"
    # Нормализуем путь для URL (заменяем \ на /)
    normalized_path = relative_path.replace('\\', '/')
    encoded_path = urllib.parse.quote(normalized_path)
    return github_base + encoded_path

def extract_subdirectories_from_summary(summary_path):
    """Извлекает ссылки на поддиректории из SUMMARY файла"""
    if not os.path.exists(summary_path):
        return []
    
    with open(summary_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем строки вида - `Папка/` — description
    subdirs = []
    pattern = r'-\s*`([^`]+/)`'
    matches = re.findall(pattern, content)
    
    for match in matches:
        subdirs.append(match.rstrip('/'))
    
    return subdirs

def extract_raw_urls_from_summary(summary_path):
    """Извлекает raw URL из SUMMARY файла"""
    if not os.path.exists(summary_path):
        return []
    
    with open(summary_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем raw URL (поддерживаем оба формата: с refs/heads/master и без).
    # Важно: URL может быть как "raw: https://...", так и "raw: [RAW](https://...)".
    # Также поддерживаем отступы перед "raw:" для формата в NPC файлах
    # И формат "→ [raw](https://...)" для Assistant Guides
    pattern1 = r'^\s*-?\s*raw:\s*(?:\[[^\]]+\]\()?)(https://raw\.githubusercontent\.com/vvechkanov/AzlantyPF2e/(?:refs/heads/)?master/[^\s\)]+)'
    pattern2 = r'→\s*\s*\[raw\]\((https://raw\.githubusercontent\.com/vvechkanov/AzlantyPF2e/(?:refs/heads/)?master/[^\s\)]+)'
    
    matches1 = re.findall(pattern1, content, re.MULTILINE)
    matches2 = re.findall(pattern2, content, re.MULTILINE)
    
    # Объединяем результаты
    raw_urls = matches1 + matches2
    
    return raw_urls

def extract_file_raw_urls_from_summary(summary_path):
    """Извлекает raw URL для файлов из SUMMARY файла.

    Важно: исключаем raw-ссылки, которые относятся к подпапкам (строки с `Папка/`).
    Возвращает список URL в том же порядке, что и extract_links_from_summary().
    """
    if not os.path.exists(summary_path):
        return []

    with open(summary_path, 'r', encoding='utf-8') as f:
        content = f.read()

    file_links = extract_links_from_summary(summary_path)
    urls_by_file = {}

    # Ищем raw URL во всем содержимом файла, а не только рядом с именами файлов
    # Поддерживаем форматы: "raw: [RAW](url)", "raw: url", "  - raw: [RAW](url)", "→ [raw](url)"
    pattern1 = r'^\s*-?\s*raw:\s*(?:\[[^\]]+\]\()?(https://raw\.githubusercontent\.com/vvechkanov/AzlantyPF2e/(?:refs/heads/)?master/[^\s\)]+)'
    pattern2 = r'→\s*\s*\[raw\]\((https://raw\.githubusercontent\.com/vvechkanov/AzlantyPF2e/(?:refs/heads/)?master/[^\s\)]+)'
    
    raw_pattern1 = re.compile(pattern1, re.MULTILINE)
    raw_pattern2 = re.compile(pattern2, re.MULTILINE)
    
    # Находим все совпадения для обоих шаблонов
    matches1 = raw_pattern1.finditer(content)
    matches2 = raw_pattern2.finditer(content)
    
    # Проходим по всем найденным raw ссылкам
    for match in list(matches1) + list(matches2):
        # Выбираем подходящую группу
        raw_url = match.group(1)
        
        if not raw_url:
            continue
        
        # Пробуем найти имя файла в URL
        filename_match = re.search(r'/([^/]+\.md)$', raw_url)
        if filename_match:
            filename = filename_match.group(1)
            # Декодируем URL-encoded имя файла
            decoded_filename = urllib.parse.unquote(filename)
            
            # Ищем соответствующий файл в списке файлов (без расширения .md)
            for file_link in file_links:
                if file_link.replace('.md', '') == decoded_filename.replace('.md', ''):
                    urls_by_file[file_link] = raw_url
                    break

    return [urls_by_file.get(f) for f in file_links if urls_by_file.get(f)]

def extract_subdirectory_raw_urls(summary_path):
    """Извлекает raw URL для поддиректорий из SUMMARY файла.

    Поддерживаем:
    - 2-строчный формат (каноничный):
        - `Папка/` — описание
          - raw: [RAW](https://...)
    - 1-строчный legacy формат:
        - `Папка/` — raw: https://...

    Возвращает dict: { "Папка": "https://..." } (без слэша на конце).
    """
    if not os.path.exists(summary_path):
        return {}

    with open(summary_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    urls_by_subdir = {}

    # 1-строчный legacy формат: - `Папка/` — ... raw: (https://...)
    one_line_re = re.compile(
        r'^\s*-\s*`([^`]+/)`\s*—.*?\braw:\s*(?:\[[^\]]+\]\()?(https://raw\.githubusercontent\.com/vvechkanov/AzlantyPF2e/(?:refs/heads/)?master/[^\s\)]+)',
        re.IGNORECASE,
    )

    # Строка-объявление подпапки: - `Папка/` — описание
    subdir_line_re = re.compile(r'^\s*-\s*`([^`]+/)`')

    # Raw-строка:   - raw: [RAW](https://...)
    raw_line_re = re.compile(
        r'^\s*-\s*raw:\s*(?:\[[^\]]+\]\()?(https://raw\.githubusercontent\.com/vvechkanov/AzlantyPF2e/(?:refs/heads/)?master/[^\s\)]+)',
        re.IGNORECASE,
    )

    current_subdir = None
    for line in lines:
        m_one = one_line_re.match(line)
        if m_one:
            subdir = m_one.group(1).rstrip('/')
            url = m_one.group(2)
            urls_by_subdir[subdir] = url
            current_subdir = None
            continue

        m_subdir = subdir_line_re.match(line)
        if m_subdir:
            current_subdir = m_subdir.group(1).rstrip('/')
            continue

        if current_subdir:
            m_raw = raw_line_re.match(line)
            if m_raw:
                urls_by_subdir[current_subdir] = m_raw.group(1)
                current_subdir = None

    return urls_by_subdir

def validate_directory(directory_path, relative_path=""):
    """Валидирует директорию и её SUMMARY файл"""
    errors = []
    warnings = []
    
    summary_path = os.path.join(directory_path, '00__SUMMARY.md')
    
    # Проверяем существование SUMMARY файла
    if not os.path.exists(summary_path):
        errors.append(f"Отсутствует SUMMARY файл: {summary_path}")
        return errors, warnings
    
    # Получаем список файлов в директории
    actual_files = get_files_in_directory(directory_path)
    
    # Получаем список поддиректорий
    actual_subdirs = []
    if os.path.exists(directory_path):
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                actual_subdirs.append(item)
    
    # Получаем ссылки из SUMMARY
    summary_links = extract_links_from_summary(summary_path)
    
    # Получаем ссылки на поддиректории из SUMMARY
    summary_subdirs = extract_subdirectories_from_summary(summary_path)
    
    # Получаем raw URL из SUMMARY (только для файлов, не для директорий)
    raw_urls = extract_file_raw_urls_from_summary(summary_path)
    
    # Проверяем, что все файлы в директории упомянуты в SUMMARY
    for file in actual_files:
        if file not in summary_links:
            errors.append(f"Файл '{file}' отсутствует в SUMMARY: {summary_path}")
    
    # Проверяем, что все ссылки в SUMMARY соответствуют существующим файлам
    for link in summary_links:
        if link not in actual_files:
            errors.append(f"В SUMMARY указан несуществующий файл '{link}': {summary_path}")
    
    # Проверяем, что все поддиректории упомянуты в SUMMARY
    for subdir in actual_subdirs:
        if subdir not in summary_subdirs:
            errors.append(f"Поддиректория '{subdir}/' отсутствует в SUMMARY: {summary_path}")
    
    # Проверяем, что все ссылки на поддиректории в SUMMARY соответствуют существующим директориям
    for subdir in summary_subdirs:
        if subdir not in actual_subdirs:
            errors.append(f"В SUMMARY указана несуществующая поддиректория '{subdir}/': {summary_path}")
    
    # Проверяем количество raw URL (только для файлов, не для директорий)
    if len(raw_urls) != len(actual_files):
        warnings.append(f"Количество raw URL ({len(raw_urls)}) не соответствует количеству файлов ({len(actual_files)}): {summary_path}")
    
    # Проверяем корректность raw URL
    urls_by_file = dict(zip(summary_links, raw_urls))
    for file in summary_links:
        url = urls_by_file.get(file)
        if not url:
            warnings.append(f"Отсутствует raw URL для '{file}': {summary_path}")
            continue

        expected_url = generate_raw_url("", os.path.join(relative_path, file))
        # Нормализуем URL для сравнения (убираем refs/heads/master если есть)
        normalized_url = url.replace('refs/heads/master/', 'master/')
        if normalized_url != expected_url:
            warnings.append(f"Некорректный raw URL для '{file}': {url}")
            warnings.append(f"   Ожидается: {expected_url}")

        # Проверяем доступность URL в сети (опционально, может быть медленно/флапать)
        if CHECK_URLS:
            print(f"Проверка доступности: {file}...", end=' ')
            if check_url_accessibility(url):
                print("✓ Доступно")
            else:
                print("✗ Недоступно")
                errors.append(f"Raw URL недоступен: {url}")
    
    # Проверяем raw URL для поддиректорий (по аналогии с файлами)
    subdir_urls_by_name = extract_subdirectory_raw_urls(summary_path)
    if len(subdir_urls_by_name) != len(summary_subdirs):
        warnings.append(
            f"Количество raw URL для поддиректорий ({len(subdir_urls_by_name)}) "
            f"не соответствует количеству поддиректорий ({len(summary_subdirs)}): {summary_path}"
        )

    for subdir in summary_subdirs:
        url = subdir_urls_by_name.get(subdir)
        if not url:
            warnings.append(f"Отсутствует raw URL для поддиректории '{subdir}/': {summary_path}")
            continue

        expected_url = generate_raw_url("", os.path.join(relative_path, subdir, "00__SUMMARY.md"))
        normalized_url = url.replace('refs/heads/master/', 'master/')
        if normalized_url != expected_url:
            warnings.append(f"Некорректный raw URL для поддиректории '{subdir}/': {url}")
            warnings.append(f"   Ожидается: {expected_url}")

        if CHECK_URLS:
            print(f"Проверка доступности: {subdir}/...", end=' ')
            if check_url_accessibility(url):
                print("✓ Доступно")
            else:
                print("✗ Недоступно")
                errors.append(f"Raw URL для поддиректории недоступен: {url}")
    
    # Рекурсивно проверяем поддиректории
    if os.path.exists(directory_path):
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                sub_errors, sub_warnings = validate_directory(item_path, os.path.join(relative_path, item))
                errors.extend(sub_errors)
                warnings.extend(sub_warnings)
    
    return errors, warnings

def main():
    """Основная функция валидации"""
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        '--path',
        default=None,
        help='Путь к корню проекта (по умолчанию папка рядом со скриптом)',
    )
    parser.add_argument('--fix', action='store_true')
    parser.add_argument(
        '--check-urls',
        action='store_true',
        help='Проверять доступность raw URL (сетевые запросы, может быть медленно)',
    )
    args = parser.parse_args()

    # По умолчанию валидируем репозиторий, где лежит этот скрипт.
    base_path = args.path or str(Path(__file__).resolve().parent)

    global CHECK_URLS
    CHECK_URLS = bool(args.check_urls)

    if args.fix:
        autofix_crosslinks(base_path)

    print("Валидация проекта AzlantyPF2e")
    print("=" * 50)
    
    errors = []
    warnings = []

    # Валидируем все подпапки, которые являются контентными ветками (имеют 00__SUMMARY.md).
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            summary_path = os.path.join(item_path, '00__SUMMARY.md')
            if os.path.exists(summary_path):
                sub_errors, sub_warnings = validate_directory(item_path, item)
                errors.extend(sub_errors)
                warnings.extend(sub_warnings)

    cross_errors, cross_warnings = validate_crosslinks(base_path)
    errors.extend(cross_errors)
    warnings.extend(cross_warnings)
    
    if not errors and not warnings:
        print("Все проверки пройдены успешно!")
    else:
        if errors:
            print(f"\nОшибки ({len(errors)}):")
            for error in errors:
                print(f"  {error}")
        
        if warnings:
            print(f"\nПредупреждения ({len(warnings)}):")
            for warning in warnings:
                print(f"  {warning}")
    
    print(f"\nИтог: {len(errors)} ошибок, {len(warnings)} предупреждений")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
