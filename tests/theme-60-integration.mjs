import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const plan=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function literal(name,next){const a=script.indexOf(`const ${name}=`),b=script.indexOf(next,a);if(a<0||b<0)throw Error(`missing ${name}`);return script.slice(a+`const ${name}=`.length,b).trim().replace(/;$/,'')}
const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math});
vm.runInContext(`globalThis.NAMED=${literal('NAMED','\nconst CHARACTERS=')}`,ctx);
const themeIds=['v-signal','zero-sight','point-blank'];
const cards=Object.entries(ctx.NAMED).filter(([,d])=>themeIds.includes(d?.themeId));
ok(cards.length===60,'three completed themes expose exactly 60 live card definitions');
ok(cards.every(([,d])=>d.rewardPool!==false),'all 60 completed theme cards are eligible for ordinary reward ranking once unlocked');
ok(!script.includes('allowStaged=')&&cards.every(([,d])=>d.rewardPool!==false),'completed theme cards remain unstaged without a scarce-pool bypass');
ok(script.includes("themeId:'point-blank',live:true"),'POINT-BLANK build profile is live');
for(const [id,step] of [['v-signal','vsEncore'],['zero-sight','zsObserver'],['point-blank','pbBreach']])ok(script.includes(`themeId:'${id}',startStep:'${step}',live:true`)&&script.includes(`id:'${step}',themeId:'${id}'`),`${id} has a live implemented theme experience`);
ok(html.includes('id="themeTutorialSelect"')&&script.includes("startThemeTutorial(document.getElementById('themeTutorialSelect')?.value||null)"),'menu exposes a real selector for all live theme experiences');
for(const marker of ["scenario==='zsObserver'","makeTutorialNamed('ZSCA','zsObserverCard')","scenario==='pbBreach'","makeTutorialNamed('PBHA','pbBreachCard')"])ok(script.includes(marker),`tutorial scenario wiring contains ${marker}`);
const neon=script.match(/'neon-arc':Object\.freeze\(\{[\s\S]*?named:Object\.freeze\(\[(.*?)\]\)\}\)/)?.[1]||'';
const red=script.match(/'red-zone':Object\.freeze\(\{[\s\S]*?named:Object\.freeze\(\[(.*?)\]\)\}\)/)?.[1]||'';
const ids=x=>[...x.matchAll(/'([^']+)'/g)].map(m=>m[1]);
const neonIds=ids(neon),redIds=ids(red);
ok(neonIds.length===12&&neonIds.every(id=>ctx.NAMED[id]?.themeId==='v-signal'),'NEON ARC 12-card encounter pool is a full V-SIGNAL showcase');
ok(redIds.length===12&&redIds.some(id=>ctx.NAMED[id]?.themeId==='zero-sight')&&redIds.some(id=>ctx.NAMED[id]?.themeId==='point-blank'),'RED ZONE 12-card encounter pool mixes ZERO-SIGHT and POINT-BLANK');
for(const [label,list] of [['neon',neonIds],['red',redIds]])ok(new Set(list.map(id=>ctx.NAMED[id]?.slot||id)).size===list.length,`${label} thematic encounter variants occupy unique physical slots`);
ok(road.includes('M8T — 기존 3테마 60장 통합 · 완료'),'ROADMAP closes the 60-card integration milestone');
ok(plan.includes('## 4. 60장 완성 후 통합 · 완료')&&plan.includes('60장 통합 밸런스/해금/로그라이크/튜토리얼 — 완료'),'canonical full-pool plan closes the integration phase');
console.log('Three-theme 60-card integration regression passed.');
