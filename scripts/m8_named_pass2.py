from pathlib import Path

p=Path('index.html')
s=p.read_text()

def rep(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    s=s.replace(old,new,1)

# Player-facing tracking for Death Sentence.
rep('<div class="pileRule">장수 제한 없음 · 맨 위만 가져오기</div></div></div>',
    '<div class="pileRule" id="discardRuleText">장수 제한 없음 · 맨 위만 가져오기</div></div></div>',
    'discard rule id')

# Clarify three second-pass named-card contracts before wiring behavior.
rep("'SQ':{n:'사형선고',t:'seal1',d:'이 카드가 포함된 3장 SET은 부족한 마지막 무늬를 추적한다. 그 카드가 버림패 맨 위가 되면 다음 획득 때 우선 표시된다.'},",
    "'SQ':{n:'사형선고',t:'seal1',d:'이 카드가 포함된 3장 SET은 부족한 마지막 무늬를 추적한다. 그 정확한 카드가 공용 버림패 맨 위면 사형선고 목표로 표시된다.'},",
    'death sentence text')
rep("'HQ':{n:'대역 배우',t:'flexSuit',d:'RUN에서 원하는 무늬처럼 취급할 수 있다. 실제 ♥가 아닌 무늬 역할을 했다면 조합 정리 때 손으로 돌아온다.'},",
    "'HQ':{n:'대역 배우',t:'flexSuit',d:'RUN에서 원하는 무늬처럼 취급할 수 있다. 실제 ♥가 아닌 무늬 역할을 한 상태로 조합이 정리되면 현재 제어자의 손으로 돌아온다.'},",
    'understudy text')
rep("'CK':{n:'조율자',t:'alternateBonus',d:'내 필드에 SET과 RUN이 모두 있으면 턴당 1회 한쪽에서 회수한 카드를 다른 쪽에 붙일 때 무료 회수로 취급한다.'},",
    "'CK':{n:'조율자',t:'alternateBonus',d:'조율자가 내 공개 조합에 있고 SET과 RUN이 모두 있으면, 다른 종류 조합에 바로 붙을 수 있는 내 카드 회수를 턴당 1회 무료로 하고 그 카드는 같은 턴 즉시 이어붙일 수 있다.'},",
    'tuner text')

# Track whether Understudy actually served as an off-heart suit in a RUN.
rep('recoverReturnOverrideToken:null,fuseArmed:false,officialStatus:',
    'recoverReturnOverrideToken:null,fuseArmed:false,flexSuitOffSuit:false,officialStatus:',
    'understudy role property')

old="function meldType(cards){if(setValid(cards))return'SET';if(runValid(cards))return'RUN';return null}function chainDamage"
new="""function meldType(cards){if(setValid(cards))return'SET';if(runValid(cards))return'RUN';return null}
function deathSentenceNeed(m){if(!m||m.type!=='SET'||m.cards.length!==3)return null;const death=m.cards.find(c=>c.tag==='seal1');if(!death)return null;const real=m.cards.filter(c=>!isJoker(c));if(real.length!==3)return null;const used=new Set(real.map(c=>c.suit));if(used.size!==3)return null;const missing=['S','H','D','C'].filter(s=>!used.has(s));if(missing.length!==1)return null;return{rank:death.rank,suit:missing[0],owner:death.owner,card:death}}
function deathSentencePriority(w,c=state.discard.at(-1)){if(!c||isJoker(c))return null;for(const side of['player','enemy'])for(const m of meldsOf(side)){const need=deathSentenceNeed(m);if(need&&need.owner===w&&c.rank===need.rank&&c.suit===need.suit)return need}return null}
function runNaturalSuit(cards){const counts={};for(const c of cards||[])if(!isJoker(c)&&!isSuitFlexible(c))counts[c.suit]=(counts[c.suit]||0)+1;return Object.entries(counts).sort((a,b)=>b[1]-a[1])[0]?.[0]||null}
function recordFlexibleSuitRoles(m){const target=m?.type==='RUN'?runNaturalSuit(m.cards):null;for(const c of m?.cards||[])if(c.tag==='flexSuit')c.flexSuitOffSuit=!!target&&target!==c.suit}
function tunerReadyForRecovery(w,targetSide,m,c){const s=sideObj(w);if(!s||targetSide!==w||s.flags?.tuner||!m||!c)return false;const own=meldsOf(w);if(!own.some(mm=>mm.cards.some(x=>x.owner===w&&x.tag==='alternateBonus')))return false;if(!own.some(mm=>mm.type==='SET')||!own.some(mm=>mm.type==='RUN'))return false;const destType=m.type==='SET'?'RUN':m.type==='RUN'?'SET':null;if(!destType)return false;return own.some(tm=>{if(tm===m||tm.type!==destType||tm.lastAttachToken===state.turnToken||tm.createdToken===state.turnToken)return false;if(meldType(tm.cards.concat(c))!==tm.type)return false;const wouldReturn=tm.type==='RUN'||(tm.type==='SET'&&tm.cards.length===3);return !wouldReturn||(canSideReturn(w)&&!s.returnedSwitchThisTurn)})}
function recoveryFreeReason(w,targetSide,m,c){const s=sideObj(w);if(tunerReadyForRecovery(w,targetSide,m,c))return'tuner';if(state.field?.tag==='roundabout'&&!s.flags.roundabout)return'roundabout';if(c.outlawFreeRecoverAt!=null&&s.turnStarts<=c.outlawFreeRecoverAt)return'outlaw';if(s.freeRecoverAfterRummy)return'rummy';return null}
function chainDamage"""
rep(old,new,'named pass2 helpers')

# Central role refresh runs after creation, extension and recovery/movement adjustments.
rep("function markSetCompletion(m,owner){if(!m)return;if(m.type==='RUN')m.chain=Math.max(0,Math.min(4,m.chain??Math.max(0,m.cards.length-3)))}",
    "function markSetCompletion(m,owner){if(!m)return;if(m.type==='RUN')m.chain=Math.max(0,Math.min(4,m.chain??Math.max(0,m.cards.length-3)));recordFlexibleSuitRoles(m)}",
    'role refresh')

# Understudy returns only if it actually represented another suit, regardless of which side controls the meld.
rep("else if(c.tag==='flexSuit'&&c.owner===owner&&c.suit==='H'){sideObj(c.owner).hand.push(c);c.age=0;log(`${c.name}: 조합 정리에서 손패로 귀환.`,'good')}",
    "else if(c.tag==='flexSuit'&&c.flexSuitOffSuit){const home=c.owner;sideObj(home).hand.push(c);c.flexSuitOffSuit=false;c.age=0;log(`${c.name}: 다른 무늬 대역 역할을 마치고 현재 제어자 손패로 귀환.`,'good')}",
    'understudy retirement')

# Tuner participates in the same free-recovery gate as fields/RUMMY, with a one-turn immediate-reattach override.
old_can="function canRecoverCard(w,targetSide,mi,ci){const s=sideObj(w),m=meldsOf(targetSide)[mi],c=m?.cards[ci];if(!m||!c||c.owner!==w||c.enteredMeldToken===state.turnToken)return false;const free=(state.field?.tag==='roundabout'&&!s.flags.roundabout)||(c.outlawFreeRecoverAt!=null&&s.turnStarts<=c.outlawFreeRecoverAt)||s.freeRecoverAfterRummy;if(s.recoveredThisTurn&&!free)return false;if(meldFixedActive(m)||cardFixedActive(c))return false;const remain=m.cards.filter((_,i)=>i!==ci);return remain.length>=3&&meldType(remain)===m.type}"
new_can="function canRecoverCard(w,targetSide,mi,ci){const s=sideObj(w),m=meldsOf(targetSide)[mi],c=m?.cards[ci];if(!m||!c||c.owner!==w||c.enteredMeldToken===state.turnToken)return false;const free=!!recoveryFreeReason(w,targetSide,m,c);if(s.recoveredThisTurn&&!free)return false;if(meldFixedActive(m)||cardFixedActive(c))return false;const remain=m.cards.filter((_,i)=>i!==ci);return remain.length>=3&&meldType(remain)===m.type}"
rep(old_can,new_can,'canRecover tuner')

old_player="function playerRecover(){const plan=recoverPlan();if(!plan){log('회수 불가 · 내 소유 카드 1장을 고르고, 빼도 조합이 유지되어야 합니다.','hit');return}const s=state.player,m=meldsOf(plan.side)[plan.mi],[c]=m.cards.splice(plan.ci,1);s.hand.push(c);s.rummyRecoveryPending=false;const free=(state.field?.tag==='roundabout'&&!s.flags.roundabout)||(c.outlawFreeRecoverAt!=null&&s.turnStarts<=c.outlawFreeRecoverAt)||s.freeRecoverAfterRummy;if(!free)s.recoveredThisTurn=true;else{if(state.field?.tag==='roundabout')s.flags.roundabout=true;s.freeRecoverAfterRummy=false;log('무료 회수 · 기본 회수 횟수를 소모하지 않습니다.','good')}s.actedThisTurn=true;c.suppressEffectToken=state.turnToken;c.recoveredToken=state.turnToken;c.recoverReturnOverrideToken=null;c.age=0;if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);markSetCompletion(m,plan.side);if(c.tag==='ambulance'){heal('player',2);if(plan.side==='enemy')addShield('player',2)}if(c.tag==='fuseRound'&&c.fuseArmed){addSwitchPower('player',16,c.name);c.fuseArmed=false}state.boardSelected.clear();state.target=null;log(`YOU 회수 · ${plan.side==='enemy'?'상대':'내'} 공개 조합의 ${cardText(c)} → 손패${m.type==='RUN'?' · CHAIN -1':''}.`,'important');render()}"
new_player="function playerRecover(){const plan=recoverPlan();if(!plan){log('회수 불가 · 내 소유 카드 1장을 고르고, 빼도 조합이 유지되어야 합니다.','hit');return}const s=state.player,m=meldsOf(plan.side)[plan.mi],freeReason=recoveryFreeReason('player',plan.side,m,plan.card),[c]=m.cards.splice(plan.ci,1);s.hand.push(c);s.rummyRecoveryPending=false;if(!freeReason)s.recoveredThisTurn=true;else{if(freeReason==='tuner')s.flags.tuner=true;else if(freeReason==='roundabout')s.flags.roundabout=true;else if(freeReason==='rummy')s.freeRecoverAfterRummy=false;log(freeReason==='tuner'?'조율자 · 다른 종류 조합으로 옮길 수 있는 회수를 무료 처리하고 같은 턴 재사용을 허용합니다.':'무료 회수 · 기본 회수 횟수를 소모하지 않습니다.','good')}s.actedThisTurn=true;c.suppressEffectToken=state.turnToken;c.recoveredToken=state.turnToken;c.recoverReturnOverrideToken=freeReason==='tuner'?state.turnToken:null;c.age=0;if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);markSetCompletion(m,plan.side);if(c.tag==='ambulance'){heal('player',2);if(plan.side==='enemy')addShield('player',2)}if(c.tag==='fuseRound'&&c.fuseArmed){addSwitchPower('player',16,c.name);c.fuseArmed=false}state.boardSelected.clear();state.target=null;log(`YOU 회수 · ${plan.side==='enemy'?'상대':'내'} 공개 조합의 ${cardText(c)} → 손패${m.type==='RUN'?' · CHAIN -1':''}.`,'important');render()}"
rep(old_player,new_player,'player tuner recovery')

old_ai="function bestRecoverAI(w){const s=sideObj(w);if(s.recoveredThisTurn)return null;let best=null;for(const targetSide of [other(w),w])for(let mi=0;mi<meldsOf(targetSide).length;mi++){const m=meldsOf(targetSide)[mi];for(let ci=0;ci<m.cards.length;ci++){if(!canRecoverCard(w,targetSide,mi,ci))continue;const c=m.cards[ci],hyp=s.hand.concat(c);let sc=-1;if(!s.newMeldUsed){const nm=bestNewMeldForTurn(w,hyp);if(nm&&nm.cards.some(x=>x.uid===c.uid))sc=Math.max(sc,nm.score)}if(sc>=0&&(!best||sc>best.score))best={side:targetSide,mi,ci,card:c,score:sc}}}return best}"
new_ai="function bestRecoverAI(w){const s=sideObj(w);let best=null;for(const targetSide of [other(w),w])for(let mi=0;mi<meldsOf(targetSide).length;mi++){const m=meldsOf(targetSide)[mi];for(let ci=0;ci<m.cards.length;ci++){if(!canRecoverCard(w,targetSide,mi,ci))continue;const c=m.cards[ci],hyp=s.hand.concat(c);let sc=tunerReadyForRecovery(w,targetSide,m,c)?18:-1;if(!s.newMeldUsed){const nm=bestNewMeldForTurn(w,hyp);if(nm&&nm.cards.some(x=>x.uid===c.uid))sc=Math.max(sc,nm.score)}if(sc>=0&&(!best||sc>best.score))best={side:targetSide,mi,ci,card:c,score:sc}}}return best}"
rep(old_ai,new_ai,'AI tuner planning')

old_exec="function executeRecoverAI(w,plan){const s=sideObj(w),m=meldsOf(plan.side)[plan.mi],[c]=m.cards.splice(plan.ci,1);s.hand.push(c);s.rummyRecoveryPending=false;const free=(state.field?.tag==='roundabout'&&!s.flags.roundabout)||(c.outlawFreeRecoverAt!=null&&s.turnStarts<=c.outlawFreeRecoverAt)||s.freeRecoverAfterRummy;if(!free)s.recoveredThisTurn=true;else{s.flags.roundabout=true;s.freeRecoverAfterRummy=false}s.actedThisTurn=true;c.suppressEffectToken=state.turnToken;c.recoveredToken=state.turnToken;c.recoverReturnOverrideToken=null;c.age=0;if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);markSetCompletion(m,plan.side);if(c.tag==='ambulance'){heal(w,2);if(plan.side!==w)addShield(w,2)}if(c.tag==='fuseRound'&&c.fuseArmed){addSwitchPower(w,16,c.name);c.fuseArmed=false}log(`${w==='player'?'YOU':'CPU'} 회수 · ${cardText(c)}${m.type==='RUN'?' · CHAIN -1':''}.`,'important');return c}"
new_exec="function executeRecoverAI(w,plan){const s=sideObj(w),m=meldsOf(plan.side)[plan.mi],freeReason=recoveryFreeReason(w,plan.side,m,plan.card),[c]=m.cards.splice(plan.ci,1);s.hand.push(c);s.rummyRecoveryPending=false;if(!freeReason)s.recoveredThisTurn=true;else{if(freeReason==='tuner')s.flags.tuner=true;else if(freeReason==='roundabout')s.flags.roundabout=true;else if(freeReason==='rummy')s.freeRecoverAfterRummy=false}s.actedThisTurn=true;c.suppressEffectToken=state.turnToken;c.recoveredToken=state.turnToken;c.recoverReturnOverrideToken=freeReason==='tuner'?state.turnToken:null;c.age=0;if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);markSetCompletion(m,plan.side);if(c.tag==='ambulance'){heal(w,2);if(plan.side!==w)addShield(w,2)}if(c.tag==='fuseRound'&&c.fuseArmed){addSwitchPower(w,16,c.name);c.fuseArmed=false}log(`${w==='player'?'YOU':'CPU'} 회수 · ${cardText(c)}${freeReason==='tuner'?' · 조율자 무료 이동':''}${m.type==='RUN'?' · CHAIN -1':''}.`,'important');return c}"
rep(old_exec,new_exec,'AI tuner recovery')

# Reset the Tuner once-per-turn flag with other turn flags.
rep("casinoCycle:false};const ri=state.discard", "casinoCycle:false,tuner:false};const ri=state.discard", 'turn-start tuner flag')

# Surface Death Sentence both on its SET and on the public discard target.
old_render="function renderDiscard(){const el=document.getElementById('discardCard'),c=state.discard.at(-1);el.innerHTML=c?`<div>${cardHTML(c)}</div>`:'<div class=\"discardEmpty\">비어 있음<br>손패 → 버림패<br>맨 위만 가져오기</div>'}"
new_render="function renderDiscard(){const el=document.getElementById('discardCard'),c=state.discard.at(-1),rule=document.getElementById('discardRuleText'),p=deathSentencePriority('player',c),e=deathSentencePriority('enemy',c),hit=p||e;el.innerHTML=c?`<div>${cardHTML(c)}</div>`:'<div class=\"discardEmpty\">비어 있음<br>손패 → 버림패<br>맨 위만 가져오기</div>';if(rule){rule.textContent=hit?`${hit.owner==='player'?'YOU':'CPU'} 사형선고 목표 · ${cardText(c)}`:'장수 제한 없음 · 맨 위만 가져오기';rule.classList.toggle('gold',!!p);rule.classList.toggle('red',!p&&!!e)}}"
rep(old_render,new_render,'death sentence render')

old_need="function meldNeedText(m){if(m.type==='SET'){const real=m.cards.filter(c=>!isJoker(c));const rank=real[0]?.rank||'?',used=new Set(real.map(c=>c.suit)),need=['S','H','D','C'].filter(x=>!used.has(x)).map(x=>`${rank}${SUIT_SYMBOL[x]}`);return`필요: ${need.join(' / ')||'동일 숫자의 남은 무늬'}`}"
new_need="function meldNeedText(m){if(m.type==='SET'){const real=m.cards.filter(c=>!isJoker(c));const rank=real[0]?.rank||'?',used=new Set(real.map(c=>c.suit)),need=['S','H','D','C'].filter(x=>!used.has(x)).map(x=>`${rank}${SUIT_SYMBOL[x]}`),death=deathSentenceNeed(m);return`필요: ${need.join(' / ')||'동일 숫자의 남은 무늬'}${death?` · 사형선고 추적 ${death.rank}${SUIT_SYMBOL[death.suit]}`:''}`}"
rep(old_need,new_need,'death sentence meld hint')

p.write_text(s)

# Add executable second-pass behavioral regressions.
t=Path('tests/named-card-behavior-2.mjs')
t.write_text(r"""import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function functionSource(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const brace=script.indexOf('{',start);let depth=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')depth++;else if(script[i]==='}'&&--depth===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const name of names)vm.runInContext(functionSource(name),ctx)}
function context(extra={}){return vm.createContext({console,Math,Set,Map,Array,Object,Number,String,Boolean,...extra})}
function card(suit,rank,extra={}){return{uid:`${suit}${rank}-${Math.random()}`,suit,rank:String(rank),owner:'player',originOwner:'player',tag:null,named:false,...extra}}

// Death Sentence: exact missing suit only, and only the current controller sees its matching discard as priority.
{
  const sq=card('S','Q',{tag:'seal1',named:true}),hq=card('H','Q'),dq=card('D','Q');
  const meld={type:'SET',cards:[sq,hq,dq]};
  const state={discard:[]},ctx=context({state,isJoker:c=>c.suit==='J',meldsOf:w=>w==='player'?[meld]:[]});
  install(ctx,'deathSentenceNeed','deathSentencePriority');
  const need=ctx.deathSentenceNeed(meld);
  ok(need?.rank==='Q'&&need?.suit==='C','Death Sentence tracks the exact missing fourth suit');
  ok(!!ctx.deathSentencePriority('player',card('C','Q')),'matching discard top is a Death Sentence priority');
  ok(!ctx.deathSentencePriority('player',card('C','K')),'wrong rank is not a Death Sentence priority');
}

// Doppelganger remains a SET support card: rank copies, suit identity does not.
{
  const ctx=context({isJoker:c=>c.suit==='J'});install(ctx,'setValid');
  ok(ctx.setValid([card('S',7),card('H',7),card('C','Q',{tag:'flexRankCopy'})]),'Doppelganger copies the SET rank');
  ok(!ctx.setValid([card('S',7),card('C',7),card('C','Q',{tag:'flexRankCopy'})]),'Doppelganger still obeys unique-suit SET rules');
}

// Understudy records whether it was truly acting off-heart.
{
  const ctx=context({isJoker:c=>c.suit==='J',isSuitFlexible:c=>c.tag==='flexSuit'});install(ctx,'runNaturalSuit','recordFlexibleSuitRoles');
  const natural=card('H','Q',{tag:'flexSuit'}),off=card('H','Q',{tag:'flexSuit'});
  ctx.recordFlexibleSuitRoles({type:'RUN',cards:[card('H',10),card('H','J'),natural]});
  ctx.recordFlexibleSuitRoles({type:'RUN',cards:[card('C',10),card('C','J'),off]});
  ok(natural.flexSuitOffSuit===false,'Understudy stays spent when it served as natural hearts');
  ok(off.flexSuitOffSuit===true,'Understudy records an off-heart suit role');
}

// Understudy retirement follows the recorded role even if the meld is controlled by the opponent.
{
  const off=card('H','Q',{tag:'flexSuit',flexSuitOffSuit:true}),natural=card('H','Q',{tag:'flexSuit',flexSuitOffSuit:false});
  const sides={player:{hand:[],spent:[]},enemy:{hand:[],spent:[]}},melds={enemy:[{type:'RUN',cards:[off]}]};
  const ctx=context({sideObj:w=>sides[w],meldsOf:w=>melds[w]||[],log:()=>{}});install(ctx,'retireMeld');
  ctx.retireMeld('enemy',0,'test');
  ok(sides.player.hand.includes(off)&&!sides.player.spent.includes(off),'off-suit Understudy returns to its current controller hand');
  melds.enemy=[{type:'RUN',cards:[natural]}];ctx.retireMeld('enemy',0,'test');
  ok(sides.player.spent.includes(natural),'natural-heart Understudy is spent normally');
}

// Tuner: must be public, requires both own meld types, legal opposite-type landing, and is once per turn.
{
  const moving=card('C',9),tuner=card('C','K',{tag:'alternateBonus'});
  const source={type:'RUN',cards:[card('C',6),card('C',7),card('C',8),moving],createdToken:1,lastAttachToken:null};
  const target={type:'SET',cards:[Object.assign(card('S',9),{_meldType:'SET'}),card('H',9),tuner],createdToken:1,lastAttachToken:null};
  const side={flags:{tuner:false,roundabout:false},returnedSwitchThisTurn:false,turnStarts:1,freeRecoverAfterRummy:false};
  const state={turnToken:7,field:null};
  const ctx=context({state,sideObj:()=>side,meldsOf:()=>[source,target],meldType:cards=>cards[0]?._meldType||null,canSideReturn:()=>true});
  install(ctx,'tunerReadyForRecovery','recoveryFreeReason');
  ok(ctx.tunerReadyForRecovery('player','player',source,moving),'Tuner recognizes a legal RUN-to-SET transfer recovery');
  ok(ctx.recoveryFreeReason('player','player',source,moving)==='tuner','Tuner takes the free-recovery reason for its transfer');
  side.flags.tuner=true;
  ok(!ctx.tunerReadyForRecovery('player','player',source,moving),'Tuner is limited to once per turn');
}

ok(html.includes('id="discardRuleText"'),'discard UI exposes a dynamic Death Sentence priority line');
ok(html.includes('사형선고 추적'),'SET readout exposes the tracked Death Sentence card');
ok(script.includes("c.recoverReturnOverrideToken=freeReason==='tuner'?state.turnToken:null"),'Tuner grants same-turn attach override only to its transfer recovery');
console.log('M8 named-card behavioral pass 2 regressions passed.');
""")

# Extend the static audit with second-pass contract guards.
a=Path('tests/named-card-audit.mjs')
audit=a.read_text()
needle="ok(html.includes(\"'DA':{n:'장물아비',t:'fencePeek',d:'버림패에서 가져올 때 바로 아래 카드도 함께 확인한다.'}\"),'Fence text no longer promises an unimplemented swap');\n"
insert=needle+"ok(script.includes('function deathSentencePriority('),'Death Sentence has an active discard-priority resolver');\nok(script.includes('function tunerReadyForRecovery('),'Tuner has an active cross-meld recovery resolver');\nok(script.includes('function recordFlexibleSuitRoles('),'Understudy records its actual RUN suit role');\n"
if audit.count(needle)!=1:raise SystemExit('audit insertion anchor mismatch')
a.write_text(audit.replace(needle,insert,1))

# Roadmap: complete the second correctness tranche only.
r=Path('ROADMAP.md')
road=r.read_text()
old="- [ ] Finish dead/partial-effect audit for choice-heavy and timing-heavy cards such as Death Sentence, Doppelganger support interactions, Tuner, and role-sensitive understudy behavior\n"
new="- [x] Second correctness pass: activate Death Sentence discard targeting, Tuner cross-meld recovery, role-sensitive Understudy retirement, and executable Doppelganger SET support coverage\n- [ ] Finish remaining choice/copy/timing audit and per-card regressions before declaring the first ~50 behavior-stable\n"
if road.count(old)!=1:raise SystemExit('roadmap pass2 anchor mismatch')
road=road.replace(old,new,1)
old2="""## Current next work
1. M8: finish the remaining dead/partial named effects, especially Death Sentence (`seal1`) and Tuner (`alternateBonus`), before adding more cards.
2. M8: audit copy/choice-heavy cards and role-sensitive return behavior with executable per-card regressions instead of text-only promises.
3. After the first ~50 are behavior-stable, rebalance frequency/strength and only then expand content or move to M9 Jokers/fields.
"""
new2="""## Current next work
1. M8: finish the remaining choice/copy/timing-heavy named-card audit and add executable regressions for each behavior that still depends on implicit ordering.
2. M8: review first-50 strength/frequency outliers only after behavior contracts are stable; keep direct SWITCH manipulation a minority.
3. When the first ~50 pass the behavior audit, mark M8 stabilization complete and move to M9 Joker/field identity cleanup before larger content expansion.
"""
if road.count(old2)!=1:raise SystemExit('roadmap current-next mismatch')
r.write_text(road.replace(old2,new2,1))
