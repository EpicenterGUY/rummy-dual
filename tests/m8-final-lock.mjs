import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('\n};',namedStart),named=script.slice(namedStart,namedEnd);
const defs=[...named.matchAll(/'([^']+)':\{[^\n]*?t:'([^']+)'/g)].map(m=>({id:m[1],tag:m[2]}));
ok(defs.length>=50,`final named lock covers first ~50 scale (${defs.length} live definitions)`);
ok(new Set(defs.map(x=>x.id)).size===defs.length,'named IDs are unique in the locked pool');

const resolve=source('resolveEffects'),onDraw=source('onDiscardDraw'),triggerRummy=source('triggerRummy');
const requiredChoiceSignatures=[
 ['S4/SJ/H5/C5/CJ/J3 free recovery','requestFreeRecoverChoice'],
 ['S9 opponent meld target','requestOpponentMeldChoice'],
 ['D9 spent recycle','requestSpentRecycleChoice'],
 ['DJ exact extortion card','requestExtortChoice'],
 ['C2 optional hand bottom','requestEffectChoice'],
];
for(const [label,sig] of requiredChoiceSignatures)ok(resolve.includes(sig),`${label} remains routed through shared/resumable choice handling`);
ok(onDraw.includes("c.tag==='bait'")&&onDraw.includes('requestHandBottomChoice'),'H3 Bait uses exact hand-bottom choice');
ok(source('requestParasiteReturnCycles').includes('requestEffectChoice'),'C7 Parasite uses exact discard choice');
ok(triggerRummy.includes("title:'마지막 웃음'")&&triggerRummy.includes('requestHandBottomChoice'),'J2 Last Laugh uses exact post-RUMMY bottom choice');
ok(source('playerDiscard').includes("c.tag==='topDeckChoice'")&&source('playerDiscard').includes('requestEffectChoice'),'D6 Reserved Shipping uses the shared decision modal');

ok(html.includes("'D7':{n:'황금손'")&&html.includes('가장 오래 든 1장을 덱 아래로 보낸다.'),'Golden Hand explicitly documents deterministic oldest-card cycling');
ok(html.includes("'D8':{n:'환전상'")&&html.includes('가장 오래 든 카드 1장을 덱 아래로 보내고 카드 1장을 뽑는다.'),'Money Changer explicitly documents deterministic oldest-card cycling');
ok(html.includes("'DQ':{n:'시장 조작자'")&&html.includes('공용 버림패 위 3장의 순서를 뒤집는다.'),'Market Maker explicitly documents deterministic reversal rather than a missing reorder choice');
ok(html.includes("'C6':{n:'중간관리자'")&&script.includes('function middleManagerReturnPlaceholder('),'Middle Manager keeps deterministic legal placeholder cleanup matching its one-placeholder wording');

ok(!script.includes('function autoExtortToNewMeld('),'legacy first-candidate Extortion path cannot return');
ok(!script.includes("attacher!==j.owner"),'Rebel replacement lock no longer depends on who supplied the replacement');
ok(!script.includes("for(const pz of m.cards)if(pz.tag==='parasite'"),'legacy Parasite oldest-card auto-discard path cannot return');
ok(!script.includes('meldsOf(foe)[0]'),'no named opponent-meld target silently hardcodes the first meld');
ok(!resolve.includes('confirm('),'named effect resolver contains no blocking browser confirm choices');

ok(road.includes('- [x] Stabilize first ~50 named cards'),'roadmap marks first ~50 named cards behavior-stable');
ok(road.includes('first ~50 named-card behavior is now locked by executable final-audit coverage'),'roadmap records completion of the remaining choice/copy/timing audit');
console.log('M8 FINAL LOCK PASS');