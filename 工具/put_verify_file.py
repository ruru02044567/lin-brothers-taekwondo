# -*- coding: utf-8 -*-
"""把 Google 驗證檔放進網站並推上線。
用法：python 工具/put_verify_file.py googleXXXXXXXXXXXXXXXX.html
檔名可從 _gsc_verify_file.txt 自動讀取。
"""
import io, os, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')

if len(sys.argv) > 1:
    fname = sys.argv[1].strip()
else:
    p = os.path.join(ROOT, '_gsc_verify_file.txt')
    if not os.path.exists(p):
        print('沒有指定檔名，也找不到 _gsc_verify_file.txt')
        sys.exit(1)
    fname = io.open(p, encoding='utf-8').read().strip()

if not fname.startswith('google') or not fname.endswith('.html'):
    print('檔名格式不對:', fname)
    sys.exit(1)

# Google 驗證檔的內容就是這一行
content = 'google-site-verification: ' + fname

target = os.path.join(DOCS, fname)
io.open(target, 'w', encoding='utf-8').write(content)
print('已寫入:', target)
print('內容:', content)


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

code, out = run('git add docs/' + fname)
print('git add:', code, out[:100])
code, out = run('git commit -q -m "加上 Google Search Console 驗證檔"')
print('git commit:', code, out[:100])
code, out = run('git push -q origin main')
print('git push:', code, out[:150])

print('\n驗證檔網址（等 1 分鐘後生效）:')
print('https://ruru02044567.github.io/lin-brothers-taekwondo/' + fname)
