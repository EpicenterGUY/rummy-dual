import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync('index.html','utf8');
const road = fs.readFileSync('ROADMAP.md','utf8');
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

{
  const ctx = vm.createContext({console, Math, Array, Object, Set, Map});
  const player = {hand:Array.from({length:8}, (_,i)=>({uid:`p${i}`}))};
  const enemy = {hand:[]};
  Object.assign(ctx, {
    state:{switchTarget:'player',switchPower:30,discard:[]},
    sideObj:w=>w==='player'?player:enemy,
    other:w=>w==='enemy'?'player':'enemy',
    meldType:()=>null
  });
  install(ctx, 'futureBurstRisk', 'opponentMeldAttachBias');
  const setCards=[{uid:'a'},{uid:'b'},{uid:'c'}];
  ok(ctx.futureBurstRisk('enemy',setCards,'SET')===12, 'future BURST risk scales with opponent hand count and urgent SWITCH pressure');
  ctx.state.discard=[{uid:'burst-top'}];
  ctx.meldType=cards=>cards.at(-1)?.uid==='burst-top'?'SET':null;
  ok(ctx.futureBurstRisk('enemy',setCards,'SET')===20, 'public top-discard fourth-card access adds a strong future BURST warning');
  ok(ctx.futureBurstRisk('enemy',setCards,'RUN')===0, 'future BURST risk does not penalize RUN creation');

  const oppSet={type:'SET',cards:[{},{},{}],chain:0};
  ok(ctx.opponentMeldAttachBias('enemy','player',oppSet,[{},{},{},{}],1)===8, 'AI favors immediately BURSTing and retiring an opponent SET');
  const oppRunLow={type:'RUN',cards:[{},{},{}],chain:2};
  const oppRunHot={type:'RUN',cards:[{},{},{}],chain:3};
  ok(ctx.opponentMeldAttachBias('enemy','player',oppRunLow,[{},{},{},{}],1)===2, 'AI still values ordinary opponent-RUN interaction');
  ok(ctx.opponentMeldAttachBias('enemy','player',oppRunHot,[{},{},{},{}],1)===-4, 'AI discounts pushing an opponent-controlled RUN into CHAIN 4+ completion flexibility');
  ok(ctx.opponentMeldAttachBias('enemy','enemy',oppRunHot,[{},{},{},{}],1)===0, 'opponent-meld bias is not applied to own melds');
}

{
  const ctx = vm.createContext({console, Math, Array, Object, Set, Map});
  const player={hand:Array.from({length:8},(_,i)=>({uid:`p${i}`}))}, enemy={hand:[]};
  Object.assign(ctx, {
    state:{turnNo:4,switchTarget:'player',switchPower:25,discard:[]},
    sideObj:w=>w==='player'?player:enemy,
    other:w=>w==='enemy'?'player':'enemy',
    meldType:cards=>cards.length===3&&cards.every(c=>c.group==='set')?'SET':cards.length===3&&cards.every(c=>c.group==='run')?'RUN':null
  });
  install(ctx, 'combinations', 'futureBurstRisk', 'bestNewMeld');
  const hand=[
    {uid:'s1',group:'set',named:false},{uid:'s2',group:'set',named:false},{uid:'s3',group:'set',named:false},
    {uid:'r1',group:'run',named:false},{uid:'r2',group:'run',named:false},{uid:'r3',group:'run',named:false}
  ];
  ok(ctx.bestNewMeld(hand)?.type==='SET', 'generic meld scoring remains backward-compatible when no AI side is supplied');
  ok(ctx.bestNewMeld(hand,'enemy')?.type==='RUN', 'AI can prefer a slightly weaker RUN when a new SET would expose an urgent future BURST lane');
}

ok(html.includes('sc+=opponentMeldAttachBias(w,targetSide,m,combined,k)'), 'extension scoring consumes the opponent-meld context bias');
ok(html.includes("bestNewMeld(hand.filter(c=>c.blockedUntilTurn!==state.turnNo),w)"), 'turn-aware AI new-meld scoring receives the acting side');
ok(road.includes('- [x] Improve opponent-meld and future-BURST risk evaluation'), 'ROADMAP marks M10 opponent-board risk evaluation complete');

console.log('RUMMY//DUEL M10 board-risk regression tests passed.');
