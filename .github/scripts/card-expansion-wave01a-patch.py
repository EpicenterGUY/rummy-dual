from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'missing {label}')
    return text.replace(old, new, 1)


index = Path('index.html')
text = index.read_text(encoding='utf-8')

# ---------------------------------------------------------------------------
# 1) Named definitions: six live theme variants.
# ---------------------------------------------------------------------------
if "'VSHA':{slot:'HA'" not in text:
    anchor = "'HA':{n:'두 번째 심장',t:'rummyPlus1',d:'이 카드로 러미하면 새 손패를 7장 받는다. 스위치가 나를 향하고 있으면 보호막 16도 얻는다.'},"
    insert = "'VSHA':{slot:'HA',themeId:'v-signal',n:'첫 방송',t:'vFirstBroadcast',d:'이 카드로 새 3장 세트/런을 만들면, 남은 손패 1장을 덱 아래로 보내고 1장 뽑는 무료 정비를 할 수 있다. 새 조합 생성 횟수는 늘지 않는다.'},\n" + anchor
    text = replace_once(text, anchor, insert, 'VSHA definition anchor')

if "'VSC6':{slot:'C6'" not in text:
    anchor = "'C6':{n:'중간관리자',t:'middleManager',d:'샛길·조커가 대신하던 실제 카드로 들어가면 대체재 1장을 원주인 손으로 돌려보낸다.'},"
    insert = "'VSC6':{slot:'C6',themeId:'v-signal',n:'RAID',t:'vRaid',d:'이 카드를 상대 공개 조합에 붙인 뒤, 자신의 다른 공개 조합에서 자신이 제어하는 카드 1장을 무료 회수할 수 있다. 회수한 카드는 일반적인 같은 턴 버스트/체인 반환 재사용 제한을 유지한다.'},\n" + anchor
    text = replace_once(text, anchor, insert, 'VSC6 definition anchor')

if "'ZSH4':{slot:'H4'" not in text:
    anchor = "'H4':{n:'불사조',t:'heal2',d:'폭발을 맞은 다음 자기 턴에 사용하면 체력 12를 회복한다. 소모패에 있다면 한 번 손으로 되돌아올 수 있다.'},"
    insert = anchor + "\n'ZSH4':{slot:'H4',themeId:'zero-sight',n:'위장망',t:'zsCamoNet',d:'이 카드가 들어간 공개 조합을 내 표적으로 지정한다. 그 조합에 내가 제어하는 다른 카드가 하나 이상 있으면 그 조합에 보호 1을 부여한다.'},"
    text = replace_once(text, anchor, insert, 'ZSH4 definition anchor')

if "'ZSS7':{slot:'S7'" not in text:
    anchor = "'S7':{n:'검은 탄환',t:'blackBullet',d:'상대 공개 조합에 붙여 스위치를 반환하면 누적 위력이 10 증가한다.'},"
    insert = anchor + "\n'ZSS7':{slot:'S7',themeId:'zero-sight',n:'철갑탄',t:'zsArmorPiercing',d:'상대 표적 조합에 붙여 스위치를 반환하면 누적 위력이 10 증가한다. 행동 시작 시 그 조합에 보호가 남아 있었다면 대신 14 증가한다.'},"
    text = replace_once(text, anchor, insert, 'ZSS7 definition anchor')

if "'PBCA':{slot:'CA'" not in text:
    anchor = "'CA':{n:'재귀 함수',t:'repeatNumeric',d:'같은 행동의 다른 네임드 중 실제 발동 조건을 만족한 효과 하나를 복제한다. 연결자 효과면 카드 1장을 뽑고, 응급 보호구 효과면 보호막 12를 얻으며, 갈아끼우기 효과면 무료 회수 1회를 얻는다. 누적 위력은 복사하지 않는다.'},"
    insert = "'PBCA':{slot:'CA',themeId:'point-blank',n:'돌입 명령',t:'pbBreachOrder',d:'상대 공개 조합에 붙이면 그 조합을 내 접전으로 지정한다. 이미 그 조합이 내 접전이라면 대신 남은 손패 1장을 덱 아래로 보내고 1장 뽑는 무료 정비를 할 수 있다.'},\n" + anchor
    text = replace_once(text, anchor, insert, 'PBCA definition anchor')

if "'PBS3':{slot:'S3'" not in text:
    anchor = "'S3':{n:'반품 청구서',t:'returnIfIgnored',d:'상대가 버림패에서 가져간 뒤 그 턴 조합에 사용하지 못하면, 턴 종료에 원래 주인의 덱 아래로 돌아간다.'},"
    insert = anchor + "\n'PBS3':{slot:'S3',themeId:'point-blank',n:'플래시뱅',t:'pbFlashbang',d:'내 접전 조합에 붙일 때 하나를 선택한다. 그 조합에 고정 1을 부여하거나 상대에게 봉인 1을 부여한다.'},"
    text = replace_once(text, anchor, insert, 'PBS3 definition anchor')

# ---------------------------------------------------------------------------
# 2) Shared helpers for RAID and Flashbang.
# ---------------------------------------------------------------------------
if 'function requestVRaidRecoverChoice(' not in text:
    anchor = 'function recycleSpecificSpentCard(w,c,label=\'재활용업자\')'
    helper = r'''function vRaidRecoveryCandidates(w,exclude=[]){
 const ex=new Set((exclude||[]).map(c=>c.uid)),out=[];
 for(const m of meldsOf(w))for(const c of freeRecoverCandidates(w,m,exclude))if(!ex.has(c.uid))out.push({meld:m,card:c});
 return out
}
function requestVRaidRecoverChoice(w,exclude=[],onAsyncResolved=null){
 const candidates=vRaidRecoveryCandidates(w,exclude);if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}
 const apply=x=>x?.meld&&x?.card?recoverSpecificFromMeld(w,x.meld,x.card,{exclude,label:'RAID 무료 회수'}):null;
 const interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;
 if(interactive)return requestEffectChoice({title:'RAID',text:'내 다른 공개 조합에서 무료 회수할 카드 1장을 고르세요. 회수 후 조합은 유효해야 합니다.',options:candidates.map((x,i)=>({key:`raid:${x.card.uid}:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:`내 ${x.meld.type}${x.meld.type==='RUN'?` · CHAIN ${x.meld.chain||0}`:''}`,entry:x})),allowSkip:true,skipLabel:'회수하지 않기',onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});
 const chosen=candidates[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false
}
function requestPointBlankFlashbang(w,c,m,onAsyncResolved=null){
 if(!m)return false;const foe=other(w),apply=key=>{if(key==='fixed'){runEffectAction('applyStatus',{actor:w},{scope:'meld',target:m,key:'fixed',amount:1,opts:{silent:true}});log(`${c.name}: 접전 조합에 고정 1.`,'important')}else{runEffectAction('applyStatus',{actor:w},{scope:'player',target:sideObj(foe),key:'seal',amount:1,opts:{silent:true}});log(`${c.name}: ${foe==='player'?'나':'상대'}에게 봉인 1.`,'important')}return key};
 const interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function';
 if(interactive)return requestEffectChoice({title:c.name,text:'접전을 흔들 효과를 고르세요.',options:[{key:'fixed',label:'조합 고정',detail:'이 접전 조합에 고정 1'},{key:'seal',label:'상대 봉인',detail:'상대의 다음 네임드 효과 봉인 1'}],onChoose:o=>{const key=o?.key||'fixed';apply(key);if(typeof onAsyncResolved==='function')onAsyncResolved(key)}});
 const key=(m.cards?.length||0)>=4?'fixed':'seal';apply(key);if(typeof onAsyncResolved==='function')onAsyncResolved(key);return false
}
'''
    text = replace_once(text, anchor, helper + anchor, 'wave01A helper anchor')

# ---------------------------------------------------------------------------
# 3) Effect resolution cases.
# ---------------------------------------------------------------------------
if "case'vFirstBroadcast'" not in text:
    old = "case'vGatherAll':case'vEndurance':break;case'zsObserver':"
    new = "case'vFirstBroadcast':if(ctx.isNew){const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}break;case'vRaid':if(ctx.isAttach&&ctx.targetOwner===foe){const paused=requestVRaidRecoverChoice(w,cards,resume);if(paused)return pause()}break;case'vGatherAll':case'vEndurance':break;case'zsCamoNet':if(ctx.meld){if(typeof setZeroSightTarget==='function')setZeroSightTarget(w,ctx.meld,{reason:'camoNet'});if((ctx.meld.cards||[]).filter(x=>x.owner===w&&x.uid!==c.uid).length>0)runEffectAction('applyStatus',{actor:w},{scope:'meld',target:ctx.meld,key:'protect',amount:1,opts:{silent:true}})}break;case'zsArmorPiercing':if(isReturning&&ctx.targetOwner===foe&&ctx.meld&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,ctx.meld)){fx.bonus+=officialStatusValue('meld',ctx.meld,'protect')>0?14:10}break;case'pbBreachOrder':if(ctx.isAttach&&ctx.targetOwner===foe&&ctx.meld){if(typeof isPointBlankClash==='function'&&isPointBlankClash(w,ctx.meld)){const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}else if(typeof setPointBlankClash==='function')setPointBlankClash(w,ctx.meld,{reason:'breachOrder'})}break;case'pbFlashbang':if(ctx.isAttach&&ctx.targetOwner===foe&&ctx.meld&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,ctx.meld)){const paused=requestPointBlankFlashbang(w,c,ctx.meld,resume);if(paused)return pause()}break;case'zsObserver':"
    text = replace_once(text, old, new, 'resolveEffects theme cases')

# ---------------------------------------------------------------------------
# 4) Reward/action tags and theme entry recognition.
# ---------------------------------------------------------------------------
if "vFirstBroadcast:['combo','cycle']" not in text:
    old = "vEncore:['cycle','combo'],vGatherAll:['hold','combo','cycle'],vEndurance:['extend','sustain','cycle'],zsObserver:['control','cycle','combo'],zsScopeAdjust:['control','cycle','interact'],zsBallistics:['pressure','control'],zsOneShot:['pressure','control','status']"
    new = "vEncore:['cycle','combo'],vFirstBroadcast:['combo','cycle'],vRaid:['interact','recover','cycle'],vGatherAll:['hold','combo','cycle'],vEndurance:['extend','sustain','cycle'],zsObserver:['control','cycle','combo'],zsScopeAdjust:['control','cycle','interact'],zsCamoNet:['control','sustain','combo'],zsArmorPiercing:['pressure','control'],zsBallistics:['pressure','control'],zsOneShot:['pressure','control','status'],pbBreachOrder:['interact','control','cycle'],pbFlashbang:['interact','control','status']"
    text = replace_once(text, old, new, 'TENDENCY_BY_TAG theme tail')

if "'point-blank':Object.freeze(['pbBreachOrder'])" not in text:
    old = "const ROGUELIKE_THEME_ENTRY_TAGS=Object.freeze({'v-signal':Object.freeze(['vEncore']),'zero-sight':Object.freeze(['zsObserver','zsScopeAdjust'])});"
    new = "const ROGUELIKE_THEME_ENTRY_TAGS=Object.freeze({'v-signal':Object.freeze(['vEncore','vFirstBroadcast']),'zero-sight':Object.freeze(['zsObserver','zsScopeAdjust','zsCamoNet']),'point-blank':Object.freeze(['pbBreachOrder'])});"
    text = replace_once(text, old, new, 'roguelike theme entry tags')

# ---------------------------------------------------------------------------
# 5) Unlock progression: all six are obtainable by total clear 3.
# ---------------------------------------------------------------------------
if "'VSHA'" not in text[text.find('const UNLOCK_GROUPS='):text.find('function unlockedNamed')]:
    old = "{id:'g1',label:'전체 1클리어',kind:'mixed',when:p=>p.totalClears>=1,items:['S6','H7','D8','C2','ZSCA','ZSC2','DA','D3'],fields:['F1']},"
    new = "{id:'g1',label:'전체 1클리어',kind:'mixed',when:p=>p.totalClears>=1,items:['S6','H7','D8','C2','ZSCA','ZSC2','VSHA','PBCA','DA','D3'],fields:['F1']},"
    text = replace_once(text, old, new, 'g1 unlocks')
    old = "{id:'g2',label:'전체 2클리어',kind:'mixed',when:p=>p.totalClears>=2,items:['S8','H5','VSH5','D9','C8','D10','C3'],fields:['F2']},"
    new = "{id:'g2',label:'전체 2클리어',kind:'mixed',when:p=>p.totalClears>=2,items:['S8','H5','VSH5','VSC6','ZSH4','D9','C8','D10','C3'],fields:['F2']},"
    text = replace_once(text, old, new, 'g2 unlocks')
    old = "{id:'g3',label:'전체 3클리어',kind:'mixed',when:p=>p.totalClears>=3,items:['S9','H10','D2','VSD4','C6','SJ','H3'],fields:[]},"
    new = "{id:'g3',label:'전체 3클리어',kind:'mixed',when:p=>p.totalClears>=3,items:['S9','H10','D2','VSD4','C6','SJ','H3','PBS3'],fields:[]},"
    text = replace_once(text, old, new, 'g3 unlocks')
    old = "{id:'zs3',label:'전체 3클리어 · ZERO-SIGHT',kind:'theme',when:p=>p.totalClears>=3,items:['ZSD6'],fields:[]},"
    new = "{id:'zs3',label:'전체 3클리어 · ZERO-SIGHT',kind:'theme',when:p=>p.totalClears>=3,items:['ZSD6','ZSS7'],fields:[]},"
    text = replace_once(text, old, new, 'zs3 unlocks')

# ---------------------------------------------------------------------------
# 6) Enemy preview pools so the new cards appear in actual roguelike combat.
# ---------------------------------------------------------------------------
if "'VSHA','VSC6'" not in text:
    old = "named:Object.freeze(['VSH5','H2','D2','D8','H10','C10','VSD4','H3','C8','H8','VSCK','CJ'])"
    new = "named:Object.freeze(['VSH5','VSHA','VSC6','H2','D2','D8','H10','C10','VSD4','H3','C8','H8','VSCK','CJ'])"
    text = replace_once(text, old, new, 'neon arc named pool')
if "'ZSH4','ZSS7','PBCA','PBS3'" not in text:
    old = "named:Object.freeze(['ZSCA','ZSC2','S5','S7B','C5B','PBH7','ZSD6','H8','PBDJ','S8','ZSSK','S6'])"
    new = "named:Object.freeze(['ZSCA','ZSC2','ZSH4','ZSS7','PBCA','PBS3','S5','S7B','C5B','PBH7','ZSD6','H8','PBDJ','S8','ZSSK','S6'])"
    text = replace_once(text, old, new, 'red zone named pool')

index.write_text(text, encoding='utf-8')

# ---------------------------------------------------------------------------
# 7) Regression coverage.
# ---------------------------------------------------------------------------
test = Path('tests/card-expansion-wave01a.mjs')
if not test.exists():
    test.write_text(r'''import fs from 'node:fs';
const src=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
const defs=[
 ['VSHA','vFirstBroadcast','v-signal','첫 방송'],
 ['VSC6','vRaid','v-signal','RAID'],
 ['ZSH4','zsCamoNet','zero-sight','위장망'],
 ['ZSS7','zsArmorPiercing','zero-sight','철갑탄'],
 ['PBCA','pbBreachOrder','point-blank','돌입 명령'],
 ['PBS3','pbFlashbang','point-blank','플래시뱅']
];
for(const [id,tag,theme,name] of defs){
 ok(src.includes(`'${id}':{slot:`),`${id} definition exists`);
 ok(src.includes(`themeId:'${theme}',n:'${name}',t:'${tag}'`),`${id} keeps the intended theme/tag/name contract`);
 ok(src.includes(`case'${tag}'`),`${id} has a live resolveEffects branch`);
}
ok(src.includes('function requestVRaidRecoverChoice('),'RAID uses the shared legal free-recovery path');
ok(src.includes("recoverSpecificFromMeld(w,x.meld,x.card,{exclude,label:'RAID 무료 회수'})"),'RAID preserves normal recovery legality and event emission');
ok(src.includes("setZeroSightTarget(w,ctx.meld,{reason:'camoNet'})"),'Camo Net uses canonical ZERO-SIGHT target metadata');
ok(src.includes("officialStatusValue('meld',ctx.meld,'protect')>0?14:10"),'Armor Piercing has only its locked +10/+14 return bonus');
ok(src.includes("setPointBlankClash(w,ctx.meld,{reason:'breachOrder'})"),'Breach Order uses canonical POINT-BLANK clash metadata');
ok(src.includes("scope:'meld',target:m,key:'fixed',amount:1")&&src.includes("scope:'player',target:sideObj(foe),key:'seal',amount:1"),'Flashbang reuses official fixed/seal states');
ok(src.includes("items:['S6','H7','D8','C2','ZSCA','ZSC2','VSHA','PBCA'"),'first-clear unlock contains the two new entry cards');
ok(src.includes("items:['S8','H5','VSH5','VSC6','ZSH4'"),'second-clear unlock contains RAID and Camo Net');
ok(src.includes("'PBS3'],fields:[]"),'third-clear mixed unlock contains Flashbang');
ok(src.includes("items:['ZSD6','ZSS7']"),'ZERO-SIGHT third-clear unlock contains Armor Piercing');
ok(!src.includes("case'vRaid':if(ctx.isAttach&&ctx.targetOwner===foe){fx.bonus"),'RAID never adds direct switch power');
ok(!src.includes("case'pbBreachOrder':if(ctx.isAttach&&ctx.targetOwner===foe){fx.bonus"),'Breach Order never adds direct switch power');
console.log('Card expansion Wave 01A regression passed.');
''', encoding='utf-8')

# ---------------------------------------------------------------------------
# 8) Keep implementation planning docs honest.
# ---------------------------------------------------------------------------
plan = Path('docs/CARD_EXPANSION_WAVE_01.md')
if plan.exists():
    p = plan.read_text(encoding='utf-8')
    p = p.replace('Status: IMPLEMENTATION TARGET / NOT YET LIVE', 'Status: WAVE 01-A LIVE (6) / WAVE 01-B·01-C TARGET (12)')
    p = p.replace('## Wave 01-A — 테마 초동 6장', '## Wave 01-A — LIVE 6장')
    p = p.replace('1. VSHA `첫 방송`\n2. VSC6 `RAID`\n3. ZSD2 `거리측정기`\n4. ZSH4 `위장망`\n5. PBCA `돌입 명령`\n6. PBHA `브리치 실드`', '1. VSHA `첫 방송` — LIVE\n2. VSC6 `RAID` — LIVE\n3. ZSH4 `위장망` — LIVE\n4. ZSS7 `철갑탄` — LIVE\n5. PBCA `돌입 명령` — LIVE\n6. PBS3 `플래시뱅` — LIVE')
    p = p.replace('이 6장은 각 테마의 시작 빈도를 올리는 카드다. 먼저 넣어야 테마 전용 후속 카드의 플레이테스트가 의미가 있다.', '초동뿐 아니라 표적 화력과 접전 제압까지 포함한 첫 라이브 슬라이스다. 기존 공용 훅과 상태만 사용하며 별도 전용 자원은 추가하지 않는다.')
    p = p.replace('상대 표적 조합에 붙여 SWITCH를 반환하면 누적 위력 +10. 그 조합의 보호 상태가 이 행동을 막거나 소모되었다면 대신 +14.', '상대 표적 조합에 붙여 SWITCH를 반환하면 누적 위력 +10. 행동 시작 시 그 조합에 보호가 남아 있었다면 대신 +14.')
    plan.write_text(p, encoding='utf-8')

road = Path('ROADMAP.md')
r = road.read_text(encoding='utf-8')
bullet = "  - [x] 카드 증원 Wave 01-A — V-SIGNAL `첫 방송/RAID`, ZERO-SIGHT `위장망/철갑탄`, POINT-BLANK `돌입 명령/플래시뱅` 6장 라이브. 기존 표적·접전·회수·정비·공식 상태 훅만 재사용하고, 신규 전용 자원과 반환 횟수 우회는 추가하지 않음. `tests/card-expansion-wave01a.mjs` + 전체 회귀 통과를 게이트로 사용"
if bullet not in r:
    anchor = '## M8'
    pos = r.find(anchor)
    if pos < 0:
        anchor = '# M8'
        pos = r.find(anchor)
    if pos < 0:
        r += '\n\n' + bullet + '\n'
    else:
        line_end = r.find('\n', pos)
        r = r[:line_end+1] + bullet + '\n' + r[line_end+1:]
    road.write_text(r, encoding='utf-8')
