import {fresh,named,plain,meld,run,nextTurn} from './helpers/v3-fixture.mjs';
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
const expected={ZSCA:'zsObserver',ZSC2:'zsScopeAdjust',ZSD2:'zsRangefinder',ZSH3:'zsBreathControl',ZSS4:'zsSuppressiveFire',ZSH4:'zsCamouflage',ZSC5:'zsBlindSpot',ZSD6:'zsBallistics',ZSC6:'zsObservationLog',ZSS7:'zsArmorPiercing',ZSH7:'zsSafeDistance',ZSC8:'zsObserverShift',ZSD8:'zsReserveMag',ZSS9:'zsCounterTrace',ZSS10:'zsLongShot',ZSCJ:'zsDrone',ZSSQ:'zsDeadAngle',ZSSK:'zsOneShot'};
const cards=Object.entries(ctx.NAMED).filter(([,d])=>d?.themeId==='zero-sight');
ok(cards.length===18,`ZERO-SIGHT full pool has exactly 18 definitions (${cards.length})`);
ok(new Set(cards.map(([,d])=>d.slot)).size===18,'ZERO-SIGHT cards occupy 18 distinct physical slots');
for(const[id,tag]of Object.entries(expected)){const d=ctx.NAMED[id];ok(!!d,`${id} definition exists`);ok(d.themeId==='zero-sight'&&d.t===tag,`${id} keeps ZERO-SIGHT tag ${tag}`);ok(d.rewardPool!==false,`${id} is eligible for ordinary roguelike rewards after 60-card integration`)}
ok(ctx.NAMED.ZSS10.prepRequired===2&&ctx.NAMED.ZSH3.prepRequired===1,'prepared ZERO-SIGHT cards declare shared handPrep requirements');
for(const tag of ['zsBreathControl','zsSuppressiveFire','zsCamouflage','zsBlindSpot','zsArmorPiercing','zsReserveMag','zsLongShot'])ok(script.includes(`case'${tag}'`),`${tag} has a live resolver branch`);
for(const tag of ['zsRangefinder','zsObservationLog','zsSafeDistance','zsObserverShift','zsCounterTrace','zsDrone','zsDeadAngle'])ok(script.includes(tag)&&script.includes('function handleZeroSightFullThemeEvent('),`${tag} is wired through the passive target-event handler`);
ok(script.includes('function requestZeroSightTopOrder(')&&script.includes('function requestZeroSightRetargetOnly('),'information and recovery target choices use shared resumable helpers');
ok(script.includes('subscribeEffectEvent(handleZeroSightFullThemeEvent);'),'ZERO-SIGHT passive effects subscribe to the shared event bus');
ok(script.includes('function prepareTargetReturnEffects('),'precision effects share the guarded return pipeline');
const unlock=script.slice(script.indexOf('const UNLOCK_GROUPS='),script.indexOf('function unlockedNamed'));
for(const id of Object.keys(expected))ok(unlock.includes(`'${id}'`),`${id} is reachable through progression unlock groups`);
ok(unlock.includes("items:['S6','H7','D8','C2','ZSCA','ZSC2','DA','D3']"),'existing ZERO-SIGHT starter timing stays untouched');
ok(unlock.includes("items:['ZSD6']")&&unlock.includes("items:['ZSSK']"),'Ballistics and ONE SHOT legacy unlock timings stay untouched');

// Counter Trace now grants shared loading; it survives the source leaving the board.
{
 const g=fresh(),trace=named(g,'ZSS9');meld(g,'player',[plain(g,'S',7),plain(g,'S',8),trace]);const target=run(g,'enemy','H',[3,4,5]);g.setZeroSightTarget('player',target);g.state.turn='enemy';g.state.switchTarget='enemy';
 const extra=plain(g,'H',6,'enemy');g.state.enemy.hand.push(extra);g.attachCards('enemy',[extra],'enemy',0);
 ok(g.state.player.status.loaded===12,'opponent target return grants loading 12');g.retireMeld('player',0);nextTurn(g);g.returnSwitch('player',10);ok(g.state.switchPower===52,'loading survives retirement and joins the next actual return');
}
// Long Shot uses shared hand preparation and consumes an owned mark to cleanse damping.
{
 const g=fresh(),c=named(g,'ZSS10'),target=run(g,'enemy','S',[7,8,9]);g.state.player.hand.push(c);g.setZeroSightTarget('player',target);g.applyOfficialStatus('meld',target,'mark',1,{actor:'player'});g.state.player.status.damp=8;g.advanceHandPreparation('player');g.advanceHandPreparation('player');g.attachCards('player',[c],'enemy',0);
 ok(g.state.switchPower===46,'prepared Long Shot loads 16 and cleanses damping 8 before returning');ok(g.meldMarkValue(target,'player')===0,'only its own mark is spent');
}

ok(!script.includes('zeroSightResource')&&!script.includes('ZERO_SIGHT_COUNT'),'ZERO-SIGHT adds no dedicated numeric resource');
ok(audit.includes("'zsArmorPiercing','zsCounterTrace','zsLongShot'"),'direct-power minority audit counts the new precision modifiers');
ok(theme.includes('ZERO-SIGHT 18/18 풀 카드군 라이브 구현'),'canonical theme document records full implementation');
ok(plan.includes('| ZERO-SIGHT | 18 | 18 | 0 | 18/18 |')&&plan.includes('- ZERO-SIGHT: **18/18 풀 구현 완료**'),'full-pool plan keeps ZERO-SIGHT at 18/18 after later theme integration');
ok(road.includes('ZERO-SIGHT 18/18 풀 카드군 구현'),'ROADMAP records ZERO-SIGHT completion');
console.log('ZERO-SIGHT 18/18 full-pool regression passed.');
