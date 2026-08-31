from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def replace_function(name,new_code):
    global s
    marker=f'function {name}('
    start=s.find(marker)
    if start<0: raise SystemExit(f'missing function {name}')
    par=0; brace=-1
    for i in range(start+len(marker)-1,len(s)):
        ch=s[i]
        if ch=='(': par+=1
        elif ch==')': par-=1
        elif ch=='{' and par==0:
            brace=i; break
    if brace<0: raise SystemExit(f'missing body {name}')
    d=0; end=-1
    for i in range(brace,len(s)):
        if s[i]=='{': d+=1
        elif s[i]=='}':
            d-=1
            if d==0:
                end=i+1; break
    if end<0: raise SystemExit(f'unterminated {name}')
    s=s[:start]+new_code+s[end:]

def rep(old,new,label,count=1):
    global s
    if s.count(old)<count: raise SystemExit(f'missing {label}: {s.count(old)}/{count}')
    s=s.replace(old,new,count)

new_trigger=r'''function triggerRummy(w,lastCards,opts={}){let reload=6;const s=sideObj(w),jokerLast=lastCards.some(c=>c.tag==='jokerLast');s.rummyReturnPending=true;s.rummyRecoveryPending=true;if(typeof getCirculationStats==='function')getCirculationStats().rummys++;if(lastCards.some(c=>c.tag==='rummyPlus1')){reload=7;if(state.switchTarget===w)addShield(w,4)}if(lastCards.some(c=>c.tag==='rummyHeal4')){heal(w,Math.ceil(15/RECOVERY_UNIT));applyStatus(w,'regen',1);if(state.switchPower>=60)addShield(w,4)}if(w==='player')state.rummy++;if(!s.hand.length&&ownedRecycleCount(w)<=0)emergencyReleaseMeld(w,'러미 재충전원 0 · 순환 정체');const beforeReloadHand=s.hand.length;drawMany(w,Math.max(0,reload-beforeReloadHand),false);let finalized=false;const finishRummy=()=>{if(finalized)return'rummy';finalized=true;if(typeof animateRummyFeedback==='function')animateRummyFeedback(w,reload);else combatBanner('러미!','rummy',40);log(`${w==='player'?'나':'상대'} 러미! 새 손패 ${reload}장.`,'good');if(w==='player'){if(typeof tutorialCheckProgress==='function')tutorialCheckProgress('rummy',{beforeHand:beforeReloadHand,reload,afterHand:s.hand.length});state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;endPlayerTurn()}return'rummy'};if(jokerLast&&opts.returned){drawMany(w,1,false);if(s.hand.length&&typeof requestHandBottomChoice==='function'){const paused=requestHandBottomChoice(w,{title:'마지막 웃음',label:'마지막 웃음',text:'반환 러미로 1장을 추가로 뽑았습니다. 덱 아래로 보낼 손패 1장을 고르세요.',onAsyncResolved:()=>{log(`${switchName(w)} 마지막 웃음 · 반환 러미 후 1장 추가 순환.`,'good');finishRummy()}});if(paused)return'choice'}else{const cand=[...s.hand].sort((a,b)=>b.age-a.age)[0];if(cand){removeFromHand(w,[cand]);cand.fromDiscard=false;cand.contractActive=false;cand.age=0;s.deck.unshift(cand)}}log(`${switchName(w)} 마지막 웃음 · 반환 러미 후 1장 추가 순환.`,'good')}else if(jokerLast&&state.switchTarget===w&&state.switchPower>0){s.jokerLastDetonateReduction=15;log(`${switchName(w)} 마지막 웃음 · 이번 턴 폭발 피해 15 감소 준비.`,'good')}return finishRummy()}'''
replace_function('triggerRummy',new_trigger)

old="if(willRummy&&!state.gameOver){triggerRummy(w,cards,{returned:false});return'rummy'}"
new="if(willRummy&&!state.gameOver){const rr=triggerRummy(w,cards,{returned:false});return rr==='choice'?'choice':'rummy'}"
rep(old,new,'new meld RUMMY choice propagation')
old="if(willRummy&&!state.gameOver){triggerRummy(w,cards,{returned:returning||forceReturn});return'rummy'}"
new="if(willRummy&&!state.gameOver){const rr=triggerRummy(w,cards,{returned:returning||forceReturn});return rr==='choice'?'choice':'rummy'}"
rep(old,new,'attach RUMMY choice propagation')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
needle='- [x] Final choice pass B: Parasite now lets the human owner choose the discard on an opponent-turn return, while CPU action resolution pauses and resumes without granting extra actions\n'
insert=needle+'- [x] Final choice pass C: Last Laugh returning-RUMMY now lets the human choose which post-refill card goes to deck bottom, and the RUMMY turn ends only after that mandatory choice resolves\n'
if needle not in r: raise SystemExit('missing Last Laugh roadmap anchor')
r=r.replace(needle,insert,1)
road.write_text(r,encoding='utf-8')

t=Path('tests/named-last-laugh-choice.mjs')
t.write_text(r'''import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const rummy=source('triggerRummy'),submit=source('submitNewMeld'),attach=source('attachCards');
ok(rummy.includes("typeof requestHandBottomChoice==='function'")&&rummy.includes("title:'마지막 웃음'"),'live Last Laugh uses the shared exact-card bottom choice when available');
ok(rummy.includes("if(paused)return'choice'")&&rummy.includes('const finishRummy=()=>'),'returning Last Laugh can pause RUMMY finalization for the mandatory choice');
ok(rummy.includes("onAsyncResolved:()=>{log(`${switchName(w)} 마지막 웃음 · 반환 러미 후 1장 추가 순환.`,'good');finishRummy()}")&&rummy.includes("if(paused)return'choice'"),'player RUMMY finalization is resumed from the Last Laugh selection callback rather than before the choice');
ok(rummy.includes("else{const cand=[...s.hand].sort")&&rummy.includes('cand.contractActive=false'),'isolated/CPU fallback stays deterministic and normalizes the bottomed card');
ok(submit.includes("const rr=triggerRummy(w,cards,{returned:false})")&&submit.includes("rr==='choice'?'choice':'rummy'"),'new-meld RUMMY propagates an async Last Laugh choice');
ok(attach.includes("const rr=triggerRummy(w,cards,{returned:returning||forceReturn})")&&attach.includes("rr==='choice'?'choice':'rummy'"),'attach RUMMY propagates an async Last Laugh choice');
ok(fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8').includes('Final choice pass C'),'roadmap records Last Laugh choice stabilization');
console.log('M8 Last Laugh choice regression passed.');
''',encoding='utf-8')
