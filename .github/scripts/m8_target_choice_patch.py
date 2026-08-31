from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing patch target: {label}')
    s=s.replace(old,new,1)

def replace_top_function(name,new_code):
    global s
    start=s.find(f'function {name}(')
    if start<0: raise SystemExit(f'missing function {name}')
    end=s.find('\nfunction ',start+1)
    if end<0: raise SystemExit(f'missing end for {name}')
    s=s[:start]+new_code.rstrip()+s[end:]

helpers=r'''function extortionCandidates(w,m){if(!m)return[];const foe=other(w),out=[];for(const om of meldsOf(foe)){if(meldFixedActive(om))continue;for(const c of om.cards){if(cardFixedActive(c)||protectedByConstruction(om,c))continue;const remain=om.cards.filter(x=>x.uid!==c.uid),added=m.cards.concat(c);if(remain.length<3||meldType(remain)!==om.type||meldType(added)!==m.type)continue;out.push({meld:om,card:c,targetSide:foe})}}return out}
function moveExtortedCard(w,m,choice){if(!choice?.meld||!choice?.card)return false;const current=extortionCandidates(w,m).find(x=>x.meld===choice.meld&&x.card.uid===choice.card.uid);if(!current)return false;const foe=current.targetSide,om=current.meld,c=current.card,i=om.cards.findIndex(x=>x.uid===c.uid);if(i<0)return false;if(insuranceBlocks(w,foe,om,c))return false;om.cards.splice(i,1);if(om.type==='RUN')om.chain=Math.max(0,(om.chain||0)-1);m.cards.push(c);m.lastTouchedOwnerStart=sideObj(w).turnStarts;markSetCompletion(om,foe);markSetCompletion(m,w);log(`강탈자: ${cardText(c)}를 상대 ${om.type}에서 새 ${m.type}으로 이동${om.type==='RUN'?' · 상대 CHAIN -1':''}.`,'important');return true}
function requestExtortChoice(w,m,onAsyncResolved=null){const candidates=extortionCandidates(w,m);if(!candidates.length)return false;const apply=choice=>moveExtortedCard(w,m,choice),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive){return requestEffectChoice({title:'강탈자',text:'상대 공개 조합에서 직접 옮길 카드 1장을 고르세요. 이동 후 양쪽 조합은 모두 유효해야 합니다.',options:candidates.map((x,i)=>({key:`extort:${x.card.uid}:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:`상대 ${x.meld.type} ${x.meld.cards.length}장 → 내 ${m.type}`,choice:x})),onChoose:o=>{if(o?.choice)apply(o.choice);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.choice||null)}})}apply(candidates[0]);return false}
function requestOpponentMeldChoice(w,opts={}){const foe=other(w),candidates=[...meldsOf(foe)];if(!candidates.length)return false;const apply=m=>{if(!meldsOf(foe).includes(m))return false;lockMeldRecovery(m,foe);log(`${opts.label||opts.title||'대상 지정'}: 상대 ${m.type} 조합을 고정했습니다.`,'important');return true},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive){return requestEffectChoice({title:opts.title||'대상 선택',text:opts.text||'대상으로 삼을 상대 공개 조합을 고르세요.',options:candidates.map((m,i)=>({key:`meld:${i}`,label:`상대 ${m.type} · ${m.cards.length}장`,detail:m.type==='RUN'?`CHAIN ${m.chain||0}`:'SET',meld:m})),onChoose:o=>{if(o?.meld)apply(o.meld);if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(o?.meld||null)}})}apply(candidates[0]);return false}'''
replace_top_function('autoExtortToNewMeld',helpers)

replace_once("case'heldBonus':if(c.age>=2){const target=meldsOf(foe)[0];if(target)lockMeldRecovery(target,foe)}break;", "case'heldBonus':if(c.age>=2){const paused=requestOpponentMeldChoice(w,{title:c.name,label:c.name,text:'고정할 상대 공개 조합 하나를 고르세요.',onAsyncResolved:resume});if(paused)return pause()}break;", 'heldBonus target choice')
replace_once("case'extortion':break;", "case'extortion':if(ctx.isNew){const paused=requestExtortChoice(w,ctx.meld,resume);if(paused)return pause()}break;", 'extortion target choice')
replace_once("if(cards.some(c=>c.tag==='extortion'))autoExtortToNewMeld(w,m);", "", 'legacy eager extortion')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
needle='- [x] Make named effect choices resumable before attack/RUMMY finalization; Connector 6+ now preserves RUMMY timing, free-recovery effects select a legal owned card, and Recycler selects from spent cards\n'
insert=needle+'- [x] Target-choice pass: Extortion now selects the exact legal card to move and Sleeper selects the opponent meld to fix; CPU keeps deterministic first-candidate resolution\n- [ ] Add an off-turn choice continuation so Bait can let the human owner choose the hand card to bottom without the CPU turn racing ahead\n'
if needle not in r: raise SystemExit('missing roadmap insertion point')
r=r.replace(needle,insert,1)
road.write_text(r,encoding='utf-8')

test=Path('tests/named-target-choice.mjs')
test.write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const resolve=source('resolveEffects'),submit=source('submitNewMeld'),extReq=source('requestExtortChoice'),meldReq=source('requestOpponentMeldChoice'),extMove=source('moveExtortedCard'),extCandidates=source('extortionCandidates');
ok(resolve.includes("case'extortion':if(ctx.isNew)")&&resolve.includes('requestExtortChoice(w,ctx.meld,resume)'),'Extortion target selection lives inside resumable named-effect resolution');
ok(!submit.includes('autoExtortToNewMeld')&&!html.includes('function autoExtortToNewMeld('),'legacy eager first-candidate Extortion path is removed');
ok(extCandidates.includes('meldFixedActive(om)')&&extCandidates.includes('protectedByConstruction(om,c)')&&extCandidates.includes("meldType(remain)!==om.type")&&extCandidates.includes("meldType(added)!==m.type"),'Extortion only offers legal movable cards that preserve both melds');
ok(extMove.includes('insuranceBlocks(w,foe,om,c)')&&extMove.indexOf('insuranceBlocks(w,foe,om,c)')<extMove.indexOf('om.cards.splice'),'interference protection resolves before the chosen Extortion card moves');
ok(extReq.includes("candidates.length>1")&&extReq.includes('requestEffectChoice')&&!extReq.includes('allowSkip:true'),'human Extortion chooses among multiple legal cards and the mandatory move cannot be skipped');
ok(resolve.includes("case'heldBonus':if(c.age>=2)")&&resolve.includes('requestOpponentMeldChoice'),'charged Sleeper routes its opponent-meld target through shared choice handling');
ok(meldReq.includes("candidates.length>1")&&meldReq.includes('requestEffectChoice')&&meldReq.includes('lockMeldRecovery(m,foe)'),'Sleeper presents multiple opponent melds to the human and fixes the exact chosen meld');
ok(html.includes("'DJ':{n:'강탈자'")&&html.includes("'S9':{n:'잠복자'"),'target-choice cards remain in the live named-card pool');
ok(fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8').includes('Target-choice pass: Extortion'),'roadmap records the target-choice pass');
console.log('M8 named target-choice regression passed.');
''',encoding='utf-8')
