import fs from 'node:fs';
const html=fs.readFileSync('index.html','utf8');
const road=fs.readFileSync('ROADMAP.md','utf8');
const terms=fs.readFileSync('docs/NEW_USER_UX_TERMS.md','utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
const start=html.indexOf('const NAMED={');
const end=html.indexOf('const UNLOCK_GROUPS=',start);
ok(start>=0&&end>start,'NAMED definition block is discoverable');
const block=html.slice(start,end);
const rows=[...block.matchAll(/'([^']+)':\{[^\n]*?n:'([^']*)'[^\n]*?d:'((?:\\'|[^'])*)'/g)].map(m=>({id:m[1],name:m[2],d:m[3]}));
ok(rows.length>=70,`audits the full live named pool (${rows.length} cards)`);
const fragments=[];
for(const row of rows){
  const sentences=row.d.split('.').map(s=>s.trim()).filter(Boolean);
  for(const sentence of sentences)if(!sentence.endsWith('다'))fragments.push(`${row.id}:${sentence}`);
}
ok(fragments.length===0,`all named-card sentences end as complete declarative/optional sentences${fragments.length?` (${fragments.join(' | ')})`:''}`);
ok(!rows.some(r=>/(폭발를|세트을|세트과)/.test(r.d)),'localized card text has no known post-substitution particle errors');
ok(!rows.some(r=>/(^|\s)\+\d/.test(r.d)),'card descriptions avoid bare +N power shorthand');
ok(!rows.some(r=>/(보호막|체력)\s*\d+\.(?:\s|$)/.test(r.d)),'card descriptions do not end effects as bare shield/health noun fragments');
ok(!rows.some(r=>/\d장\s*뽑기/.test(r.d)),'card descriptions use finite verbs instead of bare draw-count fragments');
ok(!rows.some(r=>/(^|\.\s*)완전 와일드\./.test(r.d)),'Joker descriptions state wildcard treatment as a complete sentence');
ok(rows.find(r=>r.id==='H8')?.d==='조합에 들어갈 때 보호막 20을 얻는다. 스위치가 나를 향하면 보호막 32를 얻는다.','Emergency Gear follows the normalized condition-to-effect style');
ok(rows.find(r=>r.id==='J2')?.d.includes('폭발을 맞으며 러미했다면 피해를 15 줄인다.'),'Last Laugh uses correct particle and finite damage-reduction wording');
ok(rows.find(r=>r.id==='VSD4')?.d.includes('세트를 내가 버스트로'),'V-SIGNAL Gather All uses the correct SET particle');
ok(rows.find(r=>r.id==='CK')?.d.includes('세트와 런이 모두 있으면'),'Tuner uses natural Korean coordination');
ok(road.includes('- [x] 카드 효과 문체 통일'),'ROADMAP marks card-effect style normalization complete');
ok(terms.includes('사용자 노출 카드 효과는 **조건 → 효과** 순서의 서술형을 우선한다.'),'official terminology doc locks the card-text style rule');
ok(terms.includes('선택할 수 있는 효과만 `~할 수 있다.`'),'official style guide distinguishes mandatory and optional effects');
console.log('Card effect style normalization regression passed.');
