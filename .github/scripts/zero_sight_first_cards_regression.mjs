import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync('index.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync('ROADMAP.md','utf8');
const themeDoc=fs.readFileSync('docs/THEME_GROUPS.md','utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}

ok(script.includes("'ZSCA':{slot:'CA',themeId:'zero-sight',n:'관측수',t:'zsObserver'"),'A clubs Observer is a ZERO-SIGHT CA-slot variant');
ok(script.includes("'ZSH3':{slot:'H3',themeId:'zero-sight',prepRequired:2,n:'호흡 조절',t:'zsBreathControl'"),'3 hearts Breath Control is a 2-turn prepared ZERO-SIGHT variant');
ok(script.includes("'ZSS4':{slot:'S4',themeId:'zero-sight',n:'제압 사격',t:'zsSuppressingFire'"),'4 spades Suppressing Fire is a ZERO-SIGHT S4-slot variant');
ok(script.includes("'zero-sight':Object.freeze({id:'zero-sight',displayName:'ZERO-SIGHT'")&&script.includes("themeId:'zero-sight',live:true"),'ZERO-SIGHT build profile is live');
ok(script.includes("items:['S8','H5','VSH5','ZSCA'")&&script.includes("'H3','ZSH3'")&&script.includes("'S4','ZSS4'"),'first three ZERO-SIGHT cards have staged unlocks');
ok(source('themeBuildLockText').includes("id==='zero-sight'")&&source('themeBuildLockText').includes('전체 2클리어부터'),'ZERO-SIGHT picker unlock text starts from total clear 2');

const targetAgeCode=['ensureMeldThemeMeta','isZeroSightTarget','zeroSightTargetMeld','zeroSightTargetAge'].map(source).join('\n');
const targetMeld={type:'SET',cards:[],themeMeta:{zeroSight:{targetedBy:{player:true,enemy:false},targetedTurn:{player:5,enemy:null}}}};
const ageBox={globalThis:null,state:{turnNo:7},meldsOf:s=>s==='player'?[targetMeld]:[]};ageBox.globalThis=ageBox;
vm.runInNewContext(`${targetAgeCode};globalThis.__age=zeroSightTargetAge('player');`,ageBox);
ok(ageBox.__age===2,'target age counts uninterrupted turns since the current target was set');
targetMeld.themeMeta.zeroSight.targetedTurn.player=6;
vm.runInNewContext(`${targetAgeCode};globalThis.__age2=zeroSightTargetAge('player');`,ageBox);
ok(ageBox.__age2===1,'retargeted metadata resets target age');

const grant=source('grantFreeMaintenance'),limit=source('maintenanceLimit'),perform=source('performMaintenance');
const side={hand:[{uid:1}],freeMaintenanceCharges:0,maintenanceUsed:false};
const maintBox={globalThis:null,sideObj:()=>side,ownedRecycleCount:()=>5,hasAnyLegalAction:()=>true,log:()=>{}};maintBox.globalThis=maintBox;
vm.runInNewContext(`${grant};${limit};globalThis.__api={grantFreeMaintenance,maintenanceLimit};`,maintBox);
maintBox.__api.grantFreeMaintenance('player',1,'test');
ok(side.freeMaintenanceCharges===1&&maintBox.__api.maintenanceLimit('player')===1,'free maintenance charge creates a one-card maintenance opportunity');
side.maintenanceUsed=true;
ok(maintBox.__api.maintenanceLimit('player')===1,'free maintenance remains available after normal maintenance was used');
side.freeMaintenanceCharges=0;
ok(maintBox.__api.maintenanceLimit('player')===0,'used normal maintenance blocks maintenance when no free charge remains');
ok(perform.includes("if(free)s.freeMaintenanceCharges=Math.max(0,(s.freeMaintenanceCharges||0)-1);else s.maintenanceUsed=true"),'free maintenance consumes its own charge instead of the normal maintenance flag');
ok(source('turnStart').includes('s.freeMaintenanceCharges=0'),'unused free maintenance expires at owner turn start');

const suppression=source('requestZeroSightSuppressionChoice');
let pending=null,seal=0,fixed=0,resumed=null;
const suppressBox={globalThis:null,state:{turn:'player'},requestEffectChoice:q=>{pending=q;return true},applyOfficialStatus:(scope,m,key)=>{if(scope==='meld'&&key==='seal')seal++},applyMeldFixed:()=>{fixed++;return true},other:w=>w==='player'?'enemy':'player',log:()=>{}};suppressBox.globalThis=suppressBox;
vm.runInNewContext(`${suppression};globalThis.__s=requestZeroSightSuppressionChoice;`,suppressBox);
const dummy={type:'RUN',cards:[]};
ok(suppressBox.__s('player',dummy,x=>resumed=x)===true&&pending?.options?.length===2,'player Suppressing Fire pauses for seal/fixed choice');
pending.onChoose({key:'seal'});
ok(seal===1&&fixed===0&&resumed==='seal','player can choose seal and resume the effect chain once');
suppressBox.state.turn='enemy';pending=null;resumed=null;
ok(suppressBox.__s('enemy',dummy,x=>resumed=x)===false&&fixed===1&&resumed==='fixed','CPU deterministically chooses fixed without opening a modal');

const effects=source('resolveEffects');
ok(effects.includes("case'zsObserver'")&&effects.includes("setZeroSightTarget(w,ctx.meld)")&&effects.includes("grantFreeMaintenance(w,1,c.name)"),'Observer targets its entered meld and grants free maintenance');
ok(effects.includes("case'zsBreathControl'")&&effects.includes("handPreparationReady(c,2,w)")&&effects.includes("zeroSightTargetAge(w)")&&effects.includes('addShield(w,4)'),'Breath Control requires hand preparation plus 2-turn target age and grants shield 16');
ok(effects.includes("case'zsSuppressingFire'")&&effects.includes("ctx.targetOwner===foe")&&effects.includes("isZeroSightTarget(w,ctx.meld)")&&effects.includes('requestZeroSightSuppressionChoice'),'Suppressing Fire only reacts on the owner’s targeted opposing meld');

ok(road.includes('A♣ `관측수` / 3♥ `호흡 조절` / 4♠ `제압 사격` 라이브 구현'),'roadmap records first ZERO-SIGHT live cards');
ok(road.includes('ZERO-SIGHT 캐릭터군 선택 라이브 전환'),'roadmap records live ZERO-SIGHT build selection');
ok(themeDoc.includes('무료 정비를 일반 정비와 분리된 턴 내 1회권'),'theme design records free-maintenance semantics');
ok(!script.includes('ZERO//SIGHT')&&!script.includes('POINT//BLANK'),'canonical hyphen theme naming remains intact');
console.log('ZERO-SIGHT first live cards regression passed.');
