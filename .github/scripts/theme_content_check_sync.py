from pathlib import Path
p=Path('docs/THEME_GROUPS.md')
s=p.read_text()
repls={
'- [ ] M8 첫 ~50 네임드의 선택/복사/타이밍 안정화':'- [x] M8 첫 ~50 네임드의 선택/복사/타이밍 안정화 — 선택형 효과는 공용 resumable choice 경로, 복사 카드는 실제 발동 조건을 만족하는 효과만 복사, 직전 폭발/RUMMY 등 타이밍 창을 실행 회귀로 잠금',
'- [ ] 테마 메타데이터가 기존 `NAMED` 슬롯 구조와 충돌하지 않는 데이터 모델 확정':'- [x] 테마 메타데이터가 기존 `NAMED` 슬롯 구조와 충돌하지 않는 데이터 모델 확정 — `themeId`/조합 `themeMeta`는 정체성·보드 메타데이터일 뿐 정규 `namedSlot()` 키와 카드 소유권을 바꾸지 않음',
'- [ ] 테마 카드가 같은 랭크+무늬 슬롯의 대체 네임드 후보로 정상 동작하는지 확인':'- [x] 테마 카드가 같은 랭크+무늬 슬롯의 대체 네임드 후보로 정상 동작하는지 확인 — 전투 덱은 같은 정규 슬롯 후보 중 하나만 물질화하며 V-SIGNAL/ZERO-SIGHT/POINT-BLANK 변형도 동일 불변식 사용',
'- [ ] 공용 AI가 표적/접전/RAID/회수 가치를 평가할 최소 휴리스틱 추가':'- [x] 공용 AI가 표적/접전/RAID/회수 가치를 평가할 최소 휴리스틱 추가 — `themeAIAttachBias` / `themeAIRecoveryBias` 가산층으로 기존 합법성·보드 위험 판단을 우회하지 않고 테마 가치를 평가',
'- [ ] 세 테마 각각 순수덱 / 2테마 혼합 / 일반 카드 혼합 시뮬레이션':'- [x] 세 테마 각각 순수덱 / 2테마 혼합 / 일반 카드 혼합 시뮬레이션 — 최대 테마 밀도 오픈형 빌드, 모든 2테마 조합, 일반 mixed 다중 시드에서 슬롯 중복 0과 비테마 카드 잔존을 실행 검증',
'- [ ] 직접 위력 증가 카드 비율이 기존 설계 원칙을 침범하지 않는지 회귀 검사':'- [x] 직접 위력 증가 카드 비율이 기존 설계 원칙을 침범하지 않는지 회귀 검사 — 전체 네임드 풀 20% 미만, 현재 테마 카드 풀 과반 미만을 회귀 기준으로 유지'
}
for old,new in repls.items():
    if old not in s: raise SystemExit(f'missing canonical checklist anchor: {old}')
    s=s.replace(old,new,1)
p.write_text(s)
