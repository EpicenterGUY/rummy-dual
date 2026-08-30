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

function install(ctx, ...names) {
  for (const name of names) vm.runInContext(functionSource(name), ctx);
}

// Selection order is independent from hand layout order and survives as the execution order.
{
  const ctx = vm.createContext({ console, Map, Set, Array, Object });
  install(ctx, 'orderedSelectedCards');
  const hand = [{ uid: 'A' }, { uid: 'B' }, { uid: 'C' }];
  const selected = new Set(['A', 'B']);
  const ordered = ctx.orderedSelectedCards(hand, selected, ['B', 'A']);
  ok(ordered.map(c => c.uid).join(',') === 'B,A', 'selected cards preserve explicit click order instead of hand order');
  const fallback = ctx.orderedSelectedCards(hand, selected, ['B']);
  ok(fallback.map(c => c.uid).join(',') === 'B,A', 'selected cards missing from order state are appended safely in hand order');
}

// RUN preview maps each selected card to its actual CHAIN step.
{
  const ctx = vm.createContext({ console, Math, Array, Object });
  install(ctx, 'chainDamage', 'buildAttachPreview');
  const cards = [{ uid: '8' }, { uid: '9' }, { uid: '10' }];
  const p = ctx.buildAttachPreview({ type: 'RUN', chain: 0, cards: [{}, {}, {}] }, cards);
  ok(p.steps.map(x => x.amount).join(',') === '10,15,20', 'RUN preview exposes ordered +10/+15/+20 steps');
  ok(p.total === 45, 'RUN preview totals three-card extension to +45');
  const hot = ctx.buildAttachPreview({ type: 'RUN', chain: 3, cards: [{}, {}, {}, {}, {}, {}] }, [{ uid: 'x' }, { uid: 'y' }]);
  ok(hot.steps.map(x => x.amount).join(',') === '25,25' && hot.total === 50, 'CHAIN 4+ preview caps each further step at +25');
}

// SET completion preview remains a single +24 BURST.
{
  const ctx = vm.createContext({ console, Math, Array, Object });
  install(ctx, 'chainDamage', 'buildAttachPreview');
  const p = ctx.buildAttachPreview({ type: 'SET', chain: 0, cards: [{}, {}, {}] }, [{ uid: 'fourth' }]);
  ok(p.total === 24 && p.steps.length === 1 && p.steps[0].amount === 24, 'SET fourth-card preview is BURST +24');
}

ok(html.includes('selectionOrder:[]'), 'game state stores explicit hand selection order');
ok(html.includes("targeted?'target':''"), 'selected public meld receives the existing target visual state');
ok(html.includes('canContinueTargetSelection'), 'targeted meld drives legal-next-card highlighting');
ok(html.includes('blockedUntilTurn===state.turnNo'), 'player attach UI respects current-turn blocked cards');
ok(html.includes('스위치 → 상대'), 'multi-attach preview explicitly shows the resulting SWITCH direction');
ok(html.includes('합계 +${p.total}'), 'multi-attach preview renders an aggregate total');

console.log('RUMMY//DUEL multi-attach UX regression tests passed.');
