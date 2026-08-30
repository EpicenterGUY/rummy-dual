from pathlib import Path

root = Path('.')
index = root / 'index.html'
roadmap = root / 'ROADMAP.md'
text = index.read_text(encoding='utf-8')
road = roadmap.read_text(encoding='utf-8')


def replace_once(src: str, old: str, new: str, label: str) -> str:
    if old not in src:
        raise SystemExit(f'missing anchor: {label}')
    return src.replace(old, new, 1)

css_anchor = ".combatBanner.break{color:#e08d92}.combatBanner.burst{color:#d7bd8b}.combatBanner.chain{color:#8dbab4}\n"
css_block = css_anchor + """
/* UX1 P2 · switch movement + RUMMY feedback */
.switchFlight{position:fixed;z-index:1800;min-width:48px;height:26px;padding:3px 7px;border:1px solid #6e817f;border-radius:999px;background:#24363aee;color:#d7efeb;box-shadow:0 6px 16px #0007;display:flex;align-items:center;justify-content:center;gap:4px;pointer-events:none;font-size:10px;font-weight:900;white-space:nowrap}.switchFlight.enemy{border-color:#916469;background:#493034ee;color:#f1d7d9}.switchFlight.neutral{border-color:#6a7478;background:#30393dee;color:#d4dbdc}.switchFlight b{font-size:7px}.initiativeBoard.switchKick{animation:switchBoardKick .42s ease}.initiativeSide.switchCatch{animation:switchCatch .52s ease}.handZone.rummyFlash,.enemyZone.rummyFlash{animation:rummyZoneFlash .72s ease}.cardBtn.rummyDeal,.cardBack.rummyDeal{animation:rummyDeal .5s ease both}.tutorialCoach.tutorialSuccessPulse{animation:tutorialSuccessPulse .58s ease}
@keyframes switchBoardKick{35%{transform:translateY(-2px);box-shadow:0 0 0 1px #78918c inset,0 7px 18px #0004}100%{transform:none}}@keyframes switchCatch{35%{transform:scale(1.08);filter:brightness(1.3)}100%{transform:none;filter:none}}@keyframes rummyZoneFlash{25%{box-shadow:0 0 0 2px #9e91b4 inset,0 0 20px #a798c52d}100%{box-shadow:none}}@keyframes rummyDeal{0%{opacity:.15;transform:translateY(-12px) scale(.92)}65%{opacity:1;transform:translateY(2px) scale(1.03)}100%{opacity:1;transform:none}}@keyframes tutorialSuccessPulse{30%{box-shadow:0 0 0 2px #86a98b inset,0 0 18px #8fc49b35;transform:translateY(-1px)}100%{transform:none}}
@media(max-width:390px){.switchFlight{min-width:44px;height:24px;padding:3px 6px;font-size:9px}.switchFlight b{font-size:6px}}
"""
text = replace_once(text, css_anchor, css_block, 'feedback CSS insertion')

pulse_anchor = "function pulsePanel(w,kind='light',delay=0){setTimeout(()=>{const el=document.getElementById(w==='player'?'pPanel':'ePanel');if(!el)return;const c=kind==='break'?'hitBreak':kind==='heavy'?'hitHeavy':kind==='shield'?'shieldBlock':'hitLight';el.classList.remove('hitLight','hitHeavy','hitBreak','shieldBlock');void el.offsetWidth;el.classList.add(c);setTimeout(()=>el.classList.remove(c),520)},delay)}\n"
helpers = pulse_anchor + """function switchAnchorElement(w){if(w==='player')return document.querySelector('.initiativeSide.playerSide');if(w==='enemy')return document.querySelector('.initiativeSide.enemySide');return document.querySelector('.initiativeCore')}
function animateSwitchMove(from,target,power=state.switchPower,label='반환'){if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;const fromEl=switchAnchorElement(from),toEl=switchAnchorElement(target),board=document.querySelector('.initiativeBoard');if(!fromEl||!toEl)return;const a=rectSnapshot(fromEl),b=rectSnapshot(toEl);if(!a||!b)return;board?.classList.remove('switchKick');void board?.offsetWidth;board?.classList.add('switchKick');const catchEl=target==='player'||target==='enemy'?switchAnchorElement(target):null;if(catchEl){catchEl.classList.remove('switchCatch');void catchEl.offsetWidth;catchEl.classList.add('switchCatch')}const ghost=document.createElement('div');ghost.className=`switchFlight ${target}`;ghost.setAttribute('aria-hidden','true');ghost.innerHTML=`<span>${target==='neutral'?'◇':'◆'}</span><b>${target==='neutral'?'중립':power}</b>`;const w=54,h=26,sx=a.left+(a.width-w)/2,sy=a.top+(a.height-h)/2,tx=b.left+(b.width-w)/2,ty=b.top+(b.height-h)/2;ghost.style.left=`${sx}px`;ghost.style.top=`${sy}px`;document.body.appendChild(ghost);const dx=tx-sx,dy=ty-sy,arc=Math.min(18,Math.max(8,Math.abs(dx)*.08));const anim=ghost.animate([{transform:'translate(0,0) scale(.88)',opacity:.55},{transform:`translate(${dx*.52}px,${dy*.45-arc}px) scale(1.12)`,opacity:1,offset:.5},{transform:`translate(${dx}px,${dy}px) scale(.94)`,opacity:.18}],{duration:520,easing:'cubic-bezier(.2,.75,.2,1)'});const cleanup=()=>{ghost.remove();board?.classList.remove('switchKick');catchEl?.classList.remove('switchCatch')};anim.onfinish=cleanup;anim.oncancel=cleanup}
function animateRummyFeedback(w,reload){combatBanner(`러미 · ${reload}장 리필`,'rummy',20);fxNode(`${reload}장 리필`,'heal',w,110);requestAnimationFrame(()=>{const zone=w==='player'?document.querySelector('.handZone'):document.querySelector('.enemyZone');if(!zone)return;zone.classList.remove('rummyFlash');void zone.offsetWidth;zone.classList.add('rummyFlash');setTimeout(()=>zone.classList.remove('rummyFlash'),760);if(w==='player')flashPile('deckPile');const cards=[...zone.querySelectorAll(w==='player'?'.cardBtn':'.cardBack')];cards.forEach((el,i)=>setTimeout(()=>{el.classList.remove('rummyDeal');void el.offsetWidth;el.classList.add('rummyDeal');setTimeout(()=>el.classList.remove('rummyDeal'),560)},i*45))})}
function pulseTutorialSuccess(){const coach=document.getElementById('tutorialCoach');if(!coach||coach.hidden)return;coach.classList.remove('tutorialSuccessPulse');void coach.offsetWidth;coach.classList.add('tutorialSuccessPulse');setTimeout(()=>coach.classList.remove('tutorialSuccessPulse'),640)}
"""
text = replace_once(text, pulse_anchor, helpers, 'feedback helper insertion')

old_reset = "function resetBombCycle(reason='폭탄 사이클 종료',resetChains=false){state.switchPower=0;state.switchTarget='neutral';state.lastSwitchAdd=0;state.lastSwitchActor=null;state.fuseUsed=false;state.player.graceArmed=false;state.enemy.graceArmed=false;if(resetChains)resetAllChains(reason)}"
new_reset = "function resetBombCycle(reason='폭탄 사이클 종료',resetChains=false){const oldTarget=state.switchTarget;if(oldTarget!=='neutral')animateSwitchMove(oldTarget,'neutral',0,reason);state.switchPower=0;state.switchTarget='neutral';state.lastSwitchAdd=0;state.lastSwitchActor=null;state.fuseUsed=false;state.player.graceArmed=false;state.enemy.graceArmed=false;if(resetChains)resetAllChains(reason)}"
text = replace_once(text, old_reset, new_reset, 'bomb reset switch animation')

old_target = "function setSwitchTarget(target,reason='반환'){state.switchTarget=target;log(`스위치 → ${switchName(target)} · ${reason}.`,'important');combatBanner(`스위치 → ${switchName(target)}`,'chain',80)}"
new_target = "function setSwitchTarget(target,reason='반환'){const from=state.switchTarget;state.switchTarget=target;log(`스위치 → ${switchName(target)} · ${reason}.`,'important');animateSwitchMove(from,target,state.switchPower,reason);combatBanner(`스위치 → ${switchName(target)}`,'chain',80)}"
text = replace_once(text, old_target, new_target, 'switch target movement')

old_rummy = "combatBanner('러미!','rummy',40);log(`${w==='player'?'나':'상대'} 러미! 새 손패 ${reload}장.`,'good');"
new_rummy = "animateRummyFeedback(w,reload);log(`${w==='player'?'나':'상대'} 러미! 새 손패 ${reload}장.`,'good');"
text = replace_once(text, old_rummy, new_rummy, 'RUMMY feedback hook')

old_tutorial = "if(next?.implemented){render();renderTutorialCoach();const battleId=state.battleId,stepId=step.id,stepToken=state.tutorialStepToken;setTimeout(()=>{if(state.sessionMode==='tutorial'&&state.battleId===battleId&&state.tutorialStep===stepId&&state.tutorialStepToken===stepToken)setTutorialStep(next.id)},650);return true}state.tutorialSegmentDone=true;render();renderTutorialCoach();return true}"
new_tutorial = "if(next?.implemented){render();renderTutorialCoach();pulseTutorialSuccess();const battleId=state.battleId,stepId=step.id,stepToken=state.tutorialStepToken;setTimeout(()=>{if(state.sessionMode==='tutorial'&&state.battleId===battleId&&state.tutorialStep===stepId&&state.tutorialStepToken===stepToken)setTutorialStep(next.id)},850);return true}state.tutorialSegmentDone=true;render();renderTutorialCoach();pulseTutorialSuccess();return true}"
text = replace_once(text, old_tutorial, new_tutorial, 'tutorial success feedback')

old_road = "- [ ] 세부 애니메이션 / 스위치 이동 / 러미 피드백 보강"
new_road = "- [x] 세부 애니메이션 / 스위치 이동 / 러미 피드백 보강 — 버스트/체인 반환 시 현재 위치→상대 위치 스위치 플라이트, 폭탄 종료 시 중립 복귀, 러미 6/7장 리필 배너·손패 딜 인, 튜토리얼 성공 펄스 및 850ms 전환 피드백 추가"
road = replace_once(road, old_road, new_road, 'UX1 P2 feedback roadmap')

index.write_text(text, encoding='utf-8')
roadmap.write_text(road, encoding='utf-8')

test = root / 'tests' / 'ux1-feedback.mjs'
test.write_text(r"""import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const roadmap = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);

ok(script.includes('function animateSwitchMove(from,target,power=state.switchPower') && script.includes("switchAnchorElement('neutral')") === false, 'switch movement uses board anchors without inventing a neutral side element');
ok(script.includes("function setSwitchTarget(target,reason='반환'){const from=state.switchTarget") && script.includes('animateSwitchMove(from,target,state.switchPower,reason)'), 'switch return captures the previous owner and animates to the new target');
ok(script.includes("const oldTarget=state.switchTarget;if(oldTarget!=='neutral')animateSwitchMove(oldTarget,'neutral',0,reason)"), 'bomb-cycle reset visibly returns the switch to neutral');
ok(html.includes('.switchFlight{position:fixed') && html.includes('.initiativeSide.switchCatch') && html.includes('@keyframes switchBoardKick'), 'switch flight and catch feedback styles exist');
ok(script.includes('function animateRummyFeedback(w,reload)') && script.includes('combatBanner(`러미 · ${reload}장 리필`') && script.includes("zone.querySelectorAll(w==='player'?'.cardBtn':'.cardBack')"), 'RUMMY feedback announces reload and animates the refreshed hand');
ok(html.includes('.handZone.rummyFlash,.enemyZone.rummyFlash') && html.includes('.cardBtn.rummyDeal,.cardBack.rummyDeal'), 'RUMMY zone flash and staggered deal-in styles exist for both sides');
ok(!script.includes("combatBanner('러미!','rummy',40)") && script.includes('animateRummyFeedback(w,reload);log(`'), 'triggerRummy uses the richer feedback hook instead of the old one-line banner');
ok(script.includes('function pulseTutorialSuccess()') && script.includes('renderTutorialCoach();pulseTutorialSuccess();const battleId=state.battleId') && script.includes('},850);return true}'), 'tutorial success visibly pulses before the guarded 850ms auto-advance');
ok(html.includes('.tutorialCoach.tutorialSuccessPulse') && html.includes('@keyframes tutorialSuccessPulse'), 'tutorial coach has a dedicated success transition animation');
ok(script.includes("if(matchMedia('(prefers-reduced-motion: reduce)').matches)return") && html.includes('@media (prefers-reduced-motion:reduce)'), 'new feedback respects reduced-motion preferences');
ok(roadmap.includes('- [x] 세부 애니메이션 / 스위치 이동 / 러미 피드백 보강'), 'UX1 P2 roadmap marks detailed feedback polish complete');

console.log('RUMMY//DUEL UX1 feedback regressions passed.');
""", encoding='utf-8')

print('patched UX1 feedback, roadmap and regressions')
