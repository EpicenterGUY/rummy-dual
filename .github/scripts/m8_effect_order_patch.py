from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing {label}')
    s=s.replace(old,new,1)

old="const side=sideObj(w),seen=ctx.effectSeen||new Set(),foe=other(w);const isReturning=!!ctx.willReturn;for(const c of cards){"
new="const side=sideObj(w),seen=ctx.effectSeen||new Set(),foe=other(w);const isReturning=!!ctx.willReturn,effectCards=[...(cards||[])];for(let i=0;i<effectCards.length;i++){if(effectCards[i]?.tag!=='goldenHand')continue;const j=effectCards.findIndex((x,k)=>k>i&&x?.tag==='sameDiscardRank');if(j>=0){const[dep]=effectCards.splice(j,1);effectCards.splice(i,0,dep);i++}}for(const c of effectCards){"
once(old,new,'named effect dependency order')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
anchor='- [x] Fix Smuggled Goods duration: free-suit legality lasts only for the discard-acquisition turn in hand, while a role legally committed to a RUN stays valid until that card leaves the meld\n'
line='- [x] Remove hand-click order dependency between Buyout King and Golden Hand by resolving discard-origin classification before the dependent Golden Hand check\n'
if line not in r:
    if anchor not in r: raise SystemExit('missing M8 effect-order roadmap anchor')
    r=r.replace(anchor,anchor+line,1)
road.write_text(r,encoding='utf-8')

t=Path('tests/named-effect-order.mjs')
t.write_text(r'''import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const fx=source('resolveEffects');
ok(fx.includes("effectCards=[...(cards||[])]"),'dependent effect ordering is local to resolveEffects and safe for isolated-function tests');
ok(fx.includes("effectCards[i]?.tag!=='goldenHand'")&&fx.includes("x?.tag==='sameDiscardRank'"),'resolver searches for a later Buyout King only when Golden Hand would otherwise resolve first');
ok(fx.includes('const[dep]=effectCards.splice(j,1);effectCards.splice(i,0,dep)'),'Buyout King is moved immediately before the dependent Golden Hand without globally sorting unrelated effects');
ok(fx.includes('for(const c of effectCards){'),'named effects resolve from the minimally adjusted action order');
ok(!fx.includes('orderedNamedEffectCards'),'resolveEffects has no external ordering-helper dependency');
ok(fx.includes("case'sameDiscardRank':{const lr=")&&fx.includes("case'goldenHand':if(cards.some(x=>x.fromDiscard))"),'Buyout King classification and Golden Hand dependency remain active in the same resolver');
console.log('M8 dependent effect-order regression passed.');
''',encoding='utf-8')
