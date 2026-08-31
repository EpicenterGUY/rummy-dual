from pathlib import Path
import re
s=Path('index.html').read_text()
start=s.index('const NAMED={')
end=s.index('const UNLOCK_GROUPS=', start)
block=s[start:end]
pat=re.compile(r"'([^']+)':\{[^\n]*?n:'([^']*)'[^\n]*?d:'([^']*)'", re.M)
rows=pat.findall(block)
print('NAMED_COUNT',len(rows))
terms=['SWITCH','DETONATE','CORE','SET','RUN','RUMMY','CHAIN','BURST','CPU','YOU','TOTAL','NEXT','OVERLOAD']
for cid,name,desc in rows:
    hit=[t for t in terms if t in desc]
    latin=re.findall(r'(?<![A-Za-z])[A-Za-z][A-Za-z0-9+/-]*(?:\s+[A-Za-z][A-Za-z0-9+/-]*)*',desc)
    if hit or latin:
        print(f'{cid}\t{name}\tTERMS={hit}\tLATIN={latin}\t{desc}')
print('--- ENDING AUDIT ---')
from collections import Counter
c=Counter()
for _,_,d in rows:
    if d.endswith('다.'): c['다.']+=1
    elif d.endswith('음.'): c['음.']+=1
    elif d.endswith('함.'): c['함.']+=1
    else: c['other']+=1
print(c)
