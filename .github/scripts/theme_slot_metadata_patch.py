from pathlib import Path
p=Path('ROADMAP.md')
s=p.read_text()
old='- [ ] 테마 ID/표시명/전용 조합 메타데이터가 기존 동일 랭크+무늬 슬롯 후보 구조와 충돌하지 않는지 확인'
new='- [x] 테마 ID/표시명/전용 조합 메타데이터 ↔ 동일 랭크+무늬 슬롯 불변식 검증 — `themeId`는 카드의 정체성 메타데이터일 뿐 `namedSlot`/52슬롯 키를 바꾸지 않으며, 모든 라이브 테마 변형은 정규 슬롯에 귀속됨. ZERO-SIGHT `themeMeta.zeroSight`와 POINT-BLANK `themeMeta.pointBlank`는 같은 공개 조합에서 독립 공존하고 카드 슬롯/소유권을 변경하지 않음을 실행 회귀로 잠금'
assert old in s,'theme slot metadata roadmap anchor changed'
p.write_text(s.replace(old,new,1))
