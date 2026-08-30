from pathlib import Path

idx = Path('index.html')
s = idx.read_text()
old = "function drawOne(w,fromDiscard=false){const s=sideObj(w);if(fromDiscard)return acquireDiscardCard(w,0);recycleIfNeeded(w);const c=s.deck.pop();if(!c)return null;c.fromDiscard=false;c.contractActive=false;c.age=0;s.hand.push(c);return c}function drawMany"
new = "function drawOne(w,fromDiscard=false){const s=sideObj(w);if(fromDiscard)return acquireDiscardCard(w,0);recycleIfNeeded(w);const c=s.deck.pop();if(!c)return null;c.fromDiscard=false;c.contractActive=false;c.age=0;s.hand.push(c);if(!s.deck.length&&s.spent.length)recycleIfNeeded(w);return c}function drawMany"
if old not in s:
    raise SystemExit('drawOne anchor not found')
s = s.replace(old, new, 1)
s = s.replace('<div class="pileRule">덱이 비면 다시 섞음</div>', '<div class="pileRule">덱 0장 → 소모패 즉시 섞음</div>', 1)
idx.write_text(s)

p = Path('tests/hand-circulation.mjs')
t = p.read_text()
anchor = "// Drawing from a personal deck clears stale discard-contract state; discard acquisition starts clean before onDiscardDraw re-arms it.\n"
if anchor not in t:
    raise SystemExit('test insertion anchor not found')
block = r'''// Drawing the final personal-deck card immediately rebuilds the deck from any existing personal spent pile.
{
  const player = { hand: [], deck: [], spent: [], melds: [] };
  const enemy = { hand: [], deck: [], spent: [], melds: [] };
  const last = card('C', 4), s1 = card('S', 10), s2 = card('H', 11);
  const publicDiscard = card('D', 5, { owner: 'enemy' });
  player.deck = [last];
  player.spent = [s1, s2];
  const state = { player, enemy, discard: [publicDiscard], turnNo: 1 };
  const ctx = context({ state });
  ctx.sideObj = w => w === 'player' ? player : enemy;
  ctx.shuffle = xs => xs;
  ctx.log = () => {};
  install(ctx, 'recycleIfNeeded', 'acquireDiscardCard', 'drawOne');
  const drawn = ctx.drawOne('player', false);
  ok(drawn === last && player.hand.includes(last), 'the final original deck card is still the card actually drawn');
  ok(player.spent.length === 0 && player.deck.length === 2, 'drawing the final deck card immediately rebuilds the personal deck from spent cards');
  ok(player.deck[0] === s1 && player.deck[1] === s2, 'immediate rebuild preserves the shuffled spent-card deck contents');
  ok(state.discard.length === 1 && state.discard[0] === publicDiscard, 'immediate personal recycle still leaves the shared discard untouched');
}

'''
t = t.replace(anchor, block + anchor, 1)
p.write_text(t)
