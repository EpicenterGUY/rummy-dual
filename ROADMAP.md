# RUMMY//DUEL Development Roadmap

Updated: 2026-08-30

## Core direction
RUMMY//DUEL is a 1v1 rummy battle game where both players grow one central SWITCH bomb through SET/BURST and RUN/CHAIN, including play on the opponent's public melds.

## M0 — Rule lock
- [x] 3 CORE × 60, no overkill pierce
- [x] SET 3 → BURST READY; fourth suit → +24 and retire
- [x] RUN CHAIN +10 / +15 / +20 / +25
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
- [ ] Normalize official statuses: vulnerable, seal, fixed, protect, regen
- [ ] Support player / meld / card attachment scopes
- [ ] Define reusable effect events/actions without introducing new base resources

## M8 — Named cards
- [ ] Stabilize first ~50 named cards
- [ ] Keep direct SWITCH manipulation to a minority of the pool
- [ ] Favor meld mutation, recovery, movement, discard, defense, RUMMY and timing interactions

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
1. M7: normalize the five official statuses without turning one-off card markers into global status rules.
2. M7: define player / public-meld / individual-card attachment scopes and lifecycle timing.
3. M7: introduce reusable effect events/actions gradually, keeping the prototype buildless and current cards behavior-compatible.
