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
    sentences=[x.strip() for x in desc.split('.') if x.strip()]
    fragment=any(not seg.endswith('다') for seg in sentences)
    shorthand=(' + ' in desc or re.search(r'(?<!\d)\+\d',desc) is not None)
    grammar=any(x in desc for x in ('폭발를','세트을','세트과'))
    if fragment or shorthand or grammar:
        print(f'{cid}\t{name}\tFRAGMENT={fragment}\tSHORTHAND={shorthand}\tGRAMMAR={grammar}\t{desc}')
