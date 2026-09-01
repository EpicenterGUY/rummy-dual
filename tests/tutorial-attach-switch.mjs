import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const roadmap = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) { if (!condition) throw new Error(message); console.log(`PASS: ${message}`); }
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
new Function(script);

ok(script.includes("id:'attachOwn'") && script.includes("scenario:'attachOwn'") && script.includes("attachSide:'player'") && script.includes("expectAttach:'RUN'"), 'own-attach lesson is implemented as a real RUN attach scenario');
ok(script.includes("makeTutorialCard('C','7','attachOwnCard')") && script.includes("makeTutorialMeld('player','RUN'"), 'own-attach lesson fixes a 4-5-6 club RUN plus 7 club');
ok(script.includes("id:'attachEnemy'") && script.includes("attachSide:'enemy'") && script.includes("makeTutorialCard('H','8','attachEnemyCard')") && script.includes("makeTutorialMeld('enemy','RUN'"), 'opponent-attach lesson uses a fixed enemy heart RUN');
ok(script.includes("state.switchTarget='player';state.switchPower=12"), 'opponent-attach lesson begins with SWITCH on the player so a legal return can be experienced');
ok(script.includes("id:'switch'") && script.includes("expectAttach:'SET'") && script.includes("expectSwitchTarget:'enemy'") && script.includes("minPowerGain:24"), 'SWITCH lesson requires a real SET BURST return and minimum +24 gain');
ok(script.includes("state.switchTarget='player';state.switchPower=36") && script.includes("makeTutorialCard('C','8','switchCard')") && script.includes("makeTutorialMeld('player','SET'"), 'SWITCH lesson fixes a threatened 3SET and fourth-suit completion card');
const playerAttach=source('playerAttach'),delegated=script.includes('function executePlayerAttach(')?source('executePlayerAttach'):'',attachContract=delegated||playerAttach;
ok(attachContract.includes("if(!tutorialAllows('attach',{cards:cs,targetSide:target.side,targetIndex:target.index,type}))"), 'player attach execution remains mutation-gated by the tutorial contract');
ok(attachContract.includes("attachCards('player',cs,target.side,target.index")&&(!delegated||playerAttach.includes('executePlayerAttach(cs,target')), 'tutorial attach success still reaches the real attachCards path through any rank-choice delegation');
ok(attachContract.includes("tutorialCheckProgress('attach',{cards:cs,targetSide:target.side") && attachContract.includes("afterPower:state.switchPower,afterTarget:state.switchTarget"), 'tutorial completion checks the actual resulting SWITCH state and power after delegated execution');
ok(script.includes("entry.classList.add('tutorialTarget')") && script.includes(".attachHereBtn[data-attach-side=\"${side}\"]"), 'tutorial highlights the intended meld and real attach button');
ok(roadmap.includes('- [x] 붙이기 튜토리얼') && roadmap.includes('- [x] 상대 공개 조합 붙이기 체험') && roadmap.includes('- [x] 스위치 튜토리얼'), 'UX1 roadmap records attach/opponent/SWITCH lessons complete');
ok(script.includes("step.id==='rummy'?'기본 튜토리얼 완료!") && !script.includes('다음 묶음에서는 붙이기와 상대 공개 조합 이용'), 'completion coach now distinguishes final RUMMY completion from stale attach work');

console.log('RUMMY//DUEL deterministic attach/opponent/SWITCH tutorial regressions passed.');
