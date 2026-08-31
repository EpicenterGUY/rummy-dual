import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road = fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}
function functionSource(name) {
  const marker = `function ${name}(`;
  const start = script.indexOf(marker);
  if (start < 0) throw new Error(`missing function ${name}`);
  const bodyMarker = script.indexOf('){', start);
  const brace = bodyMarker + 1;
  let depth=0,end=-1;
  for(let i=brace;i<script.length;i++){
    if(script[i]==='{')depth++;
    else if(script[i]==='}') {depth--; if(depth===0){end=i+1;break}}
  }
  if(end<0)throw new Error(`unterminated function ${name}`);
  return script.slice(start,end);
}

new Function(script);

{
  const ctx=vm.createContext({console,Math,Array,Object,Set,Map});
  Object.assign(ctx,{
    NAMED:{A:{slot:'S5'},B:{slot:'S5'},C:{slot:'H5'},J1:{}},
    weightedPick:entries=>entries[0]
  });
  vm.runInContext(functionSource('namedSlot'),ctx);
  vm.runInContext(functionSource('weightedVariantSample'),ctx);
  ok(ctx.namedSlot('A')==='S5'&&ctx.namedSlot('B')==='S5', 'different named IDs can canonicalize to the same exact rank+suit slot');
  ok(ctx.namedSlot('J1')==='J1', 'Joker identities remain outside the 52 regular rank+suit slots');
  const picked=ctx.weightedVariantSample(['A','B','C'],3,()=>1);
  ok(picked.length===2, 'variant sampling cannot consume two candidates from the same canonical slot');
  ok(picked.filter(id=>ctx.namedSlot(id)==='S5').length===1, 'exactly one S5 variant survives sampling');
  ok(picked.some(id=>ctx.namedSlot(id)==='H5'), 'a distinct exact slot remains independently selectable');
}

ok(html.includes('const variantBySlot=new Map(namedChosen.map(id=>[namedSlot(id),id]))'), 'battle build maps exactly one chosen variant onto each canonical slot');
ok(html.includes('const slots=new Set(namedChosen.map(namedSlot))'), 'battle build starts from a deduplicated set of canonical regular slots');
ok(html.includes("const cards=[...slots].slice(0,29).map(slot=>"), 'current battle deck materializes 29 unique regular slots before adding its Joker');
ok(html.includes("cards.push(makeCard('J',jid,true,owner,jid))"), 'current battle deck adds a Joker separately from regular-slot construction');
ok(road.includes('- [x] One variant per exact rank+suit slot'), 'ROADMAP locks the M11 exact-slot variant invariant');

console.log('RUMMY//DUEL M11 exact-slot invariant regression tests passed.');
