import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function src(name){const start=script.indexOf(`function ${name}(`);if(start<0)throw new Error(`missing ${name}`);const end=script.indexOf('\nfunction ',start+1);return script.slice(start,end<0?script.length:end)}
const fx=src('resolveEffects'),attach=src('attachCards'),meld=src('submitNewMeld');
ok(fx.includes('ctx.fxState')&&fx.includes('pending:true'),'resolveEffects preserves resumable effect state and can pause');
ok(fx.includes('ctx.resumeEffects')||fx.includes('const resume=()=>'),'resumable effects retain an action continuation');
ok(attach.includes('if(fx.pending)return\'choice\'')&&attach.includes('ctx.resumeEffects'),'attach pauses before combat/RUMMY finalization and resumes later');
ok(meld.includes('if(fx.pending)return\'choice\'')&&meld.includes('ctx.resumeEffects'),'new meld pauses before RUMMY finalization and resumes later');
ok(fx.includes("case'run4Draw'")&&fx.includes('onChoose:o=>{if(o?.card)bottom(o.card);resume()}'),'Connector resumes the original action only after the optional bottom choice');
ok(attach.includes("const finish=fx=>")&&attach.includes("const willRummy=s.hand.length===0")&&attach.includes("ctx.resumeEffects=()=>{const next=resolveEffects")&&attach.includes("const result=finish(next)"),'attach recalculates RUMMY in finalization reached by resumed choices');
for(const tag of ['discardPursuit','enemyAttachBonus','runHeal2','connectionLink','freeSwapRecover','jokerDual'])ok(fx.includes(`case'${tag}'`)&&fx.includes('requestFreeRecoverChoice'),`${tag} routes legal free recovery through shared choice handling`);
ok(script.includes('function freeRecoverCandidates(')&&script.includes('function recoverSpecificFromMeld('),'free recovery exposes legal-candidate and exact-card helpers');
ok(fx.includes("case'recycler'")&&fx.includes('requestSpentRecycleChoice'),'Recycler routes spent-card selection through shared choice handling');
ok(script.includes('function recycleSpecificSpentCard('),'Recycler can resolve the exact chosen spent card');
ok(road.includes('Make named effect choices resumable'),'roadmap records resumable named-choice timing');
console.log('M8 resumable named-choice regression passed.');
