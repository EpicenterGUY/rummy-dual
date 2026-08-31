import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const ctx=vm.createContext({Set});vm.runInContext(source('firstCopyEffectSource'),ctx);
const self={uid:'copy',named:true,tag:'copier'},noise={uid:'noise',named:true,tag:'marketMaker'},connector={uid:'link',named:true,tag:'run4Draw'},gear={uid:'gear',named:true,tag:'emergencyGear'};
ok(ctx.firstCopyEffectSource([self,noise,connector],self,['run4Draw','emergencyGear'])===connector,'copy cards skip unrelated named cards instead of fizzling on the first named card');
ok(ctx.firstCopyEffectSource([self,connector,gear],self,['emergencyGear'])===gear,'an ineligible Connector is skipped and a later eligible Emergency Gear can be copied');
const fx=source('resolveEffects');
ok(fx.includes("case'repeatNumeric':{const eligible=['emergencyGear'];if(type==='RUN'&&ctx.totalLength>=4)eligible.push('run4Draw');if(ctx.isAttach&&ctx.targetOwner===w)eligible.push('freeSwapRecover')"),'Recursive Function gates Connector and Free Swap copies by the original effect trigger conditions');
ok(fx.includes("case'copier':{const eligible=['emergencyGear'];if(type==='RUN'&&ctx.totalLength>=4)eligible.push('run4Draw')"),'Copier only offers Connector as a copy source when Connector would actually trigger');
ok(html.includes('실제 발동 조건을 만족한 효과 하나를 복제한다'),'copy-card text explains the timing rule');
console.log('M8 copy/timing regression passed.');
