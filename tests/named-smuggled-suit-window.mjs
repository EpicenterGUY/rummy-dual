import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const state={turnToken:7};const ctx=vm.createContext({state});vm.runInContext(source('isSuitFlexible'),ctx);
let c={tag:'smuggledSuit',smuggledActive:false,smuggledTurnToken:7};
ok(ctx.isSuitFlexible(c),'Smuggled Goods is suit-flexible on the turn it is acquired from discard');
state.turnToken=8;ok(!ctx.isSuitFlexible(c),'an unplayed Smuggled Goods loses suit flexibility on the next turn');
c.smuggledActive=true;ok(ctx.isSuitFlexible(c),'a Smuggled Goods already committed to a RUN keeps its locked meld role');
const submit=source('submitNewMeld'),attach=source('attachCards'),recover=source('playerRecover'),free=source('freeRecoverFromMeld'),retire=source('retireMeld');
ok(submit.includes("if(type==='RUN')for(const c of cards)if(c.tag==='smuggledSuit'&&c.smuggledTurnToken===state.turnToken)c.smuggledActive=true"),'new RUN locks the current-turn Smuggled Goods role');
ok(attach.includes("if(type==='RUN')for(const c of cards)if(c.tag==='smuggledSuit'&&c.smuggledTurnToken===state.turnToken)c.smuggledActive=true"),'RUN attachment locks the current-turn Smuggled Goods role');
ok(recover.includes("if(c.tag==='smuggledSuit')c.smuggledActive=false")&&free.includes("if(c.tag==='smuggledSuit')c.smuggledActive=false")&&retire.includes("if(c.tag==='smuggledSuit')c.smuggledActive=false"),'leaving the public meld clears the locked Smuggled Goods role');
ok(html.includes("c.smuggledTurnToken=state.turnToken;c.smuggledActive=false"),'discard acquisition stamps the current-turn permission instead of permanent flexibility');
console.log('M8 Smuggled Goods timing regression passed.');
