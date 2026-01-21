# Исправление валидатора
content = open(r'c:\DND\sync\Sync\Obsidian\PF2e\Кампейны\Азланти\validate_project.py', 'r', encoding='utf-8').read()
content = content.replace(
    "pattern2 = r'→\\s*\\[raw\\]\\((https://raw\\.githubusercontent\\.com/vvechkanov/AzlantyPF2e/(?:refs/heads/)?master/[^\\s\\)]+)'",
    "pattern2 = r'→\\s*\\s*\\[raw\\]\\((https://raw\\.githubusercontent\\.com/vvechkanov/AzlantyPF2e/(?:refs/heads/)?master/[^\\s\\)]+)'"
)
open(r'c:\DND\sync\Sync\Obsidian\PF2e\Кампейны\Азланти\validate_project.py', 'w', encoding='utf-8').write(content)
print("Исправлено!")
