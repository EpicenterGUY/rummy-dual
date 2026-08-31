from pathlib import Path

road = Path('ROADMAP.md')
theme = Path('docs/THEME_GROUPS.md')

r = road.read_text()
old = '- [ ] ZERO-SIGHT ↔ 일반/V-SIGNAL/POINT-BLANK 혼합 회귀 테스트'
new = '- [x] ZERO-SIGHT ↔ 일반/V-SIGNAL/POINT-BLANK 혼합 회귀 테스트 — 표적은 카드군과 분리된 공개 조합 메타데이터로 유지되며, 일반 카드의 붙이기·V-SIGNAL 앙코르 회수·혼합 조합 정리/보존·POINT-BLANK 카드 정체성이 같은 표적 이벤트 경로에서 충돌하지 않는 것을 실행 회귀로 잠금'
assert old in r, 'ROADMAP ZERO-SIGHT mixed regression anchor changed'
r = r.replace(old, new, 1)
road.write_text(r)

t = theme.read_text()
old_v = '- [ ] V-SIGNAL ↔ 일반 카드 혼합 회귀 테스트'
new_v = '- [x] V-SIGNAL ↔ 일반 카드 혼합 회귀 테스트 — `tests/vsignal-mixed-regression.mjs`에서 앙코르의 일반 조합 재진입, 전원 집합!/내구방송의 일반 카드 보존을 실행 검증'
assert old_v in t, 'THEME_GROUPS V-SIGNAL mixed regression anchor changed'
t = t.replace(old_v, new_v, 1)

old_events = '- [ ] 표적 조합 회수/이동/새 조합 생성 반응 이벤트 정리'
new_events = '- [x] 표적 조합 회수/이동/새 조합 생성 반응 이벤트 정리 — `onTargetSet` / `onTargetClear` / `onTargetMeldChange` / `onMeldMove` 및 `targetedBy` 스냅샷을 실행 회귀로 잠금'
assert old_events in t, 'THEME_GROUPS ZERO-SIGHT target event anchor changed'
t = t.replace(old_events, new_events, 1)

old_mixed = '- [ ] ZERO-SIGHT ↔ 일반/V-SIGNAL/POINT-BLANK 혼합 회귀 테스트'
new_mixed = '- [x] ZERO-SIGHT ↔ 일반/V-SIGNAL/POINT-BLANK 혼합 회귀 테스트 — 표적 조합은 카드의 `themeId`와 무관하게 일반 붙이기/회수/정리 이벤트를 내보내며, V-SIGNAL 회수 예외와 보존 및 POINT-BLANK 정체성 카드가 같은 공개 조합에서 공존함을 실행 검증'
assert old_mixed in t, 'THEME_GROUPS ZERO-SIGHT mixed regression anchor changed'
t = t.replace(old_mixed, new_mixed, 1)
theme.write_text(t)
