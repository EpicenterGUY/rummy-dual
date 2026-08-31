from pathlib import Path
import re

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()
start=s.index('const NAMED={')
end=s.index('const UNLOCK_GROUPS=', start)
head,block,tail=s[:start],s[start:end],s[end:]
terms={
    'SWITCH':'스위치',
    'DETONATE':'폭발',
    'CORE':'코어',
    'SET':'세트',
    'RUN':'런',
    'RUMMY':'러미',
    'CHAIN':'체인',
    'BURST':'버스트',
    'OVERLOAD':'과부하',
}
pat=re.compile(r"d:'((?:\\'|[^'])*)'")
changed=0

def repl(m):
    global changed
    text=m.group(1)
    out=text
    for old,new in terms.items():
        out=re.sub(rf'(?<![A-Za-z]){re.escape(old)}(?![A-Za-z])',new,out)
    if out!=text:
        changed+=1
    return "d:'"+out+"'"

block=pat.sub(repl,block)
if changed < 20:
    raise SystemExit(f'expected broad card-text localization, changed only {changed}')
s=head+block+tail
old='- [ ] 카드 효과문의 한영 혼용 제거'
new=f'- [x] 카드 효과문의 한영 혼용 제거 — 라이브 네임드 {71}장 설명의 핵심 규칙 용어를 공식 표기 `세트 / 런 / 붙이기 / 스위치 / 러미 / 폭발 / 버스트 / 체인 / 코어 / 과부하`로 통일. 카드 ID·효과 태그·테마 고유명은 유지하고 사용자 노출 `d:` 설명만 현지화'
if old not in r: raise SystemExit('ROADMAP card-text localization anchor missing')
r=r.replace(old,new,1)
index.write_text(s)
road.write_text(r)
print('localized descriptions',changed)
