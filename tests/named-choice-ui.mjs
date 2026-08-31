import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
ok(html.includes('pendingEffectChoice:null,effectChoiceQueue:[]'),'battle state owns a shared queued effect-choice channel');
ok(html.includes('.effectChoiceOverlay')&&html.includes('.effectChoiceOptions'),'shared effect-choice modal has dedicated responsive styling');
for(const name of ['ensureEffectChoiceModal','renderEffectChoiceModal','pumpEffectChoice','requestEffectChoice','resolveEffectChoice','clearEffectChoices'])ok(script.includes(`function ${name}(`),`shared effect-choice helper exists: ${name}`);
const discard=source('playerDiscard');
ok(!discard.includes("confirm('예약 발송"),'Reserved Shipping no longer uses a card-specific blocking confirm dialog');
ok(discard.includes("title:c.name,text:'버릴 때 공용 버림패 대신 내 덱 맨 위에 둘 수 있습니다.'"),'Reserved Shipping routes its decision through the shared effect-choice modal');
ok(discard.includes("c.effectChoiceDecision=o?.key||'discard';playerDiscard()"),'Reserved Shipping resumes the original discard action after the shared decision');
const fx=source('resolveEffects');
ok(fx.includes("case'run4Draw'")&&fx.includes("allowSkip:true,skipLabel:'보내지 않기'"),'Connector 6+ exposes an optional shared hand-bottom choice');
ok(fx.includes("options:candidates.map(x=>({key:x.uid")&&fx.includes('onChoose:o=>{if(o?.card)bottom(o.card)}'),'Connector player choice is bound to concrete remaining hand cards');
ok(fx.includes("else bottom([...candidates].sort((a,b)=>b.age-a.age)[0])"),'Connector CPU path remains deterministic instead of opening UI');
const ng=source('newGame');
ok(ng.includes('clearEffectChoices()'),'new battles clear stale effect-choice state');
ok(road.includes('Add a shared queued effect-choice modal'),'M8 roadmap records the shared choice foundation');
console.log('M8 shared effect-choice regression passed.');
