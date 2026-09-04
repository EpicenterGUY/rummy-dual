# TWELVE-BLOOM — Pre-live Balance Gate Results

Date: 2026-09-04

## Verdict

TWELVE-BLOOM passes the pre-live balance/UI gate without numeric card-effect changes.

- 24/24 effects remain staged behind `live:false`.
- Normal unlocks and ordinary roguelike rewards still expose **0 TWELVE-BLOOM cards**.
- The next gate is the explicit live-exposure change: normal unlock groups, normal reward pool, build/tutorial visibility, and release-facing copy.
- No base RUMMY//DUEL rule was changed by this study.

## Post-gate activation — 2026-09-05

Following this PASS, TWELVE-BLOOM was promoted to normal play. The six pre-live unlock tiers became the normal 1–6-clear unlock schedule, and the live build/tutorial/codex/reward paths were enabled without changing card-effect numbers or base RUMMY//DUEL rules.

The results below remain the frozen pre-live study snapshot; statements about zero normal exposure describe the state during that study, not the post-activation runtime.

## Coverage

Static/executable regression:

- maximum-density TWELVE-BLOOM open build, 64 deterministic seeds;
- every two-theme composition across the six-theme matrix;
- mixed composition, 128 deterministic seeds;
- physical slot exclusivity and nine-NAMED module size;
- direct-power ratio including 10♠ `낙조` and Q♠ `빛 셋`;
- long-RUN local horizontal scroll plus wrapped/aggregated TWELVE-BLOOM preview;
- all 24 effects, anti-loop matching, final-action snapshot timing, DEV-only build/codex/reward/tutorial staging.

Actual-engine stress simulation:

- GitHub Actions run `33874719996`: 9 cohorts × 500 battles.
- GitHub Actions run `33874827871`: SET/RUN structure baselines × 500 battles.
- Total analyzed battles: **5,500**.
- Real shipped engine paths were used for acquisition, meld creation, attach, recover, maintenance, RUMMY, recycle, SWITCH return, detonation and effect choices.
- Optional/required effect choices deterministically took the first legal option to stress effect resolution rather than suppress it.
- Battle cap: 120 side-turns.

## Structure comparison

| Cohort | Avg turns | capped /500 | Low hand 1–3 | RUMMY /100 | Match actions /100 | Recycles | Emergency | Full recirc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline mixed | 52.49 | 27 | 72.55% | 8.34 | 12.89 | 2,193 | 0 | 0 |
| TWELVE mixed | 52.55 | 20 | 72.95% | 8.06 | 12.90 | 1,955 | 0 | 0 |
| baseline SET | 56.08 | 13 | 69.56% | 9.75 | 4.14 | 1,683 | 0 | 0 |
| TWELVE SET | 58.34 | 22 | 68.71% | 9.74 | 4.07 | 1,751 | 0 | 0 |
| baseline RUN | 58.70 | 96 | 79.49% | 8.37 | 15.98 | 5,767 | 11 | 0 |
| TWELVE RUN | 56.08 | 85 | 80.45% | 7.59 | 16.24 | 5,214 | 2 | 0 |

Interpretation:

- Mixed battle length is effectively unchanged: **52.49 → 52.55** (+0.1%).
- TWELVE does not create the RUN circulation/long-battle pattern. The ordinary RUN baseline is actually longer and recycles more often than TWELVE RUN.
- TWELVE RUN reduces average battle length by about 4.5%, recycles by about 9.6%, and emergency releases from 11 to 2 versus the RUN baseline.
- TWELVE SET is about 4.0% longer than the SET baseline. The cap rate rises by 1.8 percentage points, but circulation remains normal and no full recirculation occurs.
- Across all structure comparisons, the match-completion rate changes only slightly. Match looseness is therefore driven primarily by SET/RUN board geometry, not by adding TWELVE-BLOOM identity cards.

## Live-theme pair stress

| Cohort | Avg turns | capped /500 | Match actions /100 | RUMMY /100 | Recycles | Emergency | Full recirc |
|---|---:|---:|---:|---:|---:|---:|---:|
| TWELVE + V-SIGNAL | 51.96 | 19 | 12.66 | 8.33 | 1,900 | 0 | 0 |
| TWELVE + ZERO-SIGHT | 52.35 | 25 | 12.67 | 8.15 | 2,053 | 0 | 0 |
| TWELVE + POINT-BLANK | 53.95 | 29 | 12.62 | 7.49 | 2,025 | 0 | 0 |
| TWELVE + MAIL-ROUTE | 50.64 | 16 | 13.06 | 7.87 | 1,648 | 0 | 0 |
| TWELVE + SCRAP-SHIFT | 50.77 | 18 | 13.04 | 8.35 | 1,878 | 0 | 0 |

No pair produces full recirculation or emergency-release pressure.

## Match looseness

The matching evaluator intentionally reads printed month/picture material from all owned public cards, not only TWELVE-BLOOM cards. Therefore a no-TWELVE control still has latent match geometry; TWELVE cards determine whether those completions have theme payoffs.

Observed new-completion actions per 100 side-turns:

- mixed: 12.89 baseline / 12.90 TWELVE;
- SET: 4.14 baseline / 4.07 TWELVE;
- RUN: 15.98 baseline / 16.24 TWELVE.

Season completions also remain nearly identical inside each structure:

- mixed: 12.28 / 12.25;
- SET: 3.88 / 3.77;
- RUN: 13.88 / 14.06.

This supports the intended rule that theme identity is not a matching requirement and shows that adding TWELVE variants does not itself loosen the matching condition.

## Direct return power

Static pool check after adding TWELVE-BLOOM:

- direct-power definitions: **14 / 198** total NAMED definitions;
- direct-power theme cards: **11 / 136** implemented theme definitions;
- both remain well below existing regression limits.

Actual-engine TWELVE direct effects were rare under stress play:

| Cohort | 10♠ triggers | Q♠ triggers | triggers /100 returns | bonus power /100 turns |
|---|---:|---:|---:|---:|
| TWELVE mixed | 18 | 23 | 0.37 | 1.91 |
| TWELVE SET | 3 | 3 | 0.06 | 0.25 |
| TWELVE RUN | 4 | 30 | 0.28 | 1.64 |
| + V-SIGNAL | 10 | 14 | 0.22 | 1.14 |
| + ZERO-SIGHT | 12 | 16 | 0.26 | 1.31 |
| + POINT-BLANK | 9 | 10 | 0.17 | 0.85 |
| + MAIL-ROUTE | 11 | 15 | 0.23 | 1.26 |
| + SCRAP-SHIFT | 5 | 31 | 0.33 | 1.91 |

10♠/Q♠ therefore do not occupy a dominant share of SWITCH returns.

## UI / long RUN

The existing board remains the primary surface.

- normal non-TWELVE battles keep month/picture information hidden;
- TWELVE preview displays only affected completion, break, or 2/3 information;
- preview chips wrap instead of extending meld width;
- long public RUN cards remain in the existing `.meldCardRow` local horizontal scroller;
- match preview data is aggregated by the fixed four seasons/five pictures rather than by card count.

Covered by `tests/twelve-bloom-preview.mjs`.

## Final gate status

Approved at the **pre-live balance** level:

- effect pool: PASS;
- mixed-theme interoperability: PASS;
- match looseness: PASS;
- direct-power ratio: PASS;
- deck circulation/deadlock: PASS;
- long-RUN UI containment: PASS;
- normal-user exposure: intentionally still OFF.

No effect number or base-rule adjustment is recommended before the live-exposure step.
