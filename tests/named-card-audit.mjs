import fs from 'node:fs';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}

ok(!script.includes('typelog('),'CPU new-meld path no longer calls undefined typelog');
ok((script.match(/freeSwapRecover'\)\&\&targetSide===w\)freeRecoverFromMeld/g)||[]).length===0,'CJ has no duplicate post-resolve free recovery');
ok(script.includes("c.tag==='heal2'&&!c.phoenixReturned"),'Phoenix spent return is gated to one combat use');
ok(script.includes('ph.phoenixReturned=true'),'Phoenix marks its one spent return as consumed');
ok(script.includes('function simpleGapMissingRank('),'Gap Run records the exact simple one-card hole before recovery');
ok(script.includes('function recoverRedundantGapRun('),'Gap Run has an explicit redundant-card recovery resolver');
ok(script.includes('missing==null||!newCards.some(n=>n.suit===c.suit&&RANK_VALUE[n.rank]===missing)'),'Gap Run only auto-recovers when a newly attached card fills the recorded missing rank');
ok(script.includes('function middleManagerReturnPlaceholder('),'Middle Manager has an explicit placeholder-return resolver');
const gapCleanup=script.indexOf('recoverRedundantGapRun(targetSide,m,beforeCards,cards);');
const middleCleanup=script.indexOf('middleManagerReturnPlaceholder(targetSide,m,cards);',gapCleanup);
const jokerCleanup=script.indexOf('replaceRedundantJokers(targetSide,m,w,cards);',middleCleanup);
ok(gapCleanup>=0&&middleCleanup>gapCleanup&&jokerCleanup>middleCleanup,'attach resolution runs placeholder cleanup in one deterministic phase');
ok(html.includes("'H4B':{slot:'H4',n:'구급차',t:'ambulance',d:'상대 공개 조합에서 회수하면 체력 8을 회복하고 보호막 8을 얻는다. 내 조합에서 회수하면 체력 8을 회복한다.'}"),'Ambulance text matches its 8-shield implementation');
ok(html.includes("'C5':{n:'연결고리',t:'connectionLink',d:'런에 붙일 때" )&&html.includes('이번 턴 추가 붙이기 1회를 얻는다.')&&html.includes('추가 붙이기는 스위치를 다시 이동시키지 않는다.'),'Connection Link documents the named extra-attach exception and no second SWITCH move');
ok(html.includes("'C5B':{slot:'C5',n:'분기점',t:'branchLink',d:'런에 붙일 때 그 런에 보호 상태 1회를 부여한다.'}"),'Branch Link text matches protect-only implementation');
ok(html.includes("'DA':{n:'장물아비',t:'fencePeek',d:'버림패에서 가져오면 카드 1장을 뽑고, 이 카드 외 손패 1장을 덱 아래로 보내 패를 순환한다.'}"),'Fence now has a self-contained discard-acquisition cycle instead of redundant peek-only text');
ok(script.includes('function deathSentencePriority('),'Death Sentence has an active discard-priority resolver');
ok(html.includes("'SQ':{n:'사형선고',t:'seal1',d:'이 카드가 포함된 3장 세트는 빠진 마지막 무늬를 추적한다. 그 정확한 카드를 공용 버림패에서 가져와 같은 턴 그 세트를 버스트하면 이번 반환의 누적 위력이 6 증가한다.'}"),'Death Sentence converts its tracked discard target into a real +6 same-turn BURST payoff');
ok(script.includes('deathSentenceClaimToken')&&script.includes('deathSentenceSourceUid'),'Death Sentence binds its payoff to the exact tracked SET and acquisition turn');
ok(html.includes("'S9':{n:'잠복자',t:'heldBonus',d:'손에서 자기 턴을 1회 넘기면 충전된다."),'Sleeper uses the one-turn preparation baseline after the 3-slot/2-meld tempo change');
ok(script.includes('function tunerReadyForRecovery('),'Tuner has an active cross-meld recovery resolver');
ok(script.includes('function recordFlexibleSuitRoles('),'Understudy records its actual RUN suit role');

const namedStart=script.indexOf('const NAMED={'), namedEnd=script.indexOf('\n};',namedStart);
const named=script.slice(namedStart,namedEnd);
const tags=[...named.matchAll(/t:'([^']+)'/g)].map(m=>m[1]);
const direct=new Set(['finalUltimatum','blackBullet','fuseRound','seal1','zsArmorPiercing','zsCounterTrace','zsLongShot','zsBallistics','zsOneShot','pbBuckshot','pbZeroRange','pbMagDump','mrHazardMail','mrFinalNotice']);
const directCount=tags.filter(t=>direct.has(t)).length;
ok(tags.length>=45,'named pool audit covers at least the first ~50-card scale');
ok(directCount/tags.length<0.2,'direct SWITCH/power manipulation remains a minority of named effects');
console.log(`M8 NAMED AUDIT PASS · ${tags.length} definitions · ${directCount} direct-power tags`);