import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
const start=html.indexOf('const NAMED={');
const end=html.indexOf('const UNLOCK_GROUPS=',start);
ok(start>=0&&end>start,'NAMED definition block is discoverable');
const block=html.slice(start,end);
const desc=[...block.matchAll(/d:'((?:\\'|[^'])*)'/g)].map(m=>m[1]);
ok(desc.length>=70,`audits the full live named pool (${desc.length} descriptions)`);
const forbidden=['SWITCH','DETONATE','CORE','SET','RUN','RUMMY','CHAIN','BURST','OVERLOAD'];
for(const term of forbidden)ok(!desc.some(d=>new RegExp(`(^|[^A-Za-z])${term}([^A-Za-z]|$)`).test(d)),`card descriptions expose no legacy ${term} rule term`);
ok(desc.some(d=>d.includes('스위치')),'localized descriptions retain official 스위치 terminology');
ok(desc.some(d=>d.includes('폭발')),'localized descriptions retain official 폭발 terminology');
ok(desc.some(d=>d.includes('세트'))&&desc.some(d=>d.includes('런')),'localized descriptions use 세트/런');
ok(desc.some(d=>d.includes('러미'))&&desc.some(d=>d.includes('버스트'))&&desc.some(d=>d.includes('체인')),'localized descriptions use 러미/버스트/체인');
ok(road.includes('- [x] 카드 효과문의 한영 혼용 제거'),'ROADMAP marks card-effect mixed-language cleanup complete');
console.log('Card effect terminology localization regression passed.');
