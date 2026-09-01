# RUMMY//DUEL Development Roadmap

Updated: 2026-09-01

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
- [x] When a personal deck empties, recycle that player’s spent pile plus cards in the shared discard currently owned by that player; opponent-owned discard and public meld cards stay in place
- [x] Zero-source circulation safety: one-sided stalls skip acquisition / use legal recovery / release one owned public meld as needed; simultaneous two-sided stalls perform one full current-owner recirculation while preserving CORE and SWITCH state, with a second stall resolved by CORE → current HP → draw
- [x] RUMMY refills 6
- [x] Low-hand protection: with 1–3 cards and only the base discard remaining, the base discard may be skipped; card-effect extra discards are still paid first
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
- [x] Close Vacancy/Rebel Joker self-recovery loops: a Joker added by the current attach cannot auto-replace itself, and any later auto-return is marked recovered for the turn
- [x] Make stuck-state legality include same-RUN continuation after the one physical SWITCH return
- [x] Bind same-turn recovered-card return exceptions to the destination melds authorized by the granting effect
- [x] Harden invalid/legacy selected character progress data
- [x] Unify Black Market discard acquisition path for player/CPU
- [x] Fix CORE LETHAL targeting feedback
- [x] Synchronize Chain Reaction text/implementation
- [x] Implement Last Laugh returning-RUMMY / DETONATE reduction behavior
- [x] Audit RUMMY-linked named cards: Second Heart, Returner, Life Support, Encore, Last Laugh, and grace interactions

## M3 — Regression tests
- [x] Full-recirculation / low-hand / Joker-loop / continuation-legality / destination-bound recovery safety regressions
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
- [x] Verify deck exhaustion/recycling under long games; recycle personal spent + currently-owned cards from shared discard, while preserving opponent-owned discard and all public meld cards
- [x] Close zero-source deadlocks for player/AI/RUMMY and make maintenance recognize currently-owned shared-discard cards as a valid personal recycle source
- [x] Audit player/AI RUMMY turn-end paths; AI now settles contracts before the single turn-end resolution even on RUMMY turns
- [x] Reset transient discard-contract state whenever a card is freshly acquired from deck/discard before source-specific effects are applied
- [x] Add per-battle circulation telemetry at result time: average hand, low-hand rate/skips, RUMMY, maintenance, and full-recirculation counts

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
- [x] Stabilize first ~50 named cards
- [x] First correctness pass: fix CPU new-meld crash, duplicate CJ recovery, Phoenix one-time return, and revive Gap Run / Middle Manager placeholder behavior
- [x] Synchronize deterministic card text for Revenge Blade, Ambulance, Fence, Golden Hand, Money Changer, Recursive Function, Connection Link, Branch Link and Copier
- [x] Keep direct SWITCH manipulation to a minority of the audited pool with an executable ratio guard
- [x] Second correctness pass: activate Death Sentence discard targeting, Tuner cross-meld recovery, role-sensitive Understudy retirement, and executable Doppelganger SET support coverage
- [x] Third timing pass: Recursive Function / Copier ignore unrelated named cards and only copy effects whose current action trigger conditions are actually satisfied
- [x] Repair previous-DETONATE action window so Revenge Blade and Phoenix can trigger on the following owner turn; Phoenix spent return no longer grants its heal before use
- [x] Fix Golden Hand source check so any discard-acquired card in the same meld action can enable its cycle, not only Golden Hand itself
- [x] Fix Smuggled Goods duration: free-suit legality lasts only for the discard-acquisition turn in hand, while a role legally committed to a RUN stays valid until that card leaves the meld
- [x] Remove hand-click order dependency between Buyout King and Golden Hand by resolving discard-origin classification before the dependent Golden Hand check
- [x] Add a shared queued effect-choice modal and migrate Reserved Shipping plus Connector 6+ hand-bottom choice; optional Connector bottoming may be skipped while CPU resolution stays deterministic
- [x] Make named effect choices resumable before attack/RUMMY finalization; Connector 6+ now preserves RUMMY timing, free-recovery effects select a legal owned card, and Recycler selects from spent cards
- [x] Target-choice pass: Extortion now selects the exact legal card to move and Sleeper selects the opponent meld to fix; CPU keeps deterministic first-candidate resolution
- [x] Add an off-turn choice continuation: when CPU takes a human-owned Bait, the owner draws first, chooses the exact hand card to bottom, and CPU play resumes only after that choice resolves
- [x] Final semantics pass A: Insurance Agent only protects cards actually owned by its side, Heart King consumes every stored heart at DETONATE, and any Rebel Joker replacement blocks same-turn return/continuation
- [x] Final choice pass B: Parasite now lets the human owner choose the discard on an opponent-turn return, while CPU action resolution pauses and resumes without granting extra actions
- [x] Final choice pass C: Last Laugh returning-RUMMY now lets the human choose which post-refill card goes to deck bottom, and the RUMMY turn ends only after that mandatory choice resolves
- [x] Final lock audit: explicit player-choice cards use shared/resumable selection; deterministic cards keep explicit oldest/reverse/placeholder wording; legacy first-target/auto-discard paths are rejected by regression
- [x] Finish remaining choice/copy/timing audit and per-card regressions; first ~50 named-card behavior is now locked by executable final-audit coverage
- [x] Favor meld mutation, recovery, movement, discard, defense, RUMMY and timing interactions

## M8A — 정식 테마군 콘텐츠 설계
정식 테마군은 폐쇄형 전용 덱이 아니라 공용 러미 행동과 연결되는 모듈형 카드군으로 설계한다. 현재 최종 설계 기준과 카드 후보 전체는 `docs/THEME_GROUPS.md`를 Source of Truth로 사용한다. 아직 라이브 코드 구현 완료를 의미하지 않는다.

### 공통 설계 잠금
- [x] 카드 도감에 카드군 전용 필터 추가 — V-SIGNAL / ZERO-SIGHT / POINT-BLANK 탭에서 현재 라이브 구현 카드를 분리해 보고, 카드군 탭에서는 미해금 카드도 카드군·이름·효과를 확인하되 실제 해금 조건은 잠금으로 표시
- [x] 별도 개발자 모드 추가 — 현재 구현 콘텐츠의 해금 제한 우회, 개발 중 카드군 선택, 전체 도감 확인을 지원하며 DEV로 시작한 대전은 실제 클리어·레벨·해금 진행도에 반영하지 않음
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
- [x] 새 조합/붙이기/회수/러미/런 완주 이벤트를 공용 효과 엔진에 필요한 만큼 노출
- [x] V-SIGNAL foundation: `themeId`/표시명 메타데이터 + 구독형 공용 이벤트 버스 + 정리 직전 `onRunFinish`/`onRetire` 훅 추가
- [x] 5♥ `앙코르` 라이브 구현 — H5 대체 네임드 변형, 자기 회수 시 다른 합법 조합으로의 반환 재사용을 카드 단위·턴당 1회·목적지 제한으로 허용
- [x] `앙코르` 등 회수 후 동일 턴 반환 예외를 카드 단위로 안전하게 구현
- [x] 4♦ `전원 집합!` / K♣ `24시간 내구방송` 라이브 구현 — 정리 직전 선택형 손패 보존, 일반 카드도 후보 가능, 보존 카드는 해당 턴 재사용 금지
- [x] 버스트 정리/런 완주 직전 카드 보존 타이밍 구현
- [x] V-SIGNAL ↔ 일반 카드 혼합 회귀 테스트

### ZERO-SIGHT — 저격수 / 표적 / 정밀 타격
- [x] 정식 테마 방향 `ZERO-SIGHT` 잠금
- [x] 전용 개념 `표적` 확정 — 자신이 기본 1개 유지, 새 표적 지정 시 기존 표적 해제, 조합 정리 시 제거
- [x] 표적을 생성하는 초동/이전/재지정 카드를 충분히 배치해 초동 안정성 확보
- [x] 표적 조합에 붙이는 카드는 ZERO-SIGHT일 필요가 없도록 혼합 시너지 잠금
- [x] 현재 정식 후보 18장 설계 확정 — 관측/덱 조작/고정·봉인/킬각 보정/준비형 공격/표적 이전 포함
- [x] 공개 조합 단위 표적 메타데이터 및 1개 제한 구현
- [x] 손에서 턴 경과 충전 상태를 카드 단위 `handPrep` 마커로 구현 — 손에 남긴 자기 턴 종료마다 +1, 손을 떠나는 행동에는 그 준비값을 현재 행동 동안만 스냅샷으로 남기고 즉시 초기화, 새로 손에 들어오면 0부터 다시 시작
- [x] 표적 조합 회수/이동/새 조합 생성 반응 이벤트 정리 — `onTargetSet` / `onTargetClear` / `onTargetMeldChange` / `onMeldMove` 추가, 기존 `onMeldCreate` / `onAttach` / `onRecover` 패킷에 표적 스냅샷 노출
- [x] 표적 없이 잡힌 스타터의 대체 패순환 처리 — A♣ `관측수`는 사용 조합을 즉시 표적으로 만들어 초동을 열고 무료 1장 교체를 제공; 2♣ `스코프 조정`은 기존 표적을 다른 공개 조합으로 이전하되 표적이 없거나 이전 목적지가 없으면 정확한 손패 1장 패순환으로 전환
- [x] ZERO-SIGHT 첫 라이브 스타터 페어 — A♣ `관측수` / 2♣ `스코프 조정`을 전체 1클리어 해금으로 추가하고 ZERO-SIGHT 오픈형 테마 선택을 활성화
- [x] 코어+보호막 부족분 공용 계산 + 6♦ `탄도 계산` 라이브 구현 — `coreShieldRequirement` / `coreShieldDeficit` 순수 헬퍼로 현재 코어+보호막 기준 킬각 부족분을 계산하며, 별도 효과 액션/자원은 만들지 않음. 탄도 계산은 표적 반환의 실제 기본 위력·기존 누적·네임드 보정·매복 감소까지 반영한 최종 반환 직전에 부족분만 최대 +12 보정
- [x] K♠ `ONE SHOT` 라이브 구현 — 전체 7클리어 해금. 상대 표적 조합 반환 시 행동 전 기존 누적 위력 50+면 +18, 반환 반응 이벤트가 표적 상태를 모두 관측한 뒤 표적 해제. 50 미만 시 현재 행동의 다른 네임드 순서를 방해하지 않고 반환 후 자신에게 봉인 1
- [x] ZERO-SIGHT ↔ 일반/V-SIGNAL/POINT-BLANK 혼합 회귀 테스트 — 표적은 카드군과 분리된 공개 조합 메타데이터로 유지되며, 일반 카드의 붙이기·V-SIGNAL 앙코르 회수·혼합 조합 정리/보존·POINT-BLANK 카드 정체성이 같은 표적 이벤트 경로에서 충돌하지 않는 것을 실행 회귀로 잠금

### POINT-BLANK — 근접 총격 / 접전 / 교대
- [x] 정식 테마 방향 `POINT-BLANK` 잠금
- [x] 전용 개념 `접전` 확정 — 상대 공개 조합 1개를 지정하고 자신의 카드가 들어가며 유지되는 근거리 전장
- [x] 접전에 진입하는 카드는 POINT-BLANK일 필요가 없도록 혼합 시너지 잠금
- [x] 접전 생성 초동 + 이동 + 회수 + 재돌입 + 패순환의 순환 엔진 확정
- [x] 현재 정식 후보 18장 설계 확정 — 봉인/고정/무료 회수/대상 교대/필드 이동/회수 카드 재배치/근거리 피니시 포함
- [x] 상대 공개 조합 단위 접전 메타데이터 / 1개 제한 / 지연 해제 구현 — 접전은 표적과 분리된 `themeMeta.pointBlank`로 관리하고 상대 공개 조합만 지정 가능; 새 접전은 기존 접전을 이전하며, 자신의 카드가 모두 빠지면 다음 자기 턴 종료를 해제 시점으로 예약하고 그 전에 재돌입하면 예약을 취소함
- [x] 무료 회수와 기본 회수 횟수를 명확히 구분 — 공용 `recoveryAccess`가 `free / reason / consumesBasic`을 반환하고 플레이어·AI·합법성 판정·`onRecover` 이벤트가 이를 공유; 기본 회수를 이미 쓴 뒤에도 조건부 무료 회수는 가능하며 UI도 `무료 회수`와 `기본 회수 사용함`을 구분
- [x] `퀵 리로드` 회수 후 추가 새 조합 예외 구현 — 기존 기본 규칙이 이미 회수 카드를 같은 턴 첫 새 조합에 허용하므로 죽은 효과를 수정; J♦ 변형 `퀵 리로드`는 접전에서 회수했을 때 그 카드를 포함하는 새 3장 조합을 이번 턴 1회 추가로 허용하며, `recoverReturnOverrideToken`은 부여하지 않아 버스트/체인 반환 재사용 금지는 그대로 유지
- [x] 이동 효과 전투 중립 원칙 잠금 — `onMeldMove`는 `combatNeutral / powerDelta:0 / returnsSwitch:false`를 명시하고 공용 `moveCardBetweenMelds`는 조합/CHAIN/메타데이터만 갱신하며 이동 자체로 BURST·CHAIN 위력·SWITCH 반환·자동 정리를 만들지 않음
- [x] 7♥ `엄폐 교대` 적대 대상 교체/fallback 구현 — 접전의 자기 카드가 상대의 직접 간섭 대상일 때 턴당 1회 같은 효과의 다른 합법적인 자기 카드로 교대; 대체 대상이 없으면 보호막 12를 얻고 원래 간섭은 계속 해결
- [x] POINT-BLANK ↔ 일반/V-SIGNAL/ZERO-SIGHT 혼합 회귀 테스트 — 접전/표적 동시 메타데이터, 테마 비의존 이동, V-SIGNAL·일반 카드 대상 교대, 이동 전투 중립을 실행 회귀로 잠금

### 후속 테마 후보 — 아직 상세 확정 전
- [x] `MAIL//ROUTE` 작업안 기록 — 편지/우편 테마, `우편 → 목적지 → 도착 → 반송 → 재배송` 엔진. 일반 카드에도 우편 표식을 붙여 혼합덱 허브로 쓰는 방향
- [x] `SCRAP//SHIFT` 작업안 기록 — 폐품/해체/재조립 테마, 다른 카드도 `부품`으로 바꾸고 회수·소모·이동을 자원화하는 방향
- [x] MAIL//ROUTE 카드 수 / 우편 표식 수명 / 목적지 규칙 / 반송 타이밍 최종 확정 — 28장(수트별 7), 일반 카드에도 붙는 비중첩 `우편`, 손패·공개 조합 사이 유지 후 버림패/소모패/기본 덱 복귀 시 해제, 플레이어당 목적지 1개, 손패→조합·조합→다른 조합을 도착으로 판정, 공개 조합→자기 손 회수를 반송으로 판정, 반송 후 재배송 가능, 동일 카드/효과의 도착·지정 도착·반송은 기본 턴당 1회
- [x] SCRAP//SHIFT 카드 풀과 부품 규칙 상세 재설계 — 24장(수트별 6) 후보 풀, 일반/타 테마의 내 소유 카드에도 붙는 비중첩 `부품`, 손패·공개 조합·소모패 유지 후 버림패/덱 진입 시 해제, 유효성을 보존하는 공개 조합→소모패 `해체`, 전투 중립 공개 조합→공개 조합 `이식`, 소모패→손패 시 표식을 소비하고 당턴 사용을 막는 `재조립`, 기본 턴당 1회 게이트와 RUMMY 선해결 규칙까지 잠금
- [x] 향후 신규 테마는 카드군부터 만들기보다 지역의 문화/직업/갈등에서 파생시키는 방식 우선 검토 — `docs/THEME_GROUPS.md`에 지역/생활권 → 문화·직업 앵커 3+ → 갈등 1+ → 핵심 동사 4+ → 공용 러미 행동 3+ → 기존 테마 중복 검사 → 전용 개념 최소화 → 마지막 네이밍/비주얼 순서의 기획 게이트를 잠금. 실존 지역을 장식적 고정관념으로 소비하지 않고 행동 구조의 근거로 사용

### 구현 전 공통 검증
- [x] M8 첫 ~50 네임드 선택/복사/타이밍 안정화 후 대규모 테마 구현 시작
- [x] 테마 ID/표시명/전용 조합 메타데이터 ↔ 동일 랭크+무늬 슬롯 불변식 검증 — `themeId`는 카드의 정체성 메타데이터일 뿐 `namedSlot`/52슬롯 키를 바꾸지 않으며, 모든 라이브 테마 변형은 정규 슬롯에 귀속됨. ZERO-SIGHT `themeMeta.zeroSight`와 POINT-BLANK `themeMeta.pointBlank`는 같은 공개 조합에서 독립 공존하고 카드 슬롯/소유권을 변경하지 않음을 실행 회귀로 잠금
- [x] 한 행동의 테마 반응 순서 + 턴당 1회 게이트 명문화 — 공용 순서는 `기본 행동 이벤트 → ZERO-SIGHT 표적 변화 → POINT-BLANK 접전 변화 → 반환 후 지연 처리`로 잠금. 이동은 표적 source→target 뒤 접전 source→target 순서. 카드 단위 `themeTurnGates` / `claimThemeTurnGate`가 같은 `turnToken`의 중복 테마 반응을 차단하고 기존 앙코르/퀵 리로드/엄폐 교대 토큰은 호환용으로 유지
- [x] AI 표적·접전·상대 조합 사용·회수 최소 휴리스틱 추가 — 기존 M10 합법성/보드 위험 점수는 그대로 두고 `themeAIAttachBias` / `themeAIRecoveryBias`를 가산층으로 추가. 내 표적 활용, 탄도 계산의 실제 부족분, ONE SHOT 50+ 성공/실패, 내 접전 재진입, V-SIGNAL의 상대 조합 사용(RAID형 진입), 무료 회수·앙코르 재진입·접전 회수 가치를 판단하며 테마 점수가 행동 합법성을 우회하지 않음
- [x] 테마 최대밀도 / 2테마 / 일반 혼합 구성 시뮬레이션 + 직접 위력 비율 검사 — `tests/theme-mix-simulation.mjs`가 라이브/개발 테마별 최대 4장 우선 편성 오픈형 9네임드 빌드, 모든 2테마 조합의 슬롯 충돌 해소, 일반 mixed 다중 시드 표본을 실행 검증. 모든 구성은 `namedSlot` 중복 0을 유지하며 테마 외 카드가 남고, 직접 누적 위력 태그는 전체 네임드 풀 20% 미만·현재 테마 카드 풀 과반 미만으로 잠금

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
- [x] 네임드 카드 설명 — 고급 튜토리얼 마지막에 8♥ `응급 보호구`를 실제 8 세트에 붙이는 실습 추가. 일반 8♥와 동일한 랭크·무늬/버스트 역할을 유지하면서 네임드 고유 효과 보호막 20이 실제 `resolveEffects()`에서 추가되는 구조를 체험하고, 네임드는 별도 카드 종류가 아니라 정규 슬롯의 효과 변형임을 안내
- [x] 테마군 튜토리얼 기반 — `THEME_TUTORIALS` 레지스트리(`themeId/startStep/live`)와 `startThemeTutorial()` 진입, 테마별 가용성 판정, `state.tutorialThemeId`, 테마 전용 단계 배지/완료 문구를 추가. 시작 화면의 `테마 체험전` 버튼은 기본 튜토리얼 완료 + 실제 live 테마 단계 등록 시에만 자동 활성화되어 미구현 체험전을 가장하지 않음
- [x] V-SIGNAL 등 실제 구현된 테마군 체험전 — 첫 live 테마 체험으로 `앙코르 재입장` 고정 시나리오 추가. 실제 V-SIGNAL 5♥ `앙코르`를 5♥-6♥-7♥-8♥ RUN에서 회수한 뒤 같은 턴 상대의 일반 5♠-5♦-5♣ SET에 붙여 BURST +24 / SWITCH 반환까지 수행한다. `expectRecoveredSameTurn`으로 회수 직후 재사용임을 검증하며, 기본 회수 카드의 반환 재사용 금지와 앙코르의 목적지 제한 1회 예외를 실제 엔진 경로로 체험. `THEME_TUTORIALS.v-signal`을 live로 전환해 기본 튜토리얼 완료 후 시작 화면에서 V-SIGNAL 체험전이 자동 활성화됨

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
- [x] 덱 / 공용 버림패 / 개인 소모패의 역할 위계 분리 — 소모패를 직접 조작하지 않는 재순환 대기로 명확화하고, 덱 소진 시 `소모패 + 공용 버림패의 내 소유 카드` 자동 회수·셔플 규칙을 상시 표시하며 데스크톱에서 시각적 비중 축소
- [ ] 360~480px 실제 모바일 폭에서 버튼/상태 문구 잘림 회귀 점검 — 370/390px 정적 fallback과 회귀 테스트 추가, 실기기 시각 검수 남음

### P2.5 — 데스크톱 / 태블릿 반응형
- [x] 기존 480px 모바일 전장을 899px 이하에서 그대로 유지
- [x] 900~1199px에서 상태/스위치를 상단에 두고 상대 손패·드로우 구역을 2열로 사용하는 태블릿/소형 PC 레이아웃
- [x] 1200px 이상 3열 전술 테이블 — 좌측 상대/드로우, 중앙 스위치·공개 조합, 우측 카드 상세, 하단 전체 폭 손패/행동
- [x] 데스크톱에서 상대 손패 카드백·공개 조합·손패 카드를 모바일보다 크게 복원하고 행동 버튼을 3열→6열로 확장
- [x] 시작 화면도 데스크톱에서 480px 고정 셸을 해제하되 메뉴 본문은 읽기 좋은 520~560px로 제한
- [x] 1200px 이상 데스크톱에서는 1440px 상한을 제거하고 `100vw × 100dvh` 전체 전장을 사용하도록 확장
- [x] PC 전용 한국어 산세리프 폰트 스택(Pretendard/Noto Sans KR/Apple SD Gothic Neo/맑은 고딕 fallback)과 주요 HUD·버튼·설명 글자 크기 상향
- [x] PC 전투 화면의 body/page 스크롤 제거 — 상태/전장/손패/접힌 로그를 뷰포트 높이 안의 고정 그리드로 배치하고 상세/공개 조합/열린 로그만 내부 스크롤 허용
- [x] 낮은 PC 뷰포트(`max-height:760px`) 전용 압축 규칙으로 1366×768 계열 브라우저 화면 대응
- [x] 실제 Chromium에서 1366×768 / 1920×1080 시작창·대전 화면 시각 검수 — Noto CJK 한글 실제 글자폭으로 잘림·겹침·가로 오버플로 없음 확인. 1080p의 넓은 공개 조합 여유 공간은 실제 조합 누적을 위한 공간으로 유지하며 추가 간격 조정 불필요

### P3 — 아트/브랜드 마감
- [x] 카드 아이콘/네임드 프레임과 새 UI 팔레트 통일 — 크림 카드 본체는 유지하되 검정/빨강 무늬를 전술 보드 톤으로 조정하고, 네임드는 옛 자주색 `N` 배지 대신 황동 `◆` 표식 + 따뜻한 이중 프레임/이름선으로 통일. 손패·공개 조합·도감 미니카드가 같은 카드 시각 언어를 공유
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
- [x] 카드 효과문의 한영 혼용 제거 — 라이브 네임드 71장 설명의 핵심 규칙 용어를 공식 표기 `세트 / 런 / 붙이기 / 스위치 / 러미 / 폭발 / 버스트 / 체인 / 코어 / 과부하`로 통일. 카드 ID·효과 태그·테마 고유명은 유지하고 사용자 노출 `d:` 설명만 현지화
- [x] 카드 효과 문체 통일 — 사용자 노출 네임드 효과문을 `조건 → 효과` 서술형으로 통일. 의무 효과는 `~한다/얻는다/뽑는다/증가한다`, 선택 효과는 `~할 수 있다`를 사용하고 `+N`, `보호막 N.`, `1장 뽑기.` 같은 단독 축약형과 `폭발를/세트을/세트과` 조사 오류를 제거
- [x] 튜토리얼 용어 반영 — 튜토리얼의 사용자 노출 목표·힌트·실습 로그·성공 문구에서 `RUN / BURST / CHAIN` 혼용을 제거하고 공식 표기 `런 / 버스트 / 체인`으로 통일. `expectMeld:'SET'` 같은 내부 판정 키와 테마 고유명 `V-SIGNAL`은 유지
- [x] 도움말 / 규칙 설명 핵심 용어 반영 + `런 완주` 규칙 동기화
- [x] 시작창 메뉴 한국어화
- [x] 기존 규칙 오버레이의 공식 용어집 갱신
- [x] 중복 / 폐기된 옛 용어 제거 — 브라우저 제목·규칙 오버레이·캐릭터/필드 설명·선택창·연습전/전투 로그에서 남아 있던 `FINAL CORE / SET / RUN / BURST / CHAIN / SWITCH / DETONATE DELAY / OVERLOAD / CORE LETHAL / YOU / CPU` 표시를 공식 한국어 표기로 정리. 브랜드 `RUMMY//DUEL`, 테마 고유명과 내부 엔진 키는 유지
- [x] 모바일 UI에서 긴 한국어 표현 잘림 점검 — 390px 이하에서 전투 배너·효과 선택창·필드 설명·페이즈/스위치 안내·시작 메뉴·모달 버튼의 긴 한국어가 고정 한 줄/flex 최소폭 때문에 잘리지 않도록 줄바꿈·최소폭·최대폭 안전 규칙 추가. 카드명·캐릭터 배지처럼 의도적으로 축약되는 정보 표시는 유지
- [x] 사용자 노출 문자열 회귀 테스트 추가

### 유지할 고유명
- [x] `RUMMY//DUEL` 브랜드 유지
- [x] `V-SIGNAL` 등 테마/세계관 고유명은 실제 구현 시 원문 유지 가능
- [x] 내부 함수/변수명 (`setValid`, `attachCards`, `switchTarget`, `detonate`, `triggerRummy` 등)은 현지화 때문에 일괄 변경하지 않음

## M9 — Jokers and fields
- [x] Finalize distinct Joker identities — J1~J5 keep separate wildcard identities for owner-deck return, RUMMY/DETONATE timing, SET/RUN split payoff, vacancy replacement, and opponent-meld rebellion
- [x] Audit Joker King return-to-owner-deck behavior — public-meld retirement restores `originOwner`, bottoms J1 into that owner deck, and never sends it to spent
- [x] Stabilize 10 behavior-changing shared fields — F1~F10 now cover recovery, discard acquisition, cycling, RUN legality, interference protection, and opponent-meld interaction without adding a new base resource

## M10 — AI 2.0
- [x] Respect recovery same-turn return restriction in planning
- [x] Search 5+ card multi-attach cases where practical — AI extension planning and stuck-state legality now enumerate up to 6-card attach combinations while preserving the existing recovery, same-turn return, and SWITCH ownership guards
- [x] Improve opponent-meld and future-BURST risk evaluation — AI now penalizes exposed 3-card SETs using public hand-count / current SWITCH pressure / top-discard burst access, favors immediate BURST cleanup of opponent SETs, and discounts opponent-controlled RUNs that would be pushed to CHAIN 4+ completion flexibility
- [x] Improve intentional small-bomb acceptance decisions — AI accepts only survivable low-cost bombs that preserve a safe current-CORE reserve, but returns instead when the available extension is high-value or creates immediate lethal pressure on the opponent

## M11 — Deckbuilder
- [x] Player-facing 52-slot deck construction — progress screen now exposes all 52 canonical rank+suit slots; custom mode selects exactly 29 regular slots plus 1 Joker for the existing 30-card battle deck, with per-slot PURE ↔ unlocked NAMED cycling and legacy automatic generation preserved as an opt-in fallback
- [x] One variant per exact rank+suit slot — named variants canonicalize through `namedSlot()`, variant sampling removes every other candidate sharing that base slot, and battle-deck materialization keeps one selected variant per canonical regular slot
- [x] Rank/suit/SET/RUN distribution analysis UI — deckbuilder reports suit counts, all 13 rank counts, 2+/3+ same-rank SET material, 3-card RUN windows, longest same-suit streak, PURE/NAMED split, and invalid 29-slot construction warnings live while editing

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
- [x] PURE도 기본 순환만으로 장기전이 가능하도록 덱 소진 시 소모패 + 공용 버림패의 현재 내 소유 카드를 재순환하는 공통 규칙 적용
- [ ] PURE 시작 덱의 숫자/무늬 분포 확정
- [ ] PURE 보상 특전 후보(선택지 +1, 교체/제거 비용 등) 밸런스 확정
- [ ] 끝까지 순수덱을 지원할 카드 외부 유물/패시브 구조 검토

### 순수카드 → 네임드화 성장
- [x] 동일 랭크+무늬의 순수 슬롯을 네임드 변형으로 교체/진화시키는 로그라이크 성장 방식 우선 검토
- [x] 기본 네임드화는 해당 슬롯의 원본 랭크+무늬를 보존한다. M11B 특수 변형도 52슬롯의 원본 슬롯은 유지하되, 보조 랭크를 하나 추가하는 제한적 예외 후보로 검증한다.
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
- [x] `RED//ZONE 레드존` — 도시전/용병/정찰/돌입 분쟁구역. ZERO-SIGHT + POINT-BLANK 중심
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

## M11B — 비대칭 상·하단값 / 회전 숫자 카드 실험
트럼프 카드가 원래 상단과 하단에 같은 랭크를 반복 표시하는 구조를 카드 설계 축으로 확장한다. 일반 카드는 기존처럼 `X/X`, 일부 특수 네임드만 `X/Y`처럼 서로 다른 두 인쇄값을 가질 수 있다. 핵심은 러미 규칙을 도미노식으로 바꾸는 것이 아니라, 카드를 조합에 사용할 때 인쇄된 두 값 중 하나를 선택할 수 있게 하는 것이다. 현재 세트·런·버스트·체인·스위치 규칙 자체는 그대로 유지하며, 이 단계는 프로토타입·밸런스 검증 대상이다.

### 기본 규칙 후보
- [x] 일반 카드는 `7/7`, `Q/Q`처럼 상단값과 하단값이 동일하며 현행 카드와 완전히 호환
- [x] 일부 특수 네임드에만 `3/7`, `5/K` 같은 비대칭 상·하단값을 허용
- [x] 비대칭 카드를 새 조합 또는 붙이기에 사용할 때 인쇄된 두 값 중 하나를 `사용값`으로 선택
- [x] 세트와 런의 숫자 판정에는 선택한 `사용값` 하나만 적용하고, 기존 동일 숫자 세트 / 연속 숫자 런 규칙은 변경하지 않음
- [x] 카드 한 장이 두 숫자를 동시에 이어 주는 도미노식 `브리지` 판정은 기본 규칙에 넣지 않음
- [x] 조합에 들어간 비대칭 카드는 선택한 사용값과 방향이 고정되며, 그 조합을 떠나 손으로 돌아온 뒤 다시 사용할 때 새로 선택 가능
- [x] 무늬, 소유권, 52슬롯상의 원본 랭크+무늬 정체성은 방향을 바꿔도 변하지 않음
- [x] 비대칭 카드는 와일드처럼 임의 숫자를 선택하는 것이 아니라 카드에 실제 인쇄된 두 값 중 하나만 선택
- [x] 사용하지 않은 반대편 값은 기본적으로 별도 상태·자원·결산값을 만들지 않으며, 필요한 카드 효과만 `다른 인쇄값` 또는 `사용하지 않은 값`으로 직접 참조
- [x] 비대칭값은 모든 네임드의 기본 사양이 아니라 희소한 능력/카드 정체성으로 제한

### 효과 확장 축
- [x] `사용값`, `사용하지 않은 값`, `높은 값/낮은 값 중 무엇을 골랐는지`, `두 인쇄값의 차이`, `양쪽 값 일치 여부`, `카드 방향`을 효과 조건 후보로 사용
- [x] 낮은 값을 골라 조합 안정성을 얻거나 높은 값을 골라 다른 세트·런 경로를 여는 등 두 숫자 사이의 선택 자체를 핵심 재미 후보로 설정
- [x] 반대편 숫자에 공용 보상을 자동으로 부여하지 않고, 카드별 효과가 필요할 때만 참조해 시스템 복잡도와 상위호환 문제를 억제
- [ ] 비대칭값을 실제로 활용하는 네임드 효과 샘플 10~20장 설계
- [ ] 숫자 차이가 큰 카드가 단순 상위호환이 되지 않도록 효과 예산 / 희귀도 / 패널티 기준 수립
- [ ] 순수 `X/X` 카드와 일반 네임드 `X/X`가 비대칭 `X/Y` 카드와 경쟁할 수 있는 유지 가치 설계

### 규칙·엔진 검증
- [ ] 기존 단일 `rank`와 호환되는 `baseRank / topRank / bottomRank / activeRank` 데이터 구조 설계
- [ ] 손에서는 `activeRank` 미확정, 조합 투입 시 확정, 조합을 떠나 손으로 돌아오면 다시 미확정으로 초기화하는 생명주기 명문화
- [ ] 버림패·소모패·덱·재순환처럼 조합 밖 영역에서는 방향 선택 상태를 유지하지 않는 기본안 검증
- [ ] 새 조합 생성·붙이기·다중 붙이기에서 각 비대칭 카드의 사용값 선택 순서와 합법성 미리보기 구조 설계
- [ ] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증
- [ ] A/Q/K 경계와 A-2-3 / Q-K-A / K-A-2 런 특수 규칙에서 비대칭 값 회귀 테스트 추가
- [ ] 조커의 와일드 판정, 기존 숫자 변경 효과, 복사 효과와 비대칭 값이 중첩될 때 우선순위 명문화
- [ ] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계

### UI / 카드 아트 검증
- [ ] 실제 카드 좌상단·우하단 랭크를 서로 다르게 표시하고 180° 회전 선택이 즉시 읽히는 카드 프레임 프로토타입 제작
- [ ] 손패에서 비대칭 카드 선택 시 두 사용값과 각각의 합법 세트/런 후보를 미리보기로 표시
- [ ] 조합에 들어간 뒤에는 선택된 사용값이 어느 쪽인지 회전 상태 또는 작은 방향 마커로 명확히 고정 표시
- [ ] 카드 상세에는 `원본 슬롯`, `두 인쇄값`, 현재 조합에 있을 때의 `사용값`을 구분해 표시
- [ ] 모바일에서 상·하단 숫자가 다른 카드가 단순 오타처럼 보이지 않도록 최초 획득/튜토리얼 설명 설계

### 밸런스 판정 기준
- [ ] 비대칭 카드 0장 / 소수 / 다수 덱의 세트·런 성공률, 패말림, 정비, 러미 빈도 비교
- [ ] 동일 슬롯의 순수 / 일반 네임드 / 비대칭 네임드 선택률을 비교해 비대칭 변형이 자동 상위호환인지 확인
- [ ] 큰 숫자 차이 자체가 덱 안정성을 지나치게 높이는지, 특히 다중 붙이기와 상대 공개 조합 이용에서 성공률 상승폭 측정
- [ ] 프로토타입 결과가 좋으면 M0/M11의 정식 카드 규칙으로 승격하고, 좋지 않으면 소수 카드의 개별 효과 또는 특정 테마 기믹으로 축소

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