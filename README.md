# RUMMY//DUEL — FINAL CORE 2.0

Single-file mobile-first prototype for GitHub Pages.

## Deploy on GitHub Pages
1. Create a GitHub repository.
2. Upload `index.html`, `.nojekyll`, and optionally this `README.md` to the repository root.
3. Open **Settings → Pages**.
4. Set **Source** to **Deploy from a branch**.
5. Select **main** and **/(root)**, then save.

## Current core rules
- 3 CORE × 60 HP; DETONATE overkill never penetrates to the next CORE.
- 3-card SET → BURST READY; 4th suit → BURST +24 and the 4SET retires immediately.
- RUN extensions use CHAIN +10 / +15 / +20 / +25; RUNs do not have a free base retirement action.
- Each player may keep up to 2 public melds. A full board blocks creating another meld until normal play or a card effect changes the board; there is no free base meld disposal action.
- Cards may be attached to the opponent's public melds, and the player who actually completes BURST/CHAIN performs the SWITCH return.
- A card recovered this turn may still be used for a new 3-card meld, maintenance, discard, or other non-return play, but it cannot be reused that same turn as material for a BURST/CHAIN/SWITCH-returning attach unless a named effect explicitly allows it.
- One central SWITCH and uncapped accumulated power; 100+ is OVERLOAD, not an automatic explosion.
- No default grace turn. DETONATE deferral exists only through named card effects such as Safety Pin.
- The shared discard pile has no card-count cap; base acquisition only takes its top card. Card/field effects may access deeper cards.
- When a personal deck is empty, only that player's spent pile is shuffled into a new deck. The shared discard pile stays public.
- Normal maintenance cycles 1 card; when completely stuck, up to 2 cards.
- RUMMY refills 6 cards.
- Shield is temporary defense and normally expires at the start of its owner's next turn.

See `ROADMAP.md` for current implementation milestones.

Everything required to run the prototype is embedded in `index.html`.
