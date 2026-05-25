"""
Split archive .md files into HTML entry fragments and upload to server.
Source of truth: the .md files on disk.
Run: $env:PYTHONIOENCODING="utf-8"; python C:\AI-assistant\split_archive_v2.py
"""
import re, os, paramiko

# === CONFIG ===
LOCAL_BASE = r"C:\DND\sync\Sync\Obsidian\PF2e\Кампейны\Азланти\archive"
LOCAL_ENTRIES = os.path.join(LOCAL_BASE, "entries")
REMOTE_BASE = "/home/ubuntu/foundryuserdata/Data/azlanti/archive"
SERVER = "129.151.213.102"
SSH_KEY = r"C:\AI-assistant\music-downloading\11.ppk"

md_sources = [
    (r"C:\DND\sync\Sync\Obsidian\PF2e\Кампейны\Азланти\Sessions\Session0\ПС2_архив 1.md", "report1", [
        ("01_hartwik.html", "Запись первая"),
        ("02_zabor.html", "Запись вторая"),
        ("03_doroga.html", "Запись третья"),
        ("04_greenford.html", "Запись четвёртая"),
        ("05_pauk.html", "Запись пятая"),
        ("06_gvozd.html", "Запись шестая"),
        ("07_itogo.html", "Запись седьмая"),
    ]),
    (r"C:\DND\sync\Sync\Obsidian\PF2e\Кампейны\Азланти\Sessions\Session1\ПС1_архив.md", "report2", [
        ("01_shestaya.html", "Запись четвёртая"),
        ("02_operaciya.html", "Запись пятая"),
        ("03_posle_boya.html", "Запись шестая"),
        ("04_tri_obezyany.html", "Запись седьмая"),
    ]),
]

# === CONVERTER ===
def para_to_html(para, is_first):
    para = para.strip()
    if not para:
        return None
    if para.startswith('>') or para == '---' or para.startswith('**'):
        return None
    if para.startswith('*НС-0774-КА') or para.startswith('*[Конец'):
        inner = para.strip('*').strip()
        if 'НС-0774-КА' in inner:
            return '<div class="signature">НС-0774-КА, полевой наблюдатель<br>Скрипторий Боньярда</div>'
        return None
    if para.startswith('*(') and para.endswith(')*'):
        inner = para[2:-2].strip()
        return f'<div class="observer-note">{inner}</div>'
    cls = ' class="no-indent"' if is_first else ''
    return f'<p{cls}>{para}</p>'

def section_to_html(section_body):
    paragraphs = re.split(r'\n\s*\n', section_body)
    html_parts = []
    is_first = True
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        result = para_to_html(para, is_first)
        if result:
            html_parts.append(result)
            if not result.startswith('<div'):
                is_first = False
    return '\n\n'.join(html_parts)

# === STEP 1: Generate HTML fragments locally ===
print("=== Generating HTML entries ===")
for md_path, report_id, entries in md_sources:
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    sections = re.split(r'\n## ', content)
    for filename, title_prefix in entries:
        found = False
        for section in sections:
            if section.strip().startswith(title_prefix):
                lines = section.split('\n', 1)
                body = lines[1] if len(lines) > 1 else ''
                html = section_to_html(body)
                out_path = os.path.join(LOCAL_ENTRIES, report_id, filename)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, 'w', encoding='utf-8') as fh:
                    fh.write(html)
                print(f"  OK: {report_id}/{filename}")
                found = True
                break
        if not found:
            print(f"  MISS: {filename} ('{title_prefix}')")

# === STEP 2: Upload everything to server ===
print("\n=== Uploading to server ===")
key = paramiko.RSAKey.from_private_key_file(SSH_KEY)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, username="ubuntu", pkey=key)
sftp = ssh.open_sftp()

# Ensure remote dirs exist
for d in [REMOTE_BASE, f"{REMOTE_BASE}/entries",
          f"{REMOTE_BASE}/entries/report1", f"{REMOTE_BASE}/entries/report2"]:
    try:
        sftp.stat(d)
    except FileNotFoundError:
        ssh.exec_command(f"mkdir -p {d}")
        print(f"  mkdir: {d}")

# Upload all files from local archive/
uploaded = 0
for root, dirs, files in os.walk(LOCAL_BASE):
    for fname in files:
        local_path = os.path.join(root, fname)
        rel = os.path.relpath(local_path, LOCAL_BASE).replace("\\", "/")
        remote_path = f"{REMOTE_BASE}/{rel}"
        sftp.put(local_path, remote_path)
        uploaded += 1
        print(f"  -> {rel}")

sftp.close()
ssh.close()
print(f"\nDone! {uploaded} files uploaded.")
print(f"URL: https://vlad-vechkanov.link/azlanti/archive/")
