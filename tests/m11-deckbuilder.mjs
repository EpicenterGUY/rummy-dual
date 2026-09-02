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

function install(ctx, ...names) {
  for (const name of names) vm.runInContext(functionSource(name), ctx);
}

new Function(script);

ok(html.includes('id="deckSlotGrid"') && html.includes('직접 덱 구성 · 선택 사항'), 'progress UI exposes the 52-slot deckbuilder');
ok(html.includes('id="deckAnalysis"') && html.includes('세트 재료') && html.includes('런 재료'), 'deckbuilder exposes live SET/RUN distribution analysis');
ok(html.includes('grid.innerHTML=ALL_REGULAR.map(slot=>'), 'deckbuilder renders every canonical regular slot from ALL_REGULAR');
ok(html.includes('정확히 29개') && html.includes('정규 29 + 조커 1 = 30장'), 'UI preserves the existing 30-card battle-deck size');
ok(html.includes("const custom=makeCustomBattleDeck(owner);if(custom)return custom;"), 'player custom construction is checked before legacy automatic generation');
ok(html.includes("progress.deckBuild?.enabled?' · 커스텀 덱':''"), 'battle setup reports when a custom deck is active');

// Save migration and exact-slot normalization.
{
  const regular = [];
  for (const s of ['S','H','D','C']) for (const r of ['A','2','3','4','5','6','7','8','9','10','J','Q','K']) regular.push(s+r);
  const named = {
    X:{slot:'S3'}, Y:{slot:'H4'}, BAD:{slot:'D5'}, J1:{}, J2:{}
  };
  const ctx = vm.createContext({console, Array, Object, Set});
  Object.assign(ctx, {
    ALL_REGULAR:regular,
    CORE_IDS:regular.slice(0,31),
    NAMED:named
  });
  install(ctx, 'namedSlot', 'defaultDeckBuild', 'normalizeDeckBuild');

  const base = ctx.defaultDeckBuild();
  ok(base.slots.length === 29 && new Set(base.slots).size === 29, 'legacy/default custom seed contains exactly 29 unique regular slots');
  ok(base.enabled === false && base.joker === 'J1', 'legacy saves migrate with custom mode disabled and Joker King fallback');

  const normalized = ctx.normalizeDeckBuild({
    enabled:true,
    slots:[...regular.slice(0,29), regular[0], 'NOPE', regular[29], regular[30]],
    variants:{S3:'X',H4:'Y',S4:'BAD',NOPE:'X'},
    joker:'J2'
  });
  ok(normalized.slots.length === 29 && new Set(normalized.slots).size === 29, 'normalization caps custom selection to 29 unique canonical slots');
  ok(normalized.variants.S3 === 'X' && normalized.variants.H4 === 'Y', 'matching named variants survive normalization');
  ok(!normalized.variants.S4 && !normalized.variants.NOPE, 'variant cannot escape its exact rank+suit slot');
  ok(normalized.joker === 'J2', 'valid selected Joker survives normalization');
}

// Distribution analysis uses actual rank/suit geometry, not theme labels.
{
  const values = {A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
  const ctx = vm.createContext({console, Array, Object, Set, Math});
  Object.assign(ctx, {RANK_VALUE:values});
  install(ctx, 'parseRegularId', 'deckBuildAnalysis');
  const a = ctx.deckBuildAnalysis(['S3','S4','S5','H3','D3','C9']);
  ok(a.suits.S===3 && a.suits.H===1 && a.suits.D===1 && a.suits.C===1, 'analysis counts all four suits correctly');
  ok(a.ranks['3']===3 && a.setPairs===1 && a.setReady===1, 'analysis identifies same-rank SET material');
  ok(a.runWindows===1 && a.longestRun===3, 'analysis identifies same-suit three-card RUN windows and longest streak');
}

// Actual custom battle deck is still 29 regular + 1 Joker and respects unlocked variants.
{
  const regular=[];
  for(const s of ['S','H','D','C'])for(const r of ['A','2','3','4','5','6','7','8','9','10','J','Q','K'])regular.push(s+r);
  const slots=regular.slice(0,29);
  const named={V:{slot:slots[0],n:'Variant'},LOCK:{slot:slots[1],n:'Locked'},J1:{n:'Joker King'},J2:{n:'Other Joker'}};
  const progress={deckBuild:{enabled:true,slots:[...slots],variants:{[slots[0]]:'V',[slots[1]]:'LOCK'},joker:'J2'}};
  const ctx=vm.createContext({console,Array,Object,Set,Math});
  Object.assign(ctx,{
    progress,
    ALL_REGULAR:regular,
    CORE_IDS:regular.slice(0,31),
    NAMED:named,
    unlockedNamed:()=>new Set(['V','J1','J2']),
    makeCard:(suit,rank,namedFlag,owner,id)=>({suit,rank,named:namedFlag,owner,id:id||null}),
    shuffle:x=>x
  });
  install(ctx,'namedSlot','parseRegularId','defaultDeckBuild','normalizeDeckBuild','makeCustomBattleDeck');
  const deck=ctx.makeCustomBattleDeck('player');
  ok(deck.length===30, 'custom battle construction produces exactly 30 cards');
  ok(deck.filter(c=>c.suit!=='J').length===29 && deck.filter(c=>c.suit==='J').length===1, 'custom deck contains 29 regular cards and one Joker');
  ok(deck.some(c=>c.id==='V'), 'unlocked selected named variant replaces its PURE slot');
  ok(!deck.some(c=>c.id==='LOCK'), 'locked selected variant safely falls back to PURE without deleting the slot');
  ok(deck.some(c=>c.id==='J2'), 'selected unlocked Joker is used');
  ok(ctx.makeCustomBattleDeck('enemy')===null, 'custom player deck never overrides enemy automatic construction');
  progress.deckBuild.slots=slots.slice(0,28);
  ok(ctx.makeCustomBattleDeck('player')===null, 'invalid 28-slot construction falls back instead of creating an undersized deck');
}

for (const line of [
  '- [x] Player-facing 52-slot deck construction',
  '- [x] One variant per exact rank+suit slot',
  '- [x] Rank/suit/SET/RUN distribution analysis UI'
]) ok(road.includes(line), `ROADMAP locks M11 item: ${line.slice(6)}`);

const m11 = road.match(/## M11 — Deckbuilder([\s\S]*?)\n## M11A —/)?.[1] || '';
ok(!m11.includes('- [ ]'), 'M11 Deckbuilder has no unfinished checklist items');

console.log('RUMMY//DUEL M11 deckbuilder and analysis regression tests passed.');
