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
const jokerCleanup=script.indexOf('replaceRedundantJokers(targetSide,m,w);',middleCleanup);
ok(gapCleanup>=0&&middleCleanup>gapCleanup&&jokerCleanup>middleCleanup,'attach resolution runs placeholder cleanup in one deterministic phase');
ok(html.includes("'H4B':{slot:'H4',n:'구급차',t:'ambulance',d:'상대 공개 조합에서 회수하면 체력 8 회복 + 보호막 8."),'Ambulance text matches its 8-shield implementation');
ok(html.includes("'C5':{n:'연결고리',t:'connectionLink',d:'RUN에 붙일 때" )&&html.includes('그 RUN에는 이번 턴 한 번 더 붙일 수 있다.'),'Connection Link documents its extra-attach behavior');
ok(html.includes("'C5B':{slot:'C5',n:'분기점',t:'branchLink',d:'RUN에 붙일 때 그 RUN에 보호 상태 1회를 부여한다.'}"),'Branch Link text matches protect-only implementation');
ok(html.includes("'DA':{n:'장물아비',t:'fencePeek',d:'버림패에서 가져올 때 바로 아래 카드도 함께 확인한다.'}"),'Fence text no longer promises an unimplemented swap');
ok(script.includes('function deathSentencePriority('),'Death Sentence has an active discard-priority resolver');
ok(script.includes('function tunerReadyForRecovery('),'Tuner has an active cross-meld recovery resolver');
ok(script.includes('function recordFlexibleSuitRoles('),'Understudy records its actual RUN suit role');

const namedStart=script.indexOf('const NAMED={'), namedEnd=script.indexOf('\n};',namedStart);
const named=script.slice(namedStart,namedEnd);
const tags=[...named.matchAll(/t:'([^']+)'/g)].map(m=>m[1]);
const direct=new Set(['finalUltimatum','blackBullet','fuseRound']);
const directCount=tags.filter(t=>direct.has(t)).length;
ok(tags.length>=45,'named pool audit covers at least the first ~50-card scale');
ok(directCount/tags.length<0.2,'direct SWITCH/power manipulation remains a minority of named effects');
console.log(`M8 NAMED AUDIT PASS · ${tags.length} definitions · ${directCount} direct-power tags`);
