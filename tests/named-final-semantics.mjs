import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const insurance=source('insuranceBlocks'),detonate=source('detonate'),replace=source('replaceRedundantJokers');
ok(insurance.includes("targetCard?.owner===targetSide?m.cards.findIndex"),'Insurance Agent only intercepts interference against a card owned by its protected side');
ok(detonate.includes('const spend=c.healCharge')&&detonate.includes('c.healCharge=0'),'Heart King removes every stored heart when DETONATE prevention resolves');
ok(html.includes('손에 있는 동안 회복할 때 심장을 최대 3개 저장')&&html.includes('저장한 심장을 모두 제거'),'Heart King text matches its hand-only charge window and spend-all detonation');
ok(replace.includes("if(j.tag==='rebelJoker')")&&!replace.includes("attacher!==j.owner"),'Rebel Joker replacement blocks follow-up regardless of who supplied the real card');
ok(replace.includes('sideObj(attacher).extraAttachRemaining=0'),'Rebel replacement removes the replacing player\'s named extra-attach allowance');
ok(!script.includes('function canContinueReturnedRun(')&&!replace.includes('rebelReturnBlockedToken')&&!replace.includes('lastAttachToken'),'Rebel semantics no longer depend on removed same-RUN continuation state');
ok(fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8').includes('Final semantics pass A'),'roadmap records the final semantics pass');
console.log('M8 final semantics regression passed.');
