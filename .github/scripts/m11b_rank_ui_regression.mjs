import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('index.html','utf8');
const road=fs.readFileSync('ROADMAP.md','utf8');
const doc=fs.readFileSync('docs/ASYMMETRIC_RANK_PROTOTYPE.md','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
new Function(script);

for(const n of ['cardRankPresentation','rankPrototypeDetailText','rankPrototypeDemoCards','renderAsymmetricRankPrototype'])ok(script.includes(`function ${n}(`),`M11B UI helper exists: ${n}`);
ok(html.includes('id="rankPrototypeCards"'),'developer panel exposes a non-live asymmetric-rank visual prototype surface');
ok(html.includes('/* M11B UI1 · asymmetric top/bottom rank frame prototype */'),'asymmetric-rank frame has a dedicated CSS layer');
ok(html.includes('.card.rankLockedBottom .cardFace{transform:rotate(180deg)}'),'bottom-rank selection physically rotates only the readable card face');
ok(html.includes('.card.rankLockedTop .bottomRankCorner{opacity:.34}')&&html.includes('.card.rankLockedBottom .topRankCorner{opacity:.34}'),'locked orientation de-emphasizes only the unused printed corner');
ok(source('renderDeveloperPanel').includes("renderAsymmetricRankPrototype()"),'developer panel refresh renders the shared asymmetric-card prototype');
ok(source('renderDetail').includes("rankPrototypeDetailText(c)"),'card detail consumes shared asymmetric-rank metadata text');

const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
const SUIT_SYMBOL={S:'♠',H:'♥',D:'♦',C:'♣',J:'★'};
const ctx=vm.createContext({console,Object,Array,Math,RANK_VALUE,SUIT_SYMBOL});
ctx.isJoker=c=>c?.suit==='J';
install(ctx,'normalizePrototypeRank','ensureRankPrototype','cardPrintedRanks','isAsymmetricRankCard','cardRankPresentation','rankPrototypeDetailText','rankPrototypeDemoCards','cardHTML');

const ordinary={uid:1,suit:'S',rank:'7',baseRank:'7',topRank:'7',bottomRank:'7',activeRank:null,rankOrientation:null,named:false,name:'순수 7',themeId:null};
const ordinaryHtml=ctx.cardHTML({...ordinary});
ok(ordinaryHtml.includes('topRankCorner')&&ordinaryHtml.includes('bottomRankCorner'),'ordinary cards use the same shared two-corner frame structure');
ok(!ordinaryHtml.includes('asymmetricRank')&&!ordinaryHtml.includes('rankStateMark'),'ordinary X/X cards gain no asymmetric marker or state class');
ok((ordinaryHtml.match(/>7<br>♠/g)||[]).length===2,'ordinary X/X cards still display the same rank at both corners');

const unresolved={uid:2,suit:'S',rank:'7',baseRank:'7',topRank:'3',bottomRank:'7',activeRank:null,rankOrientation:null,named:true,name:'회전 시험',themeId:null};
const unresolvedHtml=ctx.cardHTML({...unresolved});
ok(unresolvedHtml.includes('asymmetricRank rankUnresolved'),'unresolved X/Y card is visibly classified as asymmetric');
ok(unresolvedHtml.includes('>3<br>♠')&&unresolvedHtml.includes('>7<br>♠'),'unresolved X/Y card prints distinct top and bottom ranks');
ok(unresolvedHtml.includes('↕ 선택')&&unresolvedHtml.includes('>3<br>♠')&&unresolvedHtml.includes('>7<br>♠'),'unresolved X/Y card combines distinct printed corners with an explicit selectable-rank marker');
ok(ctx.rankPrototypeDetailText({...unresolved})===' · 원본 슬롯 7♠ · 인쇄 3/7 · 사용값 미확정','detail text separates original slot, printed ranks, and unresolved use value');

const top={...unresolved,uid:3,rank:'3',activeRank:'3',rankOrientation:'top'};
const topHtml=ctx.cardHTML({...top});
ok(topHtml.includes('rankLocked rankLockedTop')&&topHtml.includes('↑ 3 사용'),'top selection locks the top orientation and selected value');
ok(ctx.rankPrototypeDetailText({...top}).endsWith('사용값 3 ↑ 위'),'detail text exposes the locked top orientation');

const bottom={...unresolved,uid:4,rank:'7',activeRank:'7',rankOrientation:'bottom'};
const bottomHtml=ctx.cardHTML({...bottom});
ok(bottomHtml.includes('rankLocked rankLockedBottom')&&bottomHtml.includes('↓ 7 사용'),'bottom selection locks the bottom orientation and selected value');
ok(ctx.rankPrototypeDetailText({...bottom}).endsWith('사용값 7 ↓ 아래'),'detail text exposes the locked bottom orientation');

const demos=ctx.rankPrototypeDemoCards();
ok(demos.length===3&&demos.map(x=>x.card.rankOrientation||'none').join(',')==='none,top,bottom','developer visual sample covers unresolved, top-locked, and bottom-locked states');

const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('const FIELDS=',namedStart),namedBlock=script.slice(namedStart,namedEnd);
ok(namedStart>=0&&namedEnd>namedStart,'live NAMED block remains discoverable');
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'UI prototype still enables zero live asymmetric card definitions');
ok(doc.includes('UI 프로토타입 단계 1')&&doc.includes('라이브 비대칭 카드 수는 계속 **0장**'),'prototype document records visual-only non-live status');
for(const text of [
 '실제 카드 좌상단·우하단 랭크를 서로 다르게 표시하고 180° 회전 선택이 즉시 읽히는 카드 프레임 프로토타입 제작',
 '조합에 들어간 뒤에는 선택된 사용값이 어느 쪽인지 회전 상태 또는 작은 방향 마커로 명확히 고정 표시',
 '카드 상세에는 `원본 슬롯`, `두 인쇄값`, 현재 조합에 있을 때의 `사용값`을 구분해 표시'
])ok(road.includes(`- [x] ${text}`),`ROADMAP locks M11B UI item: ${text}`);
ok(/- \[[ x]\] 손패에서 비대칭 카드 선택 시 두 사용값과 각각의 합법 세트\/런 후보를 미리보기로 표시/.test(road),'player rank-choice preview remains tracked across later M11B UI phases');
console.log('M11B asymmetric-rank card-frame UI regression passed.');
