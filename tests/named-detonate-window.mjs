import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const start=source('turnStart'),end=source('turnEnd'),fx=source('resolveEffects');
ok(start.includes('s.detonateMemory=Math.max(0,s.lastDetonateTaken||0);s.lastDetonateTaken=0;'),'turn start transfers the previous DETONATE result into the current action window before clearing the pending value');
ok(start.includes('if(s.detonateMemory>0){const pi=s.spent.findIndex')&&start.includes('ph.phoenixReturned=true')&&!start.includes('ph.suppressEffectToken=null;heal(w,3)'),'Phoenix may return from spent after DETONATE without receiving its use-triggered heal for free');
ok(fx.includes("case'revenge3':if(side.detonateMemory>0&&!c.revengeUsed)"),'Revenge Blade checks the preserved previous-DETONATE window');
ok(fx.includes("case'heal2':if(side.detonateMemory>0)heal(w,3)"),'Phoenix heals only when actually used during the preserved previous-DETONATE window');
ok(end.includes('s.detonateMemory=0;'),'the previous-DETONATE action window expires when that owner turn ends');
ok(html.includes('lastDetonateTaken:0,detonateMemory:0,charId'),'new battle side state initializes the timing memory');
console.log('M8 previous-DETONATE timing regression passed.');
