import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}

ok(html.includes('<title>RUMMY//DUEL</title>')&&!html.includes('<title>RUMMY//DUEL - FINAL CORE 2.0</title>'),'browser title drops obsolete FINAL CORE version label');
const rulesStart=html.indexOf('<div id="rulesOverlay"'),rulesEnd=html.indexOf('<div id="developerOverlay"',rulesStart);
ok(rulesStart>=0&&rulesEnd>rulesStart,'rules overlay is discoverable');
const rules=html.slice(rulesStart,rulesEnd);
for(const term of ['SET','RUN','BURST','CHAIN','SWITCH','RUMMY','DETONATE','OVERLOAD','CORE','YOU','CPU']){
  ok(!new RegExp(`(^|[^A-Za-z])${term}([^A-Za-z]|$)`).test(rules),`rules overlay exposes no legacy ${term} display term`);
}
ok(rules.includes('과부하 · 코어 파괴 가능')&&rules.includes('현재 코어 체력 + 보호막'),'rules overlay uses official overload/core-lethal wording');

const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const literals=[...scripts.matchAll(/(['`])((?:\\.|(?!\1)[\s\S])*?)\1/g)].map(m=>m[2]).filter(x=>/[가-힣]/.test(x));
const rendered=literals.map(x=>x.replace(/\$\{[^}]*\}/g,'').replaceAll('RUMMY//DUEL',''));
for(const term of ['SET','RUN','BURST','CHAIN','SWITCH','DETONATE','OVERLOAD','CORE','YOU','CPU']){
  const bad=rendered.filter(x=>new RegExp(`(^|[^A-Za-z])${term}([^A-Za-z]|$)`).test(x));
  ok(bad.length===0,`Korean runtime copy exposes no legacy ${term} term`);
}
ok(!scripts.includes("combatBanner('DETONATE DELAY'"),'obsolete DETONATE DELAY banner is removed');
ok(scripts.includes("combatBanner('폭발 유예','rummy',30)"),'grace banner uses official 폭발 유예 wording');
ok(scripts.includes("'나':'상대'"),'runtime side labels use Korean player/opponent wording');
ok(scripts.includes('버스트/체인으로 폭탄을 키워 스위치를 반환합니다.'),'battle intro log uses official Korean combat terms');
ok(road.includes('- [x] 중복 / 폐기된 옛 용어 제거'),'ROADMAP marks obsolete terminology cleanup complete');
console.log('Legacy/deprecated player-facing terminology regression passed.');
