import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const fx=source('resolveEffects');
ok(fx.includes("case'goldenHand':{const paused=requestFlexibleGrant(w,c,()=>cards.filter(x=>x.fromDiscard)"),'Golden Hand checks the whole same-action card group for discard origin');
ok(!fx.includes("case'goldenHand':if(c.fromDiscard)"),'Golden Hand no longer requires itself to be the discard-acquired card');
ok(html.includes("'D7':{n:'황금손',t:'goldenHand',d:'버림패에서 가져온 카드와 같은 행동에 사용하면"),'Golden Hand text and implementation now describe the same source condition');
console.log('M8 Golden Hand source regression passed.');
