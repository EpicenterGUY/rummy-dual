from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

def rep(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'missing compat anchor: {label}')
    text = text.replace(old, new, 1)

rep("if(oldTarget!=='neutral')animateSwitchMove(oldTarget,'neutral',0,reason);", "if(oldTarget!=='neutral'&&typeof animateSwitchMove==='function')animateSwitchMove(oldTarget,'neutral',0,reason);", 'reset hook guard')
rep("animateSwitchMove(from,target,state.switchPower,reason);combatBanner", "if(typeof animateSwitchMove==='function')animateSwitchMove(from,target,state.switchPower,reason);combatBanner", 'return hook guard')
rep("animateRummyFeedback(w,reload);log(`", "if(typeof animateRummyFeedback==='function')animateRummyFeedback(w,reload);else combatBanner('러미!','rummy',40);log(`", 'RUMMY hook fallback')
rep("render();renderTutorialCoach();pulseTutorialSuccess();const battleId=", "render();renderTutorialCoach();if(typeof pulseTutorialSuccess==='function')pulseTutorialSuccess();const battleId=", 'tutorial intermediate pulse guard')
rep("state.tutorialSegmentDone=true;render();renderTutorialCoach();pulseTutorialSuccess();return true}", "state.tutorialSegmentDone=true;render();renderTutorialCoach();if(typeof pulseTutorialSuccess==='function')pulseTutorialSuccess();return true}", 'tutorial final pulse guard')
index.write_text(text, encoding='utf-8')

test = Path('tests/ux1-feedback.mjs')
t = test.read_text(encoding='utf-8')
t = t.replace("script.includes('animateSwitchMove(from,target,state.switchPower,reason)')", "script.includes(\"typeof animateSwitchMove==='function'\") && script.includes('animateSwitchMove(from,target,state.switchPower,reason)')")
t = t.replace("script.includes(\"const oldTarget=state.switchTarget;if(oldTarget!=='neutral')animateSwitchMove(oldTarget,'neutral',0,reason)\")", "script.includes(\"const oldTarget=state.switchTarget;if(oldTarget!=='neutral'&&typeof animateSwitchMove==='function')animateSwitchMove(oldTarget,'neutral',0,reason)\")")
t = t.replace("!script.includes(\"combatBanner('러미!','rummy',40)\") && script.includes('animateRummyFeedback(w,reload);log(`')", "script.includes(\"typeof animateRummyFeedback==='function'\") && script.includes(\"else combatBanner('러미!','rummy',40)\")")
t = t.replace("script.includes('renderTutorialCoach();pulseTutorialSuccess();const battleId=state.battleId')", "script.includes(\"renderTutorialCoach();if(typeof pulseTutorialSuccess==='function')pulseTutorialSuccess();const battleId=state.battleId\")")
t = t.replace("'triggerRummy uses the richer feedback hook instead of the old one-line banner'", "'triggerRummy uses the richer feedback hook with a non-visual isolation fallback'")
test.write_text(t, encoding='utf-8')

print('guarded visual feedback hooks for isolated engine tests')
