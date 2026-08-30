import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const roadmap=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(c,m){if(!c)throw new Error(m);console.log(`PASS: ${m}`)}
function functionSource(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;let depth=0,end=-1;for(let i=brace;i<script.length;i++){if(script[i]==='{')depth++;else if(script[i]==='}'){depth--;if(depth===0){end=i+1;break}}}if(end<0)throw new Error(`unterminated ${name}`);return script.slice(start,end)}
function install(ctx,...names){for(const n of names)vm.runInContext(functionSource(n),ctx)}
new Function(script);
ok(script.includes("id:'detonate'")&&script.includes("scenario:'detonate'")&&script.includes("expectPower:40")&&script.includes("expectShieldAbsorb:8")&&script.includes("expectCoreBreak:true")&&script.includes("expectReset:true")&&script.includes("completeOn:'detonate'"),'detonation lesson is deterministic and validates the resolved bomb result');
ok(script.includes("makeTutorialCard('S','5','detonateEnd')")&&script.includes("p.hp=24;p.shield=8;p.cores=3;state.switchTarget='player';state.switchPower=40"),'detonation scenario fixes shield, current CORE HP and accumulated power');
ok(script.indexOf("id:'switch'")<script.indexOf("id:'detonate'")&&script.indexOf("id:'detonate'")<script.indexOf("id:'rummy'"),'detonation lesson sits between SWITCH and final RUMMY lesson');
ok(script.includes("tutorialCheckProgress('detonate',{beforePower:tutorialBefore.power")&&script.includes("afterPower:state.switchPower,afterTarget:state.switchTarget"),'real detonate path reports its final combat state to tutorial progress');

// Execute the actual detonate/damage/coreBreak path and verify the tutorial hook receives the real result.
{
 const player={hp:24,maxHp:60,shield:8,cores:3,graceArmed:false,status:{vulnerable:0},hand:[],melds:[{type:'RUN',chain:2}]};
 const enemy={hp:60,maxHp:60,shield:0,cores:3,graceArmed:false,status:{vulnerable:0},hand:[],melds:[]};
 const state={player,enemy,switchPower:40,switchTarget:'player',lastSwitchAdd:0,lastSwitchActor:null,fuseUsed:false,gameOver:false};
 let hook=null;
 const ctx=vm.createContext({console,Math,CORE_COUNT:3,state});
 ctx.sideObj=w=>w==='player'?player:enemy;ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.switchName=w=>w==='player'?'나':'상대';ctx.log=()=>{};ctx.fxNode=()=>{};ctx.combatBanner=()=>{};ctx.pulsePanel=()=>{};ctx.checkGameOver=()=>{};ctx.officialStatusValue=(scope,target,key)=>target?.status?.[key]||0;ctx.clearOfficialStatus=(scope,target,key)=>{const n=target?.status?.[key]||0;if(target?.status)target.status[key]=0;return n};ctx.tutorialCheckProgress=(event,data)=>{hook={event,data};return true};
 install(ctx,'resetAllChains','resetBombCycle','coreBreak','damage','detonate');
 const dealt=ctx.detonate('player','턴 종료');
 ok(dealt===24,'actual detonate applies shield first and deals only current CORE HP');
 ok(player.cores===2&&player.hp===60,'actual core break opens exactly one fresh 60/60 CORE');
 ok(state.switchPower===0&&state.switchTarget==='neutral','actual core break resets the SWITCH bomb to neutral');
 ok(hook?.event==='detonate'&&hook.data.beforePower===40&&hook.data.beforeShield===8&&hook.data.afterShield===0&&hook.data.beforeCores===3&&hook.data.afterCores===2&&hook.data.dealt===24&&hook.data.afterHp===60,'tutorial hook receives the real shield/core/reset result');
}

// Execute tutorial validation itself: only the exact resolved result advances.
{
 const step={id:'detonate',title:'폭발과 코어',implemented:true,completeOn:'detonate',expectPower:40,expectShieldAbsorb:8,expectCoreBreak:true,expectNextCoreHp:60,expectReset:true};
 const next={id:'rummy',implemented:true};
 const state={sessionMode:'tutorial',tutorialStep:'detonate',tutorialHintOpen:false,tutorialSuccessText:'',battleId:1};
 const progress={tutorialPromptSeen:true,tutorialCompleted:false};
 const ctx=vm.createContext({console,Math,CORE_HP:60,state,progress,TUTORIAL_STEPS:[step,next],setTimeout:()=>0});
 ctx.currentTutorialStep=()=>step;ctx.tutorialStepIndex=()=>0;ctx.log=()=>{};ctx.render=()=>{};ctx.renderTutorialCoach=()=>{};ctx.saveProgress=()=>{};ctx.setTutorialStep=()=>{};
 install(ctx,'tutorialCheckProgress');
 const good={beforePower:40,beforeShield:8,afterShield:0,beforeHp:24,afterHp:60,beforeCores:3,afterCores:2,dealt:24,afterPower:0,afterTarget:'neutral'};
 ok(ctx.tutorialCheckProgress('detonate',good)===true,'tutorial advances on the exact real detonation result');
 ok(state.tutorialSuccessText.includes('보호막 8 흡수')&&state.tutorialSuccessText.includes('현재 코어 24 피해·파괴'),'tutorial success copy emphasizes shield absorption and current CORE break');
 state.tutorialSuccessText='';
 ok(ctx.tutorialCheckProgress('detonate',{...good,afterCores:3})===false,'tutorial rejects a detonation result that did not actually break the CORE');
}

ok(roadmap.includes('- [x] 누적 위력 / 폭발 튜토리얼')&&roadmap.includes('- [x] 폭발 연출 및 현재 코어 피해 결과 강조'),'UX1 P2 roadmap records detonation/result-emphasis completion');
console.log('RUMMY//DUEL deterministic detonation tutorial regressions passed.');
