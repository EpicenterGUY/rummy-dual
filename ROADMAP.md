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
- [ ] 튜토리얼 전용 고정 게임 상태/손패/드로우 설계
- [ ] 카드 기본 조작 튜토리얼 — 획득/선택/버리기 및 실제 행동 UI 이해
- [ ] 세트 튜토리얼
- [ ] 런 튜토리얼
- [ ] 붙이기 튜토리얼
- [ ] 상대 공개 조합 붙이기 체험
- [ ] 스위치 튜토리얼
- [ ] 러미 튜토리얼
- [x] 튜토리얼 하이라이트 / 가이드 UI 기본 프레임워크 — 화면 흐름 안 coach + 힌트/다음/재시작/종료

### P2 — 폭발/연습/재진입 완성도
- [ ] 누적 위력 / 폭발 튜토리얼
- [ ] 폭발 연출 및 현재 코어 피해 결과 강조
- [ ] 자유 연습전
- [ ] 튜토리얼 완료 상태 저장
- [ ] 튜토리얼 다시 보기
- [ ] 튜토리얼 종료 / 재시작 처리
- [ ] 행동 성공 시 자동 진행, 잘못된 행동은 상태를 망가뜨리지 않고 힌트 제공
- [ ] 세부 애니메이션 / 스위치 이동 / 러미 피드백 보강
- [ ] 모바일 가독성 및 터치 테스트
- [ ] 390px 이하 한국어 버튼/가이드 잘림 회귀 테스트

### P3 — 고급 튜토리얼
- [ ] 회수 / 정비 / 공식 상태 / 조커 고급 튜토리얼
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
- [ ] 상단 상태/캐릭터/메뉴 밀도 축소 및 모바일 우선 재배치
- [ ] 스위치 핵심 정보와 보조 문구를 1차/2차 정보로 분리
- [ ] 공개 조합과 손패 사이 여백·높이·스크롤 밀도 재조정
- [ ] 전투 기록 기본 접힘/요약 방식 검토
- [ ] 선택 가능 카드·붙이기 가능 조합 강조를 발광보다 테두리/위치 변화 중심으로 통일
- [ ] 360~480px 실제 모바일 폭에서 버튼/상태 문구 잘림 회귀 점검

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
1. UI2 P2: after the first casino-tone reset, reduce HUD density and clarify information hierarchy without weakening combat readability.
2. UX1 P1: connect deterministic basic controls → 세트 → 런 → 붙이기 → 상대 조합 → 스위치 → 러미 scenarios to the real engine.
3. L10N1 + M8: continue remaining text cleanup and named-card choice/copy/timing audit in parallel; do not begin large M9/content expansion until the first ~50 named-card behaviors and UX1 P1 are both stable.
