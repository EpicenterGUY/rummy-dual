from pathlib import Path

p=Path('index.html')
s=p.read_text()

def rep(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    s=s.replace(old,new,1)

# Text/behavior synchronization for deterministic prototype behavior.
rep("'S6':{n:'복수의 칼날',t:'revenge3',d:'직전 DETONATE를 내가 맞았다면 사용 시 보호막 16. 전투당 첫 발동에는 카드 1장도 뽑는다.'},",
    "'S6':{n:'복수의 칼날',t:'revenge3',d:'직전 DETONATE를 내가 맞았다면 전투당 1회, 사용 시 보호막 16 + 카드 1장 뽑기.'},",
    'revenge text')
rep("'H4B':{slot:'H4',n:'구급차',t:'ambulance',d:'상대 공개 조합에서 회수하면 체력 8 회복 + 보호막 10. 내 조합에서 회수하면 체력 8 회복.'},",
    "'H4B':{slot:'H4',n:'구급차',t:'ambulance',d:'상대 공개 조합에서 회수하면 체력 8 회복 + 보호막 8. 내 조합에서 회수하면 체력 8 회복.'},",
    'ambulance text')
rep("'DA':{n:'장물아비',t:'fencePeek',d:'버림패에서 가져올 때 바로 아래 카드도 확인. 같은 숫자 또는 무늬라면 두 카드 중 하나로 바꿔 가져올 수 있다.'},",
    "'DA':{n:'장물아비',t:'fencePeek',d:'버림패에서 가져올 때 바로 아래 카드도 함께 확인한다.'},",
    'fence text')
rep("'D7':{n:'황금손',t:'goldenHand',d:'버림패에서 가져온 카드와 같은 조합 행동에 들어가면 1장 뽑고, 손패 1장을 덱 아래로 보낼 수 있다.'},",
    "'D7':{n:'황금손',t:'goldenHand',d:'버림패에서 가져온 카드와 같은 조합 행동에 들어가면 1장 뽑고, 남은 손패가 있으면 그중 가장 오래 든 1장을 덱 아래로 보낸다.'},",
    'golden hand text')
rep("'D8':{n:'환전상',t:'exchangeCycle',d:'SET에 사용할 때 손패 1장을 덱 아래로 보내고 1장 뽑을 수 있다. 4SET이면 최대 2번.'},",
    "'D8':{n:'환전상',t:'exchangeCycle',d:'SET에 사용할 때 남은 손패가 있으면 가장 오래 든 1장을 덱 아래로 보내고 1장 뽑는다. 4SET이면 최대 2번.'},",
    'exchange text')
rep("'CA':{n:'재귀 함수',t:'repeatNumeric',d:'같은 행동에서 먼저 발동한 다른 네임드의 뽑기·회수·보호막·카드 이동 효과 하나를 한 번 반복한다. 누적 위력 증폭은 복사하지 않는다.'},",
    "'CA':{n:'재귀 함수',t:'repeatNumeric',d:'같은 행동의 다른 네임드가 연결자면 1장 뽑기, 응급 보호구면 보호막 12, 갈아끼우기면 무료 회수 1회를 반복한다. 누적 위력은 복사하지 않는다.'},",
    'recursive text')
rep("'C5':{n:'연결고리',t:'connectionLink',d:'RUN에 붙일 때 그 RUN의 내 제어 카드 1장을 무료 회수할 수 있다. 빼도 RUN은 유효해야 한다.'},",
    "'C5':{n:'연결고리',t:'connectionLink',d:'RUN에 붙일 때 그 RUN의 내 제어 카드 1장을 무료 회수할 수 있다. 빼도 RUN은 유효해야 하며, 그 RUN에는 이번 턴 한 번 더 붙일 수 있다.'},",
    'connection link text')
rep("'C5B':{slot:'C5',n:'분기점',t:'branchLink',d:'RUN에 붙일 때 그 조합의 내 카드 1장을 무료 회수하거나, 그 RUN에 보호 상태 1회를 부여한다.'},",
    "'C5B':{slot:'C5',n:'분기점',t:'branchLink',d:'RUN에 붙일 때 그 RUN에 보호 상태 1회를 부여한다.'},",
    'branch link text')
rep("'C8':{n:'복사기',t:'copier',d:'같은 조합에서 다른 네임드의 낼 때/붙일 때 효과 하나를 복사한다. 동일 카드 효과는 복사하지 않는다.'},",
    "'C8':{n:'복사기',t:'copier',d:'같은 행동의 다른 네임드가 응급 보호구면 보호막 20, 연결자면 1장 뽑기를 복사한다.'},",
    'copier text')

# CPU new-meld runtime crash: missing separator accidentally formed typelog(...).
rep("else state.lastEnemyMeldType=typelog(`", "else state.lastEnemyMeldType=type;log(`", 'CPU new meld typelog')

# Phoenix may return from spent only once per combat, as written.
rep("const pi=s.spent.findIndex(c=>c.tag==='heal2');if(pi>=0){const [ph]=s.spent.splice(pi,1);s.hand.push(ph);ph.suppressEffectToken=null;heal(w,3);log(`${ph.name}: 폭발 뒤 소모패에서 귀환.`,'good')}",
    "const pi=s.spent.findIndex(c=>c.tag==='heal2'&&!c.phoenixReturned);if(pi>=0){const [ph]=s.spent.splice(pi,1);s.hand.push(ph);ph.phoenixReturned=true;ph.suppressEffectToken=null;heal(w,3);log(`${ph.name}: 폭발 뒤 소모패에서 1회 귀환.`,'good')}",
    'phoenix one-time return')

# Bring two advertised meld-mutation cards online.
anchor="function replaceRedundantJokers(targetSide,m,attacher){"
if s.count(anchor)!=1:
    raise SystemExit(f'placeholder helper anchor: expected 1, got {s.count(anchor)}')
helpers="""function recoverRedundantGapRun(targetSide,m){for(let i=m.cards.length-1;i>=0;i--){const c=m.cards[i];if(c.tag!=='gapRun'||cardFixedActive(c))continue;const remain=m.cards.filter((_,j)=>j!==i);if(remain.length<3||meldType(remain)!==m.type)continue;m.cards.splice(i,1);if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);sideObj(c.owner).hand.push(c);c.suppressEffectToken=state.turnToken;c.recoveredToken=state.turnToken;c.recoverReturnOverrideToken=null;c.age=0;markSetCompletion(m,targetSide);log(`${c.name}: 빠진 실제 카드가 채워져 무료 회수${m.type==='RUN'?' · CHAIN -1':''}.`,'good');return c}return null}
function middleManagerReturnPlaceholder(targetSide,m,newCards){if(!newCards.some(c=>c.tag==='middleManager'))return null;for(let i=m.cards.length-1;i>=0;i--){const c=m.cards[i];if(newCards.some(n=>n.uid===c.uid)||!['gapRun','jokerKing','vacancyJoker','rebelJoker'].includes(c.tag)||cardFixedActive(c))continue;const remain=m.cards.filter((_,j)=>j!==i);if(remain.length<3||meldType(remain)!==m.type)continue;m.cards.splice(i,1);if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);sideObj(c.owner).hand.push(c);c.suppressEffectToken=state.turnToken;c.recoveredToken=state.turnToken;c.recoverReturnOverrideToken=null;c.age=0;markSetCompletion(m,targetSide);log(`중간관리자: 대체재 ${c.name}를 원주인 손으로 반환${m.type==='RUN'?' · CHAIN -1':''}.`,'good');return c}return null}
"""
s=s.replace(anchor,helpers+anchor,1)

# CJ already performs its one free recovery inside resolveEffects; remove the duplicate second attempt.
rep("if(cards.some(c=>c.tag==='freeSwapRecover')&&targetSide===w)freeRecoverFromMeld(w,m,cards);", "", 'duplicate freeSwapRecover')

# After an attach, resolve advertised redundant-card replacement behaviors.
rep("for(const c of cards)if(c.tag==='cutLine'&&targetSide===other(w))interfered=cutOppositeEnd(w,targetSide,m,c)||interfered;replaceRedundantJokers(targetSide,m,w);",
    "for(const c of cards)if(c.tag==='cutLine'&&targetSide===other(w))interfered=cutOppositeEnd(w,targetSide,m,c)||interfered;recoverRedundantGapRun(targetSide,m);middleManagerReturnPlaceholder(targetSide,m,cards);replaceRedundantJokers(targetSide,m,w);",
    'post-attach placeholder replacement')

p.write_text(s)

# New executable audit/regression suite for the first M8 stabilization tranche.
t=Path('tests/named-card-audit.mjs')
t.write_text(r"""import fs from 'node:fs';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}

ok(!script.includes('typelog('),'CPU new-meld path no longer calls undefined typelog');
ok((script.match(/freeSwapRecover'\)\&\&targetSide===w\)freeRecoverFromMeld/g)||[]).length===0,'CJ has no duplicate post-resolve free recovery');
ok(script.includes("c.tag==='heal2'&&!c.phoenixReturned"),'Phoenix spent return is gated to one combat use');
ok(script.includes('ph.phoenixReturned=true'),'Phoenix marks its one spent return as consumed');
ok(script.includes('function recoverRedundantGapRun('),'Gap Run has an explicit redundant-card recovery resolver');
ok(script.includes('function middleManagerReturnPlaceholder('),'Middle Manager has an explicit placeholder-return resolver');
ok(script.includes('recoverRedundantGapRun(targetSide,m);middleManagerReturnPlaceholder(targetSide,m,cards);replaceRedundantJokers'),'attach resolution runs placeholder cleanup in one deterministic phase');
ok(html.includes("'H4B':{slot:'H4',n:'구급차',t:'ambulance',d:'상대 공개 조합에서 회수하면 체력 8 회복 + 보호막 8."),'Ambulance text matches its 8-shield implementation');
ok(html.includes("'C5':{n:'연결고리',t:'connectionLink',d:'RUN에 붙일 때" )&&html.includes('그 RUN에는 이번 턴 한 번 더 붙일 수 있다.'),'Connection Link documents its extra-attach behavior');
ok(html.includes("'C5B':{slot:'C5',n:'분기점',t:'branchLink',d:'RUN에 붙일 때 그 RUN에 보호 상태 1회를 부여한다.'}"),'Branch Link text matches protect-only implementation');
ok(html.includes("'DA':{n:'장물아비',t:'fencePeek',d:'버림패에서 가져올 때 바로 아래 카드도 함께 확인한다.'}"),'Fence text no longer promises an unimplemented swap');

const namedStart=script.indexOf('const NAMED={'), namedEnd=script.indexOf('\n};',namedStart);
const named=script.slice(namedStart,namedEnd);
const tags=[...named.matchAll(/t:'([^']+)'/g)].map(m=>m[1]);
const direct=new Set(['finalUltimatum','blackBullet','fuseRound']);
const directCount=tags.filter(t=>direct.has(t)).length;
ok(tags.length>=45,'named pool audit covers at least the first ~50-card scale');
ok(directCount/tags.length<0.2,'direct SWITCH/power manipulation remains a minority of named effects');
console.log(`M8 NAMED AUDIT PASS · ${tags.length} definitions · ${directCount} direct-power tags`);
""")

# Roadmap: close only this correctness tranche, keep M8 content stabilization open.
r=Path('ROADMAP.md')
road=r.read_text()
old="""## M8 — Named cards
- [ ] Stabilize first ~50 named cards
- [ ] Keep direct SWITCH manipulation to a minority of the pool
- [ ] Favor meld mutation, recovery, movement, discard, defense, RUMMY and timing interactions
"""
new="""## M8 — Named cards
- [ ] Stabilize first ~50 named cards
- [x] First correctness pass: fix CPU new-meld crash, duplicate CJ recovery, Phoenix one-time return, and revive Gap Run / Middle Manager placeholder behavior
- [x] Synchronize deterministic card text for Revenge Blade, Ambulance, Fence, Golden Hand, Money Changer, Recursive Function, Connection Link, Branch Link and Copier
- [x] Keep direct SWITCH manipulation to a minority of the audited pool with an executable ratio guard
- [ ] Finish dead/partial-effect audit for choice-heavy and timing-heavy cards such as Death Sentence, Doppelganger support interactions, Tuner, and role-sensitive understudy behavior
- [ ] Favor meld mutation, recovery, movement, discard, defense, RUMMY and timing interactions
"""
if road.count(old)!=1:
    raise SystemExit(f'roadmap M8 block: expected 1, got {road.count(old)}')
road=road.replace(old,new,1)
old2="""## Current next work
1. M8: audit the first ~50 named cards against the locked rules, normalized statuses and current effect timings; fix text/implementation mismatches before adding more content.
2. M8: rebalance the pool so direct SWITCH/power manipulation remains a minority and meld/recovery/discard/defense/RUMMY interactions carry most variety.
3. Gradually migrate repeated named-card effect patterns onto the M7 action/event vocabulary only where it reduces duplication without changing behavior.
"""
new2="""## Current next work
1. M8: finish the remaining dead/partial named effects, especially Death Sentence (`seal1`) and Tuner (`alternateBonus`), before adding more cards.
2. M8: audit copy/choice-heavy cards and role-sensitive return behavior with executable per-card regressions instead of text-only promises.
3. After the first ~50 are behavior-stable, rebalance frequency/strength and only then expand content or move to M9 Jokers/fields.
"""
if road.count(old2)!=1:
    raise SystemExit(f'roadmap current-next block: expected 1, got {road.count(old2)}')
r.write_text(road.replace(old2,new2,1))
