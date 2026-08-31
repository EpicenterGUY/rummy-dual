from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="case'goldenHand':if(c.fromDiscard){drawOne(w,false);const cand=side.hand.filter(x=>!cards.includes(x)).sort((a,b)=>b.age-a.age)[0];if(cand){removeFromHand(w,[cand]);cand.fromDiscard=false;side.deck.unshift(cand)}}break;"
new="case'goldenHand':if(cards.some(x=>x.fromDiscard)){drawOne(w,false);const cand=side.hand.filter(x=>!cards.includes(x)).sort((a,b)=>b.age-a.age)[0];if(cand){removeFromHand(w,[cand]);cand.fromDiscard=false;side.deck.unshift(cand)}}break;"
if old not in s: raise SystemExit('missing Golden Hand implementation')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
anchor='- [x] Repair previous-DETONATE action window so Revenge Blade and Phoenix can trigger on the following owner turn; Phoenix spent return no longer grants its heal before use\n'
line='- [x] Fix Golden Hand source check so any discard-acquired card in the same meld action can enable its cycle, not only Golden Hand itself\n'
if line not in r:
    if anchor not in r: raise SystemExit('missing M8 Golden Hand roadmap anchor')
    r=r.replace(anchor,anchor+line,1)
road.write_text(r,encoding='utf-8')

t=Path('tests/named-golden-hand.mjs')
t.write_text(r'''import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const fx=source('resolveEffects');
ok(fx.includes("case'goldenHand':if(cards.some(x=>x.fromDiscard))"),'Golden Hand checks the whole same-action card group for discard origin');
ok(!fx.includes("case'goldenHand':if(c.fromDiscard)"),'Golden Hand no longer requires itself to be the discard-acquired card');
ok(html.includes("'D7':{n:'황금손',t:'goldenHand',d:'버림패에서 가져온 카드와 같은 조합 행동에 들어가면"),'Golden Hand text and implementation now describe the same source condition');
console.log('M8 Golden Hand source regression passed.');
''',encoding='utf-8')
