import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const master=fs.readFileSync(new URL('../docs/ROGUELIKE_MASTER_PLAN.md',import.meta.url),'utf8');
const starters=fs.readFileSync(new URL('../docs/ROGUELIKE_DECK_STARTERS.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function declaration(name){const marker=`const ${name}=`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let quote=null,esc=false,depth=0,started=false;for(let i=start+marker.length;i<script.length;i++){const ch=script[i];if(quote){if(esc)esc=false;else if(ch==='\\')esc=true;else if(ch===quote)quote=null;continue}if(ch==='\''||ch==='"'||ch==='`'){quote=ch;continue}if(ch==='{'||ch==='['||ch==='('){depth++;started=true}else if(ch==='}'||ch===']'||ch===')')depth--;else if(ch===';'&&started&&depth===0)return script.slice(start,i+1)}throw new Error(`unterminated declaration ${name}`)}
new Function(script);
const ctx=vm.createContext({console,Date,Math,Object,Array,String,JSON,Map,Set});
for(const name of ['NAMED','CHARACTERS','TENDENCY_BY_TAG','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_LOADOUTS'])vm.runInContext(declaration(name),ctx);
vm.runInContext('const ROGUELIKE_STARTER_DECK_SIZE=30; const ROGUELIKE_STARTER_NAMED_REGULAR_COUNT=6;',ctx);
vm.runInContext(source('normalizeRoguelikeStarterId'),ctx);
vm.runInContext(source('roguelikeStarterLoadout'),ctx);
vm.runInContext(source('roguelikeStarterDeckPlan'),ctx);
const starters4=['wanderer','collector','salvager','jester'];
const baseline=new Set(vm.runInContext('[...ROGUELIKE_STARTER_REGULAR_SLOTS]',ctx));
const seen=new Set();
for(const starter of starters4){
  const load=vm.runInContext(`roguelikeStarterLoadout('${starter}')`,ctx);
  const ids=Object.values(load.regular);
  ok(ids.length===6,`${starter} has exactly six regular named starters`);
  ok(new Set(Object.keys(load.regular)).size===6,`${starter} uses six distinct canonical regular slots`);
  for(const [slot,id] of Object.entries(load.regular)){
    const def=vm.runInContext(`NAMED[${JSON.stringify(id)}]`,ctx);
    ok(!!def,`${starter} regular ${id} exists in live NAMED data`);
    ok((def.slot||id)===slot&&baseline.has(slot),`${starter} ${id} preserves a canonical starter slot`);
    ok(!def.themeId,`${starter} ${id} is generic rather than theme-locked`);
    ok(!seen.has(id),`${starter} ${id} is not shared by another v1 starter`);seen.add(id);
  }
  const jdef=vm.runInContext(`NAMED[${JSON.stringify(load.joker)}]`,ctx);
  ok(!!jdef&&String(load.joker).startsWith('J'),`${starter} has a live named Joker`);
  ok(!seen.has(load.joker),`${starter} Joker ${load.joker} is not shared by another v1 starter`);seen.add(load.joker);
  const plan=vm.runInContext(`roguelikeStarterDeckPlan('${starter}')`,ctx);
  ok(plan.cardBlueprints.length===30&&plan.namedRegularIds.length===6&&plan.jokerVariantId===load.joker,`${starter} materializes a 30-card blueprint with its 6+1 named ids`);
  ok(plan.cardBlueprints.filter(x=>x.slot!=='J'&&x.variantId).length===6&&plan.cardBlueprints.filter(x=>x.slot==='J'&&x.variantId).length===1,`${starter} blueprint has exactly six named regulars and one named Joker`);
  const affinity={};
  for(const target of starters4){
    const weights=vm.runInContext(`CHARACTERS[${JSON.stringify(target)}].weights`,ctx);
    affinity[target]=[...ids,load.joker].reduce((sum,id)=>{const tag=vm.runInContext(`NAMED[${JSON.stringify(id)}].t`,ctx);const tendencies=vm.runInContext(`TENDENCY_BY_TAG[${JSON.stringify(tag)}]||[]`,ctx);return sum+tendencies.reduce((n,t)=>n+(weights[t]||0),0)},0);
  }
  const best=Math.max(...Object.values(affinity));
  ok(affinity[starter]===best&&Object.entries(affinity).filter(([,v])=>v===best).length===1,`${starter} loadout has uniquely highest affinity for its own character weights`);
}
const pure=vm.runInContext("roguelikeStarterDeckPlan('pure')",ctx);
ok(pure.cardBlueprints.length===30&&pure.namedRegularIds.length===0&&pure.jokerVariantId===null,'PURE blueprint stays 30 cards with zero named variants');
ok(pure.cardBlueprints.slice(0,29).every(x=>x.variantId===null&&x.pure)&&pure.cardBlueprints[29].slot==='J'&&pure.cardBlueprints[29].baseWild===true,'PURE blueprint is 29 pure regulars plus the effectless base wild Joker');
ok(road.includes('- [x] 캐릭터별 실제 시작 네임드 6 + 조커 1 조합 확정'),'ROADMAP closes actual v1 starter named composition');
ok(master.includes('## 16. 실제 스타터 네임드 조립 v1')&&master.includes('ROGUELIKE_STARTER_LOADOUTS'),'master plan records the actual starter loadout contract');
ok(starters.includes('H2 귀환자, C5 연결고리')&&starters.includes('C8 복사기, D6 예약 발송'),'starter doc exposes the locked character loadouts');
console.log('M11A starter loadout regression passed.');
