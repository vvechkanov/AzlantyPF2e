#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Валидатор проекта AzlantyPF2e
Проверяет, что все SUMMARY файлы содержат корректные ссылки на все файлы в соответствующих директориях
"""

import os
import re
import urllib.parse
import sys
from pathlib import Path

# Устанавливаем кодировку для Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

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
    
    # Ищем строки вида - `filename.md` — description
    links = []
    pattern = r'-\s*`([^`]+\.md)`'
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
    
    # Ищем raw URL (поддерживаем оба формата: с refs/heads/master и без)
    pattern = r'raw:\s*(https://raw\.githubusercontent\.com/vvechkanov/AzlantyPF2e/(?:refs/heads/)?master/[^\s]+)'
    matches = re.findall(pattern, content)
    
    return matches

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
    
    # Получаем raw URL из SUMMARY
    raw_urls = extract_raw_urls_from_summary(summary_path)
    
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
    for i, (file, url) in enumerate(zip(summary_links, raw_urls)):
        expected_url = generate_raw_url("", os.path.join(relative_path, file))
        # Нормализуем оба URL для сравнения (убираем refs/heads/master если есть)
        normalized_url = url.replace('refs/heads/master/', 'master/')
        if normalized_url != expected_url:
            warnings.append(f"Некорректный raw URL для '{file}': {url}")
            warnings.append(f"   Ожидается: {expected_url}")
    
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
    base_path = r"c:\DND\sync\Sync\Obsidian\PF2e\Кампейны\Азланти\Сюжет кампании"
    
    print("Валидация проекта AzlantyPF2e")
    print("=" * 50)
    
    errors, warnings = validate_directory(base_path, "Сюжет кампании")
    
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
