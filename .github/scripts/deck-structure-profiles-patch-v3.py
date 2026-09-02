from pathlib import Path
import runpy

runpy.run_path('.github/scripts/deck-structure-profiles-patch-v2.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')
replacements=[
    ('같은 카드군도 SET형·RUN형·혼합형으로 다르게 굴릴 수 있습니다.','같은 카드군도 세트형·런형·혼합형으로 다르게 굴릴 수 있습니다.'),
    ('SET형은 같은 숫자의 무늬 밀도를, RUN형은 같은 무늬의 연속 구간을, 혼합형은 SET/RUN 양쪽에 걸치는 교차 카드를 우선합니다.','세트형은 같은 숫자의 무늬 밀도를, 런형은 같은 무늬의 연속 구간을, 혼합형은 세트/런 양쪽에 걸치는 교차 카드를 우선합니다.'),
    ("displayName:'SET형'","displayName:'세트형'"),
    ("displayName:'RUN형'","displayName:'런형'"),
    ("short:'SET + RUN 교차'","short:'세트 + 런 교차'"),
    ('<br><small>6장 표본 · SET ${(fit.setRate*100).toFixed(1)}% / RUN ${(fit.runRate*100).toFixed(1)}% / 둘 중 하나 ${(fit.anyRate*100).toFixed(1)}%</small>','<br><small>6장 표본 · 세트 ${(fit.setRate*100).toFixed(1)}% / 런 ${(fit.runRate*100).toFixed(1)}% / 둘 중 하나 ${(fit.anyRate*100).toFixed(1)}%</small>'),
]
for old,new in replacements:
    if old not in text and new not in text:
        raise SystemExit(f'missing localization anchor: {old[:60]}')
    text=text.replace(old,new)
index.write_text(text,encoding='utf-8')

# Keep the milestone and canonical design note aligned with official Korean display terminology.
road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
r=r.replace('## M4B — 덱 조합 구조 축: SET / RUN / 혼합','## M4B — 덱 조합 구조 축: 세트 / 런 / 혼합')
r=r.replace('`SET형 / RUN형 / 혼합형`','`세트형 / 런형 / 혼합형`')
r=r.replace('SET형 29슬롯 골격','세트형 29슬롯 골격').replace('RUN형 29슬롯 골격','런형 29슬롯 골격')
r=r.replace('SET/BURST 재료 밀도 우선','세트/버스트 재료 밀도 우선').replace('RUN/CHAIN 재료 밀도 우선','런/체인 재료 밀도 우선')
r=r.replace('SET/RUN 전환점 확보','세트/런 전환점 확보').replace('SET/RUN/둘 중 하나 성립률','세트/런/둘 중 하나 성립률')
road.write_text(r,encoding='utf-8')

doc=Path('docs/DECK_STRUCTURE_PROFILES.md')
d=doc.read_text(encoding='utf-8')
d=d.replace('## SET형','## 세트형').replace('## RUN형','## 런형')
d=d.replace('SET과','세트와').replace('SET 전환','세트 전환').replace('SET의','세트의').replace('SET/RUN','세트/런')
d=d.replace('RUN과','런과').replace('RUN/CHAIN','런/체인').replace('RUN 축','런 축').replace('RUN 전환','런 전환')
d=d.replace('SET형 6장','세트형 6장').replace('RUN형 6장','런형 6장')
d=d.replace('SET 성립률','세트 성립률').replace('RUN 성립률','런 성립률')
doc.write_text(d,encoding='utf-8')

# Dedicated regression should lock the localized milestone heading and labels too.
test=Path('tests/deck-structure-profiles.mjs')
t=test.read_text(encoding='utf-8')
t=t.replace("road.includes('## M4B — 덱 조합 구조 축: SET / RUN / 혼합')","road.includes('## M4B — 덱 조합 구조 축: 세트 / 런 / 혼합')")
needle="ok(html.includes('id=\"deckStructureGrid\"')&&script.includes('[data-deck-structure]'),'battle setup exposes an independent structure picker');"
extra=needle+"\nok(script.includes(\"displayName:'세트형'\")&&script.includes(\"displayName:'런형'\")&&script.includes(\"displayName:'혼합형'\"),'structure picker uses official Korean meld terminology');"
if 'structure picker uses official Korean meld terminology' not in t:
    if needle not in t: raise SystemExit('missing deck structure UI test anchor')
    t=t.replace(needle,extra,1)
test.write_text(t,encoding='utf-8')
