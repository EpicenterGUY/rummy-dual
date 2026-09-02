import {makeGame} from './helpers/live-game.mjs';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const plan=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
const theme=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const audit=fs.readFileSync(new URL('named-card-audit.mjs',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function literal(name,next){const a=script.indexOf(`const ${name}=`);if(a<0)throw new Error(`missing ${name}`);const b=script.indexOf(next,a);if(b<0)throw new Error(`missing end ${name}`);return script.slice(a+`const ${name}=`.length,b).trim().replace(/;$/,'')}
const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math});
vm.runInContext(`globalThis.NAMED=${literal('NAMED','\nconst CHARACTERS=')}`,ctx);
const expected={PBCA:'pbBreachOrder',PBHA:'pbBreachShield',PBC2:'pbSlideStep',PBH2:'pbSidearm',PBS3:'pbFlashbang',PBS4:'pbBuckshot',PBD4:'pbCrossfire',PBC5:'pbDoorKick',PBD6:'pbReload',PBH6:'pbEmergencyRetreat',PBH7:'pbCoverSwap',PBS8:'pbZeroRange',PBC8:'pbBackdoor',PBC9:'pbRoomClear',PBH10:'pbAdrenaline',PBDJ:'pbQuickReload',PBCQ:'pbBreachLeader',PBSK:'pbMagDump'};
const cards=Object.entries(ctx.NAMED).filter(([,d])=>d?.themeId==='point-blank');
ok(cards.length===18,`POINT-BLANK full pool has exactly 18 definitions (${cards.length})`);
ok(new Set(cards.map(([,d])=>d.slot)).size===18,'POINT-BLANK cards occupy 18 distinct physical slots');
for(const[id,tag]of Object.entries(expected)){const d=ctx.NAMED[id];ok(!!d,`${id} definition exists`);ok(d.themeId==='point-blank'&&d.t===tag,`${id} keeps POINT-BLANK tag ${tag}`);ok(d.rewardPool!==false,`${id} is eligible for ordinary roguelike rewards after 60-card integration`)}
ok(script.includes("'PBH7':{slot:'H7',themeId:'point-blank',n:'엄폐 교대',t:'pbCoverSwap'")&&script.includes("'PBDJ':{slot:'DJ',themeId:'point-blank',n:'퀵 리로드',t:'pbQuickReload'"),'existing Cover Swap and Quick Reload live definitions remain unchanged');
ok(!script.includes("pbCoverSwap:['interact','sustain','control']")&&!script.includes("pbQuickReload:['recover','combo','sustain']"),'full-pool expansion preserves legacy PBH7/PBDJ roguelike scoring metadata');
for(const tag of ['pbBreachOrder','pbBreachShield','pbSlideStep','pbFlashbang','pbBuckshot','pbCrossfire','pbDoorKick','pbReload','pbEmergencyRetreat','pbZeroRange','pbBackdoor','pbRoomClear','pbAdrenaline','pbBreachLeader','pbMagDump'])ok(script.includes(`case'${tag}'`),`${tag} has a live resolver branch`);
ok(script.includes('function handlePointBlankFullThemeEvent(')&&script.includes('subscribeEffectEvent(handlePointBlankFullThemeEvent);'),'Sidearm/action/leader reactions use the shared event bus');
for(const fn of ['notePointBlankTurnAction','pointBlankTurnActions','requestPointBlankSidearmChoice','requestPointBlankBackdoorChoice','requestPointBlankRoomClearChoice','requestPointBlankLeaderReward','resolvePointBlankPostReturn'])ok(script.includes(`function ${fn}(`),`${fn} helper exists`);
const moveFns=source('requestPointBlankBackdoorChoice')+source('executePointBlankRoomClear');
ok(moveFns.includes('moveCardBetweenMelds')&&!moveFns.includes('addSwitchPower')&&!moveFns.includes('returnSwitch'),'Backdoor and Room Clear route through the combat-neutral movement primitive only');
const post=source('resolvePointBlankPostReturn');
ok(post.includes('spendPointBlankMeldCard')&&!post.includes('returnSwitch')&&!post.includes('addSwitchPower'),'Zero Range pays its RUN cost after return without a second combat event');
const unlock=script.slice(script.indexOf('const UNLOCK_GROUPS='),script.indexOf('function unlockedNamed'));
for(const id of Object.keys(expected))ok(unlock.includes(`'${id}'`),`${id} is reachable through progression unlock groups`);

// Common-event history is boolean and resets by turn token rather than growing a resource.
{
 const f1=source('pointBlankBlankActions'),f2=source('pointBlankTurnActions'),f3=source('notePointBlankTurnAction'),f4=source('pointBlankDistinctActionCount');
 const player={},state={turnToken:5,player,enemy:{}};const box={globalThis:null,state,sideObj:w=>w==='player'?player:state.enemy,Object};box.globalThis=box;
 vm.runInNewContext(`${f1};${f2};${f3};${f4};globalThis.note=notePointBlankTurnAction;globalThis.get=pointBlankTurnActions;globalThis.count=pointBlankDistinctActionCount;`,box);
 box.note('player','attach');box.note('player','recover');ok(box.count('player')===2&&box.get('player').attach&&box.get('player').recover,'two distinct common actions are recorded for Reload/Mag Dump');
 state.turnToken=6;ok(box.count('player')===0,'POINT-BLANK action history naturally expires on the next turn token');
}

// Buckshot differentiates solo entry from an already-established own presence.
{
 const resolve=source('resolveEffects');
 const base={turnToken:8,switchPower:20};
 function run(meld,cards){const g=makeGame();meld.type='RUN';meld.status=g.blankMeldStatus();g.state.enemy.melds=[meld];g.setPointBlankClash('player',meld);g.resolveEffects('player',cards,'RUN',{meld,effectSeen:new Set(),willReturn:true,isAttach:true,targetOwner:'enemy',totalLength:4});return {loaded:g.state.player.status.loaded}}

 const buck={uid:'b',owner:'player',named:true,tag:'pbBuckshot',name:'벅샷'};
 ok(run({cards:[buck,{uid:'e1',owner:'enemy'},{uid:'e2',owner:'enemy'}]},[buck]).loaded===8,'Buckshot loads 8 when it is the only owned card in the clash action');
 const ally={uid:'a',owner:'player'};ok(run({cards:[buck,ally,{uid:'e',owner:'enemy'}]},[buck]).loaded===12,'Buckshot loads 12 when another owned card already occupies the clash');
}

ok(!script.includes('pointBlankCount')&&!script.includes('POINT_BLANK_COUNT')&&!script.includes('pointBlankResource'),'POINT-BLANK creates no dedicated numeric resource');
ok(audit.includes("'pbBuckshot','pbZeroRange','pbMagDump'"),'direct-power minority audit counts only the three new PB precision finishers');
ok(theme.includes('POINT-BLANK 18/18 풀 카드군 라이브 구현'),'canonical theme document records full implementation');
ok(plan.includes('| POINT-BLANK | 18 | 18 | 0 | 18/18 |')&&plan.includes('| **합계** | **60** | **60** | **0** |'),'full-pool plan reaches 60/60 individually implemented cards');
ok(road.includes('POINT-BLANK 18/18 풀 카드군 구현'),'ROADMAP records POINT-BLANK completion');
console.log('POINT-BLANK 18/18 full-pool regression passed.');
