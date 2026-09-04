# RUMMY//DUEL — FINAL CORE 2.0

Single-file mobile-first prototype for GitHub Pages.

## Menus and development sessions

The main menu contains **대전 / 로그라이크 / 튜토리얼 / 카드 도감 / 설정**. Battle setup reveals character and deck choices in two steps. Roguelike opens Continue / New game / Records, then shows only the current starter, battle, reward, or region decision. Free practice and advanced/theme lessons live under Tutorial.

Settings provides reduced motion and larger explanatory text. **설정 → 개발자 작업실** opens the DEV sandbox with character/theme/deck/field controls, manual run rewards and existing experiments. DEV profiles, runs and completion history use separate storage; DEV battles never award normal progress. Returning home or reloading restores normal mode. See `docs/UX2_PROGRESSIVE_DISCLOSURE.md` for the UI and persistence contract.

## Deploy on GitHub Pages
1. Create a GitHub repository.
2. Upload `index.html`, `.nojekyll`, and optionally this `README.md` to the repository root.
3. Open **Settings → Pages**.
4. Set **Source** to **Deploy from a branch**.
5. Select **main** and **/(root)**, then save.

## Current core rules
- 3 CORE × 60 HP; DETONATE overkill never penetrates to the next CORE.
- 3-card SET → BURST READY; 4th suit → BURST +24 and the 4SET retires immediately.
- RUN extensions use CHAIN +10 / +15 / +20 / +25. At CHAIN 4+, the meld controller may voluntarily **complete the RUN** on their own turn to free that public-meld slot; if kept, later extensions remain +25. Completing a RUN adds no power and does not move SWITCH.
- Each player may keep up to 3 own public melds. When all 3 are full, once per own turn the player may clean up one older, non-fixed own meld for +0 power and no SWITCH movement; a meld created that turn cannot be cleaned up. Opponent melds containing your cards do not consume your slots.
- Each player may create at most two new exact 3-card melds (SET or RUN combined) per turn.
- Cards may be attached to the opponent's public melds, and the player who actually completes BURST/CHAIN performs the SWITCH return.
- Base attach is one action per player turn. One attach action may add multiple legal cards to a RUN, resolving CHAIN +10 / +15 / +20 / +25 in order while SWITCH moves only once. Repeating attach in the same turn requires a named card that explicitly grants an extra attach; that extra attach may add power but does not move SWITCH a second time.
- A card recovered this turn may still be used for a new 3-card meld, maintenance, discard, or other non-return play, but it cannot be reused that same turn as material for a BURST/CHAIN/SWITCH-returning attach unless a named effect explicitly allows it, and that exception is bound to the destination meld(s) allowed by that effect.
- One central SWITCH and uncapped accumulated power; 100+ is OVERLOAD, not an automatic explosion.
- No default grace turn. DETONATE deferral exists only through named card effects such as Safety Pin.
- The shared discard pile has no card-count cap; base acquisition only takes its top card. Card/field effects may access deeper cards.
- When a personal deck is empty, recycle that player's spent pile plus cards in the shared discard currently owned by that player; opponent-owned discard and public meld cards stay in place.
- Normal maintenance cycles 1 card; when completely stuck, up to 2 cards.
- Low-hand protection: when only the base discard remains and the hand is 1–3 cards, that base discard may be skipped; extra discards created by card effects must be paid first.
- If both players are simultaneously unable to acquire or recover cards, perform one full recirculation: return all cards from hands/decks/spent/shared discard/public melds to their current owners, shuffle, and deal up to 6 each. CORE/HP/shield/SWITCH power and target remain. A second full stall is resolved by remaining CORE, then current CORE HP, then draw.
- RUMMY refills 6 cards.
- Shield is temporary defense with no base hard cap; it normally expires at the start of its owner's next turn.

See `ROADMAP.md` for current implementation milestones.

Everything required to run the prototype is embedded in `index.html`.

### Local validation

The game remains buildless on GitHub Pages. `npm run dev -- --host 0.0.0.0 --port 4173` starts a dependency-free local preview. `/qa/m0r` is a preview-only layout fixture with selectable CSS viewport sizes and three long RUNs per side. Run `node tests/m0r-meld-expansion.mjs` for the full-engine rule regression and `node experiments/m0r-opening-tempo.mjs` for the paired opening-tempo experiment.

`/qa/ui` previews normal menus, staged run screens and DEV controls at selectable CSS viewport sizes using isolated in-memory saves. `node tests/ux2-menu-isolation.mjs` checks the actual engine's normal/DEV persistence boundaries and complete run flows. Recorded browser measurements are in `docs/UX2_LAYOUT_RESULTS.json`.
