import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync('index.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync('ROADMAP.md','utf8');
const themeDoc=fs.readFileSync('docs/THEME_GROUPS.md','utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}

ok(script.includes("displayName:'ZERO-SIGHT'")&&script.includes("displayName:'POINT-BLANK'"),'theme display names use hyphens');
ok(!script.includes('ZERO//SIGHT')&&!script.includes('POINT//BLANK'),'live UI/code contains no legacy slash theme names');
ok(themeDoc.includes('# ZERO-SIGHT')&&themeDoc.includes('# POINT-BLANK'),'canonical theme document uses hyphen names');
ok(!themeDoc.includes('ZERO//SIGHT')&&!themeDoc.includes('POINT//BLANK'),'canonical theme document contains no legacy slash names');
ok(road.includes('ZERO-SIGHT')&&road.includes('POINT-BLANK')&&!road.includes('ZERO//SIGHT')&&!road.includes('POINT//BLANK'),'roadmap uses canonical hyphen names');

const eventsLine=script.match(/const EFFECT_EVENTS=Object\.freeze\(\[([^\]]+)\]\)/)?.[1]||'';
for(const ev of ['onMeldMove','onTargetSet','onTargetClear','onTargetMeldChange'])ok(eventsLine.includes(`'${ev}'`),`shared event vocabulary exposes ${ev}`);

const funcs=['ensureMeldThemeMeta','isZeroSightTarget','zeroSightTargetActors','zeroSightTargetMeld','emitZeroSightTargetChange','clearZeroSightTarget','clearZeroSightTargetsOnMeld','setZeroSightTarget'];
const code=funcs.map(source).join('\n');
const events=[];
const p1={type:'SET',cards:[1,2,3]},p2={type:'RUN',cards:[1,2,3,4]},e1={type:'SET',cards:[1,2,3]};
const box={globalThis:null,state:{turnNo:9},meldsOf:s=>s==='player'?[p1,p2]:[e1],meldOwnerSide:m=>[p1,p2].includes(m)?'player':'enemy',emitEffectEvent:(event,payload)=>{events.push({event,...payload});return events.at(-1)},log:()=>{}};box.globalThis=box;
vm.runInNewContext(`${code};globalThis.__api={setZeroSightTarget,clearZeroSightTarget,clearZeroSightTargetsOnMeld,isZeroSightTarget,zeroSightTargetActors};`,box);
const api=box.__api;
ok(api.setZeroSightTarget('player',p1),'player can set a target');
ok(api.isZeroSightTarget('player',p1),'target metadata is active after set');
ok(events.at(-1).event==='onTargetSet'&&events.at(-1).previousMeld===null,'first target set emits onTargetSet');
api.setZeroSightTarget('player',p2);
ok(!api.isZeroSightTarget('player',p1)&&api.isZeroSightTarget('player',p2),'retarget keeps the one-target limit');
const recent=events.slice(-2);
ok(recent[0].event==='onTargetClear'&&recent[0].reason==='retarget'&&recent[0].nextMeld===p2,'retarget emits clear with next destination before new set');
ok(recent[1].event==='onTargetSet'&&recent[1].previousMeld===p1&&recent[1].reason==='retarget','retarget emits set with previous target snapshot');
api.setZeroSightTarget('enemy',p2);
ok(api.zeroSightTargetActors(p2).length===2,'both players can independently target the same meld');
const beforeRetireClear=events.length;
ok(api.clearZeroSightTargetsOnMeld(p2,{reason:'retire'})===2,'retiring a doubly targeted meld clears both target owners');
const clearEvents=events.slice(beforeRetireClear);
ok(clearEvents.length===2&&clearEvents.every(x=>x.event==='onTargetClear'&&x.reason==='retire'),'retire clear emits one target-clear event per target owner');
ok(api.zeroSightTargetActors(p2).length===0,'retire clear removes target metadata after events');

const targetChange=source('emitZeroSightTargetChange');
ok(!targetChange.includes('themeId')&&!targetChange.includes("'zero-sight'"),'target interaction events do not require the acting card to belong to ZERO-SIGHT');
const recovery=source('emitRecoveryEvent');
ok(recovery.includes("emitEffectEvent('onRecover'")&&recovery.includes('targetedBy'),'recovery packet carries a target-owner snapshot');
ok(recovery.includes("emitZeroSightTargetChange('recover'"),'recovery from a target meld emits target-meld change');
const move=source('emitMeldMoveEvent');
ok(move.includes("emitEffectEvent('onMeldMove'")&&move.includes('sourceTargetedBy')&&move.includes('targetTargetedBy'),'public-to-public move event snapshots both source and destination target state');
ok(move.includes("emitZeroSightTargetChange('moveOut'")&&move.includes("emitZeroSightTargetChange('moveIn'"),'public move emits target reactions on either targeted endpoint');
const extort=source('moveExtortedCard');
ok(extort.includes("emitMeldMoveEvent(w,c,om,m,{reason:'extortion'})"),'existing Extortion movement is routed through the shared meld-move event');
const newMeld=source('submitNewMeld');
ok(newMeld.includes("emitEffectEvent('onMeldCreate'")&&newMeld.includes('targetedBy'),'new meld creation remains a generic shared event with target snapshot');
const attach=source('attachCards');
ok(attach.includes("emitEffectEvent('onAttach'")&&attach.includes('targetedBy'),'attach packet carries current target owners');
ok(attach.includes("emitZeroSightTargetChange('attach'"),'any card attaching to a targeted meld emits the target reaction');
const retire=source('retireMeld');
const iRet=retire.indexOf("emitEffectEvent('onRetire'"),iChange=retire.indexOf("emitZeroSightTargetChange('retire'"),iClear=retire.indexOf('clearZeroSightTargetsOnMeld'),iRemove=retire.indexOf('arr.splice(index,1)');
ok(iRet>=0&&iChange>iRet&&iClear>iChange&&iRemove>iClear,'retirement exposes target state, emits target reaction/clear, then physically removes the meld');
ok(retire.includes('targetedBy'),'onRetire carries an immutable target-owner snapshot');

ok(road.includes('- [x] 표적 조합 회수/이동/새 조합 생성 반응 이벤트 정리'),'roadmap marks ZERO-SIGHT target reaction events complete');
ok(themeDoc.includes('`onTargetSet` / `onTargetClear` / `onTargetMeldChange` / `onMeldMove`'),'canonical theme doc records the target event contract');
ok(themeDoc.includes('카드군 검사 없이 `targetedBy`'),'theme doc explicitly keeps target rewards open to ordinary/mixed cards');
console.log('ZERO-SIGHT naming + target reaction event regression passed.');
