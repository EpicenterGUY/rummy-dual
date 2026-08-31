import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road = fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
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

new Function(script);

{
  const enemy={hp:60,shield:0,maxHp:60}, player={hp:60,shield:0,maxHp:60};
  const ctx=vm.createContext({console,Math,Object,Array});
  Object.assign(ctx,{
    state:{switchTarget:'enemy',switchPower:10},
    sideObj:w=>w==='enemy'?enemy:player,
    other:w=>w==='enemy'?'player':'enemy'
  });
  vm.runInContext(functionSource('aiShouldAcceptSmallBomb'),ctx);

  ok(ctx.aiShouldAcceptSmallBomb('enemy',{score:10,cards:[{}]})===true, 'AI may intentionally accept a safe 10-power bomb when the available return is low value');
  ok(ctx.aiShouldAcceptSmallBomb('enemy',{score:20,cards:[{}]})===false, 'AI returns instead of wasting a 20+ power extension');

  ctx.state.switchPower=18;
  ok(ctx.aiShouldAcceptSmallBomb('enemy',{score:10,cards:[{}]})===true, 'healthy CORE can accept the upper small-bomb budget when the return line is weak');
  ctx.state.switchPower=19;
  ok(ctx.aiShouldAcceptSmallBomb('enemy',{score:10,cards:[{}]})===false, 'raw CORE damage above the small-bomb budget is not accepted');

  enemy.hp=20; enemy.shield=0; ctx.state.switchPower=10;
  ok(ctx.aiShouldAcceptSmallBomb('enemy',{score:10,cards:[{}]})===false, 'AI preserves a minimum current-CORE reserve instead of accepting a dangerous low-HP bomb');

  enemy.hp=20; enemy.shield=20; ctx.state.switchPower=20;
  ok(ctx.aiShouldAcceptSmallBomb('enemy',null)===true, 'same-turn shield can justify absorbing a bomb with zero current-CORE damage');

  enemy.hp=60; enemy.shield=0; player.hp=15; player.shield=0; ctx.state.switchPower=10;
  ok(ctx.aiShouldAcceptSmallBomb('enemy',{score:10,cards:[{}]})===false, 'AI does not accept when returning would create immediate lethal pressure on the opponent');

  player.hp=60; ctx.state.switchTarget='player';
  ok(ctx.aiShouldAcceptSmallBomb('enemy',{score:10,cards:[{}]})===false, 'acceptance logic is inactive when the SWITCH is not targeting the AI');
}

ok(html.includes("acceptSmall=typeof aiShouldAcceptSmallBomb==='function'?aiShouldAcceptSmallBomb('enemy',ex):false"), 'AI turn loop uses the strategic small-bomb decision helper with isolated-test fallback');
ok(!html.includes('acceptThreshold=Math.max(12,Math.floor(state.enemy.hp*.35+state.enemy.shield*.5))'), 'legacy unconditional threshold heuristic is removed');
ok(road.includes('- [x] Improve intentional small-bomb acceptance decisions'), 'ROADMAP marks the final M10 small-bomb item complete');

const m10 = road.match(/## M10 — AI 2\.0([\s\S]*?)\n## M11 — Deckbuilder/)?.[1] || '';
ok(!m10.includes('- [ ]'), 'M10 AI 2.0 has no unfinished checklist items');

console.log('RUMMY//DUEL M10 small-bomb acceptance regression tests passed.');
