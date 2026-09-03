import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let brace=-1,paren=0;for(let i=start+marker.length-1;i<script.length;i++){const ch=script[i];if(ch==='(')paren++;else if(ch===')')paren--;else if(ch==='{'&&paren===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const onDraw=source('onDiscardDraw'),choice=source('requestHandBottomChoice'),bottom=source('bottomSpecificHandCard'),ai=source('aiTurn'),resume=source('continueAITurnAfterAcquisition');
ok(onDraw.includes("cardHasAbility(c,'bait')&&c.originOwner!==w")&&onDraw.indexOf('drawOne(owner,false)')<onDraw.indexOf('requestHandBottomChoice(owner'),'Bait draws for its original owner before asking which hand card to bottom');
ok(choice.includes("w==='player'")&&choice.includes('requestEffectChoice')&&choice.includes('candidates.length>1'),'human owner receives shared modal choice when multiple Bait bottom candidates exist');
ok(!choice.includes('allowSkip:true'),'Bait hand-bottom choice is mandatory rather than skippable');
ok(bottom.includes('side.deck.unshift(chosen)')&&bottom.includes('chosen.contractActive=false')&&bottom.includes('chosen.age=0'),'chosen Bait cycle card is normalized and sent to deck bottom');
ok(ai.includes("paused=onDiscardDraw('enemy',c")&&ai.includes('if(paused){render();return}'),'AI acquisition returns immediately while an off-turn Bait choice is pending');
ok(ai.includes('battleId=state.battleId')&&ai.includes('turnToken=state.turnToken')&&ai.includes("state.turn==='enemy'")&&ai.includes('continueAITurnAfterAcquisition()'),'AI continuation is guarded against stale battle/turn callbacks');
ok(resume.includes('performMaintenance')&&resume.includes("bestExtension('enemy')")&&resume.includes("turnEnd('enemy')"),'post-acquisition AI continuation owns maintenance, actions, discard and turn end');
ok(!resume.includes("turnStart('enemy')"),'resuming after Bait does not restart the CPU turn');
ok(fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8').includes('CPU play resumes only after that choice resolves'),'roadmap records completed off-turn Bait continuation');
console.log('M8 off-turn choice regression passed.');
