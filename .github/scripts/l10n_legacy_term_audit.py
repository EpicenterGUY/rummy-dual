from pathlib import Path
import re

text=Path('index.html').read_text()
terms=['SET','RUN','BURST','CHAIN','SWITCH','RUMMY','DETONATE','OVERLOAD','CORE','YOU','CPU','NEXT','TOTAL','FINAL CORE','SWITCH RALLY']
# Remove HTML/CSS/JS comments before scanning so developer notes do not count as player-facing copy.
clean=re.sub(r'<!--.*?-->','',text,flags=re.S)
clean=re.sub(r'/\*.*?\*/','',clean,flags=re.S)
# Extract quoted/template literals. This is an audit aid, not a JS parser; only print strings containing Korean,
# document title text, or explicit legacy display phrases so internal enum values stay out of the candidate list.
pat=re.compile(r"(?P<q>['\"`])(?P<body>(?:\\.|(?!\1).)*?)(?P=q)",re.S)
seen=[]
for m in pat.finditer(clean):
    body=m.group('body')
    rendered=re.sub(r'\$\{[^}]*\}','',body)
    hits=[t for t in terms if re.search(rf'(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])',rendered)]
    if not hits: continue
    if not re.search(r'[가-힣]',rendered) and not any(x in rendered for x in ['FINAL CORE','SWITCH RALLY']):
        continue
    line=clean.count('\n',0,m.start())+1
    key=(line,rendered,hits)
    if key not in seen: seen.append(key)
for line,body,hits in seen:
    body=' '.join(body.split())
    if len(body)>260: body=body[:257]+'...'
    print(f'{line}: [{", ".join(hits)}] {body}')
print(f'LEGACY_CANDIDATES={len(seen)}')
