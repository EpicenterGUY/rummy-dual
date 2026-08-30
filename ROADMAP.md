# RUMMY//DUEL Development Roadmap

Updated: 2026-08-30

## Core direction
RUMMY//DUEL is a 1v1 rummy battle game where both players grow one central SWITCH bomb through SET/BURST and RUN/CHAIN, including play on the opponent's public melds.

## M0 — Rule lock
- [x] 3 CORE × 60, no overkill pierce
- [x] SET 3 → BURST READY; fourth suit → +24 and retire
- [x] RUN CHAIN +10 / +15 / +20 / +25; CHAIN 4+ RUN may be voluntarily `런 완주`ed by its controller on their own turn to free the slot, while keeping it allows continued +25 extensions
- [x] One central uncapped SWITCH; 100+ is display-only OVERLOAD
- [x] One normal SWITCH return per turn
- [x] Public meld cap 2 per player; no free base meld/RUN disposal
- [x] Shared discard has no size cap; base take is top only
- [x] Personal spent pile only is recycled when a deck is empty
- [x] RUMMY refills 6
- [x] Shield has no base hard cap and normally expires at the owner's next turn start
- [x] Recovery rule refinement: a card recovered this turn may still be used for a new 3-card meld, maintenance, discard, or non-return effects, but cannot be reused that same turn as material for a BURST/CHAIN/SWITCH-returning attach unless a named effect explicitly grants that exception.

## M1 — Final rules ↔ live code sync
- [x] Remove free RUN retirement
- [x] Remove free public-meld disposal
- [x] Remove discard five-card cap
- [x] Make AI respect the two-meld cap
- [x] Audit remaining code-only base rules: remove the hidden shield-40 cap, obsolete retire/draw-preview routes, and superseded generic RUMMY flags; clarify Roundabout against the recovery-return guard
- [x] Add conditional RUN completion: controller-only at CHAIN 4+, no bonus power/SWITCH movement, slot opens immediately, continuation remains +25 if not completed; AI and stuck-state logic respect it

## M2 — Confirmed bug fixes
- [x] Harden invalid/legacy selected character progress data
- [x] Unify Black Market discard acquisition path for player/CPU
- [x] Fix CORE LETHAL targeting feedback
- [x] Synchronize Chain Reaction text/implementation
- [x] Implement Last Laugh returning-RUMMY / DETONATE reduction behavior
- [x] Audit RUMMY-linked named cards: Second Heart, Returner, Life Support, Encore, Last Laugh, and grace interactions

## M3 — Regression tests
- [x] Buildless JS syntax/invariant smoke test
- [x] Recovery → same-turn SWITCH-return guard behavior tests
- [x] SET validity and BURST retirement tests
- [x] RUN numeric edge checks: A-2-3 / Q-K-A / K-A-2
- [x] CHAIN progression executable check: 10 / 15 / 20 / 25+
- [x] Multi-attach CHAIN state/total tests
- [x] SWITCH ownership / one-return / DETONATE tests
- [x] CORE BREAK / shield / no-pierce tests
- [x] RUMMY / grace / Joker King tests

## M4 — Hand circulation
- [x] Recheck maintenance stuck-state definition against actual playable cards and return restrictions
- [x] Verify deck exhaustion/recycling under long games; recycle personal spent only and preserve shared discard
- [x] Audit player/AI RUMMY turn-end paths; AI now settles contracts before the single turn-end resolution even on RUMMY turns
- [x] Reset transient discard-contract state whenever a card is freshly acquired from deck/discard before source-specific effects are applied

## M5 — Multi-attach UX
- [x] Preserve explicit hand-card selection order and pass that order into attach resolution
- [x] Allow a public meld to be targeted first and highlight only legal next cards for that target
- [x] Show per-card +10/+15/+20/+25 CHAIN steps and aggregate TOTAL; SET completion previews BURST +24
- [x] Preview the resulting `SWITCH → CPU` before committing the attach

## M6 — Combat readability
- [x] Give the central SWITCH a dedicated alert line for neutral, incoming, imminent DETONATE, and enemy DETONATE states
- [x] Show current CORE + shield, CORE-lethal state, and remaining `CORE까지 N` margin directly under the SWITCH
- [x] Make the player phase strip visually enter DETONATE danger state when the SWITCH points to YOU on the player's turn
- [x] Promote SET to `BURST READY · 4번째 카드 +24 · SWITCH 반환` and RUN to `CHAIN N · NEXT +X · SWITCH 반환`
- [x] Make CORE BREAK explicitly show `OVERKILL N LOST · NO PIERCE`, with persistent CORE notes stating next-CORE penetration is zero
- [x] Add executable combat-readability regressions while preserving all M1–M5 tests

## M7 — Status/effect engine
- [x] Normalize the five shared statuses: vulnerable, seal, fixed, protect, regen; keep shield and one-off card markers separate
- [x] Define status scopes and lifecycle for player / public meld / individual card targets
- [x] Make fixed consistently block recovery, extortion, cutting and other movement paths, including cards controlled inside the opponent's public meld
- [x] Route shared seal/protect behavior through the normalized status helpers while preserving existing named-card behavior
- [x] Introduce reusable effect event/action vocabulary and a gradual action dispatcher without adding a new base resource
- [x] Add executable status-engine regressions and keep every M1–M6 suite passing

## M8 — Named cards
- [ ] Stabilize first ~50 named cards
- [x] First correctness pass: fix CPU new-meld crash, duplicate CJ recovery, Phoenix one-time return, and revive Gap Run / Middle Manager placeholder behavior
- [x] Synchronize deterministic card text for Revenge Blade, Ambulance, Fence, Golden Hand, Money Changer, Recursive Function, Connection Link, Branch Link and Copier
- [x] Keep direct SWITCH manipulation to a minority of the audited pool with an executable ratio guard
- [x] Second correctness pass: activate Death Sentence discard targeting, Tuner cross-meld recovery, role-sensitive Understudy retirement, and executable Doppelganger SET support coverage
- [ ] Finish remaining choice/copy/timing audit and per-card regressions before declaring the first ~50 behavior-stable
- [ ] Favor meld mutation, recovery, movement, discard, defense, RUMMY and timing interactions

## M8A — 정식 테마군 콘텐츠 설계
정식 테마군은 폐쇄형 전용 덱이 아니라 공용 러미 행동과 연결되는 모듈형 카드군으로 설계한다. 현재 최종 설계 기준과 카드 후보 전체는 `docs/THEME_GROUPS.md`를 Source of Truth로 사용한다. 아직 라이브 코드 구현 완료를 의미하지 않는다.

### 공통 설계 잠금
- [x] 테마 전용 개념은 허용하되 별도 전용 자원 남발 금지
- [x] 초동 카드가 전용 개념 생성 + 정비/보호/덱 조작 등 작은 기본값을 함께 제공하도록 설계
- [x] 전용 개념의 실제 보상은 가능한 한 일반 카드와 다른 테마 카드도 이용 가능하게 설계
- [x] 직접 누적 위력 +X는 소수에만 배치하고 버스트 +24 / 체인 +10·15·20·25 / 코어 60 스케일 기준 유지
- [x] 혼합덱에서 세트·런·붙이기·회수·정비·버리기·스위치 반환·러미 같은 공용 행동으로 시너지 연결

### V-SIGNAL — 버튜버 / 가상 방송 콤보
- [x] 정식 테마명 `V-SIGNAL` 잠금
- [x] `HYPE` 카운터 및 V-SIGNAL 전용 자원 폐기
- [x] 방송 시작 → 합방 → RAID → 회수/방송 종료 → 앵콜/재방송 → 러미 흐름 잠금
- [x] ♠ 화제성/염상, ♥ 팬덤/회수/러미, ♦ 합방/세트, ♣ 방송 진행/런/RAID 역할 분리
- [x] 현재 정식 후보 24장 설계 확정 — 상세 카드 목록/효과 방향은 `docs/THEME_GROUPS.md`
- [ ] 새 조합/붙이기/회수/러미/런 완주 이벤트를 공용 효과 엔진에 필요한 만큼 노출
- [ ] `앙코르` 등 회수 후 동일 턴 반환 예외를 카드 단위로 안전하게 구현
- [ ] 버스트 정리/런 완주 직전 카드 보존 타이밍 구현
- [ ] V-SIGNAL ↔ 일반 카드 혼합 회귀 테스트

### ZERO//SIGHT — 저격수 / 표적 / 정밀 타격
- [x] 정식 테마 방향 `ZERO//SIGHT` 잠금
- [x] 전용 개념 `표적` 확정 — 자신이 기본 1개 유지, 새 표적 지정 시 기존 표적 해제, 조합 정리 시 제거
- [x] 표적을 생성하는 초동/이전/재지정 카드를 충분히 배치해 초동 안정성 확보
- [x] 표적 조합에 붙이는 카드는 ZERO//SIGHT일 필요가 없도록 혼합 시너지 잠금
- [x] 현재 정식 후보 18장 설계 확정 — 관측/덱 조작/고정·봉인/킬각 보정/준비형 공격/표적 이전 포함
- [ ] 공개 조합 단위 표적 메타데이터 및 1개 제한 구현
- [ ] 손에서 턴 경과 충전 상태를 카드 단위 마커로 구현
- [ ] 표적 조합 회수/이동/새 조합 생성 반응 이벤트 정리
- [ ] ZERO//SIGHT ↔ 일반/V-SIGNAL/POINT//BLANK 혼합 회귀 테스트

### POINT//BLANK — 근접 총격 / 접전 / 교대
- [x] 정식 테마 방향 `POINT//BLANK` 잠금
- [x] 전용 개념 `접전` 확정 — 상대 공개 조합 1개를 지정하고 자신의 카드가 들어가며 유지되는 근거리 전장
- [x] 접전에 진입하는 카드는 POINT//BLANK일 필요가 없도록 혼합 시너지 잠금
- [x] 접전 생성 초동 + 이동 + 회수 + 재돌입 + 패순환의 순환 엔진 확정
- [x] 현재 정식 후보 18장 설계 확정 — 봉인/고정/무료 회수/대상 교대/필드 이동/회수 카드 재배치/근거리 피니시 포함
- [ ] 상대 공개 조합 단위 접전 메타데이터 / 1개 제한 / 지연 해제 구현
- [ ] 무료 회수와 기본 회수 횟수를 명확히 구분
- [ ] `퀵 리로드` 등 회수 후 새 조합 생성 전용 예외 구현
- [ ] POINT//BLANK ↔ 일반/V-SIGNAL/ZERO//SIGHT 혼합 회귀 테스트

### 후속 테마 후보 — 아직 상세 확정 전
- [x] `MAIL//ROUTE` 작업안 기록 — 편지/우편 테마, `우편 → 목적지 → 도착 → 반송 → 재배송` 엔진. 일반 카드에도 우편 표식을 붙여 혼합덱 허브로 쓰는 방향
- [x] `SCRAP//SHIFT` 작업안 기록 — 폐품/해체/재조립 테마, 다른 카드도 `부품`으로 바꾸고 회수·소모·이동을 자원화하는 방향
- [ ] MAIL//ROUTE 카드 수 / 우편 표식 수명 / 목적지 규칙 / 반송 타이밍 최종 확정
- [ ] SCRAP//SHIFT 카드 풀과 부품 규칙 상세 재설계
- [ ] 향후 신규 테마는 카드군부터 만들기보다 지역의 문화/직업/갈등에서 파생시키는 방식 우선 검토

### 구현 전 공통 검증
- [ ] M8 첫 ~50 네임드 선택/복사/타이밍 안정화 후 대규모 테마 구현 시작
- [ ] 테마 ID/표시명/전용 조합 메타데이터가 기존 동일 랭크+무늬 슬롯 후보 구조와 충돌하지 않는지 확인
- [ ] 한 행동에서 표적/접전/RAID/회수 반응이 중첩될 때 트리거 순서와 턴당 1회 제한 명문화
- [ ] AI가 표적·접전·RAID·회수 가치를 판단할 최소 휴리스틱 추가
- [ ] 각 테마 순수덱 / 2테마 혼합 / 일반 카드 혼합 시뮬레이션 및 직접 위력 카드 비율 검사

## UX1 — 신규 유저 UX / 튜토리얼
신규 유저 진입 장벽을 낮추는 정식 핵심 UX 작업. 상세 기준은 `docs/NEW_USER_UX_TERMS.md`를 따른다.

### P1 — 시작창 + 기본 플레이 튜토리얼
- [x] 기존 시작 화면 구조 점검 — 현재는 별도 시작창 없이 로드 즉시 `newGame()` 실행
- [x] 신규 시작창 UI 설계
- [x] `대전 시작 / 튜토리얼 / 카드 도감 / 설정` 구조 정리
- [x] 미구현 메뉴를 비활성/`준비 중` 상태로 구분
- [x] 모바일 시작창 대응
- [x] 첫 실행 튜토리얼 안내
- [x] 기존 progress 저장 스키마에 튜토리얼 상태 저장
- [x] 일반 게임 로직과 튜토리얼 로직 중복 최소화 구조 확정 (`sessionMode` + `TUTORIAL_STEPS` + 공통 컨트롤러 + 실제 엔진 재사용)
- [x] 튜토리얼 전용 고정 게임 상태/손패/드로우 설계 — 실제 카드 객체/조합 판정 엔진을 재사용하고 단계마다 상태만 결정론적으로 재구성
- [x] 카드 기본 조작 튜토리얼 — 고정 Q♦ 덱 드로우 → 지정 카드 선택 → 버리기 성공 시 자동 진행
- [x] 세트 튜토리얼 — 3♠ / 3♥ / 3♦ 고정 손패 + 실제 `meldType` / `submitNewMeld` 경로
- [x] 런 튜토리얼 — 4♣ / 5♣ / 6♣ 고정 손패 + 실제 `meldType` / `submitNewMeld` 경로
- [x] 붙이기 튜토리얼 — 고정 내 RUN에 실제 `attachCards` 체인 붙이기
- [x] 상대 공개 조합 붙이기 체험 — 고정 상대 RUN에 내 카드 붙이기 + 실제 스위치 반환
- [x] 스위치 튜토리얼 — 나를 향한 누적 36에서 4번째 8로 버스트 +24, 상대에게 스위치 반환 확인
- [x] 러미 튜토리얼 — 마지막 손패를 실제로 사용해 `triggerRummy()` → 기본 6장 리필 확인
- [x] 튜토리얼 하이라이트 / 가이드 UI 기본 프레임워크 — 화면 흐름 안 coach + 힌트/다음/재시작/종료

### P2 — 폭발/연습/재진입 완성도
- [x] 누적 위력 / 폭발 튜토리얼 — 스위치가 자신을 가리킨 채 턴 종료 → 실제 `turnEnd()` / `detonate()` 경로 체험
- [x] 폭발 연출 및 현재 코어 피해 결과 강조 — 보호막 8 → 현재 코어 24 파괴 → 초과 8 소멸/관통 없음 → 다음 코어 60/60을 고정 시나리오로 확인
- [x] 자유 연습전 — 순수 카드·필드 없음·유리한 고정 시작 손패·첫 사이클 보호막 12·CPU 행동 축소. 일반 대전과 분리된 `practice` 세션이며 승패/클리어/레벨/해금 진행도에는 영향 없음
- [x] 튜토리얼 완료 상태 저장 — 러미 실습 성공 시 `tutorialCompleted=true` 저장
- [x] 튜토리얼 다시 보기 — 완료 후 시작 메뉴를 `다시 보기` 상태로 전환하고 처음부터 재진입
- [x] 튜토리얼 종료 / 재시작 처리 — 단계 토큰으로 성공 직후 자동 진행과 수동 재시작 레이스를 차단하고, 종료는 2회 확인 후 메인으로 복귀. 완료 기록은 유지
- [x] 행동 성공 시 자동 진행, 잘못된 행동은 상태를 망가뜨리지 않고 힌트 제공 — 실제 mutation 전에 `tutorialAllows`로 차단하며 자동 진행은 battle/step token으로 stale callback 방지
- [x] 세부 애니메이션 / 스위치 이동 / 러미 피드백 보강 — 버스트/체인 반환 시 현재 위치→상대 위치 스위치 플라이트, 폭탄 종료 시 중립 복귀, 러미 6/7장 리필 배너·손패 딜 인, 튜토리얼 성공 펄스 및 850ms 전환 피드백 추가
- [x] 모바일 가독성 및 터치 정적 회귀 — 480px 앱 상한, 390px 2열 / 370px 1열 튜토리얼 액션, 최소 42px 터치 높이와 긴 한국어 줄바꿈 계약 추가
- [x] 390px 이하 한국어 버튼/가이드 잘림 회귀 테스트 — coach 목표/힌트 `overflow-wrap`, 버튼 `white-space:normal`, 370px 단일 열 fallback 검사

### P3 — 고급 튜토리얼
- [x] 회수 / 정비 / 공식 상태 고급 튜토리얼 — 기본 튜토리얼과 분리된 고급 진입. 실제 RUN 회수·체인 -1, 1장 정비 교체, 취약 1의 다음 폭발 +25% 및 소모를 고정 시나리오로 체험
- [x] 조커 고급 튜토리얼 — 광대왕 조커로 완전 와일드 버스트와 조합 정리 후 덱 아래 귀환을 체험하고, 쌍면 조커로 버스트 +24와 고유 보호막 20 효과를 실제 엔진 경로에서 확인
- [ ] 네임드 카드 설명
- [ ] 테마군 튜토리얼 기반
- [ ] V-SIGNAL 등 실제 구현된 테마군 체험전

## UI2 — 전술 카드테이블 비주얼 리디자인
도박/카지노/배팅 사이트로 읽히는 시각 문법을 줄이고, 카드와 조합이 주인공인 모바일 전략 카드게임/보드게임 톤으로 전환한다. 규칙과 전투 판정은 변경하지 않는다.

### P1 — 카지노 톤 제거 + 기본 시각 체계 재설계
- [x] 기존 UI의 카지노 인상 원인 감사 — 검정/금색/청록 네온, 두꺼운 이중 테두리, 상시 펄스, 과도한 패널 강조
- [x] 기본 팔레트를 무채도 슬레이트 + 종이 카드 + 절제된 청록/웜 포인트로 교체
- [x] 패널/버튼을 두꺼운 픽셀 박스에서 얕은 테두리·낮은 그림자의 앱 카드형으로 완화
- [x] 금색 행동 버튼을 금색 면 채움 대신 중성 배경 + 웜 포인트 테두리로 축소
- [x] 시작창 히어로를 네온 패널에서 종이 보드/카드 표면으로 재구성
- [x] 스위치 보드를 전술 상태판으로 정리하고 평상시 소유권 펄스 제거
- [x] 위험 단계가 실제로 상승할 때만 게이지가 웜/레드 계열로 변하도록 제한
- [x] 치명/폭발 임박 상태의 반복 글로우·잭팟형 펄스를 제거하고 정적 경고 우선
- [x] 트럼프 카드 프레임의 금색 광택을 낮추고 종이 질감/중성 프레임으로 조정
- [x] reduced-motion 대응 및 UI2 시각 회귀 테스트 추가

### P2 — 정보 위계 / 공간 정리
- [x] 상단 상태/캐릭터/메뉴 밀도 축소 및 모바일 우선 재배치 — 캐릭터 배지 + 단일 `메뉴` 드롭다운
- [x] 스위치 핵심 정보와 보조 문구를 1차/2차 정보로 분리 — 상태/경고/코어 여유만 상시 노출, 중복 라벨/비활성 버튼 제거
- [x] 공개 조합과 손패 사이 여백·높이·스크롤 밀도 재조정
- [x] 전투 기록 기본 접힘/요약 방식 적용 — 기본 접힘 + 짧은 disclosure 헤더 + 펼쳤을 때만 제한 높이 스크롤
- [x] 선택 가능 카드·붙이기 가능 조합 강조를 발광보다 테두리/위치 변화 중심으로 통일
- [ ] 360~480px 실제 모바일 폭에서 버튼/상태 문구 잘림 회귀 점검 — 370/390px 정적 fallback과 회귀 테스트 추가, 실기기 시각 검수 남음

### P2.5 — 데스크톱 / 태블릿 반응형
- [x] 기존 480px 모바일 전장을 899px 이하에서 그대로 유지
- [x] 900~1199px에서 상태/스위치를 상단에 두고 상대 손패·드로우 구역을 2열로 사용하는 태블릿/소형 PC 레이아웃
- [x] 1200px 이상 3열 전술 테이블 — 좌측 상대/드로우, 중앙 스위치·공개 조합, 우측 카드 상세, 하단 전체 폭 손패/행동
- [x] 데스크톱에서 상대 손패 카드백·공개 조합·손패 카드를 모바일보다 크게 복원하고 행동 버튼을 3열→6열로 확장
- [x] 시작 화면도 데스크톱에서 480px 고정 셸을 해제하되 메뉴 본문은 읽기 좋은 520~560px로 제한
- [x] 1440px 최대 전장 폭으로 1366×768 / 1920×1080 / 2560×1440 계열의 과도한 가로 늘어짐 방지
- [ ] 실제 PC 브라우저에서 1366×768 / 1920×1080 시각 검수 및 필요 시 미세 간격 조정

### P3 — 아트/브랜드 마감
- [ ] 카드 아이콘/네임드 프레임과 새 UI 팔레트 통일
- [ ] 시작창/결과창/도감의 시각 언어 통일
- [ ] 튜토리얼 coach를 동일한 전술 보드 톤으로 최종 마감
- [ ] V-SIGNAL 등 테마군은 기본 UI 위에 테마 포인트만 얹고 카지노형 네온 남발 금지

## L10N1 — 한국어 용어 / 텍스트 정리
사용자 노출 텍스트를 한국어 또는 정착 외래어로 통일한다. 코드 내부 함수/변수/데이터 키는 특별한 이유가 없으면 영문을 유지한다.

### 공식 핵심 용어 잠금
- [x] 현재 UI 전체의 주요 영문/혼용 용어 1차 조사
- [x] 핵심 규칙 용어 후보 비교 및 공식 용어집 초안 작성 (`docs/NEW_USER_UX_TERMS.md`)
- [x] SET 명칭: `세트`
- [x] RUN 명칭: `런`
- [x] ATTACH 명칭: `붙이기`
- [x] SWITCH 명칭: `스위치`
- [x] RUMMY 명칭: `러미`
- [x] DETONATE 명칭: `폭발`
- [x] OVERLOAD 사용 여부 점검 — 100+ 표시 단계만 유지, 사용자 표기는 `과부하`
- [x] BURST / CHAIN: `버스트 / 체인`
- [x] CORE / CORE BREAK / CORE LETHAL: `코어 / 코어 파괴 / 코어 파괴 가능`

### 실제 텍스트 적용
- [x] 일반 UI 용어 한국어화 1차 (`YOU/PLAYER/CPU/NEXT/TOTAL` 등 전투 핵심 노출 제거)
- [x] 전투 배너/경고 문구 한국어화 1차 (`코어 파괴`, `폭발`, `과부하`, `관통 없음`)
- [ ] 카드 효과문의 한영 혼용 제거
- [ ] 카드 효과 문체 통일
- [ ] 튜토리얼 용어 반영
- [x] 도움말 / 규칙 설명 핵심 용어 반영 + `런 완주` 규칙 동기화
- [x] 시작창 메뉴 한국어화
- [x] 기존 규칙 오버레이의 공식 용어집 갱신
- [ ] 중복 / 폐기된 옛 용어 제거
- [ ] 모바일 UI에서 긴 한국어 표현 잘림 점검
- [x] 사용자 노출 문자열 회귀 테스트 추가

### 유지할 고유명
- [x] `RUMMY//DUEL` 브랜드 유지
- [x] `V-SIGNAL` 등 테마/세계관 고유명은 실제 구현 시 원문 유지 가능
- [x] 내부 함수/변수명 (`setValid`, `attachCards`, `switchTarget`, `detonate`, `triggerRummy` 등)은 현지화 때문에 일괄 변경하지 않음

## M9 — Jokers and fields
- [ ] Finalize distinct Joker identities
- [ ] Audit Joker King return-to-owner-deck behavior
- [ ] Stabilize 10–15 behavior-changing shared fields

## M10 — AI 2.0
- [x] Respect recovery same-turn return restriction in planning
- [ ] Search 5+ card multi-attach cases where practical
- [ ] Improve opponent-meld and future-BURST risk evaluation
- [ ] Improve intentional small-bomb acceptance decisions

## M11 — Deckbuilder
- [ ] Player-facing 52-slot deck construction
- [ ] One variant per exact rank+suit slot
- [ ] Rank/suit/SET/RUN distribution analysis UI

## M11A — 로그라이크 캐릭터 / 스타터 / 순수덱
캐릭터/테마/지역/보상까지 포함한 전체 작업안은 `docs/ROGUELIKE_MASTER_PLAN.md`에 보존한다. 기존 스타터 상세는 `docs/ROGUELIKE_DECK_STARTERS.md`를 참고한다. 현재 단계에서는 후속 설계를 위한 방향 기록이며, 정확한 수치와 실제 개발 착수 시점은 아직 확정하지 않는다.

### 캐릭터와 카드군
- [x] 캐릭터는 특정 테마/카드군 사용을 강제하는 클래스 잠금이 아니라 런의 출발 방향으로 설계
- [x] 캐릭터별 시작 효과카드 일부 + 순수 트럼프 다수의 혼합 스타터 방향 잠금
- [x] 캐릭터별 카드 보상 가중치/고유 패시브 후보로 성향을 주되 다른 테마 획득은 항상 허용
- [x] 시작부터 완성된 테마 콤보를 지급하지 않고 런 중 덱 정체성이 변화하도록 설계
- [ ] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정
- [ ] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계

### PURE — 온리 순수 스타터
- [x] `PURE`는 별도 테마군이 아니라 효과카드 0장으로 시작하는 백지형 스타터/빌드 경로로 확정
- [x] 순수카드는 효과가 없어도 숫자·무늬·세트·런 재료라는 고유 가치를 유지
- [x] PURE는 직접 전투 보너스보다 카드 선택/교체/제거 등 덱 구축 자유도를 장점으로 설계
- [x] 런 도중 네임드를 받아 어느 테마로도 전환 가능
- [x] 네임드를 끝까지 받지 않는 온리 순수덱 클리어도 가능한 방향 유지
- [ ] PURE 시작 덱의 숫자/무늬 분포 확정
- [ ] PURE 보상 특전 후보(선택지 +1, 교체/제거 비용 등) 밸런스 확정
- [ ] 끝까지 순수덱을 지원할 카드 외부 유물/패시브 구조 검토

### 순수카드 → 네임드화 성장
- [x] 동일 랭크+무늬의 순수 슬롯을 네임드 변형으로 교체/진화시키는 로그라이크 성장 방식 우선 검토
- [x] 네임드화해도 해당 카드의 숫자·무늬 분포는 보존
- [x] `교체 / 추가 / 제거`를 서로 다른 덱 성장 수단으로 두고, 교체를 기본 성장축으로 검토
- [x] 모든 순수카드를 네임드화하는 것이 자동 정답이 되지 않도록 순수카드 유지 가치 보존
- [ ] 카드 보상/상점/이벤트에서 슬롯 교체 UI 설계
- [ ] 카드 제거와 네임드 교체의 경제적 가치 비교

### 로그라이크 카드 보상 작업안
- [x] 일반 전투의 기본 보상 후보를 `3장 중 1장 + 건너뛰기` 구조로 검토
- [x] 보상 후보를 `현재 빌드 강화 / 새 방향·혼합 테마 / 범용·기반 보강`의 세 역할로 나누는 방향 기록
- [x] 테마 이름만이 아니라 회수·붙이기·세트·런·정비·러미 등 실제 행동 태그를 보고 보상 가중치를 조정하는 방향 기록
- [x] 새 테마 첫 진입은 초동/기본 엔진 우선, 이후 덱 상태에 따라 엔진/피니셔가 열리는 구조 검토
- [x] 별도 테마 레벨 자원보다 실제 덱에 필요한 초동/전용 개념 생성기가 있는지 검사하는 방식 우선
- [ ] 일반전 / 엘리트 / 보스별 카드 보상 등급과 유물 보상 확정
- [ ] 행동 태그 기반 후보 생성 알고리즘 설계

### 지역 기반 로그라이크 구조 작업안
- [x] `공통 시작 구역 → 지역 분기 → 중간 보스 → 추가 지역 선택 → 후반 특수구역 → 최종 보스`를 기본 맵 흐름 후보로 기록
- [x] 테마군 1개를 지역 1개로 고정하지 않고 `지역 = 공통 문화/환경 + 여러 관련 테마군 + 지역 공용 카드` 구조 우선 검토
- [x] 공통 구역에서 순수 슬롯 개선/범용 네임드/여러 테마 초동을 제공해 빌드 씨앗을 먼저 찾고, 이후 지역이 그 방향을 밀어주는 흐름 기록
- [x] 지역 선택은 특정 테마 강제가 아니라 관련 카드군과 행동 스타일의 등장 가중치를 높이는 방식으로 검토
- [x] 카드 계층을 `전역 범용 → 지역 공용 → 테마군 → 캐릭터 고유`로 나누는 방향 기록
- [ ] 지역 수 / 런 길이 / 지역 방문 횟수 / 노드 비율 확정
- [ ] 지역별 카드 등장 가중치와 타지역 카드 출현률 확정

### 현재 지역 후보 — 모두 후속 설계 대상
- [x] `NEON//ARC 네온아크` — 미디어/방송/SNS/배송/정보 도시. V-SIGNAL + MAIL//ROUTE 중심 후보
- [x] `RED//ZONE 레드존` — 도시전/용병/정찰/돌입 분쟁구역. ZERO//SIGHT + POINT//BLANK 중심
- [x] `IRON//GRAVE 아이언그레이브` — 폐공장/고철/기계 산업폐허. SCRAP//SHIFT 중심 후보
- [x] `OLD//QUARTER 올드쿼터` — 구시가지/탐정/범죄조직/암시장/계약. 향후 탐정·마피아·도둑·밀수·거래 테마 후보
- [x] `NULL//WARD 널워드` — 기록에서 삭제된 격리구역/실험/괴이/변이. 향후 실험체·초능력·저주 계열 및 후반 특수지역 후보
- [ ] 각 지역 세계관 / 지역 공용 카드 / 이벤트 / 엘리트 / 보스 상세 설계
- [ ] 지역 명칭과 지역 수 최종 확정

### 로그라이크 밸런스 검증
- [ ] PURE / 단일 테마 / 2테마 이상 혼합 빌드 각각 클리어 가능성 테스트
- [ ] 순수카드 비율별 세트·런 성공률 / 패말림 / 정비 / 러미 빈도 측정
- [ ] 캐릭터 보상 가중치가 플레이를 유도하되 빌드를 강제하지 않는지 검증
- [ ] 지역 가중치가 선택 의미를 주면서도 예상 밖 혼합 빌드를 막지 않는지 검증
- [ ] 런 후반 덱이 시작 캐릭터와 다른 정체성으로 자연스럽게 변화할 수 있는지 검증

## M12 — Metrics and balance
- [ ] Track turn count, BURST/CHAIN/DETONATE timing, max power, opponent-meld use, multi-attach size, RUMMY, maintenance and intentional bomb acceptance
- [ ] Balance from playtest data before large content expansion

## M13 — Static code split
Only after rules and tests are stable. Keep GitHub Pages buildless.
- [ ] styles.css
- [ ] cards/data JS
- [ ] rules/game JS
- [ ] AI JS
- [ ] UI/progress JS

## Current next work
1. UX1 P1: deterministic 기본 조작 → 세트 → 런 → 붙이기 → 상대 공개 조합 → 스위치 lessons are live; next connect 러미, then move into P2 누적 위력 / 폭발 tutorial.
2. UI2 P2: finish the 360–480px real-device visual check, then defer P3 art/brand polish until gameplay/tutorial UX is steadier.
3. L10N1 + M8: continue remaining text cleanup and named-card choice/copy/timing audit in parallel; do not begin large M9/content expansion until the first ~50 named-card behaviors and UX1 P1 are both stable.