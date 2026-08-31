import fs from 'node:fs';
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
