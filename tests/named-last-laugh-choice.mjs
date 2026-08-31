import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const rummy=source('triggerRummy'),submit=source('submitNewMeld'),attach=source('attachCards');
ok(rummy.includes("typeof requestHandBottomChoice==='function'")&&rummy.includes("title:'마지막 웃음'"),'live Last Laugh uses the shared exact-card bottom choice when available');
ok(rummy.includes("if(paused)return'choice'")&&rummy.includes('const finishRummy=()=>'),'returning Last Laugh can pause RUMMY finalization for the mandatory choice');
ok(rummy.includes("onAsyncResolved:()=>{log(`${switchName(w)} 마지막 웃음 · 반환 러미 후 1장 추가 순환.`,'good');finishRummy()}")&&rummy.includes("if(paused)return'choice'"),'player RUMMY finalization is resumed from the Last Laugh selection callback rather than before the choice');
ok(rummy.includes("else{const cand=[...s.hand].sort")&&rummy.includes('cand.contractActive=false'),'isolated/CPU fallback stays deterministic and normalizes the bottomed card');
ok(submit.includes("const rr=triggerRummy(w,cards,{returned:false})")&&submit.includes("rr==='choice'?'choice':'rummy'"),'new-meld RUMMY propagates an async Last Laugh choice');
ok(attach.includes("const rr=triggerRummy(w,cards,{returned:returning||forceReturn})")&&attach.includes("rr==='choice'?'choice':'rummy'"),'attach RUMMY propagates an async Last Laugh choice');
ok(fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8').includes('Final choice pass C'),'roadmap records Last Laugh choice stabilization');
console.log('M8 Last Laugh choice regression passed.');
