from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
text=index.read_text()

# 1) Promote ZERO-SIGHT to a playable open theme now that its first starter pair is live.
old_profile=" 'zero-sight':Object.freeze({id:'zero-sight',displayName:'ZERO-SIGHT',short:'정밀 표적',desc:'표적·관측·준비형 카드군. 기반 시스템 구현 중입니다.',themeId:'zero-sight',live:false}),"
new_profile=" 'zero-sight':Object.freeze({id:'zero-sight',displayName:'ZERO-SIGHT',short:'정밀 표적',desc:'표적 생성·이전과 패순환을 중심으로 정밀한 반환을 준비합니다. 일반 카드도 함께 섞입니다.',themeId:'zero-sight',live:true}),"
assert old_profile in text,'ZERO-SIGHT profile anchor changed'
text=text.replace(old_profile,new_profile,1)

# 2) Add first live ZERO-SIGHT variants on A♣ / 2♣.
old_cards="'CA':{n:'재귀 함수',t:'repeatNumeric',d:'같은 행동의 다른 네임드 중 실제 발동 조건을 만족한 효과 하나를 복제한다. 연결자면 1장 뽑기, 응급 보호구면 보호막 12, 갈아끼우기면 무료 회수 1회. 누적 위력은 복사하지 않는다.'},\n'C2':{n:'연결자',t:'run4Draw',d:'이 카드로 RUN이 4장 이상이 되면 1장 뽑기. 6장 이상이면 뽑은 뒤 손패 1장을 덱 아래로 보낼 수 있다.'},"
new_cards="'CA':{n:'재귀 함수',t:'repeatNumeric',d:'같은 행동의 다른 네임드 중 실제 발동 조건을 만족한 효과 하나를 복제한다. 연결자면 1장 뽑기, 응급 보호구면 보호막 12, 갈아끼우기면 무료 회수 1회. 누적 위력은 복사하지 않는다.'},\n'ZSCA':{slot:'CA',themeId:'zero-sight',n:'관측수',t:'zsObserver',d:'이 카드를 사용한 공개 조합을 내 표적으로 지정한다. 지정 후 남은 손패가 있으면 그중 1장을 덱 아래로 보내고 1장 뽑아 무료 패순환한다.'},\n'C2':{n:'연결자',t:'run4Draw',d:'이 카드로 RUN이 4장 이상이 되면 1장 뽑기. 6장 이상이면 뽑은 뒤 손패 1장을 덱 아래로 보낼 수 있다.'},\n'ZSC2':{slot:'C2',themeId:'zero-sight',n:'스코프 조정',t:'zsScopeAdjust',d:'내 표적이 있으면 다른 공개 조합으로 이전한다. 표적이 없거나 옮길 다른 조합이 없으면 남은 손패 1장을 덱 아래로 보내고 1장 뽑아 패순환한다.'},"
assert old_cards in text,'CA/C2 named anchor changed'
text=text.replace(old_cards,new_cards,1)

# 3) Give the new tags normal open-deck tendencies.
old_tendency="vEncore:['cycle','combo'],vGatherAll:['hold','combo','cycle'],vEndurance:['extend','sustain','cycle']"
new_tendency="vEncore:['cycle','combo'],vGatherAll:['hold','combo','cycle'],vEndurance:['extend','sustain','cycle'],zsObserver:['control','cycle','combo'],zsScopeAdjust:['control','cycle','interact']"
assert old_tendency in text,'tendency tail anchor changed'
text=text.replace(old_tendency,new_tendency,1)

# 4) Unlock both starter variants at 1 clear and expose the theme at that timing.
old_g1=" {id:'g1',label:'전체 1클리어',kind:'mixed',when:p=>p.totalClears>=1,items:['S6','H7','D8','C2','DA','D3'],fields:['F1']},"
new_g1=" {id:'g1',label:'전체 1클리어',kind:'mixed',when:p=>p.totalClears>=1,items:['S6','H7','D8','C2','ZSCA','ZSC2','DA','D3'],fields:['F1']},"
assert old_g1 in text,'g1 unlock anchor changed'
text=text.replace(old_g1,new_g1,1)
old_lock="function themeBuildLockText(id){if(id==='v-signal')return'테마 카드 해금 필요 · 전체 2클리어부터';return'개발 중'}"
new_lock="function themeBuildLockText(id){if(id==='v-signal')return'테마 카드 해금 필요 · 전체 2클리어부터';if(id==='zero-sight')return'테마 카드 해금 필요 · 전체 1클리어부터';return'개발 중'}"
assert old_lock in text,'theme lock anchor changed'
text=text.replace(old_lock,new_lock,1)

# 5) Shared ZERO-SIGHT cycle and relocation choices. Human gets exact choice; CPU stays deterministic.
old_insert="function firstCopyEffectSource(cards,self,tags){"
new_insert="""function zeroSightCycleCandidates(w,exclude=[]){const ex=new Set((exclude||[]).map(c=>c.uid));return sideObj(w).hand.filter(c=>!ex.has(c.uid))}\nfunction cycleSpecificHandCard(w,c,label='패순환'){const side=sideObj(w),i=side.hand.findIndex(x=>x.uid===c?.uid);if(i<0)return null;const[chosen]=side.hand.splice(i,1);chosen.fromDiscard=false;chosen.contractActive=false;chosen.age=0;side.deck.unshift(chosen);const got=drawOne(w,false);if(typeof log==='function')log(`${label}: ${cardText(chosen)}를 덱 아래로 보내고 ${got?cardText(got):'카드 없음'}을 뽑았습니다.`,'good');if(w==='player'&&typeof flashPile==='function')flashPile('deckPile');return got}\nfunction requestZeroSightCycle(w,source,exclude=[],onAsyncResolved=null){const candidates=zeroSightCycleCandidates(w,exclude);if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=c=>cycleSpecificHandCard(w,c,source?.name||'ZERO-SIGHT 패순환'),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive)return requestEffectChoice({title:source?.name||'ZERO-SIGHT',text:'덱 아래로 보내고 1장 교체할 남은 손패를 고르세요.',options:candidates.map(c=>({key:c.uid,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:'덱 아래로 보낸 뒤 1장 뽑기',card:c})),onChoose:o=>{if(o?.card)apply(o.card);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.card||null)}});const chosen=[...candidates].sort((a,b)=>b.age-a.age)[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}\nfunction zeroSightRelocationTargets(w,current=null){if(!current)return[];const out=[];for(const side of[other(w),w])for(const m of meldsOf(side))if(m!==current)out.push({side,m});return out}\nfunction requestZeroSightRelocation(w,source,ctx={},onAsyncResolved=null){const current=typeof zeroSightTargetMeld==='function'?zeroSightTargetMeld(w):null,candidates=zeroSightRelocationTargets(w,current);if(!current||!candidates.length){if(typeof log==='function')log(`${source?.name||'스코프 조정'}: ${!current?'현재 표적이 없어':'옮길 다른 공개 조합이 없어'} 패순환으로 전환합니다.`,'important');return requestZeroSightCycle(w,source,ctx.cards||[],onAsyncResolved)}const apply=entry=>{if(!entry?.m)return false;return typeof setZeroSightTarget==='function'?setZeroSightTarget(w,entry.m,{reason:'scopeAdjust'}):false},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive)return requestEffectChoice({title:source?.name||'스코프 조정',text:'현재 표적을 이전할 다른 공개 조합을 고르세요.',options:candidates.map((x,i)=>({key:`zs:${i}`,label:`${x.side===w?'내':'상대'} ${x.m.type} · ${x.m.cards.length}장`,detail:'표적 이전',entry:x})),onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});apply(candidates[0]);if(typeof onAsyncResolved==='function')onAsyncResolved(candidates[0]);return false}\nfunction firstCopyEffectSource(cards,self,tags){"""
assert old_insert in text,'ZERO-SIGHT helper insertion anchor changed'
text=text.replace(old_insert,new_insert,1)

# 6) Wire starter effects into the resumable named-effect resolver.
old_resolve="case'vGatherAll':case'vEndurance':break;case'vacancyJoker':case'rebelJoker':break"
new_resolve="case'vGatherAll':case'vEndurance':break;case'zsObserver':if(ctx.meld){if(typeof setZeroSightTarget==='function')setZeroSightTarget(w,ctx.meld,{reason:'observer'});const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}break;case'zsScopeAdjust':{const paused=requestZeroSightRelocation(w,c,{...ctx,cards},resume);if(paused)return pause();break}case'vacancyJoker':case'rebelJoker':break"
assert old_resolve in text,'resolveEffects theme tail anchor changed'
text=text.replace(old_resolve,new_resolve,1)

index.write_text(text)

# Roadmap sync: this detailed implementation item did not yet exist in ROADMAP, so add it next to the mixed regression lock.
r=road.read_text()
road_anchor='- [x] ZERO-SIGHT ↔ 일반/V-SIGNAL/POINT-BLANK 혼합 회귀 테스트 — 표적은 카드군과 분리된 공개 조합 메타데이터로 유지되며, 일반 카드의 붙이기·V-SIGNAL 앙코르 회수·혼합 조합 정리/보존·POINT-BLANK 카드 정체성이 같은 표적 이벤트 경로에서 충돌하지 않는 것을 실행 회귀로 잠금'
assert road_anchor in r,'ROADMAP ZERO-SIGHT mixed anchor changed'
road_lines="- [x] 표적 없이 잡힌 스타터의 대체 패순환 처리 — A♣ `관측수`는 사용 조합을 즉시 표적으로 만들어 초동을 열고 무료 1장 교체를 제공; 2♣ `스코프 조정`은 기존 표적을 다른 공개 조합으로 이전하되 표적이 없거나 이전 목적지가 없으면 정확한 손패 1장 패순환으로 전환\n- [x] ZERO-SIGHT 첫 라이브 스타터 페어 — A♣ `관측수` / 2♣ `스코프 조정`을 전체 1클리어 해금으로 추가하고 ZERO-SIGHT 오픈형 테마 선택을 활성화\n"
r=r.replace(road_anchor,road_lines+road_anchor,1)
road.write_text(r)

# Canonical theme doc sync.
t=theme.read_text()
old_check='- [ ] 표적 없이 잡힌 스타터의 대체 패순환 처리'
assert old_check in t,'theme ZERO-SIGHT fallback anchor changed'
t=t.replace(old_check,"- [x] 표적 없이 잡힌 스타터의 대체 패순환 처리 — `관측수`는 사용한 조합 자체를 표적으로 지정해 무표적 초동을 열고, `스코프 조정`은 표적/이전 목적지가 없으면 남은 손패 1장을 정확히 골라 덱 아래로 보내고 1장 뽑는다.",1)
check_anchor='- [x] ZERO-SIGHT ↔ 일반/V-SIGNAL/POINT-BLANK 혼합 회귀 테스트'
assert check_anchor in t,'theme ZERO-SIGHT mixed anchor missing'
t=t.replace(check_anchor,"- [x] 첫 라이브 스타터 구현 — A♣ `관측수` / 2♣ `스코프 조정`; 둘 다 전용 자원 없이 표적·공용 패순환만 사용하며 전체 1클리어부터 오픈형 ZERO-SIGHT 빌드에 편성\n"+check_anchor,1)
theme.write_text(t)
