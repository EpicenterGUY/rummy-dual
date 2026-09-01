import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const doc=fs.readFileSync(new URL('../docs/ASYMMETRIC_RANK_PROTOTYPE.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const brace=script.indexOf('{',start);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
new Function(script);

for(const name of ['normalizePrototypeRank','ensureRankPrototype','cardPrintedRanks','isAsymmetricRankCard','cardRuleRank','chooseCardActiveRank','clearCardActiveRank','rankChoiceState'])ok(script.includes(`function ${name}(`),`rank scaffold helper exists: ${name}`);

{
  const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
  const ctx=vm.createContext({console,Object,Math,RANK_VALUE,NAMED:{S7X:{n:'회전 시험',d:'시험',t:'test',topRank:'3',bottomRank:'7'}},uidSeq:1});
  for(const name of ['normalizePrototypeRank','ensureRankPrototype','cardPrintedRanks','isAsymmetricRankCard','cardRuleRank','chooseCardActiveRank','clearCardActiveRank','rankChoiceState','makeCard'])vm.runInContext(source(name),ctx);
  const pure=ctx.makeCard('S','7',false,'player');
  ok(pure.baseRank==='7'&&pure.topRank==='7'&&pure.bottomRank==='7'&&pure.activeRank===null,'ordinary card materializes as symmetric X/X with no active rank');
  ok(pure.rank==='7'&&!ctx.isAsymmetricRankCard(pure),'ordinary live card keeps legacy rank behavior');
  const asym=ctx.makeCard('S','7',true,'player','S7X');
  ok(asym.baseRank==='7'&&asym.topRank==='3'&&asym.bottomRank==='7','prototype named card preserves S7 base slot while exposing 3/7 printed ranks');
  ok(asym.rank==='7'&&asym.activeRank===null&&ctx.isAsymmetricRankCard(asym),'asymmetric card is unresolved and mirrors baseRank outside a meld');
  ok(ctx.chooseCardActiveRank(asym,'3','top')===true,'top printed rank can be selected');
  ok(asym.activeRank==='3'&&asym.rank==='3'&&asym.rankOrientation==='top','selected activeRank is mirrored through legacy rank inside the prototype meld state');
  ok(ctx.cardRuleRank(asym)==='3','rule-rank helper reads active rank when resolved');
  ok(ctx.chooseCardActiveRank(asym,'K')===false,'rank choice cannot escape the two printed values');
  ctx.clearCardActiveRank(asym);
  ok(asym.activeRank===null&&asym.rankOrientation===null&&asym.rank==='7','leaving a meld clears orientation and restores base rank');
  ok(ctx.chooseCardActiveRank(asym,'7','bottom')===true&&asym.rankOrientation==='bottom','bottom orientation remains distinguishable even when it equals baseRank');
  const state=ctx.state={discard:[]};
  const player={hand:[]};
  ctx.sideObj=()=>player;ctx.resetHandPreparation=()=>null;
  vm.runInContext(source('enterHand'),ctx);
  ctx.enterHand('player',asym);
  ok(asym.activeRank===null&&asym.rank==='7'&&player.hand.includes(asym),'enterHand centralizes outside-meld rank reset');
  ctx.chooseCardActiveRank(asym,'3','top');
  vm.runInContext(source('pushDiscard'),ctx);
  ctx.pushDiscard(asym);
  ok(asym.activeRank===null&&asym.rank==='7'&&state.discard.at(-1)===asym,'shared discard centralizes outside-meld rank reset');
  const joker=ctx.makeCard('J','J1',false,'player','J1');
  ok(joker.baseRank===null&&joker.topRank===null&&joker.bottomRank===null&&joker.activeRank===null,'Joker remains outside asymmetric regular-rank scaffold');
}

const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('const FIELDS=',namedStart),namedBlock=script.slice(namedStart,namedEnd);
ok(namedStart>=0&&namedEnd>namedStart,'live NAMED block is discoverable');
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'no live asymmetric card definition is enabled by the compatibility scaffold');
ok(source('retireMeld').includes("typeof clearCardActiveRank==='function')clearCardActiveRank(c)"),'public-meld retirement resets active rank before hand/deck/spent destinations');
ok(source('fullRecirculation').includes("typeof clearCardActiveRank==='function')clearCardActiveRank(c)"),'full recirculation resets active rank before rebuilding decks');
ok(doc.includes('`rank`: 기존 엔진 호환 미러')&&doc.includes('조합 → 다른 조합 직접 이동'),'prototype document locks legacy-rank mirror and zone lifecycle');
ok(doc.includes('현재 라이브 카드 풀에는 비대칭 카드가 0장'),'prototype document explicitly keeps live asymmetric count at zero');
for(const text of [
  '기존 단일 `rank`와 호환되는 `baseRank / topRank / bottomRank / activeRank` 데이터 구조 설계',
  '손에서는 `activeRank` 미확정, 조합 투입 시 확정, 조합을 떠나 손으로 돌아오면 다시 미확정으로 초기화하는 생명주기 명문화',
  '버림패·소모패·덱·재순환처럼 조합 밖 영역에서는 방향 선택 상태를 유지하지 않는 기본안 검증'
])ok(road.includes(`- [x] ${text}`),`ROADMAP locks M11B scaffold item: ${text}`);
ok(road.includes('새 조합 생성·붙이기·다중 붙이기에서 각 비대칭 카드의 사용값 선택 순서와 합법성 미리보기 구조 설계'),'later rank-choice planning remains tracked without forcing a past checklist state');
ok(/- \[[ x]\] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증/.test(road),'selected-rank action/timing integration remains tracked without forcing the original scaffold phase state');
console.log('M11B asymmetric-rank compatibility scaffold regression passed.');
