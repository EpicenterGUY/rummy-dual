from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def replace_top_function(name,new_code):
    global s
    start=s.find(f'function {name}(')
    if start<0: raise SystemExit(f'missing function {name}')
    end=s.find('\nfunction ',start+1)
    if end<0: raise SystemExit(f'missing end for {name}')
    s=s[:start]+new_code.rstrip()+s[end:]

free_helpers=r'''function freeRecoverCandidates(w,m,exclude=[]){if(!m||meldFixedActive(m))return[];const ex=new Set((exclude||[]).map(c=>c.uid)),out=[];for(let i=0;i<m.cards.length;i++){const c=m.cards[i];if(ex.has(c.uid)||c.owner!==w||c.enteredMeldToken===state.turnToken||cardFixedActive(c))continue;const remain=m.cards.filter((_,j)=>j!==i);if(remain.length>=3&&meldType(remain)===m.type)out.push(c)}return out}
function recoverSpecificFromMeld(w,m,c,opts={}){if(!c||!freeRecoverCandidates(w,m,opts.exclude||[]).some(x=>x.uid===c.uid))return null;const i=m.cards.findIndex(x=>x.uid===c.uid);if(i<0)return null;m.cards.splice(i,1);if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);sideObj(w).hand.push(c);if(c.tag==='smuggledSuit')c.smuggledActive=false;sideObj(w).rummyRecoveryPending=false;c.suppressEffectToken=state.turnToken;c.recoveredToken=state.turnToken;c.recoverReturnOverrideToken=null;c.recoverReturnTargets=null;c.age=0;markSetCompletion(m,w);if(opts.allowReturnReuse&&typeof grantRecoveryReturnOverride==='function')grantRecoveryReturnOverride(w,c,m,{requiredType:opts.requiredType||null,ownOnly:!!opts.ownOnly});log(`${opts.label||'무료 회수'}: ${cardText(c)}${m.type==='RUN'?' · 체인 -1':''}.`,'good');return c}
function requestFreeRecoverChoice(w,m,exclude=[],opts={}){const candidates=freeRecoverCandidates(w,m,exclude);if(!candidates.length)return false;const apply=c=>recoverSpecificFromMeld(w,m,c,{...opts,exclude});const interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&(!!opts.allowSkip||candidates.length>1);if(interactive){return requestEffectChoice({title:opts.title||opts.label||'무료 회수',text:opts.text||'회수할 내 카드를 고르세요.',options:candidates.map(c=>({key:c.uid,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:m.type==='RUN'?'회수 후 체인 -1':'회수 후 조합 유지',card:c})),allowSkip:!!opts.allowSkip,skipLabel:opts.skipLabel||'회수하지 않기',onChoose:o=>{if(o?.card)apply(o.card);if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(o?.card||null)}})}apply(candidates[0]);return false}
function freeRecoverFromMeld(w,m,exclude=[],opts={}){const c=freeRecoverCandidates(w,m,exclude)[0];return c?recoverSpecificFromMeld(w,m,c,{...opts,exclude}):null}
function recycleSpecificSpentCard(w,c,label='재활용업자'){const side=sideObj(w),i=side.spent.findIndex(x=>x.uid===c?.uid);if(i<0)return null;const[old]=side.spent.splice(i,1);old.age=0;old.fromDiscard=false;old.contractActive=false;side.deck.unshift(old);drawOne(w,false);log(`${label}: ${cardText(old)}를 소모패에서 덱 아래로 되돌리고 1장 뽑기.`,'good');if(w==='player')flashPile('deckPile');return old}
function requestSpentRecycleChoice(w,label='재활용업자',onAsyncResolved=null){const side=sideObj(w),candidates=[...side.spent];if(!candidates.length)return false;const interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive){return requestEffectChoice({title:label,text:'소모패에서 덱 아래로 되돌릴 카드 1장을 고르세요.',options:candidates.map(c=>({key:c.uid,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:'덱 아래로 이동 후 1장 뽑기',card:c})),onChoose:o=>{if(o?.card)recycleSpecificSpentCard(w,o.card,label);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.card||null)}})}recycleSpecificSpentCard(w,candidates.at(-1),label);return false}'''
replace_top_function('freeRecoverFromMeld',free_helpers)

resolve=r'''function resolveEffects(w,cards,type,ctx={}){const side=sideObj(w),seen=ctx.effectSeen||new Set(),foe=other(w),isReturning=!!ctx.willReturn,fx=ctx.fxState||(ctx.fxState={bonus:0,flatReturn:false,forceReturn:false,index:0,effectCards:null});if(!fx.effectCards){const list=[...(cards||[])];for(let i=0;i<list.length;i++){if(list[i]?.tag!=='goldenHand')continue;const j=list.findIndex((x,k)=>k>i&&x?.tag==='sameDiscardRank');if(j>=0){const[dep]=list.splice(j,1);list.splice(i,0,dep);i++}}fx.effectCards=list}const effectCards=fx.effectCards,pause=()=>({bonus:fx.bonus||0,flatReturn:!!fx.flatReturn,forceReturn:!!fx.forceReturn,pending:true});for(let i=fx.index;i<effectCards.length;i++){const c=effectCards[i];fx.index=i+1;if(!c?.named||c.suppressEffectToken===state.turnToken)continue;const key=`${c.uid}:${c.tag}`;if(seen.has(key))continue;seen.add(key);if(consumeOfficialStatus('player',side,'seal')){log(`${c.name}: 봉인으로 효과가 무효.`,'hit');continue}if(ctx.isAttach&&c.tag!=='venomNeedle'&&consumeOfficialStatus('meld',ctx.meld,'seal')){log(`${c.name}: 조합의 봉인으로 효과가 무효.`,'hit');continue}if(consumeOfficialStatus('card',c,'seal')){log(`${c.name}: 카드 봉인으로 효과가 무효.`,'hit');continue}const resume=()=>{if(typeof ctx.resumeEffects==='function')ctx.resumeEffects()};switch(c.tag){case'safetyPin':break;case'finalUltimatum':if(side.hand.length===0&&isReturning)fx.bonus+=18;break;case'seizureMark':if(ctx.isAttach&&ctx.targetOwner===foe)lockMeldRecovery(ctx.meld,ctx.targetOwner);break;case'returnIfIgnored':break;case'discardPursuit':if((w==='player'?state.lastEnemyUsedDiscard:state.lastPlayerUsedDiscard)&&ctx.isAttach&&ctx.targetOwner===foe){const paused=requestFreeRecoverChoice(w,ctx.meld,cards,{title:c.name,label:c.name,allowSkip:true,text:'상대 공개 조합에 있는 내 카드 중 회수할 카드를 고르거나 건너뛸 수 있습니다.',onAsyncResolved:resume});if(paused)return pause()}break;case'venomNeedle':if(ctx.isAttach&&ctx.targetOwner===foe){runEffectAction('applyStatus',{actor:w},{scope:'meld',target:ctx.meld,key:'seal',amount:1,opts:{silent:true}});log(`${c.name}: 상대 조합의 다음 네임드 효과 봉인.`,'important')}break;case'revenge3':if(side.detonateMemory>0&&!c.revengeUsed){c.revengeUsed=true;addShield(w,4);drawOne(w,false)}break;case'blackBullet':if(ctx.isAttach&&ctx.targetOwner===foe&&isReturning)fx.bonus+=10;break;case'fuseRound':if(ctx.isAttach&&ctx.targetOwner===foe)c.fuseArmed=true;break;case'ambushTrap':break;case'heldBonus':if(c.age>=2){const target=meldsOf(foe)[0];if(target)lockMeldRecovery(target,foe)}break;case'run5Bonus':if(type==='RUN'&&ctx.totalLength>=5&&ctx.isAttach&&cards.length>=2)drawOne(w,false);break;case'enemyAttachBonus':if(type==='RUN'&&ctx.isAttach&&ctx.targetOwner===foe){const paused=requestFreeRecoverChoice(w,ctx.meld,cards,{title:c.name,label:c.name,allowSkip:true,text:'상대 RUN의 내 소유 카드 중 무료 회수할 카드를 고르세요.',onAsyncResolved:resume});if(paused)return pause()}break;case'seal1':break;case'firstMeldBonus':if(ctx.isNew&&meldsOf(w).length===1)addShield(w,5);break;case'rummyPlus1':break;case'afterRummyDraw':if(side.rummyRecoveryPending)side.freeRecoverAfterRummy=true;break;case'bait':break;case'heal2':if(side.detonateMemory>0)heal(w,3);break;case'ambulance':break;case'runHeal2':if(type==='RUN'&&(ctx.meld?.cards||cards).filter(x=>x.suit==='H').length>=3){const paused=requestFreeRecoverChoice(w,ctx.meld,cards,{title:c.name,label:c.name,allowSkip:true,text:'조건을 만족한 RUN에서 무료 회수할 내 카드를 고르세요.',onAsyncResolved:resume});if(paused)return pause()}break;case'healAttack':break;case'setHeal3':if(type==='SET')addShield(w,ctx.isAttach&&ctx.totalLength===4?6:3);break;case'emergencyGear':addShield(w,state.switchTarget===w?8:5);break;case'insuranceAgent':break;case'rummyHeal4':break;case'afterRummyBonus':if(isReturning&&side.rummyReturnPending){fx.flatReturn=true;fx.forceReturn=true}break;case'flexSuit':break;case'heartKingCharge':break;case'fencePeek':break;case'creditTrade':drawMany(w,2,false);side.creditDebt=true;side.discardsRemaining=(side.discardsRemaining||1)+1;break;case'discardContract':if(c.contractActive){c.contractActive=false;drawOne(w,false)}break;case'smuggledSuit':break;case'counterfeiter':break;case'topDeckChoice':break;case'goldenHand':if(cards.some(x=>x.fromDiscard)){drawOne(w,false);const cand=side.hand.filter(x=>!cards.includes(x)).sort((a,b)=>b.age-a.age)[0];if(cand){removeFromHand(w,[cand]);cand.fromDiscard=false;side.deck.unshift(cand)}}break;case'appraiser':break;case'exchangeCycle':if(type==='SET'){cycleOldestHandCard(w,cards);if(ctx.totalLength===4)cycleOldestHandCard(w,cards)}break;case'recycler':if(side.spent.length){const paused=requestSpentRecycleChoice(w,c.name,resume);if(paused)return pause()}break;case'sameDiscardRank':{const lr=w==='player'?state.lastEnemyDiscardRank:state.lastPlayerDiscardRank;if(lr&&c.rank===lr)c.fromDiscard=true;break}case'extortion':break;case'marketMaker':if(ctx.isNew&&state.discard.length>1){const top=state.discard.splice(Math.max(0,state.discard.length-3));top.reverse();state.discard.push(...top);log(`${c.name}: 버림패 상단 3장 순서 변경.`,'important')}break;case'set4Bonus':if(type==='SET'&&ctx.totalLength===4)sideObj(foe).blockOpponentDiscardNext=true;break;case'repeatNumeric':{const eligible=['emergencyGear'];if(type==='RUN'&&ctx.totalLength>=4)eligible.push('run4Draw');if(ctx.isAttach&&ctx.targetOwner===w)eligible.push('freeSwapRecover');const prior=firstCopyEffectSource(cards,c,eligible);if(prior?.tag==='run4Draw')drawOne(w,false);else if(prior?.tag==='emergencyGear')addShield(w,3);else if(prior?.tag==='freeSwapRecover'){const paused=requestFreeRecoverChoice(w,ctx.meld,cards,{title:c.name,label:c.name,allowReturnReuse:true,text:'복제한 갈아끼우기로 무료 회수할 카드를 고르세요.',onAsyncResolved:resume});if(paused)return pause()}break}case'run4Draw':if(type==='RUN'&&ctx.totalLength>=4){drawOne(w,false);if(ctx.totalLength>=6){const candidates=side.hand.filter(x=>!cards.includes(x)),bottom=cand=>{if(!cand||!side.hand.some(x=>x.uid===cand.uid))return false;removeFromHand(w,[cand]);cand.fromDiscard=false;cand.contractActive=false;cand.age=0;side.deck.unshift(cand);log(`${c.name}: ${cardText(cand)}를 덱 아래로 보냈습니다.`,'good');if(w==='player')flashPile('deckPile');return true};if(candidates.length){if(w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'){const opened=requestEffectChoice({title:c.name,text:'RUN이 6장 이상입니다. 뽑은 뒤 남은 손패 1장을 덱 아래로 보낼 수 있습니다.',options:candidates.map(x=>({key:x.uid,label:`${cardText(x)}${x.named?` · ${x.name}`:''}`,detail:`보유 ${x.age}턴`,card:x})),allowSkip:true,skipLabel:'보내지 않기',onChoose:o=>{if(o?.card)bottom(o.card);resume()}});if(opened)return pause()}else bottom([...candidates].sort((a,b)=>b.age-a.age)[0])}}}break;case'smugglerBridge':break;case'gapRun':break;case'connectionLink':if(type==='RUN'&&ctx.isAttach){const paused=requestFreeRecoverChoice(w,ctx.meld,cards,{title:c.name,label:c.name,allowSkip:true,text:'이 RUN에서 무료 회수할 내 카드를 고르거나 건너뛸 수 있습니다.',onAsyncResolved:resume});if(paused)return pause()}break;case'branchLink':if(type==='RUN')runEffectAction('applyStatus',{actor:w},{scope:'meld',target:ctx.meld,key:'protect',amount:1,opts:{silent:true}});break;case'middleManager':break;case'parasite':break;case'copier':{const eligible=['emergencyGear'];if(type==='RUN'&&ctx.totalLength>=4)eligible.push('run4Draw');const prior=firstCopyEffectSource(cards,c,eligible);if(prior?.tag==='emergencyGear')addShield(w,5);else if(prior?.tag==='run4Draw')drawOne(w,false);break}case'cutLine':break;case'freeSwapRecover':if(ctx.isAttach&&ctx.targetOwner===w){const paused=requestFreeRecoverChoice(w,ctx.meld,cards,{title:c.name,label:c.name,allowReturnReuse:true,text:'갈아끼우기로 무료 회수할 내 카드를 고르세요.',onAsyncResolved:resume});if(paused)return pause()}break;case'flexRankCopy':break;case'sameMeldBonus':{const last=w==='player'?state.lastPlayerReturnType:state.lastEnemyReturnType;if(isReturning&&last&&last!==type)drawOne(w,false);else if(isReturning&&last===type)addShield(w,3);break}case'alternateBonus':break;case'jokerKing':break;case'jokerLast':break;case'jokerDual':if(type==='SET'&&ctx.isAttach&&ctx.totalLength===4)addShield(w,5);if(type==='RUN'&&ctx.isAttach){const paused=requestFreeRecoverChoice(w,ctx.meld,cards,{title:c.name,label:c.name,allowSkip:true,text:'쌍면 조커 효과로 무료 회수할 내 카드를 고르세요.',onAsyncResolved:resume});if(paused)return pause()}break;case'vacancyJoker':case'rebelJoker':break}}return{bonus:fx.bonus||0,flatReturn:!!fx.flatReturn,forceReturn:!!fx.forceReturn,pending:false}}'''
replace_top_function('resolveEffects',resolve)

submit=r'''function submitNewMeld(w,cards){const s=sideObj(w);if(s.newMeldUsed||cards.length!==3)return false;if(cards.some(c=>c.blockedUntilTurn===state.turnNo))return false;const type=meldType(cards);if(!type)return false;if(meldsOf(w).length>=2)return'full';if(!beforeNewMeld(w))return false;removeFromHand(w,cards);cards.forEach(c=>c.enteredMeldToken=state.turnToken);s.actedThisTurn=true;s.newMeldUsed=true;const m={type,cards:[...cards],chain:0,createdTurn:state.turnNo,createdToken:state.turnToken,lastAttachToken:null,extraAttachGrantedToken:null,lastTouchedOwnerStart:s.turnStarts,status:blankMeldStatus()};meldsOf(w).push(m);if(type==='RUN')for(const c of cards)if(c.tag==='smuggledSuit'&&c.smuggledTurnToken===state.turnToken)c.smuggledActive=true;if(cards.some(c=>c.tag==='extortion'))autoExtortToNewMeld(w,m);markSetCompletion(m,w);const ctx={isNew:true,isAttach:false,targetOwner:w,totalLength:3,effectSeen:new Set(),meld:m,willReturn:false};fieldAction(w,cards,type,ctx);let finished=false;const finish=fx=>{if(finished)return true;finished=true;characterActionBonus(w,cards,type,ctx);triggerOpponentHandTraps(w,cards);cards.forEach(c=>c.fromDiscard=false);if(w==='player')state.lastPlayerMeldType=type;else state.lastEnemyMeldType=type;log(`${w==='player'?'나':'상대'} ${type==='SET'?'세트':'런'} 3장 구축 · ${type==='SET'?'버스트 준비':'체인 0'}.`,'important');const willRummy=s.hand.length===0;if(willRummy&&!state.gameOver){triggerRummy(w,cards,{returned:false});return'rummy'}return true};ctx.resumeEffects=()=>{const next=resolveEffects(w,cards,type,ctx);if(next.pending)return'choice';const result=finish(next);if(w==='player'&&typeof render==='function')render();return result};const fx=resolveEffects(w,cards,type,ctx);if(fx.pending)return'choice';return finish(fx)}'''
replace_top_function('submitNewMeld',submit)

attach=r'''function attachCards(w,cards,targetSide,targetIndex){
  if(!cards.length||cards.some(c=>c.blockedUntilTurn===state.turnNo))return false;
  const s=sideObj(w),m=meldsOf(targetSide)[targetIndex];
  if(!m||(m.createdToken===state.turnToken&&targetSide===w))return false;
  const continuation=canContinueReturnedRun(w,m);
  if(m.lastAttachToken===state.turnToken&&!continuation)return false;
  const beforeLen=m.cards.length,beforeChain=m.chain||0,beforeCards=[...m.cards],combined=m.cards.concat(cards),type=meldType(combined);
  if(type!==m.type)return false;
  const willBaseReturn=type==='RUN'||(type==='SET'&&beforeLen===3&&combined.length===4);
  if(willBaseReturn&&!recoveredCardsCanReturn(cards,state.turnToken,m))return false;
  if(willBaseReturn&&!continuation&&!canSideReturn(w))return false;
  if(willBaseReturn&&!continuation&&s.returnedSwitchThisTurn)return false;
  removeFromHand(w,cards);
  cards.forEach(c=>c.enteredMeldToken=state.turnToken);
  s.actedThisTurn=true;
  m.cards.push(...cards);
  if(type==='RUN')for(const c of cards)if(c.tag==='smuggledSuit'&&c.smuggledTurnToken===state.turnToken)c.smuggledActive=true;
  m.lastAttachToken=state.turnToken;
  m.lastTouchedOwnerStart=sideObj(targetSide).turnStarts+(w===targetSide?0:1);
  markSetCompletion(m,targetSide);
  let base=0,label='붙이기';
  if(type==='SET'&&beforeLen===3&&m.cards.length===4){base=24;label='세트 버스트'}
  if(type==='RUN'){for(let i=1;i<=cards.length;i++)base+=chainDamage(beforeChain+i);m.chain=Math.min(4,beforeChain+cards.length);label=`런 체인 ${m.chain}`}
  const returning=base>0&&!continuation;
  const ctx={isNew:false,isAttach:true,targetOwner:targetSide,totalLength:m.cards.length,effectSeen:new Set(),meld:m,willReturn:returning};
  fieldAction(w,cards,type,ctx);
  let finished=false;
  const finish=fx=>{
    if(finished)return true;finished=true;
    characterActionBonus(w,cards,type,ctx);
    triggerOpponentHandTraps(w,cards);
    let finalBase=base,bonus=fx.bonus||0;
    if(state.pendingTrapReduction){finalBase=Math.max(0,finalBase-state.pendingTrapReduction);state.pendingTrapReduction=0}
    const forceReturn=!continuation&&!!fx.forceReturn;
    if(returning||forceReturn){
      if(w==='player')state.lastPlayerReturnType=type;else state.lastEnemyReturnType=type;
      attackEvent(w,finalBase?[{amount:finalBase,label,kind:type==='SET'?'burst':'chain'}]:[],{bonus,label,flatReturn:fx.flatReturn,forceReturn:true});
      m.returnAttachToken=state.turnToken;
      for(const pz of m.cards)if(pz.tag==='parasite'&&pz.owner!==w){drawOne(pz.owner,false);const ps=sideObj(pz.owner),dc=ps.hand.filter(x=>x.uid!==pz.uid).sort((a,b)=>b.age-a.age)[0];if(dc){removeFromHand(pz.owner,[dc]);pushDiscard(dc)}log(`${pz.name}: 상대가 기생 조합으로 반환해 원주인이 1장 순환.`,'good')}
    }else if(continuation&&finalBase>0){combatBanner(label,'chain',0);addSwitchPower(w,finalBase,`${label} · 연속 연장`,other(w));log(`${w==='player'?'나':'상대'} 같은 런 연속 연장 · 스위치 추가 이동 없이 체인 위력 +${finalBase}.`,'important')}
    cards.forEach(c=>c.fromDiscard=false);
    if(cards.some(c=>c.tag==='connectionLink')&&type==='RUN'&&m.extraAttachGrantedToken!==state.turnToken){m.extraAttachGrantedToken=state.turnToken;m.lastAttachToken=null}
    for(const c of cards)if(c.tag==='cutLine'&&targetSide===other(w))cutOppositeEnd(w,targetSide,m,c);
    recoverRedundantGapRun(targetSide,m,beforeCards,cards);
    middleManagerReturnPlaceholder(targetSide,m,cards);
    replaceRedundantJokers(targetSide,m,w,cards);
    const willRummy=s.hand.length===0;
    const actionNote=continuation?' · 연속 체인':returning||forceReturn?' · 스위치 반환':' · 구조 변경';
    log(`${w==='player'?'나':'상대'} ${targetSide===w?'내':'상대'} ${type==='SET'?'세트':'런'}에 ${cards.length}장 붙이기${actionNote}.`,'important');
    if(type==='SET'&&m.cards.length===4){const currentIndex=meldsOf(targetSide).indexOf(m);if(currentIndex>=0)retireMeld(targetSide,currentIndex,'버스트 후 4장 세트 자동 정리')}
    if(willRummy&&!state.gameOver){triggerRummy(w,cards,{returned:returning||forceReturn});return'rummy'}
    return true;
  };
  ctx.resumeEffects=()=>{const next=resolveEffects(w,cards,type,ctx);if(next.pending)return'choice';const result=finish(next);if(w==='player'&&typeof render==='function')render();return result};
  const fx=resolveEffects(w,cards,type,ctx);
  if(fx.pending)return'choice';
  return finish(fx);
}'''
replace_top_function('attachCards',attach)

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
anchor='- [x] Add a shared queued effect-choice modal and migrate Reserved Shipping plus Connector 6+ hand-bottom choice; optional Connector bottoming may be skipped while CPU resolution stays deterministic\n'
line='- [x] Make named effect choices resumable before attack/RUMMY finalization; Connector 6+ now preserves RUMMY timing, free-recovery effects select a legal owned card, and Recycler selects from spent cards\n'
if line not in r:
    if anchor not in r: raise SystemExit('missing roadmap choice anchor')
    r=r.replace(anchor,anchor+line,1)
road.write_text(r,encoding='utf-8')

t=Path('tests/named-choice-resume.mjs')
t.write_text(r'''import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function src(name){const start=script.indexOf(`function ${name}(`);if(start<0)throw new Error(`missing ${name}`);const end=script.indexOf('\nfunction ',start+1);return script.slice(start,end<0?script.length:end)}
const fx=src('resolveEffects'),attach=src('attachCards'),meld=src('submitNewMeld');
ok(fx.includes('ctx.fxState')&&fx.includes('pending:true'),'resolveEffects preserves resumable effect state and can pause');
ok(fx.includes('ctx.resumeEffects')||fx.includes('const resume=()=>'),'resumable effects retain an action continuation');
ok(attach.includes('if(fx.pending)return\'choice\'')&&attach.includes('ctx.resumeEffects'),'attach pauses before combat/RUMMY finalization and resumes later');
ok(meld.includes('if(fx.pending)return\'choice\'')&&meld.includes('ctx.resumeEffects'),'new meld pauses before RUMMY finalization and resumes later');
ok(fx.includes("case'run4Draw'")&&fx.includes('onChoose:o=>{if(o?.card)bottom(o.card);resume()}'),'Connector resumes the original action only after the optional bottom choice');
ok(attach.indexOf('const willRummy=s.hand.length===0')>attach.indexOf('ctx.resumeEffects'),'attach recalculates RUMMY only inside finalization after resumed choices');
for(const tag of ['discardPursuit','enemyAttachBonus','runHeal2','connectionLink','freeSwapRecover','jokerDual'])ok(fx.includes(`case'${tag}'`)&&fx.includes('requestFreeRecoverChoice'),`${tag} routes legal free recovery through shared choice handling`);
ok(script.includes('function freeRecoverCandidates(')&&script.includes('function recoverSpecificFromMeld('),'free recovery exposes legal-candidate and exact-card helpers');
ok(fx.includes("case'recycler'")&&fx.includes('requestSpentRecycleChoice'),'Recycler routes spent-card selection through shared choice handling');
ok(script.includes('function recycleSpecificSpentCard('),'Recycler can resolve the exact chosen spent card');
ok(road.includes('Make named effect choices resumable'),'roadmap records resumable named-choice timing');
console.log('M8 resumable named-choice regression passed.');
''',encoding='utf-8')
