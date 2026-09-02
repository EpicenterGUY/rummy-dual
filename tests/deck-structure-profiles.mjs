import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const doc=fs.readFileSync(new URL('../docs/DECK_STRUCTURE_PROFILES.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw Error(`unterminated ${name}`)}
function declaration(name){const marker=`const ${name}=`,start=script.indexOf(marker);if(start<0)throw Error(`missing ${name}`);let q=null,e=false,d=0,seen=false;for(let i=start+marker.length;i<script.length;i++){const ch=script[i];if(q){if(e)e=false;else if(ch==='\\')e=true;else if(ch===q)q=null;continue}if(ch==="'"||ch==='"'||ch==='`'){q=ch;continue}if(ch==='{'||ch==='['||ch==='('){d++;seen=true}else if(ch==='}'||ch===']'||ch===')')d--;else if(ch===';'&&seen&&d===0)return script.slice(start,i+1)}throw Error(`unterminated ${name}`)}
new Function(script);
const ctx=vm.createContext({console,Math,Object,Array,Set,Map});
vm.runInContext("const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};",ctx);
vm.runInContext(declaration('DECK_STRUCTURE_PROFILES'),ctx);
for(const n of ['parseRegularId','deckStructureShuffle','deckStructureSlots','deckStructureHandFit'])vm.runInContext(source(n),ctx);
const all=new Set(['S','H','D','C'].flatMap(s=>['A','2','3','4','5','6','7','8','9','10','J','Q','K'].map(r=>s+r)));
for(const id of ['set','run','mixed'])for(const value of [0,.17,.49,.83]){let i=0,seq=[value,.31,.67,.11,.91];const slots=ctx.deckStructureSlots(id,()=>seq[(i++)%seq.length]);ok(slots.length===29,`${id} produces exactly 29 regular slots`);ok(new Set(slots).size===29,`${id} has no duplicate physical slots`);ok(slots.every(x=>all.has(x)),`${id} uses only legal rank+suit slots`)}
const zero=()=>0,setSlots=ctx.deckStructureSlots('set',zero),runSlots=ctx.deckStructureSlots('run',zero),mixSlots=ctx.deckStructureSlots('mixed',zero),setFit=ctx.deckStructureHandFit(setSlots,6,4096),runFit=ctx.deckStructureHandFit(runSlots,6,4096),mixFit=ctx.deckStructureHandFit(mixSlots,6,4096);
ok(setFit.setRate>runFit.setRate*3,'SET profile materially favors SET-ready six-card hands');
ok(runFit.runRate>setFit.runRate*3,'RUN profile materially favors RUN-ready six-card hands');
ok(Math.abs(mixFit.setRate-mixFit.runRate)<.05,'mixed profile keeps SET/RUN six-card rates near each other');
ok(mixFit.anyRate>=Math.min(setFit.anyRate,runFit.anyRate),'mixed profile keeps competitive any-meld hand resilience');
ok(script.includes("selectedStructure:'mixed'")&&script.includes('DECK_STRUCTURE_PROFILES,x.selectedStructure'),'selected structure persists independently in progress');
ok(html.includes('id="deckStructureGrid"')&&script.includes('[data-deck-structure]'),'battle setup exposes an independent structure picker');
ok(script.includes("displayName:'세트형'")&&script.includes("displayName:'런형'")&&script.includes("displayName:'혼합형'"),'structure picker uses official Korean meld terminology');
ok(script.includes("const structureSlots=owner==='player'?deckStructureSlots(progress.selectedStructure||'mixed'):null"),'automatic player deck fixes geometry before named variants');
ok(script.includes('chooseNamedForBuild(unlocked,charId,buildTheme,structureSlots)'),'theme/named selection is bounded by admitted structure slots');
ok(script.includes("if(!structureSlots){const support=[]"),'CPU keeps the legacy support-based deck generation path');
ok(script.includes("deckStructureSlots(progress.selectedStructure||'mixed',()=>0)"),'custom recommended reset follows the selected structure');
ok(road.includes('## M4B — 덱 조합 구조 축: 세트 / 런 / 혼합'),'ROADMAP contains the new deck-structure milestone');
ok(doc.includes('조합 골격 29슬롯 → 네임드/테마 변형 배치 → 조커 1장'),'canonical structure doc locks geometry-before-theme order');
console.log('Deck structure SET/RUN/mixed regression passed.',{setFit,runFit,mixFit});
