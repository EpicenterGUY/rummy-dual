from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label,count=1):
    global s
    if s.count(old)<count: raise SystemExit(f'missing {label}: {s.count(old)}/{count}')
    s=s.replace(old,new,count)

rep("pendingEffectChoice:null,effectChoiceQueue:[]};","pendingEffectChoice:null,effectChoiceQueue:[],aiChoiceResume:null,aiAsyncActionResult:null};",'AI choice state')

old="function resolveEffectChoice(key){const q=state.pendingEffectChoice;if(!q)return false;const option=key==='__skip__'?null:(q.options||[]).find(o=>String(o.key)===String(key));if(key!=='__skip__'&&!option)return false;state.pendingEffectChoice=null;const cb=q.onChoose;if(typeof cb==='function')cb(option);pumpEffectChoice();if(!state.pendingEffectChoice&&typeof render==='function')render();return true}"
new="function resolveEffectChoice(key){const q=state.pendingEffectChoice;if(!q)return false;const option=key==='__skip__'?null:(q.options||[]).find(o=>String(o.key)===String(key));if(key!=='__skip__'&&!option)return false;state.pendingEffectChoice=null;const cb=q.onChoose;if(typeof cb==='function')cb(option);pumpEffectChoice();if(!state.pendingEffectChoice&&!(state.effectChoiceQueue||[]).length&&typeof state.aiChoiceResume==='function'){const resumeAI=state.aiChoiceResume,result=state.aiAsyncActionResult;state.aiChoiceResume=null;state.aiAsyncActionResult=null;resumeAI(result)}if(!state.pendingEffectChoice&&typeof render==='function')render();return true}"
rep(old,new,'choice resolver AI continuation')

old="function clearEffectChoices(){state.effectChoiceQueue=[];state.pendingEffectChoice=null;if(typeof document==='undefined'){return}"
if old in s:
    new="function clearEffectChoices(){state.effectChoiceQueue=[];state.pendingEffectChoice=null;state.aiChoiceResume=null;state.aiAsyncActionResult=null;if(typeof document==='undefined'){return}"
    rep(old,new,'clear choices verbose')
else:
    old="function clearEffectChoices(){state.effectChoiceQueue=[];state.pendingEffectChoice=null;if(typeof document!=='undefined'){const root=document.getElementById('effectChoiceOverlay');if(root)root.hidden=true}}"
    new="function clearEffectChoices(){state.effectChoiceQueue=[];state.pendingEffectChoice=null;state.aiChoiceResume=null;state.aiAsyncActionResult=null;if(typeof document!=='undefined'){const root=document.getElementById('effectChoiceOverlay');if(root)root.hidden=true}}"
    rep(old,new,'clear choices compact')

anchor="function firstCopyEffectSource(cards,self,tags){const allow=new Set(tags||[]);return cards.find(x=>x.uid!==self.uid&&x.named&&allow.has(x.tag))||null}\n"
helper=r'''function discardSpecificHandCard(w,c,label='효과 버리기'){const side=sideObj(w),i=side.hand.findIndex(x=>x.uid===c?.uid);if(i<0)return false;const[chosen]=side.hand.splice(i,1);pushDiscard(chosen);log(`${label}: ${w==='player'?'내':'상대'} ${cardText(chosen)}를 버렸습니다.`,'important');return true}
function requestParasiteReturnCycles(attacker,m,onAsyncResolved=null){const parasites=(m?.cards||[]).filter(p=>p.tag==='parasite'&&p.owner!==attacker);if(!parasites.length)return false;let index=0,pausedAny=false;const step=()=>{if(index>=parasites.length){if(pausedAny&&typeof onAsyncResolved==='function')onAsyncResolved();return false}const p=parasites[index++],owner=p.owner,side=sideObj(owner);drawOne(owner,false);const candidates=[...side.hand],apply=c=>{if(c)discardSpecificHandCard(owner,c,p.name);log(`${p.name}: 상대가 기생 조합으로 스위치를 반환해 원주인이 1장 순환.`,'good')};if(owner==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1){pausedAny=true;requestEffectChoice({title:p.name,text:'기생한 조합이 스위치를 반환했습니다. 1장 뽑은 뒤 버릴 손패 1장을 고르세요.',options:candidates.map(c=>({key:c.uid,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:`보유 ${c.age}턴`,card:c})),onChoose:o=>{apply(o?.card||null);step()}});return true}const cand=[...candidates].sort((a,b)=>b.age-a.age)[0]||null;apply(cand);return step()};return step()}
'''
if anchor not in s: raise SystemExit('missing parasite helper anchor')
s=s.replace(anchor,helper+anchor,1)

old="const effectCards=fx.effectCards,pause=()=>({bonus:fx.bonus||0,flatReturn:!!fx.flatReturn,forceReturn:!!fx.forceReturn,pending:true});for(let i=fx.index;i<effectCards.length;i++){"
new="const effectCards=fx.effectCards,pause=()=>({bonus:fx.bonus||0,flatReturn:!!fx.flatReturn,forceReturn:!!fx.forceReturn,pending:true});if(ctx.isAttach&&isReturning&&!fx.parasiteChecked){fx.parasiteChecked=true;const parasitePaused=requestParasiteReturnCycles(w,ctx.meld,()=>{if(typeof ctx.resumeEffects==='function')ctx.resumeEffects()});if(parasitePaused)return pause()}for(let i=fx.index;i<effectCards.length;i++){"
rep(old,new,'parasite resumable pre-return reaction')

old="for(const pz of m.cards)if(pz.tag==='parasite'&&pz.owner!==w){drawOne(pz.owner,false);const ps=sideObj(pz.owner),dc=ps.hand.filter(x=>x.uid!==pz.uid).sort((a,b)=>b.age-a.age)[0];if(dc){removeFromHand(pz.owner,[dc]);pushDiscard(dc)}log(`${pz.name}: 상대가 기생 조합으로 반환해 원주인이 1장 순환.`,'good')}"
rep(old,"",'legacy parasite auto-discard')

old="const result=finish(next);if(w==='player'&&typeof render==='function')render();return result};"
new="const result=finish(next);if(w==='enemy')state.aiAsyncActionResult=result;if(w==='player'&&typeof render==='function')render();return result};"
rep(old,new,'async action result bridge',2)

old="function continueAITurnAfterAcquisition(){if(state.gameOver||state.turn!=='enemy')return;const urgent=state.switchTarget==='enemy'&&state.switchPower>0;if(urgent&&!bestExtension('enemy')&&maintenanceLimit('enemy')>0){const swaps=chooseAIMaintenanceCards().slice(0,maintenanceLimit('enemy'));if(swaps.length)performMaintenance('enemy',swaps)}else if(!hasAnyLegalAction('enemy')&&maintenanceLimit('enemy')>0){const swaps=chooseAIMaintenanceCards().slice(0,maintenanceLimit('enemy'));if(swaps.length)performMaintenance('enemy',swaps)}\nconst actionCap=state.sessionMode==='practice'?2:4;let actions=0,rummied=false;while(actions++<actionCap&&!state.gameOver){"
new="function continueAITurnAfterAcquisition(resumeState={}){if(state.gameOver||state.turn!=='enemy')return;if(!resumeState.skipMaintenance){const urgent=state.switchTarget==='enemy'&&state.switchPower>0;if(urgent&&!bestExtension('enemy')&&maintenanceLimit('enemy')>0){const swaps=chooseAIMaintenanceCards().slice(0,maintenanceLimit('enemy'));if(swaps.length)performMaintenance('enemy',swaps)}else if(!hasAnyLegalAction('enemy')&&maintenanceLimit('enemy')>0){const swaps=chooseAIMaintenanceCards().slice(0,maintenanceLimit('enemy'));if(swaps.length)performMaintenance('enemy',swaps)}}\nconst actionCap=state.sessionMode==='practice'?2:4;let actions=Math.max(0,resumeState.actionsUsed||0),rummied=!!resumeState.rummied;while(actions++<actionCap&&!state.gameOver&&!rummied){"
rep(old,new,'resumable AI action loop')

old="const r=attachCards('enemy',ex.cards,ex.side,ex.index);if(r==='rummy'){rummied=true;break}continue}"
new="const r=attachCards('enemy',ex.cards,ex.side,ex.index);if(r==='rummy'){rummied=true;break}if(r==='choice'){const battleId=state.battleId,turnToken=state.turnToken;state.aiChoiceResume=result=>{if(isLiveCombatSession()&&state.battleId===battleId&&state.turnToken===turnToken&&state.turn==='enemy'&&!state.gameOver)continueAITurnAfterAcquisition({skipMaintenance:true,actionsUsed:actions,rummied:result==='rummy'})};return}continue}"
rep(old,new,'AI attach choice pause')

old="const r=submitNewMeld('enemy',nm.cards);if(r==='rummy'){rummied=true;break}continue}"
new="const r=submitNewMeld('enemy',nm.cards);if(r==='rummy'){rummied=true;break}if(r==='choice'){const battleId=state.battleId,turnToken=state.turnToken;state.aiChoiceResume=result=>{if(isLiveCombatSession()&&state.battleId===battleId&&state.turnToken===turnToken&&state.turn==='enemy'&&!state.gameOver)continueAITurnAfterAcquisition({skipMaintenance:true,actionsUsed:actions,rummied:result==='rummy'})};return}continue}"
rep(old,new,'AI new meld choice pause')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
needle='- [x] Final semantics pass A: Insurance Agent only protects cards actually owned by its side, Heart King consumes every stored heart at DETONATE, and any Rebel Joker replacement blocks same-turn return/continuation\n'
insert=needle+'- [x] Final choice pass B: Parasite now lets the human owner choose the discard on an opponent-turn return, while CPU action resolution pauses and resumes without granting extra actions\n'
if needle not in r: raise SystemExit('missing parasite roadmap anchor')
r=r.replace(needle,insert,1)
road.write_text(r,encoding='utf-8')

t=Path('tests/named-parasite-choice.mjs')
t.write_text(r'''import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const parasite=source('requestParasiteReturnCycles'),resolve=source('resolveEffects'),attach=source('attachCards'),ai=source('continueAITurnAfterAcquisition'),choice=source('resolveEffectChoice');
ok(parasite.includes("owner==='player'")&&parasite.includes('requestEffectChoice')&&parasite.includes('candidates.length>1'),'human Parasite owner chooses the exact discard after the forced draw');
ok(!parasite.includes('allowSkip:true'),'Parasite discard remains mandatory');
ok(resolve.includes('fx.parasiteChecked=true')&&resolve.includes('requestParasiteReturnCycles(w,ctx.meld'),'Parasite return reaction is part of resumable pre-finalization effect resolution');
ok(!attach.includes("for(const pz of m.cards)if(pz.tag==='parasite'"),'legacy oldest-card Parasite auto-discard path is removed');
ok(ai.includes('resumeState.actionsUsed')&&ai.includes('resumeState.skipMaintenance')&&ai.includes("if(r==='choice')"),'CPU action loop preserves its action budget and skips duplicate maintenance across a choice pause');
ok(choice.includes('state.aiChoiceResume')&&choice.includes('state.aiAsyncActionResult'),'shared choice completion resumes a paused CPU action with its final action result');
ok(script.includes("if(w==='enemy')state.aiAsyncActionResult=result"),'async enemy meld/attach completion reports RUMMY or success before CPU continuation');
ok(fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8').includes('Final choice pass B'),'roadmap records Parasite choice stabilization');
console.log('M8 Parasite choice regression passed.');
''',encoding='utf-8')
