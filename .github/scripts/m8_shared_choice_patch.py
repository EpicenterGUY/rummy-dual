from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing {label}')
    s=s.replace(old,new,1)

# Shared effect-choice modal styling.
once(".targetHint{margin-top:5px;font-size:7px;color:#a9b7cd;text-align:center}\n.handZone",
     ".targetHint{margin-top:5px;font-size:7px;color:#a9b7cd;text-align:center}\n.effectChoiceOverlay{position:fixed;inset:0;z-index:1400;display:grid;place-items:center;padding:16px;background:#05070bd9}.effectChoiceOverlay[hidden]{display:none}.effectChoicePanel{width:min(92vw,430px);max-height:min(78dvh,620px);overflow:auto;padding:12px;border:2px solid #000;background:linear-gradient(180deg,#202a3d,#111722);box-shadow:0 0 0 2px #536789 inset,6px 6px 0 #0009}.effectChoiceKicker{font-size:7px;color:var(--gold);font-weight:900;letter-spacing:.7px}.effectChoiceTitle{font-size:14px;font-weight:900;margin-top:4px}.effectChoiceText{font-size:8px;color:#bcc7d9;line-height:1.55;margin:6px 0 9px}.effectChoiceOptions{display:flex;flex-direction:column;gap:6px}.effectChoiceBtn{width:100%;text-align:left;display:flex;justify-content:space-between;gap:8px;align-items:center}.effectChoiceBtn small{font-size:7px;color:var(--soft);font-weight:400}.effectChoiceSkip{margin-top:7px;width:100%}\n.handZone",
     'effect choice CSS')

once("fuseUsed:false,gameOver:false,rewarded:false};",
     "fuseUsed:false,gameOver:false,rewarded:false,pendingEffectChoice:null,effectChoiceQueue:[]};",
     'effect choice state')

helper=r'''function ensureEffectChoiceModal(){if(typeof document==='undefined')return null;let root=document.getElementById('effectChoiceOverlay');if(root)return root;root=document.createElement('div');root.id='effectChoiceOverlay';root.className='effectChoiceOverlay';root.hidden=true;root.innerHTML='<div class="effectChoicePanel pixel" role="dialog" aria-modal="true" aria-labelledby="effectChoiceTitle"><div class="effectChoiceKicker">효과 선택</div><div class="effectChoiceTitle" id="effectChoiceTitle"></div><div class="effectChoiceText" id="effectChoiceText"></div><div class="effectChoiceOptions" id="effectChoiceOptions"></div><button type="button" class="pixelBtn effectChoiceSkip" id="effectChoiceSkip">건너뛰기</button></div>';document.body.appendChild(root);return root}
function renderEffectChoiceModal(){const root=ensureEffectChoiceModal();if(!root)return;const q=state.pendingEffectChoice;if(!q){root.hidden=true;return}root.hidden=false;const title=root.querySelector('#effectChoiceTitle'),text=root.querySelector('#effectChoiceText'),opts=root.querySelector('#effectChoiceOptions'),skip=root.querySelector('#effectChoiceSkip');title.textContent=q.title||'효과 대상 선택';text.textContent=q.text||'적용할 대상을 고르세요.';opts.innerHTML='';for(const o of q.options||[]){const b=document.createElement('button');b.type='button';b.className='pixelBtn effectChoiceBtn';b.dataset.choiceKey=String(o.key);const strong=document.createElement('strong');strong.textContent=o.label||String(o.key);b.appendChild(strong);if(o.detail){const small=document.createElement('small');small.textContent=o.detail;b.appendChild(small)}b.onclick=()=>resolveEffectChoice(String(o.key));opts.appendChild(b)}skip.hidden=!q.allowSkip;skip.textContent=q.skipLabel||'건너뛰기';skip.onclick=()=>resolveEffectChoice('__skip__')}
function pumpEffectChoice(){state.effectChoiceQueue=state.effectChoiceQueue||[];if(state.pendingEffectChoice||!state.effectChoiceQueue.length){renderEffectChoiceModal();return}state.pendingEffectChoice=state.effectChoiceQueue.shift();renderEffectChoiceModal()}
function requestEffectChoice(spec){if(!spec||(!spec.allowSkip&&!(spec.options||[]).length))return false;state.effectChoiceQueue=state.effectChoiceQueue||[];const q={...spec,options:(spec.options||[]).map((o,i)=>({...o,key:String(o.key??i)}))};state.effectChoiceQueue.push(q);pumpEffectChoice();return true}
function resolveEffectChoice(key){const q=state.pendingEffectChoice;if(!q)return false;const option=key==='__skip__'?null:(q.options||[]).find(o=>String(o.key)===String(key));if(key!=='__skip__'&&!option)return false;state.pendingEffectChoice=null;const cb=q.onChoose;if(typeof cb==='function')cb(option);pumpEffectChoice();if(!state.pendingEffectChoice&&typeof render==='function')render();return true}
function clearEffectChoices(){state.effectChoiceQueue=[];state.pendingEffectChoice=null;if(typeof document!=='undefined'){const root=document.getElementById('effectChoiceOverlay');if(root)root.hidden=true}}
'''
marker='function blankStatus(){'
if helper.strip() not in s:
    if marker not in s: raise SystemExit('missing choice helper insertion marker')
    s=s.replace(marker,helper+marker,1)

# New battle/tutorial reset cannot inherit a stale modal choice.
once("state.rewarded=false;state.fullRecirculationCount=0;",
     "state.rewarded=false;clearEffectChoices();state.fullRecirculationCount=0;",
     'newGame effect choice reset')
once("state.rewarded=false;if(step.scenario==='basic')",
     "state.rewarded=false;clearEffectChoices();if(step.scenario==='basic')",
     'tutorial scenario effect choice reset')

# Connector: player chooses which remaining hand card to bottom, or may skip. AI stays deterministic.
old_c2="case'run4Draw':if(type==='RUN'&&ctx.totalLength>=4){drawOne(w,false);if(ctx.totalLength>=6){const cand=side.hand.filter(x=>!cards.includes(x)).sort((a,b)=>b.age-a.age)[0];if(cand){removeFromHand(w,[cand]);side.deck.unshift(cand)}}}break;"
new_c2="case'run4Draw':if(type==='RUN'&&ctx.totalLength>=4){drawOne(w,false);if(ctx.totalLength>=6){const candidates=side.hand.filter(x=>!cards.includes(x)),bottom=cand=>{if(!cand||!side.hand.some(x=>x.uid===cand.uid))return false;removeFromHand(w,[cand]);cand.fromDiscard=false;cand.contractActive=false;cand.age=0;side.deck.unshift(cand);log(`${c.name}: ${cardText(cand)}를 덱 아래로 보냈습니다.`,'good');if(w==='player')flashPile('deckPile');return true};if(candidates.length){if(w==='player'&&state.turn==='player'){const opened=requestEffectChoice({title:c.name,text:'RUN이 6장 이상입니다. 뽑은 뒤 남은 손패 1장을 덱 아래로 보낼 수 있습니다.',options:candidates.map(x=>({key:x.uid,label:`${cardText(x)}${x.named?` · ${x.name}`:''}`,detail:`보유 ${x.age}턴`,card:x})),allowSkip:true,skipLabel:'보내지 않기',onChoose:o=>{if(o?.card)bottom(o.card)}});if(!opened)bottom([...candidates].sort((a,b)=>b.age-a.age)[0])}else bottom([...candidates].sort((a,b)=>b.age-a.age)[0])}}}break;"
once(old_c2,new_c2,'Connector choice behavior')

# Reserved Shipping: replace card-specific confirm with the shared choice modal, preserving the selected card until the decision resolves.
old_d6="const c=cs[0];if(!tutorialAllows('discard',{card:c})){tutorialReject('discard');return}const r=rectSnapshot(document.querySelector(`.cardBtn[data-uid=\"${c.uid}\"]`));removeFromHand('player',[c]);state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();let discard=true;if(c.tag==='topDeckChoice'&&confirm('예약 발송: 버림패 대신 이 카드를 내 덱 위에 놓을까요?')){c.fromDiscard=false;c.contractActive=false;state.player.deck.push(c);discard=false;log(`${c.name}: 버림패 대신 내 덱 위로 예약 발송.`,'important');flashPile('deckPile')}else{const pawn=state.field?.tag==='pawnshop'&&c.fromDiscard;pushDiscard(c);state.lastPlayerDiscardRank=c.rank;log(`YOU 버리기: ${cardText(c)}${c.named?' ['+c.name+']':''}`);armSafetyPin('player',c);if(pawn)addShield('player',3)}"
new_d6="const c=cs[0];if(!tutorialAllows('discard',{card:c})){tutorialReject('discard');return}if(c.tag==='topDeckChoice'&&c.effectChoiceDecision==null){const opened=requestEffectChoice({title:c.name,text:'버릴 때 공용 버림패 대신 내 덱 맨 위에 둘 수 있습니다.',options:[{key:'deck',label:'내 덱 맨 위에 놓기',detail:'다음 개인 덱 뽑기에서 다시 만남'},{key:'discard',label:'공용 버림패에 버리기',detail:'일반 버리기 처리'}],onChoose:o=>{c.effectChoiceDecision=o?.key||'discard';playerDiscard()}});if(opened)return}const r=rectSnapshot(document.querySelector(`.cardBtn[data-uid=\"${c.uid}\"]`));removeFromHand('player',[c]);state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();const reserved=c.tag==='topDeckChoice'&&c.effectChoiceDecision==='deck';c.effectChoiceDecision=null;let discard=true;if(reserved){c.fromDiscard=false;c.contractActive=false;state.player.deck.push(c);discard=false;log(`${c.name}: 버림패 대신 내 덱 위로 예약 발송.`,'important');flashPile('deckPile')}else{const pawn=state.field?.tag==='pawnshop'&&c.fromDiscard;pushDiscard(c);state.lastPlayerDiscardRank=c.rank;log(`YOU 버리기: ${cardText(c)}${c.named?' ['+c.name+']':''}`);armSafetyPin('player',c);if(pawn)addShield('player',3)}"
once(old_d6,new_d6,'Reserved Shipping shared choice')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
anchor='- [x] Remove hand-click order dependency between Buyout King and Golden Hand by resolving discard-origin classification before the dependent Golden Hand check\n'
line='- [x] Add a shared queued effect-choice modal and migrate Reserved Shipping plus Connector 6+ hand-bottom choice; optional Connector bottoming may be skipped while CPU resolution stays deterministic\n'
if line not in r:
    if anchor not in r: raise SystemExit('missing M8 choice roadmap anchor')
    r=r.replace(anchor,anchor+line,1)
road.write_text(r,encoding='utf-8')

t=Path('tests/named-choice-ui.mjs')
t.write_text(r'''import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
ok(html.includes('pendingEffectChoice:null,effectChoiceQueue:[]'),'battle state owns a shared queued effect-choice channel');
ok(html.includes('.effectChoiceOverlay')&&html.includes('.effectChoiceOptions'),'shared effect-choice modal has dedicated responsive styling');
for(const name of ['ensureEffectChoiceModal','renderEffectChoiceModal','pumpEffectChoice','requestEffectChoice','resolveEffectChoice','clearEffectChoices'])ok(script.includes(`function ${name}(`),`shared effect-choice helper exists: ${name}`);
const discard=source('playerDiscard');
ok(!discard.includes("confirm('예약 발송"),'Reserved Shipping no longer uses a card-specific blocking confirm dialog');
ok(discard.includes("title:c.name,text:'버릴 때 공용 버림패 대신 내 덱 맨 위에 둘 수 있습니다.'"),'Reserved Shipping routes its decision through the shared effect-choice modal');
ok(discard.includes("c.effectChoiceDecision=o?.key||'discard';playerDiscard()"),'Reserved Shipping resumes the original discard action after the shared decision');
const fx=source('resolveEffects');
ok(fx.includes("case'run4Draw'")&&fx.includes("allowSkip:true,skipLabel:'보내지 않기'"),'Connector 6+ exposes an optional shared hand-bottom choice');
ok(fx.includes("options:candidates.map(x=>({key:x.uid")&&fx.includes('onChoose:o=>{if(o?.card)bottom(o.card)}'),'Connector player choice is bound to concrete remaining hand cards');
ok(fx.includes("else bottom([...candidates].sort((a,b)=>b.age-a.age)[0])"),'Connector CPU path remains deterministic instead of opening UI');
const ng=source('newGame');
ok(ng.includes('clearEffectChoices()'),'new battles clear stale effect-choice state');
ok(html.includes('Add a shared queued effect-choice modal'),'M8 roadmap records the shared choice foundation');
console.log('M8 shared effect-choice regression passed.');
''',encoding='utf-8')
