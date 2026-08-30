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
  for (let i = brace; i < script.length; i++) {
    if (script[i] === '{') depth++;
    else if (script[i] === '}' && --depth === 0) return script.slice(start, i + 1);
  }
  throw new Error(`unterminated function ${name}`);
}

function install(ctx, ...names) {
  for (const name of names) vm.runInContext(functionSource(name), ctx);
}

function makeContext(extra = {}) {
  return vm.createContext({ console, Math, Set, Map, Array, Object, Number, String, Boolean, ...extra });
}

function run(chain = 4, count = 7) {
  return { type: 'RUN', chain, cards: Array.from({ length: count }, (_, i) => ({ uid: `c${i}` })) };
}

// Availability: CHAIN 4+, controller turn only, and fixed cards/melds cannot be voluntarily moved.
{
  const player = { melds: [run(3)], newMeldUsed: false, actedThisTurn: false };
  const enemy = { melds: [] };
  const state = { player, enemy, gameOver: false, turn: 'player', phase: 'action' };
  const ctx = makeContext({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.meldsOf = w => ctx.sideObj(w).melds;
  ctx.meldFixedActive = () => false;
  ctx.cardFixedActive = () => false;
  install(ctx, 'canFinishRun');
  ok(!ctx.canFinishRun('player', 0), 'CHAIN 3 RUN cannot be completed');
  player.melds[0].chain = 4;
  ok(ctx.canFinishRun('player', 0), 'CHAIN 4 RUN can be completed by its controller');
  state.turn = 'enemy';
  ok(!ctx.canFinishRun('player', 0), 'controller cannot complete the RUN outside their own turn');
  state.turn = 'player';
  ctx.meldFixedActive = () => true;
  ok(!ctx.canFinishRun('player', 0), 'fixed RUN cannot be voluntarily completed');
}

// Completion frees the slot without touching SWITCH/power and counts as an action.
{
  const player = { melds: [run(4)], newMeldUsed: false, actedThisTurn: false };
  const enemy = { melds: [] };
  const state = {
    player, enemy, gameOver: false, turn: 'player', phase: 'action',
    switchPower: 85, switchTarget: 'enemy', target: { side: 'player', index: 0 },
    boardSelected: new Set([1]), selected: new Set([2]), selectionOrder: [2],
  };
  const logs = [];
  const ctx = makeContext({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.meldsOf = w => ctx.sideObj(w).melds;
  ctx.meldFixedActive = () => false;
  ctx.cardFixedActive = () => false;
  ctx.retireMeld = (w, i) => ctx.meldsOf(w).splice(i, 1);
  ctx.combatBanner = () => {};
  ctx.log = x => logs.push(x);
  ctx.switchName = w => w === 'player' ? 'YOU' : 'CPU';
  install(ctx, 'canFinishRun', 'finishRun');
  ok(ctx.finishRun('player', 0), 'RUN completion executes when eligible');
  ok(player.melds.length === 0, 'RUN completion frees the public meld slot');
  ok(player.actedThisTurn === true, 'RUN completion counts as an action');
  ok(state.switchPower === 85 && state.switchTarget === 'enemy', 'RUN completion adds no power and does not move SWITCH');
  ok(state.selected.size === 0 && state.boardSelected.size === 0 && state.target === null, 'player selection state is cleared after completion');
}

// A finishable RUN prevents the game from misclassifying the turn as completely stuck.
{
  const player = { melds: [run(4), { type: 'SET', chain: 0, cards: [{}, {}, {}] }], newMeldUsed: false };
  const enemy = { melds: [] };
  const state = { player, enemy, gameOver: false, turn: 'player', phase: 'action' };
  const ctx = makeContext({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.meldsOf = w => ctx.sideObj(w).melds;
  ctx.meldFixedActive = () => false;
  ctx.cardFixedActive = () => false;
  ctx.bestNewMeldForTurn = () => null;
  ctx.anyAttachOption = () => false;
  install(ctx, 'canFinishRun', 'hasAnyLegalAction');
  ok(ctx.hasAnyLegalAction('player'), 'finishable RUN is counted as a legal base action');
}

// CPU only gives up a mature RUN when a full board is blocking a playable new meld; prefer the longest mature RUN.
{
  const enemy = { melds: [run(4, 7), run(4, 9)], newMeldUsed: false };
  const player = { melds: [] };
  const state = { player, enemy, gameOver: false, turn: 'enemy', phase: 'wait' };
  const ctx = makeContext({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.meldsOf = w => ctx.sideObj(w).melds;
  ctx.meldFixedActive = () => false;
  ctx.cardFixedActive = () => false;
  ctx.bestNewMeldForTurn = () => ({ type: 'SET' });
  install(ctx, 'canFinishRun', 'bestFinishRunAI');
  ok(ctx.bestFinishRunAI('enemy')?.index === 1, 'CPU chooses the longer mature RUN to free a blocked slot');
  enemy.newMeldUsed = true;
  ok(ctx.bestFinishRunAI('enemy') === null, 'CPU does not complete a RUN after its new-meld action is already spent');
}

ok(html.includes('런 완주 · 슬롯 비우기'), 'player UI exposes the conditional RUN completion button');
ok(html.includes("(m.chain||0)>=4?' · 런 완주 가능':''"), 'CHAIN 4+ readout announces RUN completion readiness');
ok(script.includes("if(fr){finishRun('enemy',fr.index);continue}"), 'CPU action loop can use conditional RUN completion');
ok(script.includes('function chainDamage(step){return Math.min(25'), 'CHAIN remains capped at +25 after CHAIN 4 when the RUN is kept');

console.log('Conditional RUN completion regressions passed.');
