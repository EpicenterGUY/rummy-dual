import fs from 'node:fs';
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
  const fallback=card('H','Q',{tag:'flexSuit'});ctx.recordFlexibleSuitRoles({type:'RUN',cards:[card('C',10,{tag:'smugglerBridge'}),fallback,card('D','J',{tag:'smuggledSuit'})]});
  ok(fallback.flexSuitOffSuit===true,'Understudy mirrors RUN target-suit fallback when every real card is suit-flexible');
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
