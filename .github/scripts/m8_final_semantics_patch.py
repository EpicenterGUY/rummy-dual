from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit(f'missing {label}')
    s=s.replace(old,new,1)

rep("'HK':{n:'심장왕',t:'heartKingCharge',d:'회복할 때 심장을 최대 3개 저장. DETONATE 직전 심장 1개당 피해 8을 막고 모두 제거.'},","'HK':{n:'심장왕',t:'heartKingCharge',d:'손에 있는 동안 회복할 때 심장을 최대 3개 저장. DETONATE 직전 저장한 심장을 모두 제거하고, 심장 1개당 피해 8을 막는다.'},",'Heart King text')

old="for(const c of s.hand)if(c.tag==='heartKingCharge'&&c.healCharge>0&&raw>0){const spend=Math.min(c.healCharge,Math.ceil(raw/8));const cut=Math.min(raw,spend*8);c.healCharge-=spend;raw-=cut;log(`${c.name}: 심장 ${spend}개로 ${cut} 피해 방어.`,'good');break}"
new="for(const c of s.hand)if(c.tag==='heartKingCharge'&&c.healCharge>0&&raw>0){const spend=c.healCharge,cut=Math.min(raw,spend*8);c.healCharge=0;raw-=cut;log(`${c.name}: 저장한 심장 ${spend}개를 모두 제거 · ${cut} 피해 방어.`,'good');break}"
rep(old,new,'Heart King detonate spend-all')

old="const idx=m.cards.findIndex(c=>c.tag==='insuranceAgent'&&c.owner===targetSide&&c.uid!==targetCard?.uid);"
new="const idx=targetCard?.owner===targetSide?m.cards.findIndex(c=>c.tag==='insuranceAgent'&&c.owner===targetSide&&c.uid!==targetCard?.uid):-1;"
rep(old,new,'Insurance ownership')

old="function canContinueReturnedRun(w,m){return !!m&&m.type==='RUN'&&m.returnAttachToken===state.turnToken&&sideObj(w).returnedSwitchThisTurn&&state.switchTarget===other(w)}"
new="function canContinueReturnedRun(w,m){return !!m&&m.type==='RUN'&&m.rebelReturnBlockedToken!==state.turnToken&&m.returnAttachToken===state.turnToken&&sideObj(w).returnedSwitchThisTurn&&state.switchTarget===other(w)}"
rep(old,new,'Rebel continuation block')

old="if(j.tag==='rebelJoker'&&attacher!==j.owner){m.lastAttachToken=state.turnToken;log(`${j.name}: 반역 · 이 조합은 이번 턴 다시 반환에 사용할 수 없습니다.`,'important')}"
new="if(j.tag==='rebelJoker'){m.lastAttachToken=state.turnToken;m.rebelReturnBlockedToken=state.turnToken;log(`${j.name}: 반역 · 이 조합은 이번 턴 다시 스위치를 반환하거나 연속 연장할 수 없습니다.`,'important')}"
rep(old,new,'Rebel replacement block')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
needle='- [x] Add an off-turn choice continuation: when CPU takes a human-owned Bait, the owner draws first, chooses the exact hand card to bottom, and CPU play resumes only after that choice resolves\n'
insert=needle+'- [x] Final semantics pass A: Insurance Agent only protects cards actually owned by its side, Heart King consumes every stored heart at DETONATE, and any Rebel Joker replacement blocks same-turn return/continuation\n'
if needle not in r: raise SystemExit('missing M8 roadmap anchor')
r=r.replace(needle,insert,1)
road.write_text(r,encoding='utf-8')

t=Path('tests/named-final-semantics.mjs')
t.write_text(r'''import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const insurance=source('insuranceBlocks'),detonate=source('detonate'),replace=source('replaceRedundantJokers'),continuation=source('canContinueReturnedRun');
ok(insurance.includes("targetCard?.owner===targetSide?m.cards.findIndex"),'Insurance Agent only intercepts interference against a card owned by its protected side');
ok(detonate.includes('const spend=c.healCharge')&&detonate.includes('c.healCharge=0'),'Heart King removes every stored heart when DETONATE prevention resolves');
ok(html.includes('손에 있는 동안 회복할 때 심장을 최대 3개 저장')&&html.includes('저장한 심장을 모두 제거'),'Heart King text matches its hand-only charge window and spend-all detonation');
ok(replace.includes("if(j.tag==='rebelJoker')")&&!replace.includes("attacher!==j.owner"),'Rebel Joker replacement blocks follow-up regardless of who supplied the real card');
ok(replace.includes('m.rebelReturnBlockedToken=state.turnToken')&&replace.includes('m.lastAttachToken=state.turnToken'),'Rebel replacement records both generic attach lock and explicit return-continuation lock');
ok(continuation.includes('m.rebelReturnBlockedToken!==state.turnToken'),'same-RUN continuation cannot bypass a Rebel replacement lock');
ok(fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8').includes('Final semantics pass A'),'roadmap records the final semantics pass');
console.log('M8 final semantics regression passed.');
''',encoding='utf-8')
