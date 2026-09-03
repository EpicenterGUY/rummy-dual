from pathlib import Path

p=Path(__file__).resolve().parents[2]/'index.html'
s=p.read_text(encoding='utf-8')
old="d:'내 부품이 소모패에 들어간 턴에 손패의 다른 내 카드 1장을 새 부품으로 지정할 수 있다. 턴당 1회.'"
new="d:'내 부품이 소모패에 들어간 턴에 손패의 다른 내 카드 1장을 새 부품으로 지정할 수 있다. 이 효과는 턴당 1회만 사용할 수 있다.'"
if new not in s:
    if old not in s: raise SystemExit('missing shredder text anchor')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('SCRAP-SHIFT wave4 localization fix applied')
