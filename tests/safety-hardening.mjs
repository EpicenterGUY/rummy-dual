import {createStatusContext} from './helpers/status-fixture.mjs';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
function c(uid,owner='player',extra={}){return{uid,owner,suit:'C',rank:'4',age:0,...extra}}

{
 const player={hand:[]},enemy={hand:[]},state={player,enemy,turnToken:5};
 const ctx=createStatusContext(script,{console,Set,Math,state});ctx.sideObj=w=>w==='player'?player:enemy;ctx.isJoker=x=>x.suit==='J';ctx.meldType=cards=>cards.filter(x=>x.suit!=='J').length>=3?'RUN':null;ctx.markSetCompletion=()=>{};ctx.log=()=>{};install(ctx,'replaceRedundantJokers');
 const j=c('j','player',{suit:'J',tag:'vacancyJoker',name:'빈자리 조커'}),m={type:'RUN',chain:1,cards:[c('4'),c('5'),c('6'),j]};
 ctx.replaceRedundantJokers('player',m,'player',[j]);
 ok(m.cards.includes(j)&&player.hand.length===0,'newly attached vacancy Joker does not auto-recover itself');
 const real=c('7','player',{suit:'C',rank:'7'});m.cards.push(real);ctx.replaceRedundantJokers('player',m,'player',[real]);
 ok(!m.cards.includes(j)&&player.hand.includes(j),'pre-existing vacancy Joker can be replaced by a newly attached real card');
 ok(j.recoveredToken===state.turnToken&&j.recoverReturnOverrideToken==null,'auto-returned Joker is marked recovered and has no same-turn return override');
}

{
 const card={uid:'8',suit:'H',rank:'8',owner:'player',blockedUntilTurn:null,recoveredToken:null,recoverReturnOverrideToken:null};
 const player={hand:[card],deck:[c('d')],spent:[],melds:[],newMeldCount:0,returnedSwitchThisTurn:true,maintenanceUsed:false};
 const enemy={hand:[],deck:[],spent:[],melds:[],newMeldCount:0,returnedSwitchThisTurn:false};
 const m={type:'RUN',cards:[{suit:'H',rank:'5'},{suit:'H',rank:'6'},{suit:'H',rank:'7'}],chain:1,lastAttachToken:9,returnAttachToken:9,createdToken:null};enemy.melds=[m];
 const state={player,enemy,discard:[],turnNo:2,turnToken:9,switchTarget:'enemy',gameOver:false,turn:'player',phase:'action'};
 const ctx=createStatusContext(script,{console,Set,Map,Array,Math,state});ctx.sideObj=w=>w==='player'?player:enemy;ctx.other=w=>w==='player'?'enemy':'player';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=w=>state.switchTarget==='neutral'||state.switchTarget===w;ctx.canContinueReturnedRun=(w,x)=>w==='player'&&x===m;ctx.meldType=cards=>cards.every(x=>x.suit==='H')&&new Set(cards.map(x=>Number(x.rank))).size===cards.length?'RUN':null;ctx.meldFixedActive=()=>false;ctx.cardFixedActive=()=>false;install(ctx,'combinations','bestNewMeld','bestNewMeldForTurn','recoveredCardCanReturn','recoveredCardsCanReturn','anyAttachOption','canFinishRun','hasAnyLegalAction','ownedRecycleCount','maintenanceLimit');
 ok(ctx.anyAttachOption('player'),'same returned RUN continuation counts as a legal attach after physical SWITCH return');
 ok(ctx.maintenanceLimit('player')===1,'legal same-RUN continuation prevents false two-card stuck maintenance');
}

{
 const a={},b={},card={recoveredToken:3,recoverReturnOverrideToken:3,recoverReturnTargets:[b]};
 const ctx=createStatusContext(script,{console,Array});install(ctx,'recoveredCardCanReturn','recoveredCardsCanReturn');
 ok(!ctx.recoveredCardCanReturn(card,3,a),'destination-bound recovered card cannot return through an unauthorized meld');
 ok(ctx.recoveredCardCanReturn(card,3,b),'destination-bound recovered card may return through its authorized meld');
}

{
 const player={hand:[1,2,3],discardsRemaining:1},enemy={hand:[],discardsRemaining:1},state={player,enemy,sessionMode:'battle'};
 const ctx=createStatusContext(script,{console,state});ctx.sideObj=w=>w==='player'?player:enemy;install(ctx,'canSkipBaseDiscard');
 ok(ctx.canSkipBaseDiscard('player'),'1–3 card hand may waive the base discard');
 player.discardsRemaining=2;ok(!ctx.canSkipBaseDiscard('player'),'extra discard debt prevents low-hand waiver until paid');
 player.discardsRemaining=1;player.hand.push(4);ok(!ctx.canSkipBaseDiscard('player'),'four-card hand still owes the normal discard');
 player.hand=[1,2,3];state.sessionMode='tutorial';ok(!ctx.canSkipBaseDiscard('player'),'tutorial keeps its scripted discard step deterministic');
}

{
 const pCards=Array.from({length:7},(_,i)=>c(`p${i}`,'player'));
 const eCards=Array.from({length:7},(_,i)=>c(`e${i}`,'enemy'));
 const player={hand:[],deck:[],spent:[],melds:[{type:'RUN',cards:pCards}],cores:2,hp:37,shield:5};
 const enemy={hand:[],deck:[],spent:[],melds:[{type:'SET',cards:eCards}],cores:1,hp:44,shield:2};
 const state={player,enemy,discard:[],fullRecirculationCount:0,switchTarget:'player',switchPower:73,selected:new Set(),selectionOrder:[],boardSelected:new Set(),target:null,gameOver:false};
 const ctx=createStatusContext(script,{console,Set,Math,state});ctx.sideObj=w=>w==='player'?player:enemy;ctx.shuffle=x=>x;ctx.blankStatus=()=>({});ctx.drawMany=(w,n)=>{const s=ctx.sideObj(w);let k=0;while(k<n&&s.deck.length){s.hand.push(s.deck.pop());k++}return k};ctx.log=()=>{};ctx.combatBanner=()=>{};ctx.resolveCirculationStalemate=()=>{throw new Error('unexpected second stall')};install(ctx,'fullRecirculation');
 ctx.fullRecirculation('test');
 ok(player.hand.length===6&&enemy.hand.length===6&&player.deck.length===1&&enemy.deck.length===1,'full recirculation redeals up to six and leaves the remainder in each current owner deck');
 ok(player.melds.length===0&&enemy.melds.length===0&&state.discard.length===0,'full recirculation clears public melds and shared discard');
 ok(state.switchTarget==='player'&&state.switchPower===73&&player.cores===2&&player.hp===37&&player.shield===5,'full recirculation preserves SWITCH, CORE, HP and shield state');
 ok(state.fullRecirculationCount===1,'full recirculation is counted for second-stall protection');
}

ok(source('attachCards').includes('replaceRedundantJokers(targetSide,m,w,cards)'),'attach resolution passes current new cards into Joker replacement guard');
ok(source('recoverSpecificFromMeld').includes('grantRecoveryReturnOverride'),'free swap recovery records authorized return destinations on the exact chosen recovery');
ok(source('playerRecover').includes('ownOnly:true')&&source('executeRecoverAI').includes('ownOnly:true'),'Tuner recovery binds its exception to own opposite-type destination melds for player and AI');
ok(html.includes('저손패 보호')&&html.includes('전체 재순환'),'rules UI documents low-hand protection and full recirculation');
console.log('Safety hardening regression passed.');
