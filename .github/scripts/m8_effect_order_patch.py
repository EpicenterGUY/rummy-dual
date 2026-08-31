from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing {label}')
    s=s.replace(old,new,1)

marker='function resolveEffects(w,cards,type,ctx={})'
helper="function namedEffectPriority(c){if(c?.tag==='sameDiscardRank')return-10;if(c?.tag==='goldenHand')return 10;return 0}\nfunction orderedNamedEffectCards(cards){return(cards||[]).map((c,i)=>({c,i,p:namedEffectPriority(c)})).sort((a,b)=>a.p-b.p||a.i-b.i).map(x=>x.c)}\n"
if 'function namedEffectPriority(' not in s:
    if marker not in s: raise SystemExit('missing resolveEffects marker')
    s=s.replace(marker,helper+marker,1)
once("const side=sideObj(w),seen=ctx.effectSeen||new Set(),foe=other(w);const isReturning=!!ctx.willReturn;for(const c of cards){",
     "const side=sideObj(w),seen=ctx.effectSeen||new Set(),foe=other(w);const isReturning=!!ctx.willReturn;for(const c of orderedNamedEffectCards(cards)){",
     'named effect dependency order')

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
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const ctx=vm.createContext({console});vm.runInContext(source('namedEffectPriority')+'\n'+source('orderedNamedEffectCards'),ctx);
const golden={uid:'g',tag:'goldenHand'},normal={uid:'n',tag:'emergencyGear'},buyout={uid:'b',tag:'sameDiscardRank'};
const ordered=ctx.orderedNamedEffectCards([golden,normal,buyout]);
ok(ordered[0]===buyout&&ordered[1]===normal&&ordered[2]===golden,'Buyout King classification resolves before Golden Hand while unrelated cards keep their relative slot');
const reversed=ctx.orderedNamedEffectCards([buyout,golden]);
ok(reversed[0]===buyout&&reversed[1]===golden,'effect dependency order is independent of hand click order');
const fx=source('resolveEffects');
ok(fx.includes('for(const c of orderedNamedEffectCards(cards))'),'named-effect resolver uses dependency ordering');
ok(fx.includes("case'sameDiscardRank':{const lr=")&&fx.includes("case'goldenHand':if(cards.some(x=>x.fromDiscard))"),'Buyout King classification and Golden Hand dependency remain in the same resolver');
console.log('M8 dependent effect-order regression passed.');
''',encoding='utf-8')
