from pathlib import Path
import re
s=Path('index.html').read_text()
start=s.index('const NAMED={')
end=s.index('const UNLOCK_GROUPS=', start)
block=s[start:end]
pat=re.compile(r"'([^']+)':\{[^\n]*?n:'([^']*)'[^\n]*?d:'((?:\\'|[^'])*)'", re.M)
rows=pat.findall(block)
print('NAMED_ROWS',len(rows))
for cid,name,desc in rows:
    if not desc.endswith('다.'):
        print(f'{cid}\t{name}\t{desc}')
