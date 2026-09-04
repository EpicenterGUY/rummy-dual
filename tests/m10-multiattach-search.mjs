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

function searchContext(requiredK) {
  const hand = Array.from({length: requiredK}, (_, i) => ({uid:`h${i}`, blockedUntilTurn:null, tag:null}));
  const meld = {type:'RUN', cards:[{uid:'m1'},{uid:'m2'},{uid:'m3'}], chain:0, createdToken:null};
  const side = {hand, returnedSwitchThisTurn:false, attachCount:0, extraAttachRemaining:0};
  const ctx = vm.createContext({console, Math, Array, Object, Set, Map});
  Object.assign(ctx, {
    state:{turnToken:9,turnNo:3},
    sideObj:()=>side,
    other:w=>w==='enemy'?'player':'enemy',
    meldsOf:s=>s==='enemy'?[meld]:[],
    meldType:cards=>cards.length===3+requiredK?'RUN':null,
    recoveredCardsCanReturn:()=>true,
    canSideReturn:()=>true
  });
  install(ctx, 'chainDamage', 'combinations', 'attachAccess', 'bestExtensionFromHand', 'anyAttachOption');
  return {ctx, hand};
}

new Function(script);
ok((html.match(/for\(let k=1;k<=Math\.min\(6,hand\.length\);k\+\+\)/g)||[]).length === 2,
  'AI extension planning and stuck-state legality both use the six-card practical search cap');
ok(!html.includes('for(let k=1;k<=Math.min(4,hand.length);k++)'), 'legacy four-card search cap is removed');

{
  const {ctx, hand} = searchContext(5);
  const best = ctx.bestExtensionFromHand('enemy', hand);
  ok(best?.cards?.length === 5, 'AI planning finds a legal extension that exists only as a five-card attach');
  ok(ctx.anyAttachOption('enemy') === true, 'stuck-state legality recognizes a five-card-only attach');
}

{
  const {ctx, hand} = searchContext(6);
  const best = ctx.bestExtensionFromHand('enemy', hand);
  ok(best?.cards?.length === 6, 'AI planning also searches a practical six-card extension');
  ok(ctx.anyAttachOption('enemy') === true, 'stuck-state legality recognizes a six-card-only attach');
  ctx.canSideReturn = ()=>false;
  ok(ctx.bestExtensionFromHand('enemy', hand) === null, 'expanded search still respects SWITCH return ownership legality');
  ok(ctx.anyAttachOption('enemy') === false, 'expanded stuck-state search does not bypass return ownership legality');
}

ok(road.includes('- [x] Search 5+ card multi-attach cases where practical'), 'ROADMAP marks the M10 5+ multi-attach search item complete');

console.log('RUMMY//DUEL M10 multi-attach search regression tests passed.');
