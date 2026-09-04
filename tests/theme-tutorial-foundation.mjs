import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
new Function(script);
ok(html.includes('id="themeTutorialBtn"')&&html.includes('테마 체험전 · 준비 중'),'tutorial submenu has a dedicated theme experience entry point');
ok(script.includes("'zero-sight':Object.freeze({themeId:'zero-sight',startStep:'zsObserver',live:true})")&&script.includes("'point-blank':Object.freeze({themeId:'point-blank',startStep:'pbBreach',live:true})")&&script.includes("'scrap-shift':Object.freeze({themeId:'scrap-shift',startStep:'ssPartLabel',live:true})")&&script.includes("'twelve-bloom':Object.freeze({themeId:'twelve-bloom',startStep:'tbSeasonMatch',live:true})"),'completed ZERO-SIGHT, POINT-BLANK, SCRAP-SHIFT, and TWELVE-BLOOM experiences are live');
ok(script.includes('tutorialThemeId:null'),'tutorial state tracks the active theme independently from battle deck theme');
ok(script.includes('function themeTutorialAvailable(id)')&&script.includes('function availableThemeTutorials()')&&script.includes('function startThemeTutorial(themeId=null)'),'theme tutorial availability and launcher helpers exist');
ok(script.includes("p.tutorialCompleted&&available.length>0")&&script.includes("테마 체험전 · 기본 완료 후"),'start entry requires base tutorial completion and at least one live registered experience');
ok(script.includes("if(step?.themeId){const themeSteps=TUTORIAL_STEPS.filter")&&script.includes("label:`${themeDef(step.themeId)?.displayName||step.themeId} 체험`"),'tutorial coach can render an isolated theme-specific segment counter');
ok(script.includes("step.themeId?`${themeDef(step.themeId)?.displayName||step.themeId} 체험 완료 · 메인으로`"),'theme segment has its own completion copy');
ok(html.includes('id="themeTutorialSelect"')&&script.includes("startThemeTutorial(document.getElementById('themeTutorialSelect')?.value||null)"),'theme tutorial menu can launch each selected live experience');

// Foundation must reject unavailable experiences rather than silently falling into a normal tutorial.
{
 const logs=[];
 const ctx=vm.createContext({console,Object,Array});
 ctx.THEME_TUTORIALS={'v-signal':{themeId:'v-signal',startStep:null,live:false}};
 ctx.TUTORIAL_STEPS=[];
 ctx.progress={tutorialCompleted:true};
 ctx.log=m=>logs.push(m);
 ctx.renderStartScreen=()=>{};
 ctx.startTutorial=()=>{throw new Error('unavailable theme tutorial must not start')};
 vm.runInContext(source('themeTutorialDef'),ctx);
 vm.runInContext(source('themeTutorialAvailable'),ctx);
 vm.runInContext(source('availableThemeTutorials'),ctx);
 vm.runInContext(source('startThemeTutorial'),ctx);
 ok(ctx.themeTutorialAvailable('v-signal')===false,'registry entry with no live start step stays unavailable');
 ok(ctx.startThemeTutorial('v-signal')===false&&logs.some(x=>x.includes('아직 없습니다')),'launcher cleanly rejects a non-live theme experience');
}

ok(road.includes('- [x] 테마군 튜토리얼 기반 — `THEME_TUTORIALS` 레지스트리'),'ROADMAP marks the reusable theme tutorial foundation complete');
console.log('Theme tutorial foundation regression passed.');
