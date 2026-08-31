import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const theme=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

ok(script.includes('handPrep:{turns:0,exitTurns:0,exitTurnToken:null,exitOwner:null}'),'cards own separate handPrep metadata');
ok(script.includes('prepRequired:Math.max(0,Number(def?.prepRequired)||0)'),'named definitions can declare a preparation requirement');
ok(script.includes('function preparedTurnsAtUse'),'same-action preparation snapshot reader exists');
ok(script.includes('function handPreparationReady'),'shared ready predicate exists');
ok(source('turnEnd').includes("advanceHandPreparation(w)"),'owner turn end advances preparation once');
ok(source('renderHand').includes('handPrepTag')&&source('renderHand').includes('prepRequired'),'hand UI can display declared preparation progress');
ok(html.includes('.handPrepTag.ready'),'ready preparation marker has a visible state');

{
 const card={uid:1,prepRequired:2,handPrep:{turns:7,exitTurns:4,exitTurnToken:1,exitOwner:'enemy'}};
 const player={hand:[],deck:[],spent:[]},enemy={hand:[],deck:[],spent:[]};
 const state={turn:'player',turnToken:10,player,enemy};
 const box=context({state});
 box.sideObj=w=>w==='player'?player:enemy;
 install(box,'ensureHandPreparation','resetHandPreparation','enterHand','leaveHandPreparation','preparedTurnsAtUse','handPreparationReady','advanceHandPreparation','removeFromHand');
 box.enterHand('player',card);
 ok(card.handPrep.turns===0&&card.handPrep.exitTurnToken===null,'fresh hand entry resets prior preparation and exit snapshot');
 box.advanceHandPreparation('player');
 ok(card.handPrep.turns===1&&!box.handPreparationReady(card,2,'player'),'one completed owner turn gives one preparation only');
 box.advanceHandPreparation('player');
 ok(card.handPrep.turns===2&&box.handPreparationReady(card,2,'player'),'second completed owner turn reaches a two-turn requirement');
 box.removeFromHand('player',[card]);
 ok(player.hand.length===0&&card.handPrep.turns===0,'leaving hand immediately clears live preparation');
 ok(card.handPrep.exitTurns===2&&card.handPrep.exitTurnToken===10&&card.handPrep.exitOwner==='player','leave-hand action snapshots the exact preparation count');
 ok(box.preparedTurnsAtUse(card,'player')===2&&box.handPreparationReady(card,2,'player'),'same action can still read the preparation that existed at use');
 state.turnToken=11;
 ok(box.preparedTurnsAtUse(card,'player')===0&&!box.handPreparationReady(card,2,'player'),'exit snapshot expires after the action turn token changes');
 box.enterHand('player',card);
 box.advanceHandPreparation('enemy');
 ok(card.handPrep.turns===0,'opponent turn preparation advancement does not charge the player hand');
 box.advanceHandPreparation('player');
 ok(card.handPrep.turns===1,'re-entered card starts preparation again from zero');
}

{
 const card={uid:2,owner:'enemy',prepRequired:2,handPrep:{turns:2,exitTurns:2,exitTurnToken:5,exitOwner:'enemy'},contractActive:true,tag:null};
 const player={hand:[],deck:[],spent:[]},enemy={hand:[],deck:[],spent:[]};
 const state={turn:'player',turnToken:20,player,enemy,discard:[card]};
 const box=context({state});
 box.sideObj=w=>w==='player'?player:enemy;
 install(box,'ensureHandPreparation','resetHandPreparation','enterHand','acquireDiscardCard');
 const got=box.acquireDiscardCard('player',0);
 ok(got===card&&card.owner==='player'&&player.hand[0]===card,'discard acquisition still transfers ownership and enters hand');
 ok(card.handPrep.turns===0&&card.handPrep.exitTurnToken===null,'discard acquisition resets old-owner preparation history');
}

for(const name of ['recoverSpecificFromMeld','recoverRedundantGapRun','middleManagerReturnPlaceholder','replaceRedundantJokers','playerRecover','executeRecoverAI','turnStart','retireMeld']){
 const src=source(name);
 ok(src.includes('enterHand('),`${name} routes relevant hand returns through preparation reset`);
}
ok(source('fullRecirculation').includes('resetHandPreparation(c)'),'full recirculation clears card preparation metadata');
ok(road.includes('- [x] 손에서 턴 경과 충전 상태를 카드 단위 `handPrep` 마커로 구현'),'ROADMAP marks hand preparation foundation complete');
ok(theme.includes('준비는 공식 상태 5종이나 별도 전용 자원이 아니라 카드 단위 메타데이터'),'canonical theme doc separates preparation from official statuses/resources');
console.log('ZERO-SIGHT hand preparation regression passed.');
