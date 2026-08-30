from pathlib import Path

p=Path('index.html')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing pattern: {label}')
    s=s.replace(old,new,1)

# Insert the real-engine detonation lesson between SWITCH and RUMMY.
old=" {id:'switch',title:'스위치',goal:'나를 향한 스위치를 버스트로 상대에게 넘기고 누적 위력이 커지는 것을 확인합니다.',hint:'8♣를 내 8 세트에 붙이면 버스트 +24가 더해지고 스위치가 상대에게 넘어갑니다.',implemented:true,scenario:'switch',allow:['select','attach','clear'],selectRoles:['switchCard'],attachSide:'player',expectAttach:'SET',expectSwitchTarget:'enemy',minPowerGain:24,completeOn:'attach'},\n {id:'rummy',title:'러미'"
new=" {id:'switch',title:'스위치',goal:'나를 향한 스위치를 버스트로 상대에게 넘기고 누적 위력이 커지는 것을 확인합니다.',hint:'8♣를 내 8 세트에 붙이면 버스트 +24가 더해지고 스위치가 상대에게 넘어갑니다.',implemented:true,scenario:'switch',allow:['select','attach','clear'],selectRoles:['switchCard'],attachSide:'player',expectAttach:'SET',expectSwitchTarget:'enemy',minPowerGain:24,completeOn:'attach'},\n {id:'detonate',title:'폭발과 코어',goal:'스위치가 나를 가리킨 채 턴을 끝내면 누적 위력이 폭발하고, 보호막 뒤에 현재 코어가 피해를 받습니다.',hint:'강조된 5♠를 버려 턴을 끝내세요. 누적 40 중 보호막 8이 먼저 막고 현재 코어 24가 파괴됩니다. 남은 8은 다음 코어로 관통하지 않습니다.',implemented:true,scenario:'detonate',allow:['select','discard','clear'],selectRoles:['detonateEnd'],discardRole:'detonateEnd',expectPower:40,expectShieldAbsorb:8,expectCoreBreak:true,expectNextCoreHp:60,expectReset:true,completeOn:'detonate'},\n {id:'rummy',title:'러미'"
rep(old,new,'detonate tutorial step')

old="else if(step.scenario==='switch'){p.hand=[makeTutorialCard('C','8','switchCard'),makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','SET',[makeTutorialCard('S','8','board','player'),makeTutorialCard('H','8','board','player'),makeTutorialCard('D','8','board','player')])];state.switchTarget='player';state.switchPower=36;state.phase='action';log('스위치 실습 · 8♣를 세트에 붙여 버스트 +24로 누적 위력을 키우고 상대에게 넘기세요.','important')}else if(step.scenario==='rummy')"
new="else if(step.scenario==='switch'){p.hand=[makeTutorialCard('C','8','switchCard'),makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','SET',[makeTutorialCard('S','8','board','player'),makeTutorialCard('H','8','board','player'),makeTutorialCard('D','8','board','player')])];state.switchTarget='player';state.switchPower=36;state.phase='action';log('스위치 실습 · 8♣를 세트에 붙여 버스트 +24로 누적 위력을 키우고 상대에게 넘기세요.','important')}else if(step.scenario==='detonate'){p.hand=[makeTutorialCard('S','5','detonateEnd'),makeTutorialCard('D','9','hold')];p.hp=24;p.shield=8;p.cores=3;state.switchTarget='player';state.switchPower=40;state.phase='action';log('폭발 실습 · 5♠를 버려 턴을 끝내고 보호막 → 현재 코어 → 초과 피해 소멸 순서를 확인하세요.','important')}else if(step.scenario==='rummy')"
rep(old,new,'detonate deterministic scenario')

# Make tutorial completion validate the actual resolved combat result.
old="if(step.expectReload&&context.afterHand!==step.expectReload)return false;const next=TUTORIAL_STEPS[tutorialStepIndex()+1];"
new="if(step.expectReload&&context.afterHand!==step.expectReload)return false;if(step.expectPower!=null&&context.beforePower!==step.expectPower)return false;if(step.expectShieldAbsorb!=null&&context.beforeShield-context.afterShield!==step.expectShieldAbsorb)return false;if(step.expectCoreBreak&&context.afterCores!==context.beforeCores-1)return false;if(step.expectNextCoreHp&&context.afterHp!==step.expectNextCoreHp)return false;if(step.expectReset&&!(context.afterPower===0&&context.afterTarget==='neutral'))return false;const next=TUTORIAL_STEPS[tutorialStepIndex()+1];"
rep(old,new,'detonate tutorial validation')

old="state.tutorialSuccessText=event==='discard'?'좋아요. 카드를 뽑고 선택해 버리는 기본 흐름을 익혔습니다.':event==='rummy'?`러미 성공!"
new="state.tutorialSuccessText=event==='discard'?'좋아요. 카드를 뽑고 선택해 버리는 기본 흐름을 익혔습니다.':event==='detonate'?`폭발 확인! 보호막 ${context.beforeShield-context.afterShield} 흡수 → 현재 코어 ${context.dealt} 피해·파괴. 다음 코어 ${context.afterHp}/${CORE_HP}, 초과 피해는 관통하지 않고 스위치는 중립으로 초기화되었습니다.`:event==='rummy'?`러미 성공!"
rep(old,new,'detonate success copy')

# Capture the real detonate result and report it to tutorial progress only when the hook exists.
old="function detonate(w,reason='턴 종료'){if(state.gameOver||state.switchTarget!==w||state.switchPower<=0)return 0;const s=sideObj(w);let raw=state.switchPower;"
new="function detonate(w,reason='턴 종료'){if(state.gameOver||state.switchTarget!==w||state.switchPower<=0)return 0;const s=sideObj(w),tutorialBefore={power:state.switchPower,shield:s.shield,hp:s.hp,cores:s.cores};let raw=state.switchPower;"
rep(old,new,'detonate before snapshot')

old="log(`${switchName(w)} 폭발 · 누적 ${total}${raw!==total?` → 보정 ${raw}`:''} · 현재 CORE 실제 피해 ${dealt}.`,'hit');return dealt}"
new="log(`${switchName(w)} 폭발 · 누적 ${total}${raw!==total?` → 보정 ${raw}`:''} · 현재 CORE 실제 피해 ${dealt}.`,'hit');if(w==='player'&&typeof tutorialCheckProgress==='function')tutorialCheckProgress('detonate',{beforePower:tutorialBefore.power,beforeShield:tutorialBefore.shield,afterShield:s.shield,beforeHp:tutorialBefore.hp,afterHp:s.hp,beforeCores:tutorialBefore.cores,afterCores:s.cores,dealt,afterPower:state.switchPower,afterTarget:state.switchTarget});return dealt}"
rep(old,new,'detonate tutorial hook')

p.write_text(s)

rp=Path('ROADMAP.md')
r=rp.read_text()
r=r.replace('- [ ] 누적 위력 / 폭발 튜토리얼','- [x] 누적 위력 / 폭발 튜토리얼 — 스위치가 자신을 가리킨 채 턴 종료 → 실제 `turnEnd()` / `detonate()` 경로 체험',1)
r=r.replace('- [ ] 폭발 연출 및 현재 코어 피해 결과 강조','- [x] 폭발 연출 및 현재 코어 피해 결과 강조 — 보호막 8 → 현재 코어 24 파괴 → 초과 8 소멸/관통 없음 → 다음 코어 60/60을 고정 시나리오로 확인',1)
rp.write_text(r)

# Add executable tutorial/engine integration regression.
t=Path('tests/tutorial-detonate.mjs')
t.write_text(r'''import fs from 'node:fs';
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
''')
