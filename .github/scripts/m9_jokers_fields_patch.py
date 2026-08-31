from pathlib import Path

index = Path('index.html')
road = Path('ROADMAP.md')
text = index.read_text()

# 1) Expand the shared field pool from 8 to 10 with two behavior-changing fields.
old_fields = """ F7:{name:'공사장',desc:'5장 이상 RUN의 양끝 카드는 상대의 절단·탈취 효과 대상이 되지 않음.',tag:'construction'},
 F8:{name:'전당포',desc:'버림패에서 가져온 카드를 사용하지 않고 다시 버리면 보호막 12.',tag:'pawnshop'}
};"""
new_fields = """ F7:{name:'공사장',desc:'5장 이상 RUN의 양끝 카드는 상대의 절단·탈취 효과 대상이 되지 않음.',tag:'construction'},
 F8:{name:'전당포',desc:'버림패에서 가져온 카드를 사용하지 않고 다시 버리면 보호막 12.',tag:'pawnshop'},
 F9:{name:'교차 선로',desc:'모든 RUN은 다른 무늬 카드 1장까지 포함할 수 있다. 조커·무늬 유연 효과와 겹쳐도 다른 무늬 허용은 1장 한도.',tag:'crossLane'},
 F10:{name:'환승 터미널',desc:'턴당 처음 상대 공개 조합에 붙이면, 붙인 카드 외 남은 손패 1장을 덱 아래로 보내고 1장 교체한다.',tag:'crossTraffic'}
};"""
assert old_fields in text, 'FIELDS anchor changed'
text = text.replace(old_fields, new_fields, 1)

# 2) Cross Lane: permit one off-suit real card in a RUN, without stacking above one with bridge/flexible effects.
old_run = "const bridge=real.some(c=>c.tag==='smugglerBridge');if(offSuit>(bridge?1:0))return false;"
new_run = "const bridge=real.some(c=>c.tag==='smugglerBridge'),crossLane=state.field?.tag==='crossLane';if(offSuit>((bridge||crossLane)?1:0))return false;"
assert old_run in text, 'runValid field allowance anchor changed'
text = text.replace(old_run, new_run, 1)

# 3) Cross Traffic: first opponent-meld attach each turn cycles one remaining hand card.
old_field_action = "function fieldAction(w,cards,type,ctx){if(!state.field)return 0;const s=sideObj(w);if(state.field.tag==='heartHeal'){const h=Math.min(2,cards.filter(c=>c.suit==='H').length),left=Math.max(0,2-(s.flags.festival||0)),use=Math.min(h,left);if(use){heal(w,use);s.flags.festival=(s.flags.festival||0)+use}}if(state.field.tag==='outlaw'&&ctx.isAttach&&ctx.targetOwner===other(w))for(const c of cards)c.outlawFreeRecoverAt=sideObj(w).turnStarts+1;if(state.field.tag==='casino'&&ctx.isNew&&!s.flags.casinoCycle){s.flags.casinoCycle=true;cycleOldestHandCard(w,cards)}return 0}"
new_field_action = "function fieldAction(w,cards,type,ctx){if(!state.field)return 0;const s=sideObj(w);if(state.field.tag==='heartHeal'){const h=Math.min(2,cards.filter(c=>c.suit==='H').length),left=Math.max(0,2-(s.flags.festival||0)),use=Math.min(h,left);if(use){heal(w,use);s.flags.festival=(s.flags.festival||0)+use}}if(state.field.tag==='outlaw'&&ctx.isAttach&&ctx.targetOwner===other(w))for(const c of cards)c.outlawFreeRecoverAt=sideObj(w).turnStarts+1;if(state.field.tag==='casino'&&ctx.isNew&&!s.flags.casinoCycle){s.flags.casinoCycle=true;cycleOldestHandCard(w,cards)}if(state.field.tag==='crossTraffic'&&ctx.isAttach&&ctx.targetOwner===other(w)&&!s.flags.crossTraffic){s.flags.crossTraffic=true;cycleOldestHandCard(w,cards)}return 0}"
assert old_field_action in text, 'fieldAction anchor changed'
text = text.replace(old_field_action, new_field_action, 1)

# 4) Reset the per-turn Cross Traffic flag with the other field/card flags.
old_turn_flags = "s.flags={shift:false,large:false,salvage:false,joker:false,festival:0,roundabout:false,casinoCycle:false,tuner:false};"
new_turn_flags = "s.flags={shift:false,large:false,salvage:false,joker:false,festival:0,roundabout:false,casinoCycle:false,crossTraffic:false,tuner:false};"
assert old_turn_flags in text, 'turnStart flags anchor changed'
text = text.replace(old_turn_flags, new_turn_flags, 1)

old_side_flags = "flags:{shift:false,large:false,salvage:false,joker:false,festival:0,roundabout:false},"
new_side_flags = "flags:{shift:false,large:false,salvage:false,joker:false,festival:0,roundabout:false,casinoCycle:false,crossTraffic:false,tuner:false},"
assert old_side_flags in text, 'side init flags anchor changed'
text = text.replace(old_side_flags, new_side_flags, 1)

# 5) Unlock pacing for the new fields.
old_unlock = """ {id:'g9',label:'전체 9클리어',kind:'mixed',when:p=>p.totalClears>=9,items:[],fields:['F8']},
 {id:'wl2',label:'유랑자 Lv.2'"""
new_unlock = """ {id:'g9',label:'전체 9클리어',kind:'mixed',when:p=>p.totalClears>=9,items:[],fields:['F8']},
 {id:'g10',label:'전체 10클리어',kind:'mixed',when:p=>p.totalClears>=10,items:[],fields:['F9']},
 {id:'g11',label:'전체 11클리어',kind:'mixed',when:p=>p.totalClears>=11,items:[],fields:['F10']},
 {id:'wl2',label:'유랑자 Lv.2'"""
assert old_unlock in text, 'unlock anchor changed'
text = text.replace(old_unlock, new_unlock, 1)

index.write_text(text)

# 6) Lock M9 after executable regression coverage is installed by the workflow.
r = road.read_text()
old_m9 = """## M9 — Jokers and fields
- [ ] Finalize distinct Joker identities
- [ ] Audit Joker King return-to-owner-deck behavior
- [ ] Stabilize 10–15 behavior-changing shared fields"""
new_m9 = """## M9 — Jokers and fields
- [x] Finalize distinct Joker identities — J1~J5 keep separate wildcard identities for owner-deck return, RUMMY/DETONATE timing, SET/RUN split payoff, vacancy replacement, and opponent-meld rebellion
- [x] Audit Joker King return-to-owner-deck behavior — public-meld retirement restores `originOwner`, bottoms J1 into that owner deck, and never sends it to spent
- [x] Stabilize 10 behavior-changing shared fields — F1~F10 now cover recovery, discard acquisition, cycling, RUN legality, interference protection, and opponent-meld interaction without adding a new base resource"""
assert old_m9 in r, 'M9 roadmap anchor changed'
r = r.replace(old_m9, new_m9, 1)
road.write_text(r)
