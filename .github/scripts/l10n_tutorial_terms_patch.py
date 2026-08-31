from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()

replacements=[
("RUN 회수는 체인이 1 감소하고","런 회수는 체인이 1 감소하고",1),
("내 ♥ RUN의 앙코르 5♥","내 ♥ 런의 앙코르 5♥",2),
("같은 턴 BURST/CHAIN 반환에 못 쓰지만","같은 턴 버스트/체인 반환에 못 쓰지만",1),
("RUN 체인이 ${context.beforeChain} → ${context.afterChain}로 1 감소했습니다.","런 체인이 ${context.beforeChain} → ${context.afterChain}로 1 감소했습니다.",1),
("상대 5 세트에 재입장시켜 BURST하세요.","상대 5 세트에 재입장시켜 버스트하세요.",1),
("회수 → 다른 공개 조합 재입장 → BURST로 이어지는","회수 → 다른 공개 조합 재입장 → 버스트로 이어지는",1),
]
for old,new,expected in replacements:
    count=s.count(old)
    if count!=expected:
        raise SystemExit(f'expected {expected} tutorial copy match(es) ({count}): {old}')
    s=s.replace(old,new)

old='- [ ] 튜토리얼 용어 반영'
new='- [x] 튜토리얼 용어 반영 — 튜토리얼의 사용자 노출 목표·힌트·실습 로그·성공 문구에서 `RUN / BURST / CHAIN` 혼용을 제거하고 공식 표기 `런 / 버스트 / 체인`으로 통일. `expectMeld:\'SET\'` 같은 내부 판정 키와 테마 고유명 `V-SIGNAL`은 유지'
if r.count(old)!=1: raise SystemExit(f'ROADMAP tutorial terminology anchor count mismatch: {r.count(old)}')
r=r.replace(old,new,1)
index.write_text(s)
road.write_text(r)
