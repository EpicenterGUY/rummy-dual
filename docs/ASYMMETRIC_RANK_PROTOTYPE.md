# M11B — 비대칭 상·하단 랭크 프로토타입

이 문서는 비대칭 `X/Y` 카드의 **엔진 호환 계층**만 잠근다. 현재 라이브 카드 풀에는 비대칭 카드가 0장이며, 세트/런/버스트/체인/스위치 규칙은 아직 변경하지 않는다.

## 데이터 모델

- `baseRank`: 52슬롯의 원본 랭크. 카드 정체성, 덱빌더 슬롯, 네임드 변형 귀속은 항상 이 값 기준이다.
- `topRank`: 카드 좌상단에 인쇄될 후보 랭크.
- `bottomRank`: 카드 우하단에 인쇄될 후보 랭크.
- `activeRank`: 공개 조합에 투입될 때 선택되는 실제 세트/런 판정값. 조합 밖에서는 `null`.
- `rankOrientation`: `top` 또는 `bottom`. 같은 숫자가 양쪽에 인쇄된 일반 `X/X` 카드는 방향 의미가 없다.
- `rank`: 기존 엔진 호환 미러. 조합 밖에서는 `baseRank`, 선택이 확정된 조합 안에서는 `activeRank`와 같게 유지한다.

## 생명주기

| 영역 | activeRank | rank | 비고 |
| --- | --- | --- | --- |
| 개인 덱 | `null` | `baseRank` | 방향 없음 |
| 손패 | `null` | `baseRank` | 사용 직전까지 미확정 |
| 공용 버림패 | `null` | `baseRank` | 방향 없음 |
| 개인 소모패 | `null` | `baseRank` | 방향 없음 |
| 공개 조합 | 선택값 | 선택값 | `top/bottom` 중 실제 인쇄값 하나만 선택 |
| 조합 → 손/덱/버림/소모 | 즉시 `null` | `baseRank` | 다음 사용 때 다시 선택 가능 |
| 조합 → 다른 조합 직접 이동 | 유지 후보 | 선택값 | 공개 조합을 떠나지 않으므로 1차 기본안은 유지. 실제 이동 선택 UI 단계에서 재검증 |

## 호환 규칙

1. 일반 카드와 기존 네임드는 기본적으로 `X/X`이며 `topRank=bottomRank=baseRank`다.
2. 현재 엔진의 수많은 `c.rank` 판정을 즉시 전부 교체하지 않는다. `rank` 미러를 유지해 기존 회귀를 보존한다.
3. `namedSlot()`과 52슬롯 정체성은 `baseRank+suit`에서 절대 바뀌지 않는다. `activeRank`는 슬롯 교체가 아니다.
4. 조커는 이 스캐폴드의 랭크 인쇄값을 사용하지 않는다. `baseRank/topRank/bottomRank/activeRank=null`이며 기존 와일드 판정이 우선이다.
5. 실제 비대칭 카드 정의, 사용값 선택 UI, 세트/런 합법성 탐색은 다음 단계 전까지 라이브에 넣지 않는다.

## 현재 중앙 초기화 경로

- `enterHand()` — 공개 조합에서 회수되거나 다른 효과로 손에 들어오면 선택값 제거.
- `pushDiscard()` — 공용 버림패 진입 시 선택값 제거.
- `retireMeld()` — 조합 정리로 손/덱/소모패 어디로 가든 먼저 선택값 제거.
- `fullRecirculation()` — 모든 영역을 덱으로 되돌리는 긴급 재순환에서 선택값 제거.

다음 구현 단계는 `새 조합 생성 / 단일 붙이기 / 다중 붙이기`에서 비대칭 카드마다 가능한 사용값 조합을 열거하고, 실제 행동을 확정하기 전에 선택값을 고르게 하는 것이다.
## 2단계 — 사용값 plan 열거와 합법성 미리보기

이 단계도 라이브 카드/행동에는 연결하지 않는다. 합성 비대칭 카드로 가능한 `top/bottom` 선택을 **원본 카드 상태를 바꾸지 않고** 탐색한다.

- `rankChoiceOptions(card)`: 이미 `activeRank`가 고정된 카드는 1개 고정 후보, 일반 `X/X`도 1개 기본 후보, 미확정 `X/Y`만 `top → bottom` 두 후보를 낸다.
- `rankChoicePlans(cards)`: 사용자가 고른 카드 배열 순서를 유지하며 후보의 데카르트 곱을 만든다. 현재 다중 붙이기 탐색 상한과 맞춰 기본 최대 64개 plan으로 제한한다.
- `projectRankChoiceCards(cards, plan)`: 실제 카드 객체는 건드리지 않고 얕은 복제본의 `rank/activeRank/rankOrientation`만 plan대로 투영한다.
- `legalRankChoicePlansForNewMeld(cards)`: 정확히 3장의 projection을 기존 `meldType()`에 통과시켜 합법 세트/런 plan만 반환한다.
- `legalRankChoicePlansForAttach(meld, cards)`: 대상 공개 조합 + projection이 원래 조합 종류를 유지하는 plan만 반환한다. 단일/다중 붙이기에 같은 함수를 쓴다.
- `rankChoicePreview(cards, meld?)`: 향후 UI가 사용할 수 있도록 선택 필요 여부, 합법 plan 수, 각 카드의 선택 랭크/방향을 직렬화한다.

### 경계 규칙

`activeRank`는 기존 엔진의 `rank` 미러로 투영되므로 새 런 규칙을 만들지 않는다. 따라서 기존과 동일하게 `A-2-3`, `Q-K-A`는 허용하고 `K-A-2`는 허용하지 않는다. 비대칭 카드는 이 판정을 우회하지 않고, 두 인쇄값 중 선택된 하나가 기존 `setValid/runValid`에 들어갈 뿐이다.

### 아직 하지 않는 것

- 실제 네임드 정의에 `topRank != bottomRank`를 넣지 않는다.
- 손패 클릭/붙이기 버튼에서 방향 선택 모달을 열지 않는다.
- AI가 방향을 선택하지 않는다.
- 조커·카운터피터·랭크 복사와의 최종 우선순위를 아직 확정하지 않는다.

## 3단계 — 행동 확정과 숫자 우선순위

아직 라이브 비대칭 카드 정의와 플레이어 방향 선택 UI는 추가하지 않는다. 이 단계는 2단계의 projection 결과를 **실제 행동 직전** 안전하게 확정하는 계층이다.

- `rankChoiceActionPlan(cards, meld?, requestedPlan?)`: 새 조합/붙이기의 합법 plan 중 요청한 방향 조합이 실제 합법 목록에 있는지 다시 확인한다. 미확정 비대칭 카드가 있는데 plan이 없으면 `choice-required`로 거부한다.
- `applyRankChoicePlan(cards, plan)`: 모든 카드의 plan을 먼저 검증한 뒤 비대칭 카드만 `activeRank/rankOrientation/rank`에 일괄 반영한다. 하나라도 맞지 않으면 아무 카드도 바꾸지 않으며 중간 실패 시 snapshot으로 롤백한다.
- `submitNewMeld(..., rankPlan)`과 `attachCards(..., rankPlan)`은 기존 모든 기본 가드를 먼저 확인한 다음 공개 조합으로 카드를 이동하기 직전에만 plan을 확정한다. 따라서 실패한 행동이 손패 카드의 방향을 오염시키지 않는다.
- 기존 함수 추출형 회귀와 호환하기 위해 rank-choice helper가 없는 격리 테스트 환경에서는 예전 `meldType()` 경로로 fallback한다. 실제 전체 게임에서는 helper가 항상 존재한다.

### 숫자 판정 우선순위

1. **조커 와일드**: 조커는 `baseRank/topRank/bottomRank/activeRank`를 사용하지 않는다. 기존 세트/런의 빈 자리를 대신하는 완전 와일드 판정이 가장 먼저 독립적으로 적용된다.
2. **인쇄값 선택**: 일반 정규 카드는 `X/X`, 비대칭 정규 카드는 `X/Y` 중 하나를 선택해 `activeRank`를 확정한다. 이 값이 기존 `rank` 미러가 되어 이후 판정의 입력이 된다.
3. **카드 고유 숫자 보정**: 카운터피터는 런 판정에서 선택된 값의 `-1/0/+1`을 임시 후보로 탐색한다. 도플갱어(`flexRankCopy`)는 세트 판정에서 다른 고정 카드 랭크를 복사한다. 두 효과 모두 `activeRank`나 원본 인쇄값을 다시 쓰지 않는다.
4. **효과/공격/러미 처리**: 합법 조합이 확정된 뒤 버스트·체인·카드 효과·러미가 기존 순서대로 실행된다. 이 시점의 실제 카드 `rank`는 선택된 `activeRank`와 일치한다.
5. **조합 정리**: 버스트 정리, 런 완주, 회수/재순환 등으로 공개 조합을 떠날 때 기존 중앙 초기화 경로가 `activeRank/rankOrientation`을 지우고 `rank=baseRank`로 되돌린다.

합성 회귀에서는 비대칭 세트로 새 조합을 만든 뒤 러미까지 선택값이 유지되는지, 비대칭 카드로 상대 세트를 버스트하거나 런 체인을 올릴 때 선택값이 공개 조합/공격 처리에 들어가는지, 잘못된 plan이 실제 카드 상태를 부분 변경하지 않는지 검사한다.

## 4단계 — CPU 사용값 선택

라이브 비대칭 카드를 추가하지 않은 채 CPU가 미래의 `X/Y` 카드를 정상적으로 사용할 수 있는 최소 계획 계층을 연결한다.

- 새 3장 조합: `bestNewMeld`가 손패 조합마다 `legalRankChoicePlansForNewMeld()`의 합법 방향을 모두 검사한다. 각 projection에 기존 새 조합 점수와 `futureBurstRisk()`를 그대로 적용하고 최고 점수의 `rankPlan`을 보존한다.
- 단일/다중 붙이기: `bestExtensionFromHand`가 최대 6장 조합의 모든 `legalRankChoicePlansForAttach()`를 검사한다. 선택된 projection으로 버스트 +24, 런 체인 단계 합계, 상대 공개 조합 보정, 테마 AI 보정을 계산한다.
- 스위치 반환 가치는 기존 AI 구조를 유지한다. 붙이기 후보의 점수 자체가 버스트/체인 위력을 포함하고, 현재 스위치가 CPU를 향하면 `continueAITurnAfterAcquisition()`이 새 조합보다 반환 가능한 붙이기를 우선한다. 따라서 비대칭 plan도 동일한 반환 판단에 들어간다.
- 실행 시 `bestNewMeld` / `bestExtensionFromHand`가 선택한 `rankPlan`을 각각 `submitNewMeld(..., rankPlan)` / `attachCards(..., rankPlan)`에 전달한다. CPU도 플레이어와 같은 원자적 plan 검증을 통과해야 실제 카드 방향이 확정된다.
- 완전 막힘 판정 `anyAttachOption`도 baseRank만 보지 않고 합법 top/bottom plan 존재 여부를 검사하므로, 다른 면으로는 붙일 수 있는 카드를 정비 대상으로 잘못 판정하지 않는다.
- 동점 plan은 기존 plan 열거 순서(카드 선택 순서, 위→아래)를 유지해 랜덤 노이즈 없이 결정적으로 선택한다.

이 단계도 현재 라이브 카드풀에는 `topRank/bottomRank` 비대칭 정의를 추가하지 않는다. 합성 회귀로만 CPU 선택과 실제 plan 전달을 검증한다.
