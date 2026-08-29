import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);
ok(!html.includes('버림패 5장 제한'), 'discard pile has no five-card cap logic');
ok(!html.includes('공용 버림패 <b id="discardCount">0</b>/5'), 'discard UI has no /5 cap');
ok(html.includes('function canRetireStaleRun(){return false}'), 'free RUN retirement is disabled');
ok(html.includes("if(meldsOf(w).length>=2)return'full'"), 'full public board blocks new meld creation');
ok(html.includes("s.melds.length<2&&bestNewMeld(s.hand)"), 'maintenance/legal-action check respects the two-meld cap');
ok(html.includes('function acquireDiscardCard(w,indexFromTop=0)'), 'discard acquisition uses a shared helper');
ok(html.includes("c=acquireDiscardCard('player',0)"), 'player Black Market second-card path uses shared acquisition');
ok(html.includes("c=acquireDiscardCard('enemy',0)"), 'AI Black Market second-card path uses shared acquisition');
ok(html.includes("typeof unlock==='function'&&!!unlock(p)"), 'invalid saved character IDs cannot crash char unlock checks');
ok(html.includes('같은 종류면 보호막 12.'), 'Chain Reaction text matches its 12-shield implementation');
ok(html.includes('jokerLastDetonateReduction=15'), 'Last Laugh DETONATE reduction is implemented');
ok(html.includes('if(jokerLast&&opts.returned)'), 'Last Laugh bonus cycle requires a returning RUMMY');
ok(html.includes("addSwitchPower(w,amount,label,other(w))"), 'SWITCH returns evaluate CORE LETHAL against the post-return target');
console.log('RUMMY//DUEL rules smoke tests passed.');
