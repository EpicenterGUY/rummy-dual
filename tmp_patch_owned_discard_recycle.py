from pathlib import Path

p=Path('index.html')
s=p.read_text()

old="""function recycleIfNeeded(w){const s=sideObj(w);if(!s.deck.length&&s.spent.length){s.deck=shuffle(s.spent.splice(0));log(`${w==='player'?'내':'상대'} 소모패를 섞어 새 덱을 만들었습니다.`,'important')}}
function acquireDiscardCard(w,indexFromTop=0){const s=sideObj(w),idx=state.discard.length-1-indexFromTop;if(idx<0)return null;const[c]=state.discard.splice(idx,1),oldOwner=c.owner;c.owner=w;c.contractActive=false;if(c.tag==='returnIfIgnored'&&oldOwner!==w)c.blockedUntilTurn=state.turnNo;c.fromDiscard=true;c.age=0;s.hand.push(c);return c}
function drawOne(w,fromDiscard=false){const s=sideObj(w);if(fromDiscard)return acquireDiscardCard(w,0);recycleIfNeeded(w);const c=s.deck.pop();if(!c)return null;c.fromDiscard=false;c.contractActive=false;c.age=0;s.hand.push(c);if(!s.deck.length&&s.spent.length)recycleIfNeeded(w);return c}function drawMany(w,n,announce=true){let got=0;for(let i=0;i<n;i++)if(drawOne(w,false))got++;if(announce&&got)log(`${w==='player'?'내':'상대'}가 ${got}장 뽑았습니다.`);return got}"""
new="""function recycleIfNeeded(w){const s=sideObj(w);if(s.deck.length)return 0;const spent=s.spent.splice(0),ownedDiscard=[];for(let i=state.discard.length-1;i>=0;i--){const c=state.discard[i];if(c.owner!==w)continue;ownedDiscard.push(c);state.discard.splice(i,1)}const pool=spent.concat(ownedDiscard);if(!pool.length)return 0;s.deck=shuffle(pool);log(`${w==='player'?'내':'상대'} 재순환 · 소모패 ${spent.length}장${ownedDiscard.length?` + 공용 버림패의 내 카드 ${ownedDiscard.length}장`:''} → 새 덱 ${pool.length}장.`,'important');return pool.length}
function acquireDiscardCard(w,indexFromTop=0){const s=sideObj(w),idx=state.discard.length-1-indexFromTop;if(idx<0)return null;const[c]=state.discard.splice(idx,1),oldOwner=c.owner;c.owner=w;c.contractActive=false;if(c.tag==='returnIfIgnored'&&oldOwner!==w)c.blockedUntilTurn=state.turnNo;c.fromDiscard=true;c.age=0;s.hand.push(c);return c}
function drawOne(w,fromDiscard=false){const s=sideObj(w);if(fromDiscard)return acquireDiscardCard(w,0);recycleIfNeeded(w);const c=s.deck.pop();if(!c)return null;c.fromDiscard=false;c.contractActive=false;c.age=0;s.hand.push(c);if(!s.deck.length)recycleIfNeeded(w);return c}function drawMany(w,n,announce=true){let got=0;for(let i=0;i<n;i++)if(drawOne(w,false))got++;if(announce&&got)log(`${w==='player'?'내':'상대'}가 ${got}장 뽑았습니다.`);return got}"""
assert s.count(old)==1,s.count(old)
s=s.replace(old,new)

old_ui='''<div class="pileStation spentStation"><div class="spentPile" aria-label="내 소모패 · 직접 조작하지 않음 · 덱이 비면 자동 재순환"><span class="spentMark">재순환 대기<br><b id="playerSpentCount">0</b><small>소모패</small></span></div><div class="pileMeta"><span class="drawPath spentPath">사용·정리 → 소모패</span><div class="pileRule"><b class="spentAutoLabel">직접 사용 불가</b> · 덱 0장 시 자동 셔플</div></div></div>'''
new_ui='''<div class="pileStation spentStation"><div class="spentPile" aria-label="내 소모패 · 직접 조작하지 않음 · 덱이 비면 소모패와 공용 버림패의 내 소유 카드 자동 재순환"><span class="spentMark">재순환 대기<br><b id="playerSpentCount">0</b><small>소모패</small></span></div><div class="pileMeta"><span class="drawPath spentPath">사용·정리 → 소모패</span><div class="pileRule"><b class="spentAutoLabel">직접 사용 불가</b><br>덱 0장 → 소모패 + 버림패 내 카드 자동 셔플</div></div></div>'''
assert s.count(old_ui)==1,s.count(old_ui)
s=s.replace(old_ui,new_ui)

old_rules='''<div class="ruleBlock"><h3>덱 · 버림패 · 소모패</h3><p><b>공용 버림패</b>는 양쪽이 맨 위 카드를 가져올 수 있는 공용 공간입니다. <b>소모패</b>는 각자의 자동 재순환 대기 더미라서 기본적으로 직접 사용할 수 없습니다. 개인 덱의 마지막 카드를 뽑으면 그 플레이어의 소모패만 즉시 섞여 새 덱이 되며, 공용 버림패는 섞이지 않습니다.</p></div>'''
new_rules='''<div class="ruleBlock"><h3>덱 · 버림패 · 소모패</h3><p><b>공용 버림패</b>는 양쪽이 맨 위 카드를 가져올 수 있는 공용 공간입니다. <b>소모패</b>는 각자의 자동 재순환 대기 더미라서 기본적으로 직접 사용할 수 없습니다. 개인 덱의 마지막 카드를 뽑으면 <b>그 플레이어의 소모패 + 공용 버림패에 남아 있는 현재 그 플레이어 소유 카드</b>만 회수해 함께 섞어 새 덱을 만듭니다. 상대 소유 카드와 공개 조합 카드는 그대로 남습니다.</p></div>'''
assert s.count(old_rules)==1,s.count(old_rules)
s=s.replace(old_rules,new_rules)
p.write_text(s)

r=Path('ROADMAP.md')
road=r.read_text()
repls={
'- [x] Personal spent pile only is recycled when a deck is empty':'- [x] When a personal deck empties, recycle that player’s spent pile plus cards in the shared discard currently owned by that player; opponent-owned discard and public meld cards stay in place',
'- [x] Verify deck exhaustion/recycling under long games; recycle personal spent only and preserve shared discard':'- [x] Verify deck exhaustion/recycling under long games; recycle personal spent + currently-owned cards from shared discard, while preserving opponent-owned discard and all public meld cards',
'- [x] 덱 / 공용 버림패 / 개인 소모패의 역할 위계 분리 — 소모패를 `직접 사용 불가 · 덱 0장 시 자동 셔플` 재순환 대기 영역으로 명확화하고 데스크톱에서 시각적 비중 축소':'- [x] 덱 / 공용 버림패 / 개인 소모패의 역할 위계 분리 — 소모패를 직접 조작하지 않는 재순환 대기로 명확화하고, 덱 소진 시 `소모패 + 공용 버림패의 내 소유 카드` 자동 회수·셔플 규칙을 상시 표시하며 데스크톱에서 시각적 비중 축소',
'- [x] 네임드를 끝까지 받지 않는 온리 순수덱 클리어도 가능한 방향 유지':'- [x] 네임드를 끝까지 받지 않는 온리 순수덱 클리어도 가능한 방향 유지\n- [x] PURE도 기본 순환만으로 장기전이 가능하도록 덱 소진 시 소모패 + 공용 버림패의 현재 내 소유 카드를 재순환하는 공통 규칙 적용'
}
for a,b in repls.items():
    assert road.count(a)==1,(a,road.count(a))
    road=road.replace(a,b)
r.write_text(road)

h=Path('tests/hand-circulation.mjs')
t=h.read_text()
marker="""// Drawing from a personal deck clears stale discard-contract state; discard acquisition starts clean before onDiscardDraw re-arms it.
"""
insert=r'''// PURE-safe recycle: an empty personal deck reclaims both personal spent and currently-owned cards from the shared discard.
{
  const player = { hand: [], deck: [], spent: [], melds: [] };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const spentCard = card('S', 10, { owner: 'player' });
  const ownDiscard = card('D', 5, { owner: 'player' });
  const enemyDiscard = card('C', 9, { owner: 'enemy' });
  const transferredAway = card('H', 4, { owner: 'enemy', originOwner: 'player' });
  const boardCard = card('S', 7, { owner: 'player' });
  player.spent = [spentCard];
  player.melds = [{ type: 'SET', cards: [boardCard, card('H', 7), card('D', 7)] }];
  const state = { player, enemy, discard: [enemyDiscard, ownDiscard, transferredAway], turnNo: 1 };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs;
  ctx.log = () => {};
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne');
  const drawn = ctx.drawOne('player', false);
  const recycled = new Set([...player.hand, ...player.deck].map(c => c.uid));
  ok(recycled.has(spentCard.uid) && recycled.has(ownDiscard.uid), 'empty deck recycles personal spent plus currently-owned shared-discard cards');
  ok(drawn && player.spent.length === 0, 'recycle can immediately supply the next draw even when PURE has no named-card circulation effect');
  ok(state.discard.length === 2 && state.discard.includes(enemyDiscard) && state.discard.includes(transferredAway), 'opponent-owned discard remains public even when originOwner was the recycling player');
  ok(!state.discard.includes(ownDiscard), 'currently-owned player card is removed from shared discard during recycle');
  ok(player.melds[0].cards.includes(boardCard) && !recycled.has(boardCard.uid), 'public meld cards are never reclaimed by deck recycling');
}

// Recycle must also work when spent is empty and the only available personal cards are in shared discard.
{
  const player = { hand: [], deck: [], spent: [], melds: [] };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const ownDiscard = card('C', 6, { owner: 'player' });
  const enemyDiscard = card('D', 8, { owner: 'enemy' });
  const state = { player, enemy, discard: [enemyDiscard, ownDiscard], turnNo: 1 };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs;
  ctx.log = () => {};
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne');
  const drawn = ctx.drawOne('player', false);
  ok(drawn === ownDiscard && player.hand.includes(ownDiscard), 'owned shared-discard card alone can rebuild an empty personal deck');
  ok(state.discard.length === 1 && state.discard[0] === enemyDiscard, 'rebuilding from owned discard leaves opponent card in the shared pile');
}

// Drawing the final card eagerly rebuilds from both spent and owned shared-discard cards.
{
  const player = { hand: [], deck: [], spent: [], melds: [] };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const last = card('C', 4), spentCard = card('S', 10), ownDiscard = card('H', 11, { owner: 'player' });
  const enemyDiscard = card('D', 5, { owner: 'enemy' });
  player.deck = [last];
  player.spent = [spentCard];
  const state = { player, enemy, discard: [enemyDiscard, ownDiscard], turnNo: 1 };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs;
  ctx.log = () => {};
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne');
  const drawn = ctx.drawOne('player', false);
  ok(drawn === last, 'final original deck card is still drawn before eager owned-card recycling');
  ok(player.deck.length === 2 && player.spent.length === 0, 'final draw eagerly rebuilds deck from spent plus owned shared discard');
  ok(!state.discard.includes(ownDiscard) && state.discard.length === 1 && state.discard[0] === enemyDiscard, 'eager rebuild removes only the current owner’s discard cards');
}

'''
assert t.count(marker)==1,t.count(marker)
t=t.replace(marker,insert+marker)
h.write_text(t)

u=Path('tests/spent-pile-ux.mjs')
u.write_text(r'''import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
ok(html.includes('class="pileStation spentStation"'),'spent pile has a distinct non-primary station class');
ok(html.includes('재순환 대기<br><b id="playerSpentCount">0</b><small>소모패</small>'),'spent pile identifies itself as a recycle queue while preserving the official 소모패 term');
ok(html.includes('직접 사용 불가</b><br>덱 0장 → 소모패 + 버림패 내 카드 자동 셔플'),'spent pile explains the complete PURE-safe recycle source');
ok(html.includes('aria-label="내 소모패 · 직접 조작하지 않음 · 덱이 비면 소모패와 공용 버림패의 내 소유 카드 자동 재순환"'),'spent pile accessibility text explains the full passive recycle rule');
ok(html.includes('/* UI2 · spent pile clarity */')&&html.includes('@media (min-width:900px){.spentStation{opacity:.86}'),'desktop visually subordinates the passive spent pile');
ok(html.includes('<h3>덱 · 버림패 · 소모패</h3>'),'rules overlay contains a dedicated pile-role explanation');
ok(html.includes('그 플레이어의 소모패 + 공용 버림패에 남아 있는 현재 그 플레이어 소유 카드')&&html.includes('상대 소유 카드와 공개 조합 카드는 그대로 남습니다.'),'rules explain owner-filtered discard recycling without touching public melds');
ok(road.includes('recycle that player’s spent pile plus cards in the shared discard currently owned by that player'),'M0 locks owner-filtered shared-discard recycling');
ok(road.includes('PURE도 기본 순환만으로 장기전이 가능하도록'),'PURE roadmap records the circulation compatibility fix');
console.log('Spent pile UX regression passed.');
''')
