import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const roadmap = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}

new Function(script);

ok(script.includes("id:'basic'") && script.includes("scenario:'basic'") && script.includes("discardRole:'basicDraw'") && script.includes("implemented:true"), 'basic lesson is a deterministic implemented scenario');
ok(script.includes("id:'set'") && script.includes("scenario:'set'") && script.includes("expectMeld:'SET'"), 'SET lesson requires the real SET result');
ok(script.includes("id:'run'") && script.includes("scenario:'run'") && script.includes("expectMeld:'RUN'"), 'RUN lesson requires the real RUN result');
ok(script.includes("makeTutorialCard('D','Q','basicDraw')") && script.includes("makeTutorialCard('S','2','hold')"), 'basic lesson fixes one draw target while retaining a hold card to avoid accidental RUMMY');
ok(script.includes("makeTutorialCard('S','3','setCard')") && script.includes("makeTutorialCard('H','3','setCard')") && script.includes("makeTutorialCard('D','3','setCard')"), 'SET lesson uses the planned 3-suit fixed hand');
ok(script.includes("makeTutorialCard('C','4','runCard')") && script.includes("makeTutorialCard('C','5','runCard')") && script.includes("makeTutorialCard('C','6','runCard')"), 'RUN lesson uses the planned club sequence');
ok(script.includes("function resetTutorialSide") && script.includes("state.switchTarget='neutral';state.switchPower=0"), 'tutorial scenario rebuilds combat state deterministically instead of creating a separate rules engine');
ok(script.includes("if(!tutorialAllows(tutorialAction,{fromDiscard}))") && script.includes("if(!tutorialAllows('select',{card:c}))") && script.includes("if(!tutorialAllows('discard',{card:c}))"), 'draw, selection and discard mutation paths obey the tutorial action gate');
const playerMeld=source('playerMeld'),delegated=script.includes('function executePlayerMeld(')?source('executePlayerMeld'):'',meldContract=delegated||playerMeld;
ok(meldContract.includes("if(!tutorialAllows('meld',{cards:cs,type:t}))") && meldContract.includes("const result=submitNewMeld('player',cs") && meldContract.includes("result&&tutorialCheckProgress('meld',{type:t,cards:cs})") && (!delegated||playerMeld.includes('executePlayerMeld(cs')), 'SET/RUN success is confirmed only after the real submitNewMeld path succeeds through any rank-choice delegation');
ok(script.includes("stepToken=state.tutorialStepToken") && script.includes("state.tutorialStepToken===stepToken"), 'successful lessons auto-advance with stale-session and stale-step protection');
ok(script.includes("function renderTutorialHighlights") && html.includes('.cardBtn.tutorialLocked') && html.includes('.pixelBtn.tutorialTarget'), 'tutorial target and locked affordances are visible without a separate game screen');
ok(script.includes("document.getElementById('resetBtn').hidden=true"), 'random new-game reset is hidden during deterministic tutorial lessons');
ok(roadmap.includes('- [x] 카드 기본 조작 튜토리얼') && roadmap.includes('- [x] 세트 튜토리얼') && roadmap.includes('- [x] 런 튜토리얼'), 'UX1 roadmap records the completed first hands-on tranche');

console.log('RUMMY//DUEL deterministic basic/SET/RUN tutorial regressions passed.');
