import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

function extractFunction(name) {
  const line = script.split('\n').find(row => row.includes(`function ${name}(`));
  if (!line) throw new Error(`missing function ${name}`);
  const start = line.indexOf(`function ${name}(`);
  let depth = 0;
  let began = false;
  let end = -1;
  for (let i = start; i < line.length; i++) {
    if (line[i] === '{') { depth++; began = true; }
    else if (line[i] === '}') {
      depth--;
      if (began && depth === 0) { end = i + 1; break; }
    }
  }
  if (end < 0) throw new Error(`could not extract function ${name}`);
  const source = line.slice(start, end);
  return new Function(`${source}; return ${name};`)();
}

new Function(script);
ok(!html.includes('버림패 5장 제한'), 'discard pile has no five-card cap logic');
ok(!html.includes('공용 버림패 <b id="discardCount">0</b>/5'), 'discard UI has no /5 cap');
ok(!html.includes('function canRetireStaleRun(') && !html.includes('data-stale-retire'), 'free RUN retirement path is absent');
ok(html.includes("if(meldsOf(w).length>=3)return'full'"), 'full public board blocks new meld creation');
ok(html.includes('function bestNewMeldForTurn(w,hand=sideObj(w).hand)'), 'turn-aware new-meld legality helper exists');
ok(html.includes("s.melds.length<3&&bestNewMeldForTurn(w)"), 'maintenance/legal-action check respects board cap and current-turn card restrictions');
ok(html.includes('function acquireDiscardCard(w,indexFromTop=0)'), 'discard acquisition uses a shared helper');
ok(html.includes("c=acquireDiscardCard('player',0)"), 'player Black Market second-card path uses shared acquisition');
ok(html.includes("c=acquireDiscardCard('enemy',0)"), 'AI Black Market second-card path uses shared acquisition');
ok(html.includes("typeof unlock==='function'&&!!unlock(p)"), 'invalid saved character IDs cannot crash char unlock checks');
ok(html.includes('같은 종류라면 장전 8을 얻어 이번 반환에 사용한다.'), 'Chain Reaction documents its shared loaded status');
ok(html.includes('jokerLastDetonateReduction=15'), 'Last Laugh DETONATE reduction is implemented');
ok(html.includes('if(jokerLast&&opts.returned)'), 'Last Laugh bonus cycle requires a returning RUMMY');
ok(html.includes("addSwitchPower(w,statusResult.amount,label,other(w))"), 'SWITCH returns evaluate CORE LETHAL against the post-return target');
ok(html.includes('회수한 카드는 같은 턴 버스트/체인 반환 재료로 다시 사용할 수 없습니다'), 'rules UI documents the recovery return guard');
ok(html.includes('recoverReturnOverrideToken'), 'named recovery return exception has an explicit runtime token');
ok(html.includes('recoveredCardsCanReturn(cards,state.turnToken,m)'), 'attach path checks destination-aware recovered-card return eligibility');
ok(!html.includes('const ex=bestExtensionFromHand(w,hyp,c.uid);if(ex)sc=Math.max(sc,ex.score+0.5)'), 'AI no longer values base recovery by illegal same-turn return reuse');

const recoveredCardCanReturn = extractFunction('recoveredCardCanReturn');
ok(recoveredCardCanReturn({recoveredToken:null,recoverReturnOverrideToken:null}, 7), 'normal card can be used for a SWITCH-returning attach');
ok(!recoveredCardCanReturn({recoveredToken:7,recoverReturnOverrideToken:null}, 7), 'card recovered this turn cannot immediately return SWITCH');
ok(recoveredCardCanReturn({recoveredToken:6,recoverReturnOverrideToken:null}, 7), 'card recovered on a previous turn can return SWITCH');
ok(recoveredCardCanReturn({recoveredToken:7,recoverReturnOverrideToken:7}, 7), 'explicit named-card exception can reuse a recovered card for return');

const runSequenceOK = extractFunction('runSequenceOK');
ok(runSequenceOK([1,2,3],0,0,3), 'A-2-3 numeric RUN sequence is legal');
ok(!runSequenceOK([13,1,2],0,0,3), 'K-A-2 is not a low-A RUN sequence');
ok(runSequenceOK([12,13,14],0,0,3), 'Q-K-A high-A numeric sequence is legal');

const chainDamage = extractFunction('chainDamage');
ok([1,2,3,4,5].map(chainDamage).join(',') === '10,15,20,25,25', 'CHAIN damage progression is 10/15/20/25/25');

console.log('RUMMY//DUEL rules smoke tests passed.');