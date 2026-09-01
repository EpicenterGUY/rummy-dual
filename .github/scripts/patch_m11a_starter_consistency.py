from pathlib import Path

root=Path(__file__).resolve().parents[2]
road_path=root/'ROADMAP.md'
master_path=root/'docs'/'ROGUELIKE_MASTER_PLAN.md'
test_path=root/'tests'/'m11a-roguelike-run-init.mjs'

def replace_once(text,old,new,label):
    if old not in text:
        raise SystemExit(f'missing anchor: {label}')
    return text.replace(old,new,1)

road=road_path.read_text(encoding='utf-8')
old="- [x] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계 — 일반 1대1의 캐릭터/테마/30장 덱 선택과 로그라이크 스타터를 분리하고 `유랑자 / 수집가 / 회수꾼 / 광대 / PURE` 전용 선택 UI를 추가. `rummyDuelRoguelikeRunDraftV1` 초안은 공통 시작 구역, 지역 경로, 노드 위치, 카드군 하드잠금 없음, 원본 랭크+무늬 슬롯 정체성을 명시하며 PURE만 시작 네임드 0장을 확정값으로 기록. 시작 덱 총 장수·순수/효과 비율·패시브·정확한 보상 확률은 미확정 상태로 보존하고 현재 일반 전투에는 아직 연결하지 않음"
new="- [x] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계 — 일반 1대1의 캐릭터/테마/30장 덱 선택과 로그라이크 스타터를 분리하고 `유랑자 / 수집가 / 회수꾼 / 광대 / PURE` 전용 선택 UI를 추가. `rummyDuelRoguelikeRunDraftV1` 저장 초안은 공통 시작 구역, 빈 지역 경로, 카드군 하드잠금 없음, 원본 랭크+무늬 슬롯 정체성과 v1 30장 스타터 계약을 기록한다. 일반 4스타터는 순수 23 + 네임드 정규 6 + 네임드 조커 1, PURE는 순수 정규 29 + 기본 와일드 조커 1이며 직접 전투 패시브는 전원 없음. 실제 보상 등장 확률만 후속 밸런스로 남기고 현재 일반 전투에는 아직 연결하지 않음"
road=replace_once(road,old,new,'road stale run-init summary')
road_path.write_text(road,encoding='utf-8')

master=master_path.read_text(encoding='utf-8')
master=replace_once(master,
'- 숫자/무늬 분포는 안정적인 방향을 우선 검토한다.',
'- 숫자/무늬 분포는 v1에서 공통 정규 29슬롯 `S3,S4,S5,S6,S7,S8,S9,H2,H3,H4,H7,H8,H9,D2,D3,D4,D5,D6,D7,D8,C3,C4,C5,C6,C7,C8,C9,S10,H10`으로 잠근다.',
'master PURE distribution stale wording')
master_path.write_text(master,encoding='utf-8')

t=test_path.read_text(encoding='utf-8')
anchor="ok(road.includes('- [x] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계'),'ROADMAP marks only the run-init architecture/UI item complete');"
replacement=anchor+"\nok(!road.includes('PURE만 시작 네임드 0장을 확정값으로 기록')&&!road.includes('시작 덱 총 장수·순수/효과 비율·패시브·정확한 보상 확률은 미확정 상태'),'ROADMAP contains no stale pre-baseline run-init wording');"
t=replace_once(t,anchor,replacement,'run-init stale wording regression')
test_path.write_text(t,encoding='utf-8')

print('patched M11A starter baseline consistency wording and regression')
