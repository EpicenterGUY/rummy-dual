from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="function runNaturalSuit(cards){const counts={};for(const c of cards||[])if(!isJoker(c)&&!isSuitFlexible(c))counts[c.suit]=(counts[c.suit]||0)+1;return Object.entries(counts).sort((a,b)=>b[1]-a[1])[0]?.[0]||null}"
new="function runNaturalSuit(cards){const real=(cards||[]).filter(c=>!isJoker(c)),counts={};for(const c of real)if(!isSuitFlexible(c))counts[c.suit]=(counts[c.suit]||0)+1;return Object.entries(counts).sort((a,b)=>b[1]-a[1])[0]?.[0]||real[0]?.suit||null}"
if s.count(old)!=1:raise SystemExit(f'runNaturalSuit: expected 1, got {s.count(old)}')
p.write_text(s.replace(old,new,1))

t=Path('tests/named-card-behavior-2.mjs')
x=t.read_text()
needle="  ok(off.flexSuitOffSuit===true,'Understudy records an off-heart suit role');\n"
insert=needle+"  const fallback=card('H','Q',{tag:'flexSuit'});ctx.recordFlexibleSuitRoles({type:'RUN',cards:[card('C',10,{tag:'smugglerBridge'}),fallback,card('D','J',{tag:'smuggledSuit'})]});\n  ok(fallback.flexSuitOffSuit===true,'Understudy mirrors RUN target-suit fallback when every real card is suit-flexible');\n"
if x.count(needle)!=1:raise SystemExit('behavior test anchor mismatch')
t.write_text(x.replace(needle,insert,1))
