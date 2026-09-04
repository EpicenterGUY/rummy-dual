# TWELVE-BLOOM — Design Lock

Updated: 2026-09-04

## 0. Status

TWELVE-BLOOM is the renamed successor to the former HWA-TU candidate.

It keeps the twelve-month / seasonal-card visual inspiration, but it does not ask the player to know traditional hwatu/hanafuda scoring vocabulary. The player-facing language is limited to concepts that can be understood from the card text itself:

- 달
- 계절맞춤
- 붉은 띠 / 풀빛 띠 / 푸른 띠
- 새 셋
- 빛 셋
- 윤달

This document is a design lock, not a live implementation. Until the matching engine, UI preview, AI weighting, unlocks, tutorial, and full regression are implemented, TWELVE-BLOOM must not appear as a normal selectable/live theme or normal roguelike reward theme.

---

## 1. Core identity

달을 모은다 → 계절을 맞춘다 → 정확한 그림맞춤을 노린다 → 공개 카드의 위치를 바꿔 다음 맞춤을 준비한다.

TWELVE-BLOOM is an open set-collection layer that sits on top of normal RUMMY//DUEL play.

- SET/RUN legality continues to use the printed rank and suit.
- BURST/CHAIN/SWITCH/RUMMY timing stays unchanged.
- A card can participate in a TWELVE-BLOOM match while still being an ordinary, another-theme, or PURE-slot card.
- The theme grants no extra basic new-meld action and no extra basic attach action.
- There is no bloom point, month gauge, ribbon counter, or other accumulating numeric resource.

## 2. Month mapping

Only TWELVE-BLOOM matching reads ranks as months.

| Rank | Month |
| --- | ---: |
| A | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | 4 |
| 5 | 5 |
| 6 | 6 |
| 7 | 7 |
| 8 | 8 |
| 9 | 9 |
| 10 | 10 |
| J | 11 |
| Q | 12 |

### K and the leap month

K is not automatically a 13th month and not automatically a wildcard.

A card effect may designate one of the player's owned public K cards as 윤달 and assign it one month from 1–12.

1. Each player can maintain at most one designated 윤달 card across both public boards.
2. Designating a new 윤달 clears that player's previous 윤달 designation.
3. The chosen month is fixed until a card effect explicitly reassigns it or that K leaves the public board.
4. The K keeps its printed K rank and suit for normal SET/RUN legality.
5. 윤달 can replace at most one missing month in one 계절맞춤 check.
6. 윤달 cannot satisfy an exact 그림맞춤, because 그림맞춤 checks exact printed rank+suit slots.
7. Entering hand, deck, discard, or spent clears the 윤달 designation.

### Jokers

Jokers do not count as a month or exact picture for TWELVE-BLOOM by default.

A future card could explicitly say otherwise, but the locked 24-card candidate pool below contains no such exception. This prevents ordinary Joker wildcard rules from making the match layer too loose.

## 3. Public material

A player's TWELVE-BLOOM material is:

- that player's owned cards in their own public melds;
- that player's owned cards currently sitting in the opponent's public melds.

The following do not count:

- hand;
- personal deck;
- shared discard;
- personal spent;
- opponent-owned cards.

Therefore an ordinary card, V-SIGNAL card, ZERO-SIGHT card, POINT-BLANK card, MAIL-ROUTE card, or SCRAP-SHIFT card can all be matching material if the player owns the physical card and it is public.

Theme identity is never a matching requirement.

## 4. Season matches

There are four broad 계절맞춤 patterns.

| Match | Required months |
| --- | --- |
| 봄맞춤 | 1 · 2 · 3 |
| 여름맞춤 | 4 · 5 · 6 |
| 가을맞춤 | 7 · 8 · 9 |
| 겨울맞춤 | 10 · 11 · 12 |

A season match needs at least one owned public card for each of its three months.

- Suit does not matter.
- Extra cards of the same month do not add stacks.
- One 윤달 may fill one missing month under the rules above.
- A Joker does not fill a month.
- A single physical card cannot count as two different months in the same check.

Season matches are the broad engine condition. They are intentionally easier than exact picture matches and are used for cycling, protection, movement, and setup more often than direct power.

## 5. Exact picture matches

Exact 그림맞춤 patterns use printed rank+suit slots and therefore cannot be satisfied by 윤달 or Jokers.

| Match | Exact public slots |
| --- | --- |
| 붉은 띠 | A♥ · 2♥ · 3♥ |
| 풀빛 띠 | 4♥ · 5♥ · 6♥ |
| 푸른 띠 | 7♥ · 8♥ · 9♥ |
| 새 셋 | 2♦ · 4♦ · 8♦ |
| 빛 셋 | A♠ · 8♠ · Q♠ |

The card occupying an exact slot may be PURE, ordinary NAMED, or another theme variant. Only the printed slot matters.

Exact picture matches are advanced rewards, not hidden alternate win conditions and not extra poker/rummy hands.

## 6. New-completion timing

TWELVE-BLOOM effects primarily read new completion, not permanent possession.

After a public-board-changing action resolves its physical card movement, the game compares the owner's match state before and after that action.

Relevant actions:

- new meld creation;
- attach;
- recovery;
- combat-neutral meld movement;
- dismantle / retirement or other public-card removal.

A match is newly completed only when it changes from incomplete to complete for that owner.

### Anti-loop contract

1. A continuously complete match does not repeatedly trigger merely because another unrelated card moved.
2. Breaking and rebuilding the same named match in the same turn cannot reward it twice; the owner+match key uses the normal turn token gate.
3. By default, a reward triggers only when the match owner performed the action that newly completed it.
4. A card that reacts to the opponent completing or breaking the owner's match must say so explicitly.
5. Match completion itself adds 0 power and never moves SWITCH.
6. Match completion grants no extra basic new-meld or attach count.
7. If one action completes a season match and an exact picture match simultaneously, both may be reported, but each individual card effect still follows its own once-per-turn gate.

## 7. UI / information policy

TWELVE-BLOOM must not turn every battle into a second hidden-board puzzle.

### Normal non-theme decks

- Do not permanently show month numbers, ribbon labels, bird/light labels, or match trackers.
- Normal rank/suit visuals remain unchanged.

### When TWELVE-BLOOM is relevant

Show only contextual information:

- compact tooltip/glossary: A=1월 … Q=12월;
- small 2/3 preview only for a match affected by the currently selected action;
- subtle completion chip for a currently complete match;
- exact picture name only when its three exact slots are complete or the current action could complete it;
- long RUNs keep their existing local horizontal scroll; no second row of permanent month badges is added.

The preview is advisory. The actual engine remains the source of truth.

## 8. Suit roles

- ♣ 탐색 / 달 조정 / 패순환 — near-match detection, maintenance, 윤달 assignment, RUMMY cycling.
- ♥ 띠 / 생존 / 회수 — ribbon picture matches, protection, healing, controlled recovery.
- ♦ 새 / 이동 / 상대 공개 조합 — moving owned public cards, opponent-meld play, bird trio.
- ♠ 빛 / 압박 / 반환 — seal/vulnerable pressure and the small direct-return-power finisher lane.

## 9. Locked 24-card candidate pool

The pool is 24 cards, six per suit. Names and exact numbers can still receive balance tuning during implementation, but each card's action lane and physical slot are locked for the first implementation pass.

### ♣ — 탐색 / 패순환 / 윤달

1. A♣ 달력 펼치기 — 새 3장 조합에 들어가면 남은 손패 1장을 무료 정비한다. 이번 행동으로 계절맞춤도 새로 완성했다면 정비 후 카드 1장을 뽑고 손패 1장을 덱 아래로 보낸다.
2. 3♣ 빈달 찾기 — 사용한 행동이 끝난 뒤 내 공개 카드가 어떤 계절에서 정확히 2개월만 갖춘 상태라면 카드 1장을 뽑고 손패 1장을 덱 아래로 보낸다. 턴당 1회.
3. 5♣ 계절 표본 — 내 행동으로 계절맞춤을 새로 완성하면 카드 1장을 뽑는다. 턴당 1회.
4. 7♣ 윤달 표식 — 사용하면 내 공개 K 1장을 윤달로 지정하고 1~12월 중 하나를 고른다. 합법 대상이 없으면 남은 손패 1장을 무료 정비한다.
5. 10♣ 겨울 채집 — 겨울맞춤을 새로 완성하면 카드 1장을 뽑고 손패 1장을 덱 아래로 보낸다. 그 행동이 반환이어도 추가 SWITCH 이동은 만들지 않는다.
6. Q♣ 한 해 넘기기 — RUMMY 리필 뒤 내 공개 계절맞춤이 하나 이상 완성되어 있으면 손패 1장을 무료 정비한다.

### ♥ — 띠 / 생존 / 회수

1. A♥ 붉은 띠 — 붉은 띠 그림맞춤을 새로 완성하면 보호막 12.
2. 3♥ 봄매듭 — 봄맞춤을 새로 완성하면 그 행동에 사용된 내 공개 카드 1장에 보호 1.
3. 5♥ 풀빛 띠 — 풀빛 띠 그림맞춤을 새로 완성하면 현재 코어 8 회복.
4. 7♥ 푸른 띠 — 푸른 띠 그림맞춤을 새로 완성하면 유효성을 유지하는 내 공개 카드 1장을 무료 회수할 수 있다. 일반 동일 턴 반환 제한은 유지.
5. 10♥ 계절 되감기 — 현재 완성된 계절맞춤 하나를 고르고, 그 계절의 내 공개 카드 중 빼도 조합이 유지되는 카드 1장을 무료 회수할 수 있다. 이 효과로 깨진 맞춤은 같은 턴 다시 완성해도 그 맞춤 보상을 재발동하지 않는다.
6. K♥ 윤달 매듭 — 이 카드가 공개 조합에 들어가면 자신을 윤달로 지정해 1~12월 중 하나를 고를 수 있다. 그 지정으로 계절맞춤이 새로 완성되면 보호막 8.

### ♦ — 새 / 이동 / 상대 공개 조합

1. 2♦ 봄새 — 이 카드가 상대 공개 조합에 들어가는 행동으로 계절맞춤을 새로 완성하면 카드 1장을 뽑는다.
2. 4♦ 건너는 새 — 내 공개 카드 1장을 원본과 목적지가 모두 유효한 다른 공개 조합으로 이동할 수 있다. 이동 자체는 전투 중립. 이동으로 계절맞춤을 새로 완성하면 카드 1장을 뽑는다.
3. 6♦ 날갯짓 — 이번 턴 처음 내 카드가 내 조합과 상대 조합 사이를 이동하면 남은 손패 1장을 무료 정비한다.
4. 8♦ 돌아오는 새 — 상대 공개 조합에서 이 카드를 회수하면 다른 내 공개 카드 1장을 합법적인 다른 공개 조합으로 이동할 수 있다. 이동 자체는 전투 중립.
5. 10♦ 새 셋 — 새 셋 그림맞춤을 새로 완성하면 카드 2장을 뽑고 손패 1장을 덱 아래로 보낸다.
6. Q♦ 철새 길 — 턴당 처음 내 카드가 상대 공개 조합에 들어가면서 계절맞춤을 새로 완성하면 그 들어간 내 카드 1장에 보호 1.

### ♠ — 빛 / 압박 / 반환

1. A♠ 첫빛 — 턴당 처음 계절맞춤을 새로 완성하면 상대 공개 조합 하나에 봉인 1을 부여할 수 있다. 상대 조합이 없으면 보호막 8.
2. 3♠ 비치는 틈 — 상대 공개 조합을 이용한 행동으로 계절맞춤을 새로 완성하면 그 상대 조합에 봉인 1. 이미 봉인이 있으면 대신 내 카드 1장에 보호 1.
3. 6♠ 겹빛 — 한 행동으로 계절맞춤과 그림맞춤을 각각 하나 이상 동시에 새로 완성하면 상대에게 취약 1. 턴당 1회.
4. 8♠ 큰빛 — 빛 셋 그림맞춤을 새로 완성하면 내 공개 카드 1장에 보호 1을 부여하고 보호막 8.
5. 10♠ 낙조 — SWITCH를 반환하는 행동이 계절맞춤을 새로 완성했다면 이번 반환 누적 위력이 10 증가한다. 턴당 1회.
6. Q♠ 빛 셋 — 빛 셋 그림맞춤이 이미 완성된 상태에서 이 카드가 포함된 조합으로 SWITCH를 반환하면 이번 반환 누적 위력이 14 증가한다. 턴당 1회.

Direct return-power cards are limited to 10♠ 낙조 and Q♠ 빛 셋 in the first pool.

## 10. Implementation gate

Before TWELVE-BLOOM can become live:

- [x] Name and player-facing vocabulary locked.
- [x] A–Q month mapping locked.
- [x] K leap-month lifecycle and one-designation limit locked.
- [x] Joker default non-participation locked.
- [x] Four season matches locked.
- [x] Five exact picture matches locked.
- [x] Mixed-deck public-material rule locked.
- [x] New-completion / same-turn anti-loop contract locked.
- [x] 24-card / six-per-suit candidate pool locked.
- [x] No extra base new-meld/attach actions and no numeric theme resource.
- [x] Match evaluator + before/after snapshots implemented — public material is read across both boards by card ownership, with season/picture snapshots and newly-completed/broken diffs.
- [x] Leap-month metadata lifecycle implemented — one owned public K per player, 1–12 assignment, atomic reassignment, and automatic clearing on hand/deck/discard/spent/public-retire exits.
- [x] Contextual match preview UI implemented — hidden unless TWELVE-BLOOM-relevant material exists; selected new-meld/attach/recovery projections show only affected completion, break, or 2/3 missing-piece information.
- [ ] 24 card effects implemented.
- [ ] Unlock/codex/build/tutorial/roguelike integration implemented.
- [ ] Single-theme / every two-theme / mixed / long-RUN UI regression completed.
- [ ] Match looseness and direct-power ratio simulation completed.
