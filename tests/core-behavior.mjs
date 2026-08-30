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
  let depth = 0;
  let end = -1;
  for (let i = brace; i < script.length; i++) {
    const ch = script[i];
    if (ch === '{') depth++;
    else if (ch === '}') {
      depth--;
      if (depth === 0) { end = i + 1; break; }
    }
  }
  if (end < 0) throw new Error(`unterminated function ${name}`);
  return script.slice(start, end);
}

function makeContext(extra = {}) {
  return vm.createContext({
    console,
    Math,
    Set,
    Map,
    Array,
    Object,
    Number,
    String,
    Boolean,
    ...extra,
  });
}

function install(ctx, ...names) {
  for (const name of names) vm.runInContext(functionSource(name), ctx);
}

function card(suit, rank, extra = {}) {
  return {
    uid: `${suit}${rank}-${Math.random()}`,
    suit,
    rank: String(rank),
    owner: 'player',
    originOwner: 'player',
    named: false,
    tag: null,
    fromDiscard: false,
    enteredMeldToken: null,
    recoveredToken: null,
    recoverReturnOverrideToken: null,
    blockedUntilTurn: null,
    ...extra,
  };
}

// SET validity: meld validity allows 3–4 cards, while new meld creation separately enforces exactly 3.
{
  const ctx = makeContext();
  ctx.isJoker = c => c.suit === 'J';
  install(ctx, 'setValid');
  ok(ctx.setValid([card('S',7), card('H',7), card('D',7)]), '3-card same-rank unique-suit SET is valid');
  ok(ctx.setValid([card('S',7), card('H',7), card('D',7), card('C',7)]), 'completed 4SET remains a valid meld before retirement');
  ok(!ctx.setValid([card('S',7), card('S',7), card('D',7)]), 'SET rejects duplicate suits');
}

// submitNewMeld: exactly three cards only.
{
  const player = { hand: [], melds: [], newMeldUsed: false, actedThisTurn: false };
  const enemy = { hand: [], melds: [] };
  const state = { player, enemy, turnNo: 1, turnToken: 3, gameOver: false };
  const ctx = makeContext({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.meldsOf = w => ctx.sideObj(w).melds;
  ctx.meldType = cards => cards.length >= 3 ? 'SET' : null;
  ctx.beforeNewMeld = () => true;
  ctx.removeFromHand = (w, cards) => {
    const ids = new Set(cards.map(c => c.uid));
    ctx.sideObj(w).hand = ctx.sideObj(w).hand.filter(c => !ids.has(c.uid));
  };
  ctx.autoExtortToNewMeld = () => false;
  ctx.markSetCompletion = () => {};
  ctx.fieldAction = () => {};
  ctx.resolveEffects = () => ({ bonus: 0, forceReturn: false, flatReturn: false });
  ctx.characterActionBonus = () => {};
  ctx.triggerOpponentHandTraps = () => {};
  ctx.log = () => {};
  ctx.triggerRummy = () => {};
  ctx.blankMeldStatus = () => ({ seal: 0, fixed: 0, protect: 0, fixedOwner: null, fixedThroughStart: null });
  install(ctx, 'submitNewMeld');

  const four = [card('S',7), card('H',7), card('D',7), card('C',7)];
  player.hand = [...four];
  ok(ctx.submitNewMeld('player', four) === false, 'new meld rejects four-card SET creation');
  ok(player.melds.length === 0, 'rejected four-card new SET does not enter the board');

  const three = [card('S',7), card('H',7), card('D',7)];
  player.hand = [...three, card('C',2)];
  player.newMeldUsed = false;
  ok(ctx.submitNewMeld('player', three) === true, 'new meld accepts exact three-card SET');
  ok(player.melds.length === 1 && player.melds[0].cards.length === 3, 'accepted 3SET enters public board as three cards');
}

function makeAttachContext({ type, baseCards, handCards, chain = 0, token = 7 }) {
  const player = {
    hand: [...handCards, card('C',2)],
    melds: [],
    returnedSwitchThisTurn: false,
    actedThisTurn: false,
    turnStarts: 1,
  };
  const enemy = {
    hand: [card('S',2)],
    melds: [{
      type,
      cards: [...baseCards],
      chain,
      lastAttachToken: null,
      createdToken: null,
      lastTouchedOwnerStart: 0,
      status: { protected: 0, sealNamed: 0 },
    }],
    returnedSwitchThisTurn: false,
    turnStarts: 1,
  };
  const state = {
    player,
    enemy,
    turnNo: 1,
    turnToken: token,
    gameOver: false,
    pendingTrapReduction: 0,
    lastPlayerReturnType: null,
    lastEnemyReturnType: null,
  };
  const capture = { attacks: [], retired: [] };
  const ctx = makeContext({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.other = w => w === 'player' ? 'enemy' : 'player';
  ctx.meldsOf = w => ctx.sideObj(w).melds;
  ctx.canSideReturn = () => true;
  ctx.removeFromHand = (w, cards) => {
    const ids = new Set(cards.map(c => c.uid));
    ctx.sideObj(w).hand = ctx.sideObj(w).hand.filter(c => !ids.has(c.uid));
  };
  ctx.markSetCompletion = m => {
    if (m.type === 'RUN') m.chain = Math.max(0, Math.min(4, m.chain ?? Math.max(0, m.cards.length - 3)));
  };
  ctx.fieldAction = () => {};
  ctx.resolveEffects = () => ({ bonus: 0, flatReturn: false, forceReturn: false });
  ctx.characterActionBonus = () => {};
  ctx.triggerOpponentHandTraps = () => {};
  ctx.attackEvent = (w, hits, opts) => {
    capture.attacks.push({ w, hits, opts });
    ctx.sideObj(w).returnedSwitchThisTurn = true;
    return { total: hits.reduce((n, h) => n + h.amount, 0) + (opts.bonus || 0) };
  };
  ctx.drawOne = () => null;
  ctx.pushDiscard = () => {};
  ctx.log = () => {};
  ctx.freeRecoverFromMeld = () => null;
  ctx.cutOppositeEnd = () => false;
  ctx.recoverRedundantGapRun = () => null;
  ctx.middleManagerReturnPlaceholder = () => null;
  ctx.replaceRedundantJokers = () => {};
  ctx.retireMeld = (owner, index, reason) => {
    const [m] = ctx.meldsOf(owner).splice(index, 1);
    capture.retired.push({ owner, reason, m });
  };
  ctx.triggerRummy = () => {};
  ctx.meldType = cards => {
    if (type === 'SET') {
      if (cards.length < 3 || cards.length > 4) return null;
      const ranks = new Set(cards.map(c => c.rank));
      const suits = new Set(cards.map(c => c.suit));
      return ranks.size === 1 && suits.size === cards.length ? 'SET' : null;
    }
    const suit = cards[0]?.suit;
    if (!suit || cards.some(c => c.suit !== suit)) return null;
    const vals = cards.map(c => Number(c.rank)).sort((a, b) => a - b);
    for (let i = 1; i < vals.length; i++) if (vals[i] !== vals[i - 1] + 1) return null;
    return 'RUN';
  };
  install(ctx, 'recoveredCardCanReturn', 'recoveredCardsCanReturn', 'chainDamage', 'attachCards');
  return { ctx, state, player, enemy, capture };
}

// BURST on opponent public SET: +24, one SWITCH-returning attack, then immediate 4SET retirement.
{
  const d7 = card('D',7);
  const { ctx, enemy, capture } = makeAttachContext({
    type: 'SET',
    baseCards: [card('S',7), card('H',7), card('C',7)],
    handCards: [d7],
  });
  ok(ctx.attachCards('player', [d7], 'enemy', 0) === true, 'player can complete BURST on opponent public SET');
  ok(capture.attacks.length === 1, 'BURST produces exactly one attack event');
  ok(capture.attacks[0].hits[0].amount === 24, 'BURST attack contributes +24 power');
  ok(enemy.melds.length === 0, 'completed 4SET retires immediately after BURST');
  ok(capture.retired[0]?.reason.includes('버스트'), '4SET retirement is explicitly caused by BURST resolution');
}

// RUN multi-attach: 8-9-10 onto 5-6-7 is +10 +15 +20 = 45, one return, CHAIN 3.
{
  const attach = [card('H',8), card('H',9), card('H',10)];
  const { ctx, enemy, capture } = makeAttachContext({
    type: 'RUN',
    baseCards: [card('H',5), card('H',6), card('H',7)],
    handCards: attach,
    chain: 0,
  });
  ok(ctx.attachCards('player', attach, 'enemy', 0) === true, 'three-card RUN multi-attach resolves in one action');
  ok(capture.attacks.length === 1, 'multi-attach returns SWITCH only once');
  ok(capture.attacks[0].hits[0].amount === 45, 'RUN multi-attach total is 10+15+20 = 45');
  ok(enemy.melds[0].chain === 3, 'three-card RUN multi-attach advances CHAIN to 3');
  ok(enemy.melds[0].cards.length === 6, 'multi-attach adds all three cards to the RUN');
}

// Recovery guard in the actual attach path, with named override token exception.
{
  const recovered = card('H',8, { recoveredToken: 7 });
  const setup = makeAttachContext({
    type: 'RUN',
    baseCards: [card('H',5), card('H',6), card('H',7)],
    handCards: [recovered],
    token: 7,
  });
  ok(setup.ctx.attachCards('player', [recovered], 'enemy', 0) === false, 'actual attach path blocks same-turn recovered card from returning SWITCH');
  ok(setup.capture.attacks.length === 0 && setup.enemy.melds[0].cards.length === 3, 'blocked recovered-card attach leaves board and attack state unchanged');
  recovered.recoverReturnOverrideToken = 7;
  ok(setup.ctx.attachCards('player', [recovered], 'enemy', 0) === true, 'explicit named override token permits same-turn recovered-card return');
}

// SWITCH rally ownership and one-return-per-turn.
{
  const player = { hp: 60, shield: 0, returnedSwitchThisTurn: false, creditDebt: false, discardsRemaining: 1 };
  const enemy = { hp: 60, shield: 0, returnedSwitchThisTurn: false, creditDebt: false, discardsRemaining: 1 };
  const state = { switchTarget: 'neutral', switchPower: 0, lastSwitchAdd: 0, lastSwitchActor: null, gameOver: false };
  const ctx = makeContext({ state, OVERLOAD: 100 });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.other = w => w === 'player' ? 'enemy' : 'player';
  ctx.switchName = w => w === 'player' ? 'YOU' : 'CPU';
  ctx.log = () => {};
  ctx.fxNode = () => {};
  ctx.combatBanner = () => {};
  install(ctx, 'canSideReturn', 'addSwitchPower', 'setSwitchTarget', 'returnSwitch');

  let r = ctx.returnSwitch('player', 10, 'CHAIN');
  ok(!r.blocked && state.switchPower === 10 && state.switchTarget === 'enemy', 'neutral SWITCH starts at +10 and points to opponent');
  r = ctx.returnSwitch('player', 15, 'CHAIN');
  ok(r.blocked && state.switchPower === 10, 'same player cannot return SWITCH twice in one turn');
  r = ctx.returnSwitch('enemy', 15, 'CHAIN');
  ok(!r.blocked && state.switchPower === 25 && state.switchTarget === 'player', 'opponent can return the same bomb and increase accumulated power');
}

function makeDamageContext({ hp = 60, shield = 0, cores = 3, power = 0, target = 'neutral' } = {}) {
  const player = { hp, maxHp: 60, shield, cores, graceArmed: false, status: { vulnerable: 0, seal: 0, regen: 0 }, hand: [], melds: [{ type: 'RUN', chain: 3 }] };
  const enemy = { hp: 60, maxHp: 60, shield: 0, cores: 3, graceArmed: false, status: { vulnerable: 0, seal: 0, regen: 0 }, hand: [], melds: [{ type: 'RUN', chain: 2 }] };
  const state = { player, enemy, switchPower: power, switchTarget: target, lastSwitchAdd: 0, lastSwitchActor: null, fuseUsed: false, gameOver: false };
  const ctx = makeContext({ state, CORE_COUNT: 3 });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.other = w => w === 'player' ? 'enemy' : 'player';
  ctx.meldsOf = w => ctx.sideObj(w).melds;
  ctx.switchName = w => w === 'player' ? 'YOU' : 'CPU';
  ctx.log = () => {};
  ctx.fxNode = () => {};
  ctx.combatBanner = () => {};
  ctx.pulsePanel = () => {};
  ctx.checkGameOver = () => {};
  ctx.officialStatusValue = (scope, target, key) => target?.status?.[key] || 0;
  ctx.clearOfficialStatus = (scope, target, key) => { const n = target?.status?.[key] || 0; if (target?.status) target.status[key] = 0; return n; };
  install(ctx, 'resetAllChains', 'resetBombCycle', 'coreBreak', 'damage', 'detonate');
  return { ctx, state, player, enemy };
}

// Shield first, then current CORE only.
{
  const { ctx, player } = makeDamageContext({ hp: 60, shield: 20, cores: 3 });
  const dealt = ctx.damage('player', 30, { label: 'TEST' });
  ok(dealt === 10 && player.shield === 0 && player.hp === 50, 'shield absorbs damage before current CORE');
  ok(player.cores === 3, 'nonlethal damage does not break a CORE');
}

// Huge damage breaks only one CORE and discards overkill; CORE BREAK resets SWITCH and all CHAIN values.
{
  const { ctx, state, player, enemy } = makeDamageContext({ hp: 60, shield: 0, cores: 3, power: 137, target: 'player' });
  ctx.damage('player', 137, { label: 'DETONATE' });
  ok(player.cores === 2 && player.hp === 60, '137 damage breaks exactly one 60-HP CORE and activates the next at 60/60');
  ok(state.switchPower === 0 && state.switchTarget === 'neutral', 'CORE BREAK resets accumulated power and SWITCH direction');
  ok(player.melds[0].chain === 0 && enemy.melds[0].chain === 0, 'CORE BREAK resets all public RUN CHAIN values to 0');
}

// DETONATE consumes the current bomb, applies shield/core damage, then resets the cycle.
{
  const { ctx, state, player } = makeDamageContext({ hp: 60, shield: 5, cores: 3, power: 25, target: 'player' });
  const dealt = ctx.detonate('player', 'turn end');
  ok(dealt === 20 && player.hp === 40 && player.shield === 0, 'DETONATE applies shield first then 20 CORE damage from a 25 bomb');
  ok(state.switchPower === 0 && state.switchTarget === 'neutral', 'DETONATE resets the bomb cycle to neutral');
}

console.log('RUMMY//DUEL core behavior regression tests passed.');
