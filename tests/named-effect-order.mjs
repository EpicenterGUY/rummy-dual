import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const fx=source('resolveEffects');
ok(fx.includes("effectCards=[...(cards||[])]"),'dependent effect ordering is local to resolveEffects and safe for isolated-function tests');
ok(fx.includes("effectCards[i]?.tag!=='goldenHand'")&&fx.includes("x?.tag==='sameDiscardRank'"),'resolver searches for a later Buyout King only when Golden Hand would otherwise resolve first');
ok(fx.includes('const[dep]=effectCards.splice(j,1);effectCards.splice(i,0,dep)'),'Buyout King is moved immediately before the dependent Golden Hand without globally sorting unrelated effects');
ok(fx.includes('for(const c of effectCards){'),'named effects resolve from the minimally adjusted action order');
ok(!fx.includes('orderedNamedEffectCards'),'resolveEffects has no external ordering-helper dependency');
ok(fx.includes("case'sameDiscardRank':{const lr=")&&fx.includes("case'goldenHand':if(cards.some(x=>x.fromDiscard))"),'Buyout King classification and Golden Hand dependency remain active in the same resolver');
console.log('M8 dependent effect-order regression passed.');
