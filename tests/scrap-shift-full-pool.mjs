import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const doc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const plan=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,b=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){b=i;break}}if(b<0)throw new Error(`missing body ${name}`);let d=0;for(let i=b;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function literal(name,next){const a=script.indexOf(`const ${name}=`);if(a<0)throw new Error(`missing ${name}`);const b=script.indexOf(next,a);if(b<0)throw new Error(`missing end ${name}`);return script.slice(a+`const ${name}=`.length,b).trim().replace(/;$/,'')}

new Function(script);
const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math});
vm.runInContext(`globalThis.NAMED=${literal('NAMED','\nconst CHARACTERS=')}`,ctx);
const defs=Object.entries(ctx.NAMED).filter(([,d])=>d?.themeId==='scrap-shift');
ok(defs.length===24,`SCRAP-SHIFT live pool has exactly 24 definitions (${defs.length})`);
const slots=defs.map(([id,d])=>d.slot||id);
ok(new Set(slots).size===24,'SCRAP-SHIFT uses 24 distinct physical rank+suit slots');
for(const suit of ['S','H','D','C'])ok(slots.filter(x=>x[0]===suit).length===6,`SCRAP-SHIFT ${suit} suit has exactly six cards`);

const ids=[
 'SSDA','SSC2','SSH4','SSSA',
 'SSD3','SSC6','SSH6','SSS5',
 'SSD5','SSC4','SSH2','SSS10',
 'SSD7','SSC8','SSH8','SSS7',
 'SSD9','SSC10','SSH10','SSS3',
 'SSDJ','SSCQ','SSHK','SSSK'
];
for(const id of ids)ok(ctx.NAMED[id]?.themeId==='scrap-shift',`${id} is a live SCRAP-SHIFT definition`);

ok(script.includes("'scrap-shift':Object.freeze({id:'scrap-shift',name:'SCRAP-SHIFT',displayName:'SCRAP-SHIFT',concept:'부품 · 해체 · 이식 · 재조립',live:true})"),'theme registry marks SCRAP-SHIFT live');
ok(script.includes("'scrap-shift':Object.freeze({id:'scrap-shift',displayName:'SCRAP-SHIFT',short:'부품 순환'")&&script.includes("themeId:'scrap-shift',live:true"),'automatic theme build profile is live');
ok(script.includes("'scrap-shift':Object.freeze({themeId:'scrap-shift',startStep:'ssPartLabel',live:true})"),'SCRAP-SHIFT theme tutorial is live');
ok(script.includes("id:'ssPartLabel',themeId:'scrap-shift'")&&script.includes("completeOn:'partSet'"),'theme tutorial completes on an actual part designation');
ok(source('setScrapShiftPart').includes("tutorialCheckProgress('partSet'"),'shared part setter reports the tutorial milestone from the real effect path');
ok(html.includes('data-codex-filter="theme:scrap-shift">SCRAP-SHIFT</button>'),'card encyclopedia exposes the SCRAP-SHIFT tab in normal UI');

const unlockBlock=literal('UNLOCK_GROUPS','\nconst CHARACTER_UNLOCK=');
const unlockCtx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math,charLevel:()=>1,CHARACTERS:{}});
vm.runInContext(`globalThis.UNLOCK_GROUPS=${unlockBlock}`,unlockCtx);
const groups=Array.from(unlockCtx.UNLOCK_GROUPS).filter(g=>String(g.id).startsWith('ssf'));
ok(groups.length===6,'SCRAP-SHIFT uses six staged progression groups');
for(let i=1;i<=6;i++){
 const g=groups.find(x=>x.id===`ssf${i}`);
 ok(!!g&&g.items.length===4,`SCRAP-SHIFT unlock stage ${i} contains four cards`);
 ok(g.when({totalClears:i})===true&&g.when({totalClears:i-1})===false,`SCRAP-SHIFT unlock stage ${i} opens at exactly ${i} total clears`);
}
ok(new Set(groups.flatMap(g=>Array.from(g.items))).size===24,'six unlock stages cover all 24 SCRAP-SHIFT cards exactly once');
ok(source('themeBuildLockText').includes("id==='scrap-shift'")&&source('themeBuildLockText').includes('전체 1클리어부터'),'theme picker exposes the real first unlock condition');

ok(script.includes("id:'iron-grave'")&&script.includes("rewardThemes:Object.freeze(['scrap-shift'])"),'Iron Grave is the preferred live SCRAP-SHIFT region');
ok(script.includes("'scrap-shift':Object.freeze(['ssPartLabel','ssConveyor','ssRepairKit','ssDismantleDriver'])"),'roguelike new-theme entry recognizes the four foundation actions before payoff cards');
for(const tag of ['ssPartLabel','ssConveyor','ssRepairKit','ssDismantleDriver','ssSortingBench','ssMagnetRetriever','ssRefurbish','ssScrapRampage'])ok(script.includes(`${tag}:[`),`${tag} has build/reward tendency metadata`);

const resolver=source('resolveEffects');
for(const tag of ['ssPartLabel','ssConveyor','ssRepairKit','ssDismantleDriver','ssStandardSpec','ssTempWeld','ssMagnetRetriever','ssOverheatedPart','ssSpareScrew','ssExchangeSpec','ssAssemblyLine','ssScrapRampage'])ok(resolver.includes(`case'${tag}'`),`${tag} has a live resolver path`);
for(const tag of ['ssSortingBench','ssCompatPort','ssRegenWorkshop','ssDisposalOrder','ssBranchRail','ssModuleBus','ssMainFrame'])ok(source('handleScrapShiftThemeEvent').includes(tag),`${tag} remains wired through the shared SCRAP-SHIFT event handler`);
ok(source('resolveScrapShiftTurnStart').includes('ssSpareChassis'),'Spare Chassis remains wired through the owner turn-start lifecycle');
ok(source('noteScrapShiftPartSpent').includes('ssShredder'),'Shredder remains wired through the shared part-to-spent lifecycle hook');
ok(source('turnEnd').includes('resolveScrapShiftTheseus(w)'),'Theseus Frame remains in the shared end-turn path');
ok(source('insuranceBlocks').includes('scrapShiftBoltCutterProtect'),'Bolt Cutter remains in the shared hostile-interference path');
ok(source('triggerRummy').includes('requestScrapShiftRummyRefurbish'),'Refurbish remains in the shared RUMMY flow');

ok(!/scrap(?:Point|Count|Resource|Gauge)|고철\s*(?:포인트|점수|카운터)/i.test(source('setScrapShiftPart')+source('dismantleScrapShiftPart')+source('reassembleScrapShiftPart')+source('scrapShiftTurnActionState')),'SCRAP-SHIFT still creates no dedicated numeric resource after live promotion');
ok(resolver.includes("case'ssScrapRampage':if(isReturning&&scrapShiftRampageReady(w))fx.bonus+=14"),'Scrap Rampage is the narrow direct-return-power finisher');
ok(!source('scrapShiftTurnActionState').includes('grantExtraAttach')&&!source('requestScrapShiftAssemblyLineChoice').includes('grantExtraAttach'),'live SCRAP-SHIFT does not bypass the simplified one-base-attach contract');

ok(road.includes('## M8SS — SCRAP-SHIFT 24/24 풀 카드군 · 완료'),'ROADMAP marks the SCRAP-SHIFT milestone complete');
ok(road.includes('- [x] 해금·도감·자동 테마 빌드·체험전 연결 후 일반 보상 승격'),'ROADMAP closes the live integration gate');
ok(road.includes('- [x] SCRAP-SHIFT 단일/모든 2테마/일반 mixed + 전체 회귀'),'ROADMAP closes the composition/regression gate');
ok(doc.includes('정식 라이브 테마')&&doc.includes('24장 / 수트별 6장 전체 효과와 해금·도감·자동 빌드·체험전·로그라이크 일반 보상 연결까지 완료'),'canonical theme doc records full live integration');
ok(plan.includes('24/24 라이브 구현 완료'),'full-pool plan records the completed live SCRAP-SHIFT pool');

console.log('SCRAP-SHIFT 24/24 live full-pool regression passed.');
