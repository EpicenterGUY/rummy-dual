import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');

function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const name of names)vm.runInContext(source(name),ctx)}
function card(owner='enemy',extra={}){return{uid:Math.random().toString(36),owner,themeId:null,...extra}}

new Function(script);
const eventsLine=script.match(/const EFFECT_EVENTS=Object\.freeze\(\[([^\]]+)\]\)/)?.[1]||'';
for(const ev of ['onClashSet','onClashClear','onClashMeldChange'])ok(eventsLine.includes(`'${ev}'`),`shared event vocabulary exposes ${ev}`);

// Core foundation: opponent-only assignment, one clash per actor, delayed release, and re-entry cancellation.
{
  const p1=card('player'),p2=card('player');
  const ownMeld={type:'SET',cards:[card('player'),card('player'),card('player')]};
  const m1={type:'RUN',cards:[card('enemy'),p1,card('enemy')]};
  const m2={type:'SET',cards:[card('enemy'),p2,card('enemy')]};
  const player={melds:[ownMeld],turnStarts:3};
  const enemy={melds:[m1,m2],turnStarts:4};
  const state={turnNo:10,turnToken:100,turn:'enemy',player,enemy};
  const events=[];
  const ctx=vm.createContext({console,Array,Object,Set,Math,state});
  ctx.sideObj=w=>w==='player'?player:enemy;
  ctx.other=w=>w==='player'?'enemy':'player';
  ctx.meldsOf=w=>ctx.sideObj(w).melds;
  ctx.emitEffectEvent=(event,payload={})=>{const packet={event,...payload};events.push(packet);return packet};
  ctx.log=()=>{};
  install(ctx,'meldOwnerSide','ensurePointBlankMeta','isPointBlankClash','pointBlankClashActors','pointBlankClashMeld','pointBlankOwnCardCount','emitPointBlankClashChange','clearPointBlankClash','clearPointBlankClashesOnMeld','refreshPointBlankClashMeld','setPointBlankClash','expirePointBlankClashAtTurnEnd');

  ok(ctx.setPointBlankClash('player',ownMeld)===false,'POINT-BLANK cannot designate its own public meld as a clash');
  ok(ctx.setPointBlankClash('player',m1)===true&&ctx.isPointBlankClash('player',m1),'player can designate an opponent public meld as a clash');
  ok(m1.themeMeta.pointBlank.releaseAtTurnEndStart.player===null,'a clash containing the actor’s card is stable with no release timer');
  events.length=0;
  ok(ctx.setPointBlankClash('player',m2)===true,'a new opponent meld can replace the current clash');
  ok(!ctx.isPointBlankClash('player',m1)&&ctx.isPointBlankClash('player',m2),'each actor keeps at most one POINT-BLANK clash');
  ok(events.some(e=>e.event==='onClashClear'&&e.reason==='relocate'&&e.nextMeld===m2),'clash relocation clears the old meld with the next destination snapshot');
  ok(events.some(e=>e.event==='onClashSet'&&e.previousMeld===m1),'clash relocation sets the new meld with the previous meld snapshot');

  // Lose the last friendly card during the opponent turn: release is deferred through the next player turn end.
  m2.cards=m2.cards.filter(c=>c.owner!=='player');
  events.length=0;
  ctx.refreshPointBlankClashMeld(m2,{change:'recover',actionActor:'enemy'});
  ok(m2.themeMeta.pointBlank.releaseAtTurnEndStart.player===4,'losing the final friendly card on the opponent turn schedules release for the next player turn end');
  ok(events.some(e=>e.event==='onClashMeldChange'&&e.change==='recover'&&e.ownCards===0),'clash change event exposes the newly unmanned state');
  ok(ctx.expirePointBlankClashAtTurnEnd('player')===false&&ctx.isPointBlankClash('player',m2),'clash does not expire before the scheduled owner turn starts');

  // Re-enter before that turn ends: pending release is cancelled.
  player.turnStarts=4;state.turn='player';m2.cards.push(card('player'));
  ctx.refreshPointBlankClashMeld(m2,{change:'attach',actionActor:'player'});
  ok(m2.themeMeta.pointBlank.releaseAtTurnEndStart.player===null,'re-entry before the deadline cancels delayed clash release');
  ok(ctx.expirePointBlankClashAtTurnEnd('player')===false&&ctx.isPointBlankClash('player',m2),'restabilized clash survives the owner turn end');

  // Lose all friendly cards again during the current player turn: this turn end is the next owner turn end.
  m2.cards=m2.cards.filter(c=>c.owner!=='player');
  ctx.refreshPointBlankClashMeld(m2,{change:'recover',actionActor:'player'});
  ok(m2.themeMeta.pointBlank.releaseAtTurnEndStart.player===4,'same-turn loss schedules the current owner turn end');
  events.length=0;
  ok(ctx.expirePointBlankClashAtTurnEnd('player')===true,'unmanned clash expires at the scheduled owner turn end');
  ok(!ctx.isPointBlankClash('player',m2),'delayed expiry removes clash metadata');
  ok(events.some(e=>e.event==='onClashClear'&&e.reason==='unmanned-turn-end'),'delayed expiry emits an explicit clash-clear reason');
}

// ZERO-SIGHT target and POINT-BLANK clash are independent metadata layers on the same meld.
{
  const mixed={type:'RUN',cards:[card('enemy'),card('player'),card('enemy')]};
  const player={melds:[],turnStarts:2},enemy={melds:[mixed],turnStarts:2};
  const state={turnNo:5,turnToken:50,turn:'player',player,enemy};
  const ctx=vm.createContext({console,Array,Object,Set,Math,state});
  ctx.sideObj=w=>w==='player'?player:enemy;
  ctx.other=w=>w==='player'?'enemy':'player';
  ctx.meldsOf=w=>ctx.sideObj(w).melds;
  ctx.emitEffectEvent=()=>({});ctx.log=()=>{};
  install(ctx,'meldOwnerSide','ensureMeldThemeMeta','isZeroSightTarget','zeroSightTargetMeld','clearZeroSightTarget','setZeroSightTarget','ensurePointBlankMeta','isPointBlankClash','pointBlankClashMeld','pointBlankOwnCardCount','clearPointBlankClash','refreshPointBlankClashMeld','setPointBlankClash');
  ok(ctx.setZeroSightTarget('player',mixed)&&ctx.setPointBlankClash('player',mixed),'one opponent meld can simultaneously be a ZERO-SIGHT target and POINT-BLANK clash');
  ctx.clearPointBlankClash('player',{silent:true});
  ok(ctx.isZeroSightTarget('player',mixed)&&!ctx.isPointBlankClash('player',mixed),'clearing POINT-BLANK clash never clears ZERO-SIGHT target metadata');
  ctx.setPointBlankClash('player',mixed,{silent:true});
  ctx.clearZeroSightTarget('player',{silent:true});
  ok(!ctx.isZeroSightTarget('player',mixed)&&ctx.isPointBlankClash('player',mixed),'clearing ZERO-SIGHT target never clears POINT-BLANK clash metadata');
}

// Existing public-meld mutation routes refresh the clash lifecycle without hard dependencies in isolated tests.
const recovery=source('emitRecoveryEvent');
ok(recovery.includes("typeof refreshPointBlankClashMeld==='function'")&&recovery.includes("change:'recover'"),'recovery refreshes POINT-BLANK clash stability');
const move=source('emitMeldMoveEvent');
ok(move.includes("change:'moveOut'")&&move.includes("change:'moveIn'"),'public-card movement refreshes both source and destination clash stability');
const attach=source('attachCards');
ok(attach.includes("refreshPointBlankClashMeld(m,{change:'attach'"),'ordinary attach resolution refreshes POINT-BLANK clash stability');
const retire=source('retireMeld');
ok(retire.includes("clearPointBlankClashesOnMeld(m,{reason:'retire'})"),'meld retirement clears POINT-BLANK clash before physical removal');
const turnEnd=source('turnEnd');
ok(turnEnd.includes("expirePointBlankClashAtTurnEnd==='function'"),'owner turn end resolves delayed POINT-BLANK release');
const setSource=source('setPointBlankClash');
ok(!setSource.includes('themeId')&&!setSource.includes("'point-blank'"),'clash assignment depends on board ownership, not card-theme membership');

ok(road.includes('- [x] 상대 공개 조합 단위 접전 메타데이터 / 1개 제한 / 지연 해제 구현'),'ROADMAP marks POINT-BLANK clash foundation complete');
ok(themeDoc.includes('- [x] 상대 공개 조합 단위 `접전` 메타데이터 설계'),'canonical theme doc marks clash metadata complete');
ok(themeDoc.includes('- [x] 접전 1개 제한 / 이전 / 아군 카드 부재 시 지연 해제 처리'),'canonical theme doc marks one-clash/delayed-release lifecycle complete');

console.log('POINT-BLANK clash metadata and delayed-release regression passed.');
