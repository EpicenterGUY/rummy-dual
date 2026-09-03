import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const fx=source('resolveEffects');
ok(fx.includes("if(!fx.effectCards){const list=[...(cards||[])]")&&fx.includes('fx.effectCards=list'),'dependent effect ordering is initialized locally inside resolveEffects and survives resumable passes');
ok(fx.includes("list[i]?.tag!=='goldenHand'")&&fx.includes("x?.tag==='sameDiscardRank'"),'resolver searches for a later Buyout King only when Golden Hand would otherwise resolve first');
ok(fx.includes('const[dep]=list.splice(j,1);list.splice(i,0,dep)'),'Buyout King is moved immediately before the dependent Golden Hand without globally sorting unrelated effects');
ok(fx.includes('const effectCards=fx.effectCards')&&fx.includes('for(let i=fx.index;i<effectCards.length;i++)'),'named effects resume from the minimally adjusted action order without replaying prior effects');
ok(!fx.includes('orderedNamedEffectCards'),'resolveEffects has no external ordering-helper dependency');
ok(fx.includes("case'sameDiscardRank':{const lr=")&&fx.includes("case'goldenHand':{const paused=requestFlexibleGrant(w,c,()=>cards.filter(x=>x.fromDiscard)"),'Buyout King classification and Golden Hand dependency remain active in the same resolver');
console.log('M8 dependent effect-order regression passed.');
