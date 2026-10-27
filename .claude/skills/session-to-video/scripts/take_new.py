# -*- coding: utf-8 -*-
import glob, os, sys, subprocess
D=r"C:\Users\vechk\Downloads"; T=r"C:\Azlanti\Video\Session0\02__Жульничество\audio\_дубли_2026-10-11"
done=os.path.join(T,"_принято.txt"); seen=open(done,encoding="utf-8").read().split("\n") if os.path.exists(done) else []
fs=sorted(glob.glob(os.path.join(D,"ElevenLabs_2026-10-1*_Носой 3_gen_*.mp3")), key=os.path.getmtime)
n=int(open(os.path.join(T,"_счётчик.txt")).read())+1
import re
stamp=lambda b: re.search(r"T(\d\d_\d\d_\d\d)",b).group(1)
have={stamp(x) for x in seen if x}
for f in fs:
    b=os.path.basename(f)
    if b in seen: continue
    if stamp(b) in have: seen.append(b); continue      # повторное скачивание того же файла
    have.add(stamp(b))
    subprocess.run([sys.executable,"add_take.py",str(n),f,"--text"]); seen.append(b); n+=1
open(done,"w",encoding="utf-8").write("\n".join(x for x in seen if x)+"\n")
