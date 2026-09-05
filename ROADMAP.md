# RUMMY//DUEL Development Roadmap

Updated: 2026-09-02

## Core direction
RUMMY//DUEL is a 1v1 rummy battle game where both players grow one central SWITCH bomb through SET/BURST and RUN/CHAIN, including play on the opponent's public melds.

## M0 — Rule lock
- [x] 3 CORE × 60, no overkill pierce
- [x] SET 3 → BURST READY; fourth suit → +24 and retire
- [x] RUN CHAIN +10 / +15 / +20 / +25; CHAIN 4+ RUN may be voluntarily `런 완주`ed by its controller on their own turn to free the slot, while keeping it allows continued +25 extensions
- [x] One central uncapped SWITCH; 100+ is display-only OVERLOAD
- [x] One normal SWITCH return per turn
- [x] Base new-meld limit: SET/RUN combined, at most two new exact 3-card melds per turn; retirement does not refund this allowance
- [x] Public meld cap 3 per player; when all 3 own slots are full, one older non-fixed own meld may be voluntarily cleaned up once per own turn for +0 power / no SWITCH movement; same-turn-created melds are excluded
- [x] Shared discard has no size cap; base take is top only
- [x] When a personal deck empties, recycle that player’s spent pile plus cards in the shared discard currently owned by that player; opponent-owned discard and public meld cards stay in place
- [x] Zero-source circulation safety: one-sided stalls skip acquisition / use legal recovery / release one owned public meld as needed; simultaneous two-sided stalls perform one full current-owner recirculation while preserving CORE and SWITCH state, with a second stall resolved by CORE → current HP → draw
- [x] RUMMY refills 6
- [x] Low-hand protection: with 1–3 cards and only the base discard remaining, the base discard may be skipped; card-effect extra discards are still paid first
- [x] Shield has no base hard cap and normally expires at the owner's next turn start
- [x] Recovery rule refinement: a card recovered this turn may still be used for a new 3-card meld, maintenance, discard, or non-return effects, but cannot be reused that same turn as material for a BURST/CHAIN/SWITCH-returning attach unless a named effect explicitly grants that exception.

## M0R — 공개 조합 전개 속도 개편: 구현 및 검증
이번 작업은 `ab8578b`를 기준으로 시작했다. 새 라이브 규칙은 공개 최대 3개 / 세트·런 합산 정확히 3장 조합 턴당 최대 2개이며, 생성 횟수를 카드 효과나 슬롯 정리로 늘리지 않는다. **기능 회귀와 CSS viewport 검증을 잠그되 최종 밸런스 확정은 보류**한다. 상세 감사·방법·한계는 `docs/M0R_MELD_EXPANSION.md`를 따른다.

- [x] 공개 조합 3슬롯 구현 — 플레이어/상대 모두 네 번째 생성 거부, 정리된 슬롯 즉시 재사용
- [x] 턴당 새 조합 2개 구현 — 세트+세트, 세트+런, 런+런 허용; 세 번째 거부; 빈 슬롯과 턴 생성 횟수는 별도 제약
- [x] 신규 자기 조합 당턴 붙이기 확장 금지 유지 — 단일/다중 붙이기, AI 탐색, 합법 행동 판정 모두 검사
- [x] 시작 손패 8 + 획득 1 및 첫 2조합 후 3장 유지 실행 검증; 비교 시드 초반 전투 시뮬레이션은 `experiments/m0r-opening-tempo.mjs` 및 `docs/M0R_TEMPO_RESULTS.json`
- [x] 런타임 네임드 71종(개발자 전용 포함)의 다음 일반 조합 이벤트 비재발동 감사; 겁쟁이 왕/카지노 첫 조합·턴 게이트 검증; 퀵 리로드는 추가 생성 대신 회수 후 합법 새 조합에서 보호막 8·카드당 턴당 1회로 개편
- [x] AI 3슬롯/2생성 반영 — 두 조합을 보존하는 제한된 선행 탐색, 긴급 반환 우선, 빈 슬롯이 있을 때 회수→재편성 평가, 만원일 때 런 완주; 행동 예산 연습 4/일반 6
- [x] 360×800 / 390×844 / 430×932 / 768×1024 / 852×744 / 1024×768 / 1366×768 / 1920×1080 Chromium CSS viewport 검사 — 양쪽 각 13장 런 3개, 가로 viewport 이탈 없음; 긴 런 로컬 스크롤, 1·2·3 바로 보기, Fold 카드 최소 44px. `docs/M0R_LAYOUT_RESULTS.json`
- [x] 튜토리얼·도움말·버튼·README의 생성/슬롯 문구 갱신; 카드군 이름은 하이픈 사용
- [x] 실행 회귀 — 전체 `tests/*.mjs` 125개 파일 통과. 생성 1·2 허용/3 거부, 슬롯 3 허용/4 거부, 당턴 확장 금지, 기존 확장·회수·러미·버스트·체인·반환·런 완주·퀵 리로드 포함
- [x] TWELVE-BLOOM 영향 1차 검토 — 당시 HWA-TU 후보의 계절맞춤을 일반/테마 혼합 공개 카드에서 관측; 추가 생성 보너스 금지. 이후 TWELVE-BLOOM으로 이름과 규칙을 재잠금
- [ ] Android/iOS/Fold 실기기 터치·안전영역 확인
- [ ] 인간 실전/M12로 최종 체감 밸런스 잠금 판단 — TWELVE-BLOOM 실제 효과 구현과 5,500전 프리라이브 엔진 검증은 완료했지만 인간 플레이 표본은 별도 수집

## M0S — 기본 행동 단순화 / 3슬롯 필드 정리 — 2026-09-04
- [x] 기존 M0R의 공개 조합 3칸 / 새 조합 2회 / 신규 자기 조합 당턴 확장 금지 / 시작 손패 8장을 유지
- [x] 기본 붙이기를 전역 턴당 1회로 단순화하고, 한 행동의 다중 카드 런 확장에 체인 위력을 순서대로 합산
- [x] `canContinueReturnedRun` / `returnAttachToken` / 조합별 `lastAttachToken` 기반 같은 RUN 연속 붙이기 기본 예외 제거
- [x] 5♣ `연결고리`를 명시적인 「추가 붙이기 1회」 네임드로 재설계하고, 반역자 조커는 추가 붙이기 허용을 제거하는 카운터로 재설계
- [x] 자기 공개 조합 3칸이 모두 찼을 때만 턴당 1회 가능한 `조합 정리` 구현 — 당턴 생성/고정 조합 제외, 보호는 방해하지 않음, 일반 `onRetire`/`retireMeld` 경로 사용, 위력 +0 / SWITCH 이동 없음
- [x] AI가 기본 붙이기 1회와 다중 붙이기를 공유하고, 만원 상태에서 새 조합 후보가 있을 때 낮은 가치의 CHAIN 0 런을 우선 정리하되 버스트 준비 세트·성장 RUN은 보존하도록 평가
- [x] 전투 버튼/규칙·용어/튜토리얼/연습전 문구를 「새 조합 두 번 · 붙이기 한 번 · 내 필드 세 칸」으로 동기화
- [x] V-SIGNAL / ZERO-SIGHT / POINT-BLANK / MAIL-ROUTE / SCRAP-SHIFT의 회수·이동·추가 행동 경로가 전역 붙이기 횟수를 우회하지 않도록 감사; CYCLE-WORKS 후보와 당시 후보 단계의 TWELVE-BLOOM도 추가 기본 생성 보너스를 요구하지 않는 정책 유지
- [ ] Android/iOS/Fold 실기기 터치·안전영역 재확인 — 소스/브라우저 회귀와 별개인 실기기 검증

## M1 — Final rules ↔ live code sync
- [x] Remove free RUN retirement
- [x] Remove free public-meld disposal
- [x] Remove discard five-card cap
- [x] Make AI respect the three-meld cap
- [x] Audit remaining code-only base rules: remove the hidden shield-40 cap, obsolete retire/draw-preview routes, and superseded generic RUMMY flags; clarify Roundabout against the recovery-return guard
- [x] Add conditional RUN completion: controller-only at CHAIN 4+, no bonus power/SWITCH movement, slot opens immediately, continuation remains +25 if not completed; AI and stuck-state logic respect it

## M2 — Confirmed bug fixes
- [x] Close Vacancy/Rebel Joker self-recovery loops: a Joker added by the current attach cannot auto-replace itself, and any later auto-return is marked recovered for the turn
- [x] Make stuck-state legality use the global base attach count; repeated attach exists only when a named effect explicitly grants an extra attach
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


## M4B — 덱 조합 구조 축: 세트 / 런 / 혼합
테마 카드군은 **효과 빌드**, 조합 구조는 **숫자·무늬 골격 빌드**로 분리한다. 자동 덱은 먼저 29개 물리 슬롯의 조합 골격을 만든 뒤 그 안에 해금 네임드/테마 변형을 배치한다. 자세한 기준은 `docs/DECK_STRUCTURE_PROFILES.md`를 따른다.

- [x] 대전 준비에 `세트형 / 런형 / 혼합형` 독립 선택 축 추가 — 카드군 선택과 별개로 저장
- [x] 세트형 29슬롯 골격 — 7개 중심 랭크를 4무늬로 겹치고 1장 보조 슬롯을 더해 세트/버스트 재료 밀도 우선
- [x] 런형 29슬롯 골격 — 2개 무늬 13연속 + 제3무늬 3연속으로 런/체인 재료 밀도 우선
- [x] 혼합형 29슬롯 골격 — 1개 무늬 13연속 + 4개 교차 랭크의 타 무늬 + 보조 연속 구간으로 세트/런 전환점 확보
- [x] 골격 → 네임드/테마 변형 순서로 자동 덱 생성 변경 — 선택 테마는 최대 4장, 물리 슬롯 중복 금지 유지
- [x] 커스텀 덱 `추천 29슬롯 복원`이 현재 선택 조합 구조를 사용하도록 연결
- [x] 6장 손패 표본 기반 세트/런/둘 중 하나 성립률을 덱 분석에 표시
- [x] 구조별 자동 덱·테마 혼합·진행도 저장·전체 회귀 테스트 추가
- [ ] 인간 실전 및 M12 전투 기록으로 구조별 승률/러미율/저손패 정체율을 비교해 최종 골격 수치 조정

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
- [x] V-SIGNAL 24/24 풀 카드군 구현 — 정식 후보 24장 전부를 실제 NAMED 변형·공용 효과 엔진·해금·도감/덱빌더에 연결. HYPE 같은 전용 숫자 자원 없이 세트·런·붙이기·회수·정비·이동·러미·공식 상태를 재사용하고, 자동 테마 빌드 최대 4장 및 확장형 2테마 조합 회귀를 함께 잠금

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
- [x] `퀵 리로드` 회수 후 재편성 보상 — M0R에서 추가 새 조합 예외를 제거하고, 접전에서 회수한 턴 합법적인 새 조합에 쓰면 보호막 8·카드당 턴당 1회로 변경. 생성 최대 2회·공개 최대 3개·반환 재사용 제한 유지
- [x] 이동 효과 전투 중립 원칙 잠금 — `onMeldMove`는 `combatNeutral / powerDelta:0 / returnsSwitch:false`를 명시하고 공용 `moveCardBetweenMelds`는 조합/CHAIN/메타데이터만 갱신하며 이동 자체로 BURST·CHAIN 위력·SWITCH 반환·자동 정리를 만들지 않음
- [x] 7♥ `엄폐 교대` 적대 대상 교체/fallback 구현 — 접전의 자기 카드가 상대의 직접 간섭 대상일 때 턴당 1회 같은 효과의 다른 합법적인 자기 카드로 교대; 대체 대상이 없으면 보호막 12를 얻고 원래 간섭은 계속 해결
- [x] POINT-BLANK ↔ 일반/V-SIGNAL/ZERO-SIGHT 혼합 회귀 테스트 — 접전/표적 동시 메타데이터, 테마 비의존 이동, V-SIGNAL·일반 카드 대상 교대, 이동 전투 중립을 실행 회귀로 잠금

### 후속 테마 후보 — 아직 상세 확정 전
- [x] `MAIL-ROUTE` 작업안 기록 — 편지/우편 테마, `우편 → 목적지 → 도착 → 반송 → 재배송` 엔진. 일반 카드에도 우편 표식을 붙여 혼합덱 허브로 쓰는 방향
- [x] `SCRAP-SHIFT` 작업안 기록 — 폐품/해체/재조립 테마, 다른 카드도 `부품`으로 바꾸고 회수·소모·이동을 자원화하는 방향
- [x] MAIL-ROUTE 카드 수 / 우편 표식 수명 / 목적지 규칙 / 반송 타이밍 최종 확정 — 28장(수트별 7), 일반 카드에도 붙는 비중첩 `우편`, 손패·공개 조합 사이 유지 후 버림패/소모패/기본 덱 복귀 시 해제, 플레이어당 목적지 1개, 손패→조합·조합→다른 조합을 도착으로 판정, 공개 조합→자기 손 회수를 반송으로 판정, 반송 후 재배송 가능, 동일 카드/효과의 도착·지정 도착·반송은 기본 턴당 1회
- [x] SCRAP-SHIFT 카드 풀과 부품 규칙 상세 재설계 — 24장(수트별 6) 후보 풀, 일반/타 테마의 내 소유 카드에도 붙는 비중첩 `부품`, 손패·공개 조합·소모패 유지 후 버림패/덱 진입 시 해제, 유효성을 보존하는 공개 조합→소모패 `해체`, 전투 중립 공개 조합→공개 조합 `이식`, 소모패→손패 시 표식을 소비하고 당턴 사용을 막는 `재조립`, 기본 턴당 1회 게이트와 RUMMY 선해결 규칙까지 잠금
- [x] `TWELVE-BLOOM` 정식 후보 정비 — 구 HWA-TU 이름을 폐기하고 12달/계절 카드 모티브를 유지하되 사전 화투 용어 없이 `달 / 계절맞춤 / 붉은 띠 / 풀빛 띠 / 푸른 띠 / 새 셋 / 빛 셋 / 윤달`만 사용. `docs/TWELVE_BLOOM_DESIGN.md`
- [x] TWELVE-BLOOM 기본 판정 잠금 — A~Q=1~12월, K는 효과로 지정한 공개 카드 1장만 윤달. K의 실제 랭크/수트와 SET/RUN 판정은 유지하며 윤달은 계절맞춤의 빠진 달 1개만 대체, 그림맞춤 대체 불가. 조커는 기본적으로 달/그림 재료가 아님
- [x] 계절맞춤 / 그림맞춤 구조 잠금 — 봄 1·2·3 / 여름 4·5·6 / 가을 7·8·9 / 겨울 10·J·Q를 넓은 엔진 조건으로 사용. 그림맞춤은 A♥·2♥·3♥ / 4♥·5♥·6♥ / 7♥·8♥·9♥ / 2♦·4♦·8♦ / A♠·8♠·Q♠의 정확 슬롯 5종만 사용
- [x] TWELVE-BLOOM 혼합덱 규칙 잠금 — 카드군과 무관하게 양측 공개 조합의 `내 소유 카드`를 달/그림 재료로 사용. 손패/덱/버림패/소모패/상대 소유 카드는 제외하고, 지속 완성은 재발동하지 않으며 같은 맞춤은 한 턴 재완성 보상 1회로 제한
- [x] TWELVE-BLOOM 24장 정식 후보 풀 재설계 — 수트별 6장. ♣ 탐색/패순환/윤달, ♥ 띠/생존/회수, ♦ 새/이동/상대 조합, ♠ 빛/압박/반환. 직접 누적 위력은 10♠ 낙조 +10 / Q♠ 빛 셋 +14 두 장만 사용
- [x] TWELVE-BLOOM 1차 엔진 기반 — A~Q 달 매핑, 양측 공개 조합의 내 소유 카드 수집, 4계절/5그림 evaluator, 전후 snapshot diff, owner+match 턴 게이트, 공개 K 1장 윤달 지정/재지정 및 손패·덱·버림패·소모패·정리 이탈 시 자동 해제. 이 기반 단계에서는 비라이브로 유지
- [x] TWELVE-BLOOM 상황형 미리보기 기반 — 비채용 전투에서는 항상 숨김. 향후 관련 카드가 존재할 때 선택 중 새 조합/붙이기/회수의 최종 공개판을 투영해 `완성`, `해제`, `2/3 + 빠진 달/정확 슬롯`만 얇은 보조줄로 표시하며 긴 조합 폭을 늘리지 않음
- [x] TWELVE-BLOOM 24/24 효과 구현 — 4개 수트 각 6장 전부를 당시 비라이브 NAMED 변형·공용 효과 엔진에 연결하고, 교차 이동 정비 / 상대 조합 진입 보호 / 봉인·보호 분기 / 빛 셋 방어 / 행동 전 빛 셋 반환 +14까지 `tests/twelve-bloom-fourth-slice.mjs`로 잠금. 라이브 승격 전까지 일반 해금·보상은 차단
- [x] TWELVE-BLOOM 라이브 전 DEV 통합 — 당시 `live:false` 자동 빌드 프로필 / 6단계 staging 해금안 / DEV 도감·덱빌더 / 24장 AI·로그라이크 행동 태그 / entry-payoff 분류 / 실제 `onBloomMatchChange` 봄맞춤 체험전을 연결. `tests/twelve-bloom-staging-integration.mjs`로 프리라이브 일반 모드 0장 노출과 DEV 경로를 잠금
- [x] TWELVE-BLOOM UI/UX 구현 검증 — 비채용 덱은 달/그림 정보를 숨기고, 관련 선택에서만 완성/해제/2·3 힌트를 표시. 긴 공개 런은 `.meldCardRow` 로컬 가로 스크롤을 유지하고 preview chip은 별도 wrap. `tests/twelve-bloom-preview.mjs`
- [x] TWELVE-BLOOM 밸런스/회귀 검증 — TWELVE 포함 6테마 최대밀도/모든 2테마 구성 회귀와 실제 엔진 5,500전 완료. mixed 전투 길이 52.49→52.55로 사실상 동일, RUN의 장기 순환은 일반 RUN 기준선에서도 확인되어 TWELVE 고유 문제가 아니며, 10♠/Q♠ 직접 보너스는 전체 반환의 0.06~0.37회/100반환 수준. full recirculation 0. `docs/TWELVE_BLOOM_BALANCE_RESULTS.md`
- [x] TWELVE-BLOOM 일반 라이브 승격 — 2026-09-05 프리라이브 PASS 뒤 theme/build/tutorial을 `live:true`로 전환하고 기존 6단계 해금안을 정식 `UNLOCK_GROUPS`에 편입. 전체 1~6클리어에서 4장씩 누적 24장을 해금하며, 일반 자동 덱·커스텀 덱·도감·테마 체험전과 `unlockedNamed()` 기반 로그라이크 보상에 별도 예외 없이 연결. 카드 수치와 기본 RUMMY//DUEL 규칙은 변경하지 않음. `tests/twelve-bloom-staging-integration.mjs`
- [x] 향후 신규 테마는 카드군부터 만들기보다 지역의 문화/직업/갈등에서 파생시키는 방식 우선 검토 — `docs/THEME_GROUPS.md`에 지역/생활권 → 문화·직업 앵커 3+ → 갈등 1+ → 핵심 동사 4+ → 공용 러미 행동 3+ → 기존 테마 중복 검사 → 전용 개념 최소화 → 마지막 네이밍/비주얼 순서의 기획 게이트를 잠금. 실존 지역을 장식적 고정관념으로 소비하지 않고 행동 구조의 근거로 사용

### 구현 전 공통 검증
- [x] M8 첫 ~50 네임드 선택/복사/타이밍 안정화 후 대규모 테마 구현 시작
- [x] 테마 ID/표시명/전용 조합 메타데이터 ↔ 동일 랭크+무늬 슬롯 불변식 검증 — `themeId`는 카드의 정체성 메타데이터일 뿐 `namedSlot`/52슬롯 키를 바꾸지 않으며, 모든 라이브 테마 변형은 정규 슬롯에 귀속됨. ZERO-SIGHT `themeMeta.zeroSight`와 POINT-BLANK `themeMeta.pointBlank`는 같은 공개 조합에서 독립 공존하고 카드 슬롯/소유권을 변경하지 않음을 실행 회귀로 잠금
- [x] 한 행동의 테마 반응 순서 + 턴당 1회 게이트 명문화 — 공용 순서는 `기본 행동 이벤트 → ZERO-SIGHT 표적 변화 → POINT-BLANK 접전 변화 → 반환 후 지연 처리`로 잠금. 이동은 표적 source→target 뒤 접전 source→target 순서. 카드 단위 `themeTurnGates` / `claimThemeTurnGate`가 같은 `turnToken`의 중복 테마 반응을 차단하고 기존 앙코르/퀵 리로드/엄폐 교대 토큰은 각 카드의 회수/보상/교대 게이트로 유지
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

## UX2 — 일반 UI 단순화 / DEV UI 분리 / 로그라이크 단계형 진입
- [x] 일반 메인을 대전 / 로그라이크 / 튜토리얼 / 카드 도감 / 설정의 5개 진입점으로 정리하고 필요한 시점에 선택을 공개한다.
- [x] 대전의 캐릭터·덱 방향 선택을 단계화하고, 자유 연습·고급/테마 튜토리얼은 튜토리얼 하위로 이동한다.
- [x] 로그라이크 계속하기 / 새 게임 / 기록과 스타터 → 현재 전투·지역·보상 흐름을 기존 런 저장에 연결한다.
- [x] 테스트 보상·런 덱 실험·개발 카드군·진행도 조작을 DEV로 분리하고 DEV 선택·런·완료 기록을 일반 저장에서 격리한다.
- [x] 플레이어용 표시 설정과 일반/DEV 도감 구분을 구현한다.
- [x] 저장 격리·진입/복귀 회귀 및 360/390/480/Fold/태블릿/1366×768/1920×1080 레이아웃을 검증한다.

구현/저장 경계는 `docs/UX2_PROGRESSIVE_DISCLOSURE.md`, 브라우저 CSS 뷰포트 51개 측정은 `docs/UX2_LAYOUT_RESULTS.json`, 실행 회귀는 `tests/ux2-menu-isolation.mjs`를 참고한다. 실기기 안전 영역 검증과 M11A 상점·이벤트·엘리트 연결은 별도 미완료 항목으로 유지한다.

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
- [x] 360~480px 라이브 Chromium 폭에서 버튼/상태 문구 잘림 회귀 점검 — Chrome DevTools 모바일 viewport로 Noto CJK 실제 한글 글자폭의 360/370/390/430/480 CSS px 시작창·전투 화면을 검사해 문서 가로 오버플로와 핵심 패널 viewport 이탈 0건 확인. 360/390/480px 대표 화면은 스크린샷으로 추가 검수
- [ ] Android/iOS 실제 물리 기기 최종 확인 — 브라우저 주소창·safe-area·시스템 글꼴/확대 설정까지 포함한 마지막 실기기 확인만 남음

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
- [x] 시작창/결과창/도감의 시각 언어 통일 — 시작 히어로는 종이/황동 포인트, 메뉴·결과·도감 인터랙션은 슬레이트/청록 표면으로 통일하고 해금·필드 정보에만 절제된 황동 강조를 사용
- [x] 튜토리얼 coach를 동일한 전술 보드 톤으로 최종 마감 — coach/힌트/연습 안내를 슬레이트 보드와 청록·황동의 낮은 채도 강조로 통일하고, 단계 배지·버튼·타겟 강조에서 네온/강한 픽셀 그림자를 제거
- [x] V-SIGNAL 등 테마군은 기본 UI 위에 테마 포인트만 얹고 카지노형 네온 남발 금지 — 공통 전술 보드/카드 표면은 유지하고 V-SIGNAL 자주·ZERO-SIGHT 청회·POINT-BLANK 황동 포인트를 시작 밑줄, HUD 배지, 테마 선택 카드, 네임드 ◆ 표식에만 제한. 테마별 배경 교체·광원·애니메이션은 사용하지 않음

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


## M8T — 기존 3테마 60장 통합 · 완료
V-SIGNAL 24장 + ZERO-SIGHT 18장 + POINT-BLANK 18장의 개별 구현 뒤, 실제 일반 플레이 풀로 승격하는 통합 단계다.

- [x] 60장 전체를 해금 이후 일반 로그라이크 보상 후보로 승격 — 임시 `rewardPool:false` staging 제거
- [x] POINT-BLANK 일반 카드군 선택 활성화 — V-SIGNAL / ZERO-SIGHT / POINT-BLANK 3테마 모두 일반 빌드 가능
- [x] 카드 도감의 3테마 탭에서 각 24 / 18 / 18 전체 효과 사전 확인 유지
- [x] ZERO-SIGHT `관측수 · 표적 지정` 체험전 추가
- [x] POINT-BLANK `브리치 실드 · 접전 진입` 체험전 추가
- [x] 테마 체험전 선택 UI 추가 — 여러 라이브 테마를 각각 직접 시작 가능
- [x] 네온 아크 적 덱을 V-SIGNAL 풀 카드로 재편
- [x] 레드 존 적 덱을 ZERO-SIGHT + POINT-BLANK 혼합 풀로 재편
- [x] 기존 해금 단계는 유지해 초반 카드 폭증을 방지하고, 해금된 카드만 보상/덱빌더에 진입
- [x] 60장 직접 위력 비율·물리 슬롯 유일성·테마 혼합 회귀 유지
- [x] 전체 `tests/*.mjs` 회귀 통과

## M8MR — MAIL-ROUTE 28/28 풀 카드군 · 완료
우편 표식과 공개 조합 목적지를 이용하는 이동·회수형 오픈 테마. 일반/다른 테마 카드도 발송할 수 있고 전용 숫자 자원은 만들지 않는다.

- [x] 28장 / 수트별 7장 정식 후보 명단 잠금
- [x] `우편` 비중첩 표식 + 발송자 기록 + 수명 주기 구현
- [x] 플레이어당 목적지 1개 + 표적/접전 독립 공존
- [x] 새 조합·붙이기·조합 이동의 도착/지정 도착 파생 이벤트 구현
- [x] 공개 조합→자기 손 회수의 반송 이벤트 + 재배송 예외 구현
- [x] 28장 전체 정의/효과/해금/도감/덱빌더/체험전 연결
- [x] 플레이어 선택은 공용 재개형 선택 UI, AI는 동일 합법 후보 사용
- [x] 일반 로그라이크 보상 해금 후 허용, 기존 고정 지역 적 덱은 유지
- [x] MAIL-ROUTE 단일/2테마/일반 혼합 + 전체 회귀

## M8SS — SCRAP-SHIFT 24/24 풀 카드군 · 완료
부품 표식을 일반/다른 테마의 내 소유 카드에도 붙여 해체·이식·재조립하는 순환형 오픈 테마. 24장 전체 효과·해금·도감·자동 빌드·체험전·일반 보상까지 라이브 통합했다.

- [x] `SCRAP-SHIFT` 테마 레지스트리 추가 및 최종 `live:true` 승격
- [x] `부품` 비중첩 카드 표식 + 손패/공개 조합/소모패 유지 + 버림패/개인 덱 진입 시 정리 기반 구현
- [x] 공용 파생 이벤트 `onPartSet` / `onDismantle` / `onReassemble` 추가
- [x] 해체 공용 헬퍼 — 조합 유효성 유지, RUN 체인 -1, 회수와 분리, 전투 중립, 표적→접전 갱신
- [x] 재조립 공용 헬퍼 — 소모패 부품→손패, 표식 소비, 같은 턴 조합/버리기/정비 금지
- [x] 부품 표식 UI 추가 — 테마 카드 여부와 무관하게 실제 카드에 `부품` 표시
- [x] AI 기본 버리기/정비가 재조립 잠금 카드를 자발적으로 소비하지 않도록 공용 잠금 적용
- [x] 1차 수직 슬라이스 4장 — A♦ 부품 라벨 / 2♣ 컨베이어 / 4♥ 수리 키트 / A♠ 분해 드라이버. 부품 지정·이식·재조립·해체를 DEV 전용 카드로 실제 행동 경로에 연결
- [x] 2차 반응 슬라이스 4장 — 3♦ 분류대 / 6♣ 호환 포트 / 6♥ 재생 공방 / 5♠ 폐기 명령. `onPartSet`·`onMeldMove`·`onReassemble`·`onDismantle` 수동 반응과 턴당 1회 게이트 연결
- [x] 무료 패순환으로 개인 덱에 들어가는 부품도 표식을 해제하도록 수명주기 누락 경로 보정
- [x] 3차 유틸리티 슬라이스 4장 — 5♦ 표준 규격 / 4♣ 임시 용접 / 2♥ 자석 회수기 / 10♠ 과열 부품. 부품 상태의 세트 진입·런 보호·무료 회수·반환 취약을 실제 행동 경로에 연결
- [x] 4차 수명주기 슬라이스 4장 — 7♦ 예비 나사 / 8♣ 분기 레일 / 8♥ 예비 섀시 / 7♠ 파쇄기. 버림패 기동·세트↔런 이식·상대 효과 소모 추적·대체 부품 지정을 공용 부품 수명주기에 연결
- [x] 5차 교차행동 슬라이스 4장 — 9♦ 교환 규격 / 10♣ 모듈 버스 / 10♥ 리퍼비시 / 3♠ 볼트 커터. 정비 후 추가 순환·RUN 유지 보상·러미 후 선택 재조립·적대 이동/소모 보호를 기존 공용 행동 경로에 연결
- [x] 6차 피니셔 슬라이스 4장 — J♦ 메인 프레임 / Q♣ 조립 라인 / K♥ 테세우스 프레임 / K♠ 스크랩 폭주. 버스트 정리·새 RUN·턴 행동 종류·반환 시점을 공용 이벤트/행동 경로에 연결
- [x] 과열 부품의 같은 턴 취약 중복 적용을 공용 테마 턴 게이트로 차단
- [x] 24장 / 수트별 6장 정의 및 실제 효과 구현
- [x] 이식 카드군 효과를 기존 `onMeldMove` 공용 이동과 연결
- [x] 해금·도감·자동 테마 빌드·체험전 연결 후 일반 보상 승격 — 전체 1~6클리어 4장씩 단계 해금, 부품 라벨 체험전, 아이언그레이브 보상 가중치 연결
- [x] SCRAP-SHIFT 단일/모든 2테마/일반 mixed + 전체 회귀 — 자동 빌드 4장 상한/9장 혼합/물리 슬롯 배타성 유지

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
캐릭터/테마/지역/보상까지 포함한 전체 작업안은 `docs/ROGUELIKE_MASTER_PLAN.md`에 보존한다. 기존 스타터 상세는 `docs/ROGUELIKE_DECK_STARTERS.md`를 참고한다. 현재는 공통 시작 → 첫 지역 3연전·중간 보스 → 미방문 지역 선택 → 두 번째 지역 3연전·중간 보스 → 널워드 2교전·최종 보스 → 마지막 보상·런 완료까지 이어지는 14전투 프로토타입을 구현했다. 최종 런 길이, 적/보스 난도, 드롭 확률과 경제 수치는 검증 후 확정한다.

### 캐릭터와 카드군
- [x] 캐릭터는 특정 테마/카드군 사용을 강제하는 클래스 잠금이 아니라 런의 출발 방향으로 설계
- [x] 캐릭터별 시작 효과카드 일부 + 순수 트럼프 다수의 혼합 스타터 방향 잠금
- [x] 캐릭터별 카드 보상 가중치/고유 패시브 후보로 성향을 주되 다른 테마 획득은 항상 허용
- [x] 시작부터 완성된 테마 콤보를 지급하지 않고 런 중 덱 정체성이 변화하도록 설계
- [x] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정
  - 모든 스타터는 v1에서 30장(정규 슬롯 29 + 조커 1)으로 시작한다. 일반 4스타터는 순수 23 + 네임드 정규 6 + 네임드 조커 1, PURE는 효과카드 0장을 유지한다.
  - 유랑자/수집가/회수꾼/광대의 기존 `weights`를 `character-tendency-score-v1` 보상 후보 랭킹 가중치로 잠근다. 이는 확률표나 카드군 잠금이 아니며 다른 테마 후보를 제외하지 않는다.
  - v1 스타터 직접 전투 패시브는 전원 `none`으로 잠근다. 캐릭터 차이는 시작 네임드 구성과 소프트 보상 랭킹에서 만들고 실제 등장 확률/희귀도는 후속 경제 데이터에서 정한다.
- [x] 캐릭터별 실제 시작 네임드 6 + 조커 1 조합 확정
  - 유랑자: `H2 귀환자 / C5 연결고리 / S10 폭주기관차 / D2 외상 거래 / C6 중간관리자 / H10 연명 + J1 광대왕 조커`.
  - 수집가: `S9 잠복자 / H7 행운의 일곱 / H8 응급 보호구 / H9 보험설계사 / D7B 감정사(D7 슬롯) / D8 환전상 + J3 쌍면 조커`.
  - 회수꾼: `S3 쥐구멍 / S4 미끼 사냥꾼 / D3 사기 계약서 / D7 황금손 / C7 기생충 / H3 미끼 + J4 빈자리 조커`.
  - 광대: `C8 복사기 / D6 예약 발송 / D5 위조범 / D4 밀수품 / C4 샛길 / C3 밀수업자 + J5 반역자 조커`.
  - 네 스타터의 v1 시작 네임드는 서로 정확한 카드 ID를 공유하지 않고, 테마 전용 `themeId` 카드도 넣지 않는다. 현재 캐릭터 성향 점수에서 각 구성은 자기 캐릭터 점수가 다른 캐릭터보다 가장 높도록 회귀로 검증한다.
- [x] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계 — 일반 1대1의 캐릭터/테마/30장 덱 선택과 로그라이크 스타터를 분리하고 `유랑자 / 수집가 / 회수꾼 / 광대 / PURE` 전용 선택 UI를 추가. `rummyDuelRoguelikeRunDraftV1` 저장 초안은 공통 시작 구역, 빈 지역 경로, 카드군 하드잠금 없음, 원본 랭크+무늬 슬롯 정체성과 v1 30장 스타터 계약을 기록한다. 일반 4스타터는 순수 23 + 네임드 정규 6 + 네임드 조커 1, PURE는 순수 정규 29 + 기본 와일드 조커 1이며 직접 전투 패시브는 전원 없음. 실제 보상 등장 확률만 후속 밸런스로 남기고 일반 대전과 별개인 로그라이크 런 전투로 연결

### PURE — 온리 순수 스타터
- [x] `PURE`는 별도 테마군이 아니라 효과카드 0장으로 시작하는 백지형 스타터/빌드 경로로 확정
- [x] 순수카드는 효과가 없어도 숫자·무늬·세트·런 재료라는 고유 가치를 유지
- [x] PURE는 직접 전투 보너스보다 카드 선택/교체/제거 등 덱 구축 자유도를 장점으로 설계
- [x] 런 도중 네임드를 받아 어느 테마로도 전환 가능
- [x] 네임드를 끝까지 받지 않는 온리 순수덱 클리어도 가능한 방향 유지
- [x] PURE도 기본 순환만으로 장기전이 가능하도록 덱 소진 시 소모패 + 공용 버림패의 현재 내 소유 카드를 재순환하는 공통 규칙 적용
- [x] PURE 시작 덱의 숫자/무늬 분포 확정
  - 정규 29슬롯은 현재 기준 구조 `CORE_IDS.slice(0,29)`를 그대로 사용한다: S3–S9 + S10, H2–H4/H7–H10, D2–D8, C3–C9.
  - 30번째 카드는 조합 판정에서만 와일드인 `기본 와일드 조커`로 두며 네임드/고유 효과/광대왕의 정리 후 즉시 덱 복귀 효과를 갖지 않는다. 따라서 PURE는 30장 모두 효과카드 0장이다.
- [ ] PURE 보상 특전 후보(선택지 +1, 교체/제거 비용 등) 밸런스 확정
- [ ] 끝까지 순수덱을 지원할 카드 외부 유물/패시브 구조 검토

### 순수카드 → 네임드화 성장
- [x] 동일 랭크+무늬의 순수 슬롯을 네임드 변형으로 교체/진화시키는 로그라이크 성장 방식 우선 검토
- [x] 기본 네임드화는 해당 슬롯의 원본 랭크+무늬를 보존한다. M11B 특수 변형도 52슬롯의 원본 슬롯은 유지하되, 보조 랭크를 하나 추가하는 제한적 예외 후보로 검증한다.
- [x] `교체 / 추가 / 제거`를 서로 다른 덱 성장 수단으로 두고, 교체를 기본 성장축으로 검토
- [x] 모든 순수카드를 네임드화하는 것이 자동 정답이 되지 않도록 순수카드 유지 가치 보존
- [x] 카드 보상/상점/이벤트에서 슬롯 교체 UI 설계 — 공용 `replace-slot-variant` 계획 객체가 보상/상점/이벤트 출처를 정규화하고 `현재 변형(또는 순수) → 새 네임드`, 원본 rank+suit 슬롯 보존, 덱 장수 불변, 취소 가능을 같은 계약으로 표시. 행동 태그 보상 후보를 확인 후 별도 런 덱에 적용하며 일반 대전 덱이나 진행도는 변경하지 않음. 상점/이벤트 실제 적용은 결제/조건 구현 전까지 미지원
- [x] 카드 제거와 네임드 교체의 경제적 가치 비교
  - 현재 30장(일반 슬롯 29 + 조커 1) 기준 4,000-seed 구조 실험에서 6장 손패 조합 가능률은 32.48%, 서로 겹치지 않는 2조합 잠재력은 0.68%였다.
  - 동일 rank+suit 네임드 교체는 덱 크기와 숫자/무늬 구조를 그대로 보존하므로 구조 변화량이 0이다. 교체의 경제 가치는 카드 효과와 희소도에서 나온다.
  - 조커를 제외한 일반 슬롯 1장 제거 평균은 조합 가능률 +0.25%p, 평균 합법 3장 조합 수 +0.012였지만 2조합 잠재력은 -0.13%p였다.
  - 슬롯별 편차도 커서 H10 제거는 조합 가능률 +2.25%p, S7 제거는 -2.38%p였다. 제거는 덱 압축이 되기도 하고 핵심 RUN 축을 파괴하기도 한다.
  - 따라서 제거는 동일 슬롯 교체의 단순 상위 보상이 아니라 별도 희소 성장 행동으로 분리하고, 확정 전에 덱 구조 변화 경고/분석을 보여 준다. 정확한 비용·희귀도·노드 등급은 실전 M12 데이터 이후 확정한다.
### 로그라이크 카드 보상 작업안
- [x] 일반 전투의 기본 보상 후보를 `3장 중 1장 + 건너뛰기` 구조로 검토
- [x] 보상 후보를 `현재 빌드 강화 / 새 방향·혼합 테마 / 범용·기반 보강`의 세 역할로 나누는 방향 기록
- [x] 테마 이름만이 아니라 회수·붙이기·세트·런·정비·러미 등 실제 행동 태그를 보고 보상 가중치를 조정하는 방향 기록
- [x] 새 테마 첫 진입은 초동/기본 엔진 우선, 이후 덱 상태에 따라 엔진/피니셔가 열리는 구조 검토
- [x] 별도 테마 레벨 자원보다 실제 덱에 필요한 초동/전용 개념 생성기가 있는지 검사하는 방식 우선
- [ ] 일반전 / 엘리트 / 보스별 카드 보상 등급과 유물 보상 확정
- [x] 행동 태그 기반 후보 생성 알고리즘 설계 — `action-tags-v1`은 네임드 효과의 기존 성향 메타를 세트/런/붙이기/회수/정비/러미/버림패/스위치/상태 등 플레이 행동 태그로 정규화하고, 현재 덱 프로필과 비교해 `현재 강화 / 새 방향 / 기반 보강` 3역할을 각각 1장씩 결정적으로 랭킹. 기본 성장축에 맞춰 현재 원본 슬롯에 존재하는 네임드 교체만 후보로 허용하고 현재 변형/조커/덱 외 슬롯은 제외. 새 테마는 알려진 초동 카드를 피니셔보다 우선하지만 하드 테마 잠금은 없으며, 정확한 드롭 확률·희귀도·일반/엘리트/보스 보상 수치는 여전히 미확정

- [x] 스타터 청사진 기반 실제 런 덱 저장 및 동일 슬롯 보상 적용 — 초안 v4에서 도입한 runDeck/revision(현재 v8), 구버전 마이그레이션, 저장 복원, 후보 재검증, 중복·오래된 선택·저장 실패 회귀 포함
- [x] 런 덱 기반 별도 실험 전투 시작과 전투 상태 격리 — DEV 작업실에서 전용 사본의 런 덱 실험전을 시작하며 30개 청사진을 새 전투 카드 객체로 복제. PURE 기본 와일드 조커와 저장된 네임드 변형을 그대로 전투에 전달하되 위치·상태·효과 마커·승패는 런 덱에 역류하지 않고 일반 클리어/레벨/해금 및 M12 표본에서도 제외. 결과 다시 하기는 현재 저장 덱을 새로 복제
- [x] 테스트 보상 노드 발급·고정 후보·1회 수령/건너뛰기 — 초안 v5의 rewardNodes 이력에 노드 ID·발급 덱 지문·후보·처리 결과를 저장. 후보 재추첨 없이 노드당 1장 수령 또는 건너뛰기만 허용하며 덱 교체와 수령 결과를 한 번에 저장. v4 교체 덱 보존, 중복 발급/수령·오래된 버튼·저장 실패·손상 이력 회귀 포함. 현재 수동 테스트 노드이며 실험전 승패와 무관
- [x] 공통 시작 → 4개 지역 선택 → 선택 지역 3연전 연결 — 네온아크/레드존/아이언그레이브/올드쿼터 중 1곳 선택을 v6 런 저장에 보존. 마지막 공통 보상 처리 전 진입·지역 재선택·다른 지역 전투 영수증을 거부하고 기존 v5 런 덱/보상은 유지. 최초 6전투 슬라이스에 아래 중간 보스 1전을 추가했다.
- [x] 지역 실전 보상 성향 v1 — 지역별 행동/라이브 테마 보정을 `현재 강화 / 새 방향`에 최대 +6점 적용하고 `기반 보강` 및 새 테마의 알려진 후속 카드에는 가산하지 않는다. 공통 시작/수동 테스트 보상은 기존 `action-tags-v1`, 새 지역 승리 보상만 `action-tags-region-v1`과 지역 ID를 기록. 기존 고정 후보 보존, 후보 자격·다른 지역 카드·건너뛰기 유지, 발급 지역 검증 및 5스타터 × 4지역 × 64시드 비교 회귀 포함. 이는 후보 랭킹 프로토타입이며 드롭 확률 확정은 아니다.
- [x] 지역 적 12종 / 중간 보스 4종과 7번째 전투 연결 — 지역마다 적 전용 29슬롯+조커 1 덱과 공용 필드를 고정하고 일반 3전투의 정규 네임드 6/8/10장 → 보스 12장으로 구성. 보스도 기본 코어 3×60과 공용 AI/효과 규칙을 사용. 기존 6승 v6 저장은 같은 지역 보스부터 이어가며 승리 보상 처리 후 구역 완료. 사전 상대/필드 안내, 보스 결과 표시, 실패·무승부·중복 결과·영수증 보존 및 512개 AI 조합 선택 샘플 검증. 적 난도·보스 전용 보상 등급은 미확정.
- [ ] 실제 맵/전투 노드와 보상 발급 연결 — 14전투 경로·보상·런 완료는 연결했으며 상점/이벤트/엘리트 노드와 맵 구성 확장은 남음
  - [x] 공통 시작 구역 3연전 실전 슬라이스 — RUN TEST와 별개인 실전 버튼/전투 자격을 추가하고, 승리 시 runId·노드 ID·revision·덱 지문을 검증해 `battle` 출처 보상 영수증을 1회 저장. 수령/건너뛰기 전 다음 전투 잠금, 패배·무승부 재도전, 일반 클리어·레벨·해금·M12 표본 격리 및 중복/오래된 승리 거부
  - [x] 런 경로 지도 v1 — 현재 저장된 전투 영수증과 기존 경로 계산만 읽어 공통 시작→선택 지역→널워드의 진행을 가로 지도에 표시. 완료/승리 후 보상 대기/다음 전투/잠금/지역 선택 관문을 분리하고, 아직 고르지 않은 지역은 미리 확정하지 않는다. 전투 수·보상·상점·이벤트·경제 규칙은 변경하지 않음
- [x] 완료 런 아카이브 v1 — 최종 보상 처리로 `completed`가 된 런을 별도 `rummyDuelRoguelikeRunHistoryV1` 저장소에 runId 기준 1회 보관. 방문 경로·14전투 승리·수령/건너뛰기 이력·최종 30장 청사진/지문·교체 횟수를 최대 24개까지 보존하고, 일반 로그라이크의 기록 화면에서 완료 내역과 최종 덱을 표시한다. DEV 런은 전용 완료 기록으로 격리한다. 일반 대전 클리어/레벨/해금 및 M12 표본 저장은 변경하지 않으며 아카이브 저장 실패가 런 완료 자체를 되돌리지 않는다.
- [ ] 상점·이벤트 결제/조건 연결

### 지역 기반 로그라이크 구조 작업안
- [x] `공통 시작 구역 → 지역 분기 → 중간 보스 → 추가 지역 선택 → 후반 특수구역 → 최종 보스`를 기본 맵 흐름 후보로 기록
- [x] 테마군 1개를 지역 1개로 고정하지 않고 `지역 = 공통 문화/환경 + 여러 관련 테마군 + 지역 공용 카드` 구조 우선 검토
- [x] 공통 구역에서 순수 슬롯 개선/범용 네임드/여러 테마 초동을 제공해 빌드 씨앗을 먼저 찾고, 이후 지역이 그 방향을 밀어주는 흐름 기록
- [x] 지역 선택은 특정 테마 강제가 아니라 관련 카드군과 행동 스타일의 등장 가중치를 높이는 방식으로 검토
- [x] 카드 계층을 `전역 범용 → 지역 공용 → 테마군 → 캐릭터 고유`로 나누는 방향 기록
- [ ] 지역 수 / 런 길이 / 지역 방문 횟수 / 노드 비율 확정
- [ ] 지역별 카드 등장 가중치와 타지역 카드 출현률 확정
- [ ] 고정 시작 29슬롯에서 테마 초동의 진입 가능성 검토 — ZERO-SIGHT 초동 CA/C2 등 덱 밖 슬롯은 현재 동일 슬롯 교체 보상에 들어올 수 없다. 지역 성향은 이 자격을 우회하지 않으며 새 슬롯 진입 수단은 별도 설계한다.

### 현재 지역 후보 — 4개 분기 지역 + 널워드 후반 구역 프로토타입, 상세 콘텐츠 후속 설계
- [x] `NEON//ARC 네온아크` — 미디어/방송/SNS/배송/정보 도시. V-SIGNAL + MAIL-ROUTE 중심 후보
- [x] `RED//ZONE 레드존` — 도시전/용병/정찰/돌입 분쟁구역. ZERO-SIGHT + POINT-BLANK 중심
- [x] `IRON//GRAVE 아이언그레이브` — 폐공장/고철/기계 산업폐허. SCRAP-SHIFT 중심 후보
- [x] `OLD//QUARTER 올드쿼터` — 구시가지/탐정/범죄조직/암시장/계약. 향후 탐정·마피아·도둑·밀수·거래 테마 후보
- [x] `NULL//WARD 널워드` — 기록에서 삭제된 격리구역/실험/괴이/변이. 두 지역 뒤 교전 2회·최종 보스가 있는 후반 구역 프로토타입으로 연결. 실험체·초능력·저주 계열 상세 콘텐츠는 후속 설계
- [ ] 각 지역 세계관 / 지역 공용 카드 / 이벤트 / 엘리트 / 보스 상세 설계
- [x] 중간 보스 이후 두 번째 지역 선택·진행 — 첫 보스 보상 처리 후 미방문 3곳 중 선택하고 기존 덱·보상 이력을 유지한 채 일반 3전투와 보스 1전으로 연결. v7의 최대 2지역 경로를 저장하며 v6 이전 저장은 그대로 이어간다. 방문 순서·보상 문턱·오래된 선택·저장 실패를 검증하고 두 번째 지역의 보상 성향·적/필드·보스 결과 표시를 연결. 12개 순서 조합 / 두 번째 지역 전투 시작·결과 48개 및 전체 121개 회귀 통과. 11전투는 두 지역 도입 당시 범위이며, 아래 후반 구역으로 14전투까지 확장했다. 최종 런 길이 확정은 아니다.
- [x] 두 번째 지역 이후 후반 특수구역·최종 보스·런 완료 연결 — 널워드의 격리 감시자/기록 말소자/최종 보스 공백 관리자와 고정 덱·공용 필드, 널워드 보상 성향을 추가. 기존 v7의 11승 저장은 보상 처리 뒤 널워드부터 이어가며, 마지막 보상 수령/건너뛰기와 완료 상태·시각·최종 덱을 v8에 한 번에 저장. 완료 뒤 추가 전투/테스트 보상은 닫고 최종 덱 실험전·새 런 시작을 제공. 12개 경로·36개 후반 전투 시작/결과·96개 AI 조합 샘플 및 전체 122개 회귀 통과. 일반 클리어/해금과 메타 보상은 별개이며, 완료 아카이브는 아래 v1 저장으로 분리했다. 14연전의 난도/승률은 미확정.
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
- [x] 비대칭값을 실제로 활용하는 네임드 효과 샘플 10~20장 설계 — `docs/ASYMMETRIC_RANK_PROTOTYPE.md`에 서로 다른 정규 슬롯의 설계 전용 12장 샘플을 추가. Δ1~2 / 3~4 / 5~6 / 7+를 각 3장씩 배치하고 사용값·미사용값·높은/낮은 값·상대 조합·상태·체인 반환을 고르게 시험하며 현재 라이브 비대칭 정의는 0장 유지
- [x] 숫자 차이가 큰 카드가 단순 상위호환이 되지 않도록 효과 예산 / 희귀도 / 패널티 기준 수립 — Δ1~2 소 / Δ3~4 중 / Δ5~6 대 / Δ7+ 극단의 제작 등급을 잠그고, Δ5+는 상시 양의 효과를 금지하며 실제 템포 비용/패널티를 요구. 한 인쇄값은 반드시 baseRank를 보존하고 직접 누적 위력은 샘플 12장 중 1장만 허용 · 권장 등장 등급은 소=일반 후보 / 중=고급 후보 / 대=희귀 후보 / 극단=특수·이벤트 후보로만 문서화하며 현재 런타임에는 희귀도 시스템을 추가하지 않음
- [x] 순수 `X/X` 카드와 일반 네임드 `X/X`가 비대칭 `X/Y` 카드와 경쟁할 수 있는 유지 가치 설계 — 일반 X/X 네임드는 유연성 세금이 없어 더 강하고 안정적인 효과 예산을 허용하고, PURE X/X는 원본 슬롯 안정성과 향후 로그라이크 교체/제거/보상 경제의 자유도로 차별화. 비대칭은 동일 슬롯 대체 선택지일 뿐 추가 슬롯을 만들지 않으며 실제 동일 슬롯 선택률은 M12 표본에서 재검증

### 규칙·엔진 검증
- [x] 기존 단일 `rank`와 호환되는 `baseRank / topRank / bottomRank / activeRank` 데이터 구조 설계 — 모든 정규 카드는 원본 슬롯용 `baseRank`, 인쇄값 `topRank/bottomRank`, 조합 안 선택값 `activeRank`를 가질 수 있다. 기존 엔진 호환을 위해 `rank`는 조합 밖에서는 `baseRank`, 향후 선택이 확정된 조합 안에서는 `activeRank`를 미러링하는 전환 계층으로 잠금. 현재 라이브 비대칭 정의는 0장
- [x] 손에서는 `activeRank` 미확정, 조합 투입 시 확정, 조합을 떠나 손으로 돌아오면 다시 미확정으로 초기화하는 생명주기 명문화 — `chooseCardActiveRank` / `clearCardActiveRank`와 `rankOrientation`으로 top/bottom 방향을 분리하고 `docs/ASYMMETRIC_RANK_PROTOTYPE.md`에 영역별 생명주기를 고정
- [x] 버림패·소모패·덱·재순환처럼 조합 밖 영역에서는 방향 선택 상태를 유지하지 않는 기본안 검증 — 손 진입, 공용 버림패 진입, 공개 조합 정리, 전체 재순환 경로에서 `activeRank/rankOrientation`을 제거하고 `rank=baseRank`로 복귀. 조합→조합 이동은 공개 조합을 떠나지 않으므로 선택값 유지 후보로 잠금
- [x] 새 조합 생성·붙이기·다중 붙이기에서 각 비대칭 카드의 사용값 선택 순서와 합법성 미리보기 구조 설계 — 선택한 카드 순서를 그대로 유지한 채 각 미확정 `X/Y`의 위→아래 후보를 최대 64개 조합으로 열거하고, 원본 카드를 변형하지 않는 projection에 기존 `meldType`을 적용해 새 3장 조합/단일·다중 붙이기의 합법 plan과 방향 라벨을 반환. 아직 실제 버튼/행동에는 연결하지 않은 dormant preview 계층
- [x] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증 — 행동 전 projection으로 합법성을 확인한 뒤 모든 실패 가능 기본 가드를 통과한 시점에 `applyRankChoicePlan()`이 `activeRank → rank`를 원자적으로 확정하고, 그 다음에만 손패 제거·공개 조합 삽입·버스트/체인 계산·효과·러미가 진행된다. 런 완주는 공개 조합에 고정된 선택값을 그대로 이벤트에 전달한 뒤 정리 시 초기화. 현재 라이브 비대칭 카드는 0장
- [x] A/Q/K 경계와 A-2-3 / Q-K-A / K-A-2 런 특수 규칙에서 비대칭 값 회귀 테스트 추가 — 합성 비대칭 카드의 선택값으로 A-2-3 및 Q-K-A는 기존 런 규칙 그대로 허용하고 K-A-2는 거부하며, 일반 3-4-5와 세트/다중 붙이기 방향 조합도 실행 회귀로 고정
- [x] 조커의 와일드 판정, 기존 숫자 변경 효과, 복사 효과와 비대칭 값이 중첩될 때 우선순위 명문화 — `조커 와일드 > 인쇄값 선택 > 카드 고유 숫자 보정`으로 잠금. 조커는 `activeRank`를 갖지 않고 기존 완전 와일드를 유지한다. 카운터피터의 런 ±1은 선택된 `activeRank`를 기준으로 합법성에서만 탐색하며 선택값을 변경하지 않는다. 도플갱어의 세트 랭크 복사는 세트 판정에서 선택값 위에 적용되지만 `activeRank/rankOrientation` 기록 자체는 유지한다
- [x] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계 — `bestNewMeld`와 최대 6장 `bestExtensionFromHand`가 각 카드 조합의 모든 합법 top/bottom plan을 projection으로 비교하고, 새 조합은 기존 SET/RUN 점수·미래 버스트 노출 위험을 선택값 기준으로 계산하며, 붙이기는 실제 버스트 +24 / 체인 10·15·20·25… / 상대 공개 조합·테마 보정을 선택 plan의 projection에 적용한다. 선택된 `rankPlan`을 실제 `submitNewMeld/attachCards`에 전달하며, 막힘 판정 `anyAttachOption`도 비대칭 plan을 인식한다. 점수가 같으면 기존 위→아래 열거 순서를 유지해 결정적으로 선택하고 현재 라이브 비대칭 카드는 0장
- [x] 덱빌더 숫자·무늬·세트·런 분포는 원본 52슬롯(`baseRank+suit`) 기준으로 고정하고 비대칭 `X/Y`의 선택 유연성은 별도 분석으로 분리 — `deckBuildAnalysis()`는 변형 인쇄값을 절대 중복 집계하지 않고 `basis:'base-slot'`을 반환한다. `deckBuildAsymmetricFlexAnalysis()`는 향후 실제 비대칭 변형이 선택된 경우에만 잠재 선택 랭크를 별도 표시하며 기초 세트/런 통계를 바꾸지 않는다. 현재 라이브 비대칭 카드는 0장

### UI / 카드 아트 검증
- [x] 실제 카드 좌상단·우하단 랭크를 서로 다르게 표시하고 180° 회전 선택이 즉시 읽히는 카드 프레임 프로토타입 제작 — 공용 `cardHTML()`이 `topRank/bottomRank`를 분리 렌더링하고, 아래값 선택 시 카드 면만 180° 회전해 선택값이 좌상단으로 올라오도록 구현. 개발자 패널에 라이브 카드와 분리된 합성 3/7 미확정·위 선택·아래 선택 3상태 미리보기 추가
- [x] 손패에서 비대칭 카드 선택 시 두 사용값과 각각의 합법 세트/런 후보를 미리보기로 표시 — `playerRankChoiceHint()`가 현재 선택/타겟 기준 모든 합법 top/bottom plan을 세트·런과 함께 selection strip에 요약하고, `canAttachTo`·붙이기 강조·새 조합 버튼도 projection 기반 합법성을 사용. 실제 새 조합/붙이기 실행 직전에는 공용 선택 모달에서 합법 plan을 명시적으로 고르게 하며 합법 plan이 1개뿐이어도 엔진이 임의 방향을 추측하지 않음
- [x] 조합에 들어간 뒤에는 선택된 사용값이 어느 쪽인지 회전 상태 또는 작은 방향 마커로 명확히 고정 표시 — `rankLockedTop/rankLockedBottom` 상태와 `↑/↓ 사용` 마커를 공용 카드 렌더러가 표시하고, 선택하지 않은 반대 코너는 약하게 처리. 아래값 선택은 카드 면 180° 회전과 함께 고정
- [x] 카드 상세에는 `원본 슬롯`, `두 인쇄값`, 현재 조합에 있을 때의 `사용값`을 구분해 표시 — 비대칭 카드만 `원본 슬롯 / 인쇄 X/Y / 사용값 미확정 또는 ↑·↓ 값` 메타를 추가하고 일반 X/X 카드 상세는 기존 표시를 유지
- [x] 모바일에서 상·하단 숫자가 다른 카드가 단순 오타처럼 보이지 않도록 최초 획득/튜토리얼 설명 설계 — 미확정 카드 중앙에 `↕ 선택` 표식을 상시 표시하고, 플레이어 손에 비대칭 카드가 처음 들어온 순간 손패 위에 비차단 설명 패널을 1회 노출한다. 확인 후 진행도에 저장하며 실제 라이브 비대칭 카드가 생기기 전까지 가짜 튜토리얼 카드는 추가하지 않음

### 밸런스 판정 기준
- [x] 개발자 전용 0/4/10장 실제 전투 샌드박스 + 분리 지표 기록 — 개발자 패널에서 동일 원본 29슬롯+광대왕 조커의 기준 0장 / 소수 4장 / 스트레스 10장 코호트를 시작하며 상대는 항상 0장 X/X 기준덱. 합성 X/Y는 `NAMED`/해금/자동 덱에 등록하지 않고 별도 `rummyDuelM11BExperimentV1` 기록에 턴·정비·러미·상대 조합·다중 붙이기·↑/↓ 사용값을 최대 60판 보존. DEV/실험전은 진행도와 M12 일반/연습 `rummyDuelBattleMetricsV1` 표본에서 제외하며 `newGame()` 전투 지표 초기화도 회귀 잠금
- [x] M11B 실험 표본 준비도 / 0장 대비 코호트 차이 패널 — 개발자 패널에서 0/4/10장 각각 10판을 `1차 비교 가능`, 20판을 `안정권`으로 표시하고, 0장 기준 대비 4장/10장의 승률·평균 턴·정비·러미·상대 공개 조합 사용·최대 다중붙이기 차이를 자동 요약. 이 기준은 데이터 수집 준비도일 뿐 통계적 유의성·밸런스 합격 판정이 아니며 최종 M11B/M12 밸런스 항목은 계속 미완료로 유지
- [x] 0/4/10장 페어 시드 실험 — 동일 비교 시드에서는 플레이어 0/4/10장 코호트의 원본 29슬롯 카드 순서가 같고 상대 0장 기준덱 순서도 동일하도록 개발자 실험 덱만 결정론적으로 셔플. 완료한 코호트를 시드별로 추적하고 3종을 모두 끝낸 `완성 페어` 수를 표시하며, 시드는 덱 순서만 통제하고 인간/AI 행동까지 고정하는 완전 리플레이로 취급하지 않음
- [x] 실제 행동 baseRank 반사실 텔레메트리 — M11B 실험전에서 합성 X/Y가 들어간 성공 행동마다 해당 손패 카드만 `baseRank`로 되돌린 projection을 기존 `meldType`으로 재판정해, 선택권이 없으면 불가능했던 `구제 행동`과 세트/런·상대 공개 조합·다중붙이기 구제 횟수, base에서도 합법하지만 조합 타입만 바뀐 횟수를 별도 기록. 실제 행동을 막거나 수정하지 않는 관측 전용 계층이며 최종 성공률/밸런스 판정은 표본 수집 전까지 미완료 유지
- [x] 완성 페어 전용 0/4/10장 차이 분석 — 같은 `pairSeed`에서 세 코호트를 모두 완료한 기록만 묶고, 같은 시드·같은 코호트 재실험은 가장 최근 판만 사용. 승률·턴·정비·러미·상대 공개 조합 사용·판별 최대 다중붙이기를 시드 안에서 먼저 0장 기준으로 차감한 뒤 완성 페어 전체 평균을 개발자 패널에 별도 표시하며, 구제 행동/판도 함께 보여준다. 전체 코호트 평균은 그대로 남기고 페어 분석 역시 표본 수가 작을 때 밸런스 결론으로 취급하지 않음
- [x] 인쇄값 차이 Δ등급 행동 텔레메트리 — 비대칭 성공 행동에 사용된 합성 X/Y의 인쇄값 차이를 기록하고, 한 행동에 여러 X/Y가 있으면 최대 Δ를 기준으로 `Δ1~2 / Δ3~4 / Δ5~6 / Δ7+`에 분류. 등급별 관측 행동·baseRank 구제율·세트/런·상대 공개 조합·다중붙이기 구제 횟수를 개발자 패널에 표시하며, Δ정보가 없는 기존 기록은 별도 제외 수로 표시. 큰 숫자 차이의 실제 밸런스 결론은 표본 전까지 미완료 유지
- [x] 라이브 승격 전 구조적 밀도 시뮬레이션 — `experiments/m11b-asymmetric-density.mjs`가 동일한 기본 29슬롯 + 광대왕 조커, 동일 4,000개 시드의 6장 손패에서 실제 `meldType` / 비대칭 rank-plan 합법성으로 0장 / 4장 / 10장 합성 비대칭 밀도를 비교. 조합 가능률 32.48% → 37.60% → 40.52%, 비대칭 선택 때문에 새로 살아나는 손패 +0 / +5.13 / +8.05%p, 평균 합법 3장 조합 수 0.551 → 0.690 → 0.786을 확인. 첫 라이브 실험은 최대 4장 수준의 콘텐츠 밀도를 우선하고 세트/버스트 상시 보상을 겹치지 않는 임시 게이트를 적용하며, 이는 엔진 하드캡이 아님
- [ ] 비대칭 카드 0장 / 소수 / 다수 덱의 세트·런 성공률, 패말림, 정비, 러미 빈도 비교
- [ ] 동일 슬롯의 순수 / 일반 네임드 / 비대칭 네임드 선택률을 비교해 비대칭 변형이 자동 상위호환인지 확인
- [ ] 큰 숫자 차이 자체가 덱 안정성을 지나치게 높이는지, 특히 다중 붙이기와 상대 공개 조합 이용에서 성공률 상승폭 측정
- [ ] 프로토타입 결과가 좋으면 M0/M11의 정식 카드 규칙으로 승격하고, 좋지 않으면 소수 카드의 개별 효과 또는 특정 테마 기믹으로 축소

## M12 — Metrics and balance
- [x] Track turn count, BURST/CHAIN/DETONATE timing, max power, opponent-meld use, multi-attach size, RUMMY, maintenance and intentional bomb acceptance — 전투별 구조화 이벤트를 수집해 결과 요약에 표시하고 일반/연습 전투 최근 240판을 `rummyDuelBattleMetricsV1` 로컬 기록으로 보존. 튜토리얼/DEV 전투는 밸런스 표본에서 제외
- [x] Review/export local playtest metrics — 개발자 패널에서 최근 240판의 일반/연습 표본 수, 일반전 승률, 평균 턴·최대 위력·버스트·체인·폭발·상대 조합 사용·러미·정비와 다중붙이기/소폭탄 수용을 즉시 요약하고 최근 8판 상세·JSON 복사·기록 초기화를 지원
- [x] Structure / circulation cohort telemetry — 전투 샘플을 v2로 확장해 `playerStructure`/커스텀 덱 여부와 플레이어·상대별 손패 합계·2/3장 이하 턴·저손패 보호·러미·정비를 원시 카운트로 저장. 개발자 패널은 세트형/런형/혼합형/커스텀을 분리해 일반전 승률·평균 턴·평균 손패·2장 이하 비율·러미/정비 100턴당 빈도를 비교하며 기존 v1 표본은 구조 미기록으로 보존·비교 제외. M12 순환 실험 코호트에도 라이브 TWELVE-BLOOM을 추가
- [x] Structure cohort readiness / observation gate — 세트형/런형/혼합형의 순환 지표 포함 일반전 v2 표본을 각 10판 `1차 비교 가능`, 20판 `안정권`으로 표시하고 연습전은 승률 게이트에서 제외. 세 구조가 모두 10판을 넘은 뒤 승률 범위 20%p, 평균 턴 8, 2장 이하 10%p, 러미/정비 2회/100턴 또는 전체 재순환 발생을 `추가 확인 신호`로만 표시하며 자동 수치 조정·통계적 유의성·합격/실패 판정은 하지 않음
- [x] Guided M12 structure playtest collector — 개발자 M12 패널이 구조별 일반전 v2 표본 수에서 가장 적은 세트형/런형/혼합형을 다음 추천으로 제시하고, 동률은 직전 구조 다음 순서로 순환. 한 번의 버튼으로 DEV를 종료하고 추천 구조를 일반 진행도에 적용하며 커스텀 덱을 해제한 뒤 정상 대전 준비의 덱 단계로 이동. 캐릭터/테마는 유지해 같은 조합의 3구조 묶음 플레이를 권장하고, 10판 게이트 후에는 20판 안정권까지 같은 방식으로 안내
- [x] M12 retention fix + theme×structure matrix — 기존 최근 50판 제한으로는 구조별 20/20/20 안정권(최소 60판)에 동시에 도달할 수 없던 모순을 수정해 `rummyDuelBattleMetricsV1` 보존 한도를 240판으로 확대. 일반전 v2·자동 구조 덱만 테마별 세트/런/혼합 셀로 분리해 승률·2장 이하·러미를 표시하고, 같은 테마의 세 셀이 각 3판 이상이면 테마 내부 구조 범위를 별도 표시해 전체 구조 차이가 특정 테마 편중 때문인지 확인. 3판은 관찰 시작점일 뿐 유의성/합격 기준이 아님
- [x] M12 character×structure correction matrix — 일반전 v2·자동 구조 덱을 유랑자/수집가/회수꾼/광대별 세트/런/혼합 셀로 분리해 승률·2장 이하·러미를 표시. 같은 캐릭터의 세 셀이 각 3판 이상이면 캐릭터 내부 승률·평균 턴·저손패·러미 범위를 관찰값으로 표시. 캐릭터는 전투 패시브가 아니라 자동 덱 네임드 가중치만 바꾸므로, 이 교차표는 전체 구조 통계가 특정 캐릭터의 구성 편향에 끌렸는지 확인하는 보정 용도로만 사용
- [x] M12 character+theme matched-context correction — 일반전 v2·자동 구조 덱을 `playerChar + playerTheme` 컨텍스트로 묶고, 각 컨텍스트에서 세트/런/혼합 중 최소 셀 수만큼 최근 표본을 동일 수로 잘라 구조별 균형 표본을 합산. 원시 전체 승률과 매칭 후 승률의 이동 및 승률·평균 턴·2장 이하·러미 범위를 별도 표시해 캐릭터/테마 구성 편중을 동시에 보정. 3개 매칭 블록부터 관찰 참고로 표시하며 유의성/합격 기준은 아님. 구조 추천은 전체 부족 구조 우선 원칙을 유지하면서 동률일 때 현재 캐릭터+테마에서 덜 쌓인 구조를 우선
- [x] M12 matched 3-battle structure block collector — 정상 일반전 표본을 중복 저장하지 않고 기존 v2 행에 `playtestBlockId/Step`만 덧붙여, 같은 정상 진행도 캐릭터+테마를 고정한 세트/런/혼합 1판씩의 3전 블록을 수집. 블록 시작 순서는 현재 컨텍스트와 전체 표본에서 덜 쌓인 구조를 우선하고 이후 세 구조를 순환. 결과 저장 시 블록 ID·컨텍스트·예정 구조가 모두 일치한 판만 블록 완료로 인정하며, 결과 화면에서 다음 블록전으로 바로 이어갈 수 있음. 수동으로 다른 설정을 플레이한 판은 일반 M12 표본에는 남되 블록 완료에는 미포함
- [ ] Balance from playtest data before large content expansion

## M13 — Static code split
Only after rules and tests are stable. Keep GitHub Pages buildless.
- [ ] styles.css
- [ ] cards/data JS
- [ ] rules/game JS
- [ ] AI JS
- [ ] UI/progress JS

## Current next work
1. UI2 P2: 360–480px live Chromium audit is locked; only final Android/iOS physical-device safe-area/system-UI verification remains.
2. M12: collect real playtest samples from the new per-battle metrics history and balance from data before large content expansion.
3. M11A/M11B: keep roguelike progression and asymmetric top/bottom-rank cards in prototype/design validation until M12 evidence supports promotion; defer M13 file splitting until rules/tests remain stable through those experiments.


## 2026-09-03 · ZERO-SIGHT 풀 카드군
- [x] ZERO-SIGHT 18/18 풀 카드군 구현
- [x] 신규 14장 실제 효과·해금·도감/덱빌더 연결
- [x] 표적 1개 계약과 일반/V-SIGNAL 혼합 상호작용 유지
- [x] 신규 14장 로그라이크 보상은 60장 통합 전까지 staged 처리


## 2026-09-03 · POINT-BLANK 풀 카드군
- [x] POINT-BLANK 18/18 풀 카드군 구현
- [x] 신규 16장 실제 효과·해금·도감/덱빌더 연결
- [x] 접전 1개·지연 해제·전투 중립 이동·기본/무료 회수 계약 유지
- [x] 붙이기/회수/버리기/정비 공용 행동 이력을 전용 숫자 자원 없이 재사용
- [x] 신규 16장 로그라이크 보상은 60장 통합 전까지 staged 처리
