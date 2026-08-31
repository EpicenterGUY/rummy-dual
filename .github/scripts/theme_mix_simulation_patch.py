from pathlib import Path
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
r=road.read_text()
old='- [ ] 각 테마 순수덱 / 2테마 혼합 / 일반 카드 혼합 시뮬레이션 및 직접 위력 카드 비율 검사'
new='- [x] 테마 최대밀도 / 2테마 / 일반 혼합 구성 시뮬레이션 + 직접 위력 비율 검사 — `tests/theme-mix-simulation.mjs`가 라이브/개발 테마별 최대 4장 우선 편성 오픈형 9네임드 빌드, 모든 2테마 조합의 슬롯 충돌 해소, 일반 mixed 다중 시드 표본을 실행 검증. 모든 구성은 `namedSlot` 중복 0을 유지하며 테마 외 카드가 남고, 직접 누적 위력 태그는 전체 네임드 풀 20% 미만·현재 테마 카드 풀 과반 미만으로 잠금'
assert old in r,'ROADMAP theme mix simulation anchor changed'
road.write_text(r.replace(old,new,1))

t=theme.read_text()
anchor='- AI는 테마 전용 별도 규칙을 만들지 않고 이미 합법인 행동의 점수에만 작은 테마 보정을 더한다. 표적 킬각, 접전 재진입, V-SIGNAL 상대 조합 진입, 무료/재사용 회수를 우선 보되 기존 버스트·체인·보드 위험 판단을 덮어쓰지 않는다.'
add=anchor+"\n- 테마 구성 안정성은 최대 테마 밀도 오픈형 빌드·모든 2테마 조합·일반 mixed 다중 시드 회귀로 검사한다. 같은 숫자+무늬 슬롯은 언제나 한 변형만 남기고, 직접 누적 위력 카드는 전체 풀의 소수로 유지한다."
assert anchor in t,'theme mix principle anchor changed'
theme.write_text(t.replace(anchor,add,1))
