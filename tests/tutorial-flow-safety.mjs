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

ok(script.includes('tutorialStepToken:0') && script.includes('tutorialExitArmed:false'), 'tutorial state tracks step revision and exit confirmation');
ok(script.includes('state.tutorialStepToken++;state.tutorialStep=id'), 'every tutorial step setup invalidates stale step callbacks');
ok(script.includes('stepToken=state.tutorialStepToken') && script.includes('state.tutorialStepToken===stepToken'), 'auto advance requires the same tutorial step revision');
ok(script.includes("function restartTutorialStep(){if(state.sessionMode!=='tutorial'||!state.tutorialStep)return false") && script.includes('단계 재시작 · 고정 상태를 처음부터 다시 구성했습니다.'), 'manual step restart rebuilds deterministic state explicitly');
ok(script.includes("if(!state.tutorialExitArmed){state.tutorialExitArmed=true") && script.includes("},2400);return false}progress.tutorialPromptSeen=true;saveProgress();showStartScreen();return true}"), 'tutorial exit requires a second confirmation tap and preserves progress state');
ok(script.includes("state.sessionMode='menu';state.tutorialStep=null;state.tutorialExitArmed=false"), 'returning to menu clears tutorial exit state and invalidates session work');
ok(script.includes("exit.textContent=state.tutorialExitArmed?'한 번 더 눌러 종료':'튜토리얼 종료'"), 'coach gives explicit Korean exit confirmation feedback');

const drawStart=script.indexOf('function playerDraw('), drawGuard=script.indexOf("if(!tutorialAllows(tutorialAction",drawStart), drawMutation=script.indexOf("c=drawOne('player'",drawStart);
ok(drawStart>=0 && drawGuard>drawStart && drawMutation>drawGuard, 'tutorial draw rejection occurs before draw mutation');
const playerMeld=source('playerMeld'), delegatedMeld=script.includes('function executePlayerMeld(')?source('executePlayerMeld'):'', meldContract=delegatedMeld||playerMeld;
const meldGuard=meldContract.indexOf("if(!tutorialAllows('meld'"), meldMutation=meldContract.indexOf("submitNewMeld('player'");
ok(meldGuard>=0 && meldMutation>meldGuard && (!delegatedMeld||playerMeld.includes('executePlayerMeld(cs')), 'tutorial meld rejection occurs before meld mutation through any rank-choice delegation');
const playerAttach=source('playerAttach'), delegatedAttach=script.includes('function executePlayerAttach(')?source('executePlayerAttach'):'', attachContract=delegatedAttach||playerAttach;
const attachGuard=attachContract.indexOf("if(!tutorialAllows('attach'"), attachMutation=attachContract.indexOf("attachCards('player'");
ok(attachGuard>=0 && attachMutation>attachGuard && (!delegatedAttach||playerAttach.includes('executePlayerAttach(cs,target')), 'tutorial attach rejection occurs before attach mutation through any rank-choice delegation');
const discardStart=script.indexOf('function playerDiscard('), discardGuard=script.indexOf("if(!tutorialAllows('discard'",discardStart), discardMutation=script.indexOf("removeFromHand('player'",discardStart);
ok(discardStart>=0 && discardGuard>discardStart && discardMutation>discardGuard, 'tutorial discard rejection occurs before hand mutation');
ok(roadmap.includes('- [x] 튜토리얼 종료 / 재시작 처리') && roadmap.includes('- [x] 행동 성공 시 자동 진행'), 'UX1 P2 roadmap records stable exit/restart and wrong-action handling');

console.log('RUMMY//DUEL tutorial flow safety regressions passed.');
