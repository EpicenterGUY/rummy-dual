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

function context(extra = {}) {
  return vm.createContext({ console, Math, Set, Map, Array, Object, Number, String, Boolean, ...extra });
}

function install(ctx, ...names) {
  for (const name of names) vm.runInContext(functionSource(name), ctx);
}

function basicSide() {
  return {
    hp: 60,
    maxHp: 60,
    cores: 3,
    shield: 0,
    status: { vulnerable: 0, seal: 0, regen: 0 },
    hand: [],
    deck: [],
    spent: [],
    melds: [],
    returnedSwitchThisTurn: false,
    recoveredThisTurn: false,
    graceArmed: false,
    creditDebt: false,
    discardsRemaining: 1,
    lastDamageTaken: 0,
    lastDetonateTaken: 0,
    rummyReturnPending: false,
    rummyRecoveryPending: false,
    freeRecoverAfterRummy: false,
    jokerLastDetonateReduction: 0,
  };
}

// Base RUMMY: refill 6, mark both post-RUMMY windows, end player's turn exactly once.
{
  const player = basicSide(), enemy = basicSide();
  const state = {
    player, enemy, rummy: 0,
    switchTarget: 'neutral', switchPower: 0,
    playerJustRummied: false, enemyJustRummied: false,
    selected: new Set(), boardSelected: new Set(), target: null,
  };
  let endCount = 0, seq = 0;
  const ctx = context({ state, RECOVERY_UNIT: 4 });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.drawMany = (w, n) => { for (let i = 0; i < n; i++) ctx.sideObj(w).hand.push({ uid: `d${++seq}`, age: 0, tag: null }); return n; };
  ctx.heal = () => 0;
  ctx.applyStatus = () => {};
  ctx.addShield = () => 0;
  ctx.removeFromHand = (w, cards) => { const ids = new Set(cards.map(c => c.uid)); ctx.sideObj(w).hand = ctx.sideObj(w).hand.filter(c => !ids.has(c.uid)); };
  ctx.switchName = w => w === 'player' ? 'YOU' : 'CPU';
  ctx.combatBanner = () => {};
  ctx.log = () => {};
  ctx.endPlayerTurn = () => { endCount++; };
  install(ctx, 'triggerRummy');
  ctx.triggerRummy('player', [], { returned: false });
  ok(player.hand.length === 6, 'base RUMMY refills exactly six cards');
  ok(state.rummy === 1, 'player RUMMY counter increments once');
  ok(endCount === 1, 'player RUMMY ends the player turn exactly once');
  ok(player.rummyReturnPending && player.rummyRecoveryPending, 'RUMMY independently arms first-return and first-recovery windows');
}

// Last Laugh returning-RUMMY: draw one extra then bottom one, keeping six in hand.
{
  const player = basicSide(), enemy = basicSide();
  const state = {
    player, enemy, rummy: 0,
    switchTarget: 'enemy', switchPower: 40,
    playerJustRummied: false, enemyJustRummied: false,
    selected: new Set(), boardSelected: new Set(), target: null,
  };
  let seq = 0;
  const ctx = context({ state, RECOVERY_UNIT: 4 });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.drawMany = (w, n) => { for (let i = 0; i < n; i++) ctx.sideObj(w).hand.push({ uid: `j${++seq}`, age: i, tag: null, fromDiscard: false }); return n; };
  ctx.heal = () => 0; ctx.applyStatus = () => {}; ctx.addShield = () => 0;
  ctx.removeFromHand = (w, cards) => { const ids = new Set(cards.map(c => c.uid)); ctx.sideObj(w).hand = ctx.sideObj(w).hand.filter(c => !ids.has(c.uid)); };
  ctx.switchName = () => 'YOU'; ctx.combatBanner = () => {}; ctx.log = () => {}; ctx.endPlayerTurn = () => {};
  install(ctx, 'triggerRummy');
  ctx.triggerRummy('player', [{ uid: 'J2', tag: 'jokerLast' }], { returned: true });
  ok(player.hand.length === 6, 'Last Laugh returning-RUMMY still finishes with six cards in hand');
  ok(player.deck.length === 1, 'Last Laugh returning-RUMMY bottoms exactly one of the seven drawn cards');
  ok(player.jokerLastDetonateReduction === 0, 'returning Last Laugh does not arm DETONATE reduction');
}

// Last Laugh RUMMY while still holding the bomb arms the -15 DETONATE modifier.
{
  const player = basicSide(), enemy = basicSide();
  const state = {
    player, enemy, rummy: 0,
    switchTarget: 'player', switchPower: 35,
    playerJustRummied: false, enemyJustRummied: false,
    selected: new Set(), boardSelected: new Set(), target: null,
  };
  let seq = 0;
  const ctx = context({ state, RECOVERY_UNIT: 4 });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.drawMany = (w, n) => { for (let i = 0; i < n; i++) ctx.sideObj(w).hand.push({ uid: `r${++seq}`, age: 0, tag: null }); return n; };
  ctx.heal = () => 0; ctx.applyStatus = () => {}; ctx.addShield = () => 0; ctx.removeFromHand = () => {};
  ctx.switchName = () => 'YOU'; ctx.combatBanner = () => {}; ctx.log = () => {}; ctx.endPlayerTurn = () => {};
  install(ctx, 'triggerRummy');
  ctx.triggerRummy('player', [{ uid: 'J2', tag: 'jokerLast' }], { returned: false });
  ok(player.jokerLastDetonateReduction === 15, 'Last Laugh non-return RUMMY arms 15 DETONATE reduction when SWITCH still points at player');
}

// Safety Pin: one grace per bomb cycle, preserve bomb on first end, detonate on next end.
{
  const player = basicSide(), enemy = basicSide();
  const state = { player, enemy, switchTarget: 'player', switchPower: 48, fuseUsed: false, gameOver: false };
  let detonations = 0;
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.switchName = () => 'YOU'; ctx.log = () => {}; ctx.combatBanner = () => {};
  ctx.detonate = () => { detonations++; state.switchPower = 0; state.switchTarget = 'neutral'; return 48; };
  install(ctx, 'armSafetyPin', 'turnEnd');
  const pin = { tag: 'safetyPin', name: '안전핀' };
  ok(ctx.armSafetyPin('player', pin), 'Safety Pin arms grace when the bomb points at its user');
  ctx.turnEnd('player');
  ok(detonations === 0 && state.switchPower === 48 && state.switchTarget === 'player', 'first graced turn end preserves bomb power and direction');
  ok(!player.graceArmed && state.fuseUsed, 'grace is consumed while bomb-cycle fuse usage remains locked');
  ok(!ctx.armSafetyPin('player', pin), 'second Safety Pin cannot be armed in the same bomb cycle');
  ctx.turnEnd('player');
  ok(detonations === 1 && state.switchTarget === 'neutral', 'next unreturned turn end detonates after grace has been spent');
}

// Joker King returns to original owner's deck bottom when its meld retires.
{
  const player = basicSide(), enemy = basicSide();
  const joker = { uid: 'J1', tag: 'jokerKing', name: '광대왕 조커', owner: 'enemy', originOwner: 'player', fromDiscard: true, age: 4, suppressEffectToken: 9 };
  const normal = { uid: 'N1', tag: null, name: '순수 카드', owner: 'enemy', originOwner: 'enemy' };
  enemy.melds.push({ type: 'SET', cards: [joker, normal] });
  const ctx = context();
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.meldsOf = w => ctx.sideObj(w).melds;
  ctx.log = () => {};
  install(ctx, 'retireMeld');
  ctx.retireMeld('enemy', 0, 'test');
  ok(enemy.melds.length === 0, 'retired Joker King meld leaves the public board');
  ok(player.deck[0] === joker && joker.owner === 'player', 'Joker King returns to original owner deck bottom/control');
  ok(!player.spent.includes(joker) && !enemy.spent.includes(joker), 'Joker King is never consumed into a spent pile on retirement');
  ok(enemy.spent.includes(normal), 'ordinary card from the retired meld goes to its controller spent pile');
}

// Encore must only modify an actual first return after RUMMY, never a non-returning new meld.
{
  const player = basicSide(), enemy = basicSide();
  const state = { player, enemy, turnToken: 5, playerJustRummied: true, enemyJustRummied: false, lastPlayerReturnType: null, lastEnemyReturnType: null };
  player.rummyReturnPending = true;
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.other = w => w === 'player' ? 'enemy' : 'player';
  ctx.log = () => {};
  const encore = { uid: 'HJ', named: true, tag: 'afterRummyBonus', suppressEffectToken: null, name: '앙코르' };
  install(ctx, 'resolveEffects');
  let fx = ctx.resolveEffects('player', [encore], 'SET', { isNew: true, isAttach: false, willReturn: false, totalLength: 3, effectSeen: new Set(), meld: { status: {} }, targetOwner: 'player' });
  ok(!fx.forceReturn && !fx.flatReturn, 'Encore does not turn a non-returning new meld into a free SWITCH return');
  fx = ctx.resolveEffects('player', [encore], 'RUN', { isNew: false, isAttach: true, willReturn: true, totalLength: 4, effectSeen: new Set(), meld: { status: {} }, targetOwner: 'player' });
  ok(fx.forceReturn && fx.flatReturn, 'Encore makes the first actual post-RUMMY return flat');
  player.rummyReturnPending = false;
  fx = ctx.resolveEffects('player', [encore], 'RUN', { isNew: false, isAttach: true, willReturn: true, totalLength: 4, effectSeen: new Set(), meld: { status: {} }, targetOwner: 'player' });
  ok(!fx.forceReturn && !fx.flatReturn, 'Encore cannot modify a later return after the post-RUMMY return window is consumed');
}

// Return and recovery windows are independent and consume on their own event.
{
  const player = basicSide(), enemy = basicSide();
  player.rummyReturnPending = true;
  player.rummyRecoveryPending = true;
  const state = { player, enemy, switchTarget: 'neutral', switchPower: 0, lastSwitchAdd: 0, lastSwitchActor: null, gameOver: false, turnToken: 12 };
  const ctx = context({ state, OVERLOAD: 100 });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.other = w => w === 'player' ? 'enemy' : 'player';
  ctx.switchName = () => 'YOU'; ctx.log = () => {}; ctx.fxNode = () => {}; ctx.combatBanner = () => {};
  install(ctx, 'canSideReturn', 'addSwitchPower', 'setSwitchTarget', 'returnSwitch');
  ctx.returnSwitch('player', 10, 'CHAIN');
  ok(!player.rummyReturnPending && player.rummyRecoveryPending, 'first return consumes only the post-RUMMY return window');

  const recovered = { uid: 'R', owner: 'player', enteredMeldToken: null, suppressEffectToken: null, recoveredToken: null, recoverReturnOverrideToken: null, age: 2 };
  const meld = { type: 'RUN', cards: [recovered, { uid: 'a', owner: 'player' }, { uid: 'b', owner: 'player' }, { uid: 'c', owner: 'player' }], chain: 2 };
  player.melds = [meld];
  ctx.meldType = cards => cards.length >= 3 ? 'RUN' : null;
  ctx.markSetCompletion = () => {};
  ctx.cardText = c => c.uid;
  install(ctx, 'freeRecoverFromMeld');
  ctx.freeRecoverFromMeld('player', meld, []);
  ok(!player.rummyRecoveryPending, 'first successful recovery consumes the independent post-RUMMY recovery window');
}

// Second Heart: RUMMY refills seven and grants 16 shield when SWITCH points at the user.
{
  const player = basicSide(), enemy = basicSide();
  const state = {
    player, enemy, rummy: 0,
    switchTarget: 'player', switchPower: 20,
    playerJustRummied: false, enemyJustRummied: false,
    selected: new Set(), boardSelected: new Set(), target: null,
  };
  let seq = 0, shieldUnits = 0;
  const ctx = context({ state, RECOVERY_UNIT: 4 });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.drawMany = (w, n) => { for (let i = 0; i < n; i++) ctx.sideObj(w).hand.push({ uid: `ha${++seq}`, age: 0, tag: null }); return n; };
  ctx.heal = () => 0; ctx.applyStatus = () => {};
  ctx.addShield = (w, n) => { shieldUnits += n; return n * 4; };
  ctx.removeFromHand = () => {}; ctx.switchName = () => 'YOU'; ctx.combatBanner = () => {}; ctx.log = () => {}; ctx.endPlayerTurn = () => {};
  install(ctx, 'triggerRummy');
  ctx.triggerRummy('player', [{ uid: 'HA', tag: 'rummyPlus1' }], { returned: false });
  ok(player.hand.length === 7, 'Second Heart RUMMY refills seven cards');
  ok(shieldUnits === 4, 'Second Heart grants four shield units = 16 shield while SWITCH points at user');
}

// Life Support: RUMMY heals 16, grants regen 1, and at power 60+ grants 16 shield.
{
  const player = basicSide(), enemy = basicSide();
  const state = {
    player, enemy, rummy: 0,
    switchTarget: 'enemy', switchPower: 60,
    playerJustRummied: false, enemyJustRummied: false,
    selected: new Set(), boardSelected: new Set(), target: null,
  };
  let seq = 0, healUnits = 0, shieldUnits = 0, regen = 0;
  const ctx = context({ state, RECOVERY_UNIT: 4 });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.drawMany = (w, n) => { for (let i = 0; i < n; i++) ctx.sideObj(w).hand.push({ uid: `h10${++seq}`, age: 0, tag: null }); return n; };
  ctx.heal = (w, n) => { healUnits += n; return n * 4; };
  ctx.applyStatus = (w, key, n) => { if (key === 'regen') regen += n; };
  ctx.addShield = (w, n) => { shieldUnits += n; return n * 4; };
  ctx.removeFromHand = () => {}; ctx.switchName = () => 'YOU'; ctx.combatBanner = () => {}; ctx.log = () => {}; ctx.endPlayerTurn = () => {};
  install(ctx, 'triggerRummy');
  ctx.triggerRummy('player', [{ uid: 'H10', tag: 'rummyHeal4' }], { returned: false });
  ok(player.hand.length === 6, 'Life Support keeps normal six-card RUMMY refill');
  ok(healUnits === 4, 'Life Support heals four recovery units = 16 CORE');
  ok(regen === 1, 'Life Support applies regen 1');
  ok(shieldUnits === 4, 'Life Support grants four shield units = 16 shield at accumulated power 60+');
}

// Returner: only an unconsumed first-recovery window can arm its free recovery.
{
  const player = basicSide(), enemy = basicSide();
  const state = { player, enemy, turnToken: 22, lastPlayerReturnType: null, lastEnemyReturnType: null };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.other = w => w === 'player' ? 'enemy' : 'player';
  ctx.log = () => {};
  const returner = { uid: 'H2', named: true, tag: 'afterRummyDraw', suppressEffectToken: null, name: '귀환자' };
  install(ctx, 'resolveEffects');
  player.rummyRecoveryPending = true;
  ctx.resolveEffects('player', [returner], 'SET', { isNew: true, isAttach: false, willReturn: false, totalLength: 3, effectSeen: new Set(), meld: { status: {} }, targetOwner: 'player' });
  ok(player.freeRecoverAfterRummy, 'Returner arms a free recovery while the first post-RUMMY recovery is still pending');
  player.freeRecoverAfterRummy = false;
  player.rummyRecoveryPending = false;
  ctx.resolveEffects('player', [returner], 'SET', { isNew: true, isAttach: false, willReturn: false, totalLength: 3, effectSeen: new Set(), meld: { status: {} }, targetOwner: 'player' });
  ok(!player.freeRecoverAfterRummy, 'Returner cannot retroactively make a later recovery free after the first recovery window was consumed');
}

console.log('RUMMY//DUEL RUMMY/grace/Joker regression tests passed.');
