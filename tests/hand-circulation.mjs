import {createStatusContext} from './helpers/status-fixture.mjs';
import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

function functionSource(name) {
  const marker = `function ${name}(`;
  const start = script.indexOf(marker);
  if (start < 0) throw new Error(`missing function ${name}`);
  const bodyMarker = script.indexOf('){', start);
  if (bodyMarker < 0) throw new Error(`missing body for ${name}`);
  const brace = bodyMarker + 1;
  let depth = 0, end = -1;
  for (let i = brace; i < script.length; i++) {
    if (script[i] === '{') depth++;
    else if (script[i] === '}') {
      depth--;
      if (depth === 0) { end = i + 1; break; }
    }
  }
  if (end < 0) throw new Error(`unterminated function ${name}`);
  return script.slice(start, end);
}

function context(extra = {}) {
  return createStatusContext(script,{ console, Math, Set, Map, Array, Object, Number, String, Boolean, ...extra });
}

function install(ctx, ...names) {
  for (const name of names) vm.runInContext(functionSource(name), ctx);
}

let seq = 0;
function card(suit, rank, extra = {}) {
  return {
    uid: `${suit}${rank}-${++seq}`,
    suit,
    rank: String(rank),
    named: false,
    owner: 'player',
    blockedUntilTurn: null,
    recoveredToken: null,
    recoverReturnOverrideToken: null,
    contractActive: false,
    fromDiscard: false,
    age: 0,
    ...extra,
  };
}

function meldType(cards) {
  if (cards.length >= 3 && cards.length <= 4) {
    const ranks = new Set(cards.map(c => c.rank));
    const suits = new Set(cards.map(c => c.suit));
    if (ranks.size === 1 && suits.size === cards.length) return 'SET';
  }
  if (cards.length >= 3) {
    const suit = cards[0]?.suit;
    if (suit && cards.every(c => c.suit === suit)) {
      const vals = cards.map(c => Number(c.rank)).sort((a, b) => a - b);
      if (vals.every((v, i) => i === 0 || v === vals[i - 1] + 1)) return 'RUN';
    }
  }
  return null;
}

function makeLegalityContext() {
  const player = {
    hand: [], deck: [card('C', 13)], spent: [], melds: [],
    newMeldCount:0, returnedSwitchThisTurn: false, maintenanceUsed: false,
  };
  const enemy = {
    hand: [], deck: [], spent: [], melds: [],
    newMeldCount:0, returnedSwitchThisTurn: false, maintenanceUsed: false,
  };
  const state = { player, enemy, discard: [], turnNo: 9, turnToken: 21, switchTarget: 'neutral', gameOver: false, turn: 'player', phase: 'action' };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.other = w => w === 'player' ? 'enemy' : 'player';
  ctx.meldsOf = w => ctx.sideObj(w).melds;
  ctx.canSideReturn = w => state.switchTarget === 'neutral' || state.switchTarget === w;
  ctx.meldType = meldType;
  ctx.meldFixedActive = () => false;
  ctx.cardFixedActive = () => false;
  install(ctx, 'combinations', 'bestNewMeld', 'bestNewMeldForTurn', 'recoveredCardCanReturn', 'recoveredCardsCanReturn', 'anyAttachOption', 'canFinishRun', 'hasAnyLegalAction', 'ownedRecycleCount', 'maintenanceLimit');
  return { ctx, state, player, enemy };
}

// Normal legal new meld means ordinary one-card maintenance, not stuck compensation.
{
  const { ctx, player } = makeLegalityContext();
  player.hand = [card('S', 7), card('H', 7), card('D', 7), card('C', 2)];
  ok(ctx.hasAnyLegalAction('player'), 'legal 3SET counts as a basic legal action');
  ok(ctx.maintenanceLimit('player') === 1, 'legal basic action keeps maintenance at one card');
}

// A full three-meld board blocks a new meld, so a hand with no attach is genuinely stuck.
{
  const { ctx, player } = makeLegalityContext();
  player.hand = [card('S', 7), card('H', 7), card('D', 7), card('C', 2)];
  player.melds = [
    { type: 'SET', cards: [card('S', 3), card('H', 3), card('D', 3)], lastAttachToken: null, createdToken: null },
    { type: 'SET', cards: [card('S', 4), card('H', 4), card('D', 4)], lastAttachToken: null, createdToken: null },
    { type: 'SET', cards: [card('S', 5), card('H', 5), card('D', 5)], lastAttachToken: null, createdToken: null },
  ];
  ok(!ctx.hasAnyLegalAction('player'), 'new meld in hand does not count when public board is already 3/3 and no attach exists');
  ok(ctx.maintenanceLimit('player') === 2, 'full-board dead hand receives two-card stuck maintenance');
}

// A card blocked for the current turn cannot falsely prevent stuck compensation.
{
  const { ctx, state, player } = makeLegalityContext();
  player.hand = [card('S', 7), card('H', 7), card('D', 7, { blockedUntilTurn: state.turnNo }), card('C', 2)];
  ok(!ctx.hasAnyLegalAction('player'), 'current-turn blocked card is excluded from new-meld legality');
  ok(ctx.maintenanceLimit('player') === 2, 'blocked-only meld line still qualifies as completely stuck');
}

// A recovered card may exist in hand but cannot count as an immediate returning attach unless explicitly overridden.
{
  const { ctx, state, player, enemy } = makeLegalityContext();
  const recovered = card('H', 8, { recoveredToken: state.turnToken });
  player.hand = [recovered, card('C', 2), card('D', 11)];
  enemy.melds = [{ type: 'RUN', cards: [card('H', 5), card('H', 6), card('H', 7)], chain: 0, lastAttachToken: null, createdToken: null }];
  ok(!ctx.anyAttachOption('player'), 'same-turn recovered card is excluded from returning attach legality');
  ok(ctx.maintenanceLimit('player') === 2, 'illegal recovered-card return does not suppress stuck maintenance');
  recovered.recoverReturnOverrideToken = state.turnToken;
  ok(ctx.anyAttachOption('player'), 'explicit named override restores the recovered-card attach as a legal basic return');
  ok(ctx.maintenanceLimit('player') === 1, 'legal override attach returns maintenance to normal one-card limit');
}

// After already using the one SWITCH return, an otherwise attach-only hand is stuck for basic-rummy purposes.
{
  const { ctx, player, enemy } = makeLegalityContext();
  player.hand = [card('H', 8), card('C', 2), card('D', 11)];
  player.returnedSwitchThisTurn = true;
  enemy.melds = [{ type: 'RUN', cards: [card('H', 5), card('H', 6), card('H', 7)], chain: 0, lastAttachToken: null, createdToken: null }];
  ok(!ctx.anyAttachOption('player'), 'one-return-per-turn rule removes further basic attach options');
  ok(ctx.maintenanceLimit('player') === 2, 'return-spent attach-only hand gets stuck maintenance');
}

// Maintenance operation puts exchanged cards at deck bottom and draws from deck top.
{
  const player = { hand: [], deck: [], spent: [], melds: [], maintenanceUsed: false, actedThisTurn: false };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const state = { player, enemy, discard: [] };
  const a = card('S', 2), keep = card('H', 9), bottom = card('C', 3), top = card('D', 12);
  player.hand = [a, keep];
  player.deck = [bottom, top];
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs;
  ctx.log = () => {};
  ctx.removeFromHand = (w, cards) => {
    const ids = new Set(cards.map(c => c.uid));
    ctx.sideObj(w).hand = ctx.sideObj(w).hand.filter(c => !ids.has(c.uid));
  };
  ctx.maintenanceLimit = () => 1;
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne', 'performMaintenance');
  const got = ctx.performMaintenance('player', [a]);
  ok(got.length === 1 && got[0] === top, 'maintenance draws replacement from the personal deck top');
  ok(player.deck[0] === a, 'exchanged card is placed at the personal deck bottom');
  ok(player.hand.includes(keep) && player.hand.includes(top) && !player.hand.includes(a), 'maintenance preserves other hand cards and replaces only selected card');
  ok(player.maintenanceUsed && player.actedThisTurn, 'maintenance consumes its once-per-turn use and marks an action');
}

// Deck exhaustion recycles only personal spent cards and never consumes the shared discard pile.
{
  const player = { hand: [], deck: [], spent: [], melds: [] };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const publicDiscard = card('D', 5, { owner: 'enemy' });
  const s1 = card('S', 10), s2 = card('H', 11);
  player.spent = [s1, s2];
  const state = { player, enemy, discard: [publicDiscard], turnNo: 1 };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs;
  ctx.log = () => {};
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne');
  const drawn = ctx.drawOne('player', false);
  ok(drawn === s2 && player.hand.includes(s2), 'empty personal deck draws from recycled personal spent pile');
  ok(player.spent.length === 0 && player.deck.length === 1 && player.deck[0] === s1, 'spent pile is fully recycled into the personal deck');
  ok(state.discard.length === 1 && state.discard[0] === publicDiscard, 'shared discard pile remains untouched by personal deck recycling');
}

// Drawing the final personal-deck card immediately rebuilds the deck from any existing personal spent pile.
{
  const player = { hand: [], deck: [], spent: [], melds: [] };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const last = card('C', 4), s1 = card('S', 10), s2 = card('H', 11);
  const publicDiscard = card('D', 5, { owner: 'enemy' });
  player.deck = [last];
  player.spent = [s1, s2];
  const state = { player, enemy, discard: [publicDiscard], turnNo: 1 };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs;
  ctx.log = () => {};
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne');
  const drawn = ctx.drawOne('player', false);
  ok(drawn === last && player.hand.includes(last), 'the final original deck card is still the card actually drawn');
  ok(player.spent.length === 0 && player.deck.length === 2, 'drawing the final deck card immediately rebuilds the personal deck from spent cards');
  ok(player.deck[0] === s1 && player.deck[1] === s2, 'immediate rebuild preserves the shuffled spent-card deck contents');
  ok(state.discard.length === 1 && state.discard[0] === publicDiscard, 'immediate personal recycle still leaves the shared discard untouched');
}

// PURE-safe recycle: an empty personal deck reclaims both personal spent and currently-owned cards from the shared discard.
{
  const player = { hand: [], deck: [], spent: [], melds: [] };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const spentCard = card('S', 10, { owner: 'player' });
  const ownDiscard = card('D', 5, { owner: 'player' });
  const enemyDiscard = card('C', 9, { owner: 'enemy' });
  const transferredAway = card('H', 4, { owner: 'enemy', originOwner: 'player' });
  const boardCard = card('S', 7, { owner: 'player' });
  player.spent = [spentCard];
  player.melds = [{ type: 'SET', cards: [boardCard, card('H', 7), card('D', 7)] }];
  const state = { player, enemy, discard: [enemyDiscard, ownDiscard, transferredAway], turnNo: 1 };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs;
  ctx.log = () => {};
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne');
  const drawn = ctx.drawOne('player', false);
  const recycled = new Set([...player.hand, ...player.deck].map(c => c.uid));
  ok(recycled.has(spentCard.uid) && recycled.has(ownDiscard.uid), 'empty deck recycles personal spent plus currently-owned shared-discard cards');
  ok(drawn && player.spent.length === 0, 'recycle can immediately supply the next draw even when PURE has no named-card circulation effect');
  ok(state.discard.length === 2 && state.discard.includes(enemyDiscard) && state.discard.includes(transferredAway), 'opponent-owned discard remains public even when originOwner was the recycling player');
  ok(!state.discard.includes(ownDiscard), 'currently-owned player card is removed from shared discard during recycle');
  ok(player.melds[0].cards.includes(boardCard) && !recycled.has(boardCard.uid), 'public meld cards are never reclaimed by deck recycling');
}

// Recycle must also work when spent is empty and the only available personal cards are in shared discard.
{
  const player = { hand: [], deck: [], spent: [], melds: [] };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const ownDiscard = card('C', 6, { owner: 'player' });
  const enemyDiscard = card('D', 8, { owner: 'enemy' });
  const state = { player, enemy, discard: [enemyDiscard, ownDiscard], turnNo: 1 };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs;
  ctx.log = () => {};
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne');
  const drawn = ctx.drawOne('player', false);
  ok(drawn === ownDiscard && player.hand.includes(ownDiscard), 'owned shared-discard card alone can rebuild an empty personal deck');
  ok(state.discard.length === 1 && state.discard[0] === enemyDiscard, 'rebuilding from owned discard leaves opponent card in the shared pile');
}

// Drawing the final card eagerly rebuilds from both spent and owned shared-discard cards.
{
  const player = { hand: [], deck: [], spent: [], melds: [] };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const last = card('C', 4), spentCard = card('S', 10), ownDiscard = card('H', 11, { owner: 'player' });
  const enemyDiscard = card('D', 5, { owner: 'enemy' });
  player.deck = [last];
  player.spent = [spentCard];
  const state = { player, enemy, discard: [enemyDiscard, ownDiscard], turnNo: 1 };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs;
  ctx.log = () => {};
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne');
  const drawn = ctx.drawOne('player', false);
  ok(drawn === last, 'final original deck card is still drawn before eager owned-card recycling');
  ok(player.deck.length === 2 && player.spent.length === 0, 'final draw eagerly rebuilds deck from spent plus owned shared discard');
  ok(!state.discard.includes(ownDiscard) && state.discard.length === 1 && state.discard[0] === enemyDiscard, 'eager rebuild removes only the current owner’s discard cards');
}

// Drawing from a personal deck clears stale discard-contract state; discard acquisition starts clean before onDiscardDraw re-arms it.
{
  const player = { hand: [], deck: [], spent: [], melds: [] };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const stale = card('D', 3, { tag: 'discardContract', contractActive: true });
  player.deck = [stale];
  const publicContract = card('D', 3, { tag: 'discardContract', contractActive: true, owner: 'enemy' });
  const state = { player, enemy, discard: [publicContract], turnNo: 3 };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs; ctx.log = () => {};
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne');
  ctx.drawOne('player', false);
  ok(stale.contractActive === false, 'personal-deck draw clears stale discard-contract state');
  ctx.acquireDiscardCard('player', 0);
  ok(publicContract.contractActive === false, 'discard acquisition resets contract state before discard-draw effects are applied');
}

// The AI end path must settle contracts and then call turnEnd even when RUMMY occurred.
ok(!html.includes("if(!rummied)settleContracts('enemy');turnEnd('enemy')"), 'AI no longer skips contract settlement on RUMMY turns');
ok(html.includes("settleContracts('enemy');turnEnd('enemy')"), 'AI always performs one contract settlement followed by one turn-end resolution');

console.log('RUMMY//DUEL hand-circulation regression tests passed.');
