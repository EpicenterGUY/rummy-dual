from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'missing {label}')
    return text.replace(old, new, 1)


index = Path('index.html')
text = index.read_text(encoding='utf-8')

if 'function roguelikeRunHistoryKey()' not in text:
    anchor = "function prepareRoguelikeRunDraft(starterId=progress?.roguelikeStarter||'wanderer'){const draft=createRoguelikeRunDraft(starterId);return saveRoguelikeRunDraft(draft)?draft:null}\nfunction roguelikeRunCompletionText(draft){"
    history = r"""function prepareRoguelikeRunDraft(starterId=progress?.roguelikeStarter||'wanderer'){const draft=createRoguelikeRunDraft(starterId);return saveRoguelikeRunDraft(draft)?draft:null}
function roguelikeRunHistoryKey(){return'rummyDuelRoguelikeRunHistoryV1'}
function roguelikeEmptyRunHistory(){return{version:1,entries:[]}}
function roguelikeRunHistoryEntry(draft){
 const clean=normalizeRoguelikeRunDraft(draft);if(!clean||clean.status!=='completed')return null;
 const rewards=clean.rewardNodes.entries,battleWins=rewards.filter(n=>n.source==='battle').length,rewardClaimed=rewards.filter(n=>n.status==='claimed').length,rewardSkipped=rewards.filter(n=>n.status==='skipped').length,namedCount=clean.runDeck.cards.filter(c=>c.variantId).length;
 const finalDeck={version:1,revision:clean.runDeck.revision,cards:clean.runDeck.cards.map(c=>({...c}))};
 return{version:1,runId:clean.runId,completedAt:clean.completedAt,starterId:clean.starterId,starterName:roguelikeStarterProfile(clean.starterId).name,regionPath:[...clean.regionPath],regionNames:clean.regionPath.map(id=>roguelikeRegionRewardProfile(id)?.name||id),battleWins,rewardClaimed,rewardSkipped,deckRevision:clean.runDeck.revision,namedCount,finalDeck,finalDeckSignature:roguelikeRunDeckSignature(finalDeck),rewards:rewards.map(n=>({sequence:n.sequence,source:n.source,status:n.status,selectedId:n.selectedId,...(n.battleNodeId?{battleNodeId:n.battleNodeId}:{}),...(n.regionId?{regionId:n.regionId}:{})}))}
}
function normalizeRoguelikeRunHistory(input){
 if(!input||input.version!==1||!Array.isArray(input.entries)||input.entries.length>100)return null;
 const entries=[],seen=new Set();
 for(const raw of input.entries){
  if(!raw||raw.version!==1||typeof raw.runId!=='string'||!raw.runId||seen.has(raw.runId)||typeof raw.completedAt!=='string'||!Number.isFinite(Date.parse(raw.completedAt))||new Date(raw.completedAt).toISOString()!==raw.completedAt||typeof raw.starterId!=='string'||!raw.starterId||typeof raw.starterName!=='string'||!raw.starterName)return null;
  if(!Array.isArray(raw.regionPath)||raw.regionPath.length>8||new Set(raw.regionPath).size!==raw.regionPath.length||raw.regionPath.some(id=>typeof id!=='string'||!id)||!Array.isArray(raw.regionNames)||raw.regionNames.length!==raw.regionPath.length||raw.regionNames.some(name=>typeof name!=='string'||!name))return null;
  if(!Number.isSafeInteger(raw.battleWins)||raw.battleWins<1||!Number.isSafeInteger(raw.rewardClaimed)||raw.rewardClaimed<0||!Number.isSafeInteger(raw.rewardSkipped)||raw.rewardSkipped<0||!Number.isSafeInteger(raw.deckRevision)||raw.deckRevision<0||!Number.isSafeInteger(raw.namedCount)||raw.namedCount<0||typeof raw.finalDeckSignature!=='string'||!raw.finalDeckSignature||!Array.isArray(raw.rewards)||raw.rewards.length!==raw.rewardClaimed+raw.rewardSkipped)return null;
  const finalDeck=normalizeRoguelikeRunDeck(raw.finalDeck,raw.starterId);if(!finalDeck||finalDeck.revision!==raw.deckRevision||raw.namedCount!==finalDeck.cards.filter(c=>c.variantId).length||raw.finalDeckSignature!==roguelikeRunDeckSignature(finalDeck))return null;
  let claimed=0,skipped=0,battles=0;const rewards=[];
  for(let i=0;i<raw.rewards.length;i++){
   const r=raw.rewards[i];if(!r||r.sequence!==i+1||!['prototype','battle'].includes(r.source)||!['claimed','skipped'].includes(r.status))return null;
   if(r.status==='claimed'){if(typeof r.selectedId!=='string'||!r.selectedId)return null;claimed++}else{if(r.selectedId!==null)return null;skipped++}
   if(r.source==='battle'){if(typeof r.battleNodeId!=='string'||!r.battleNodeId)return null;battles++}else if(r.battleNodeId!==undefined||r.regionId!==undefined)return null;
   if(r.regionId!==undefined&&(typeof r.regionId!=='string'||!r.regionId))return null;
   rewards.push({sequence:r.sequence,source:r.source,status:r.status,selectedId:r.selectedId,...(r.battleNodeId?{battleNodeId:r.battleNodeId}:{}),...(r.regionId?{regionId:r.regionId}:{})})
  }
  if(claimed!==raw.rewardClaimed||skipped!==raw.rewardSkipped||battles!==raw.battleWins)return null;
  seen.add(raw.runId);entries.push({version:1,runId:raw.runId,completedAt:raw.completedAt,starterId:raw.starterId,starterName:raw.starterName,regionPath:[...raw.regionPath],regionNames:[...raw.regionNames],battleWins:raw.battleWins,rewardClaimed:raw.rewardClaimed,rewardSkipped:raw.rewardSkipped,deckRevision:raw.deckRevision,namedCount:raw.namedCount,finalDeck,finalDeckSignature:raw.finalDeckSignature,rewards})
 }
 return{version:1,entries}
}
function loadRoguelikeRunHistory(){if(typeof localStorage==='undefined')return roguelikeEmptyRunHistory();try{return normalizeRoguelikeRunHistory(JSON.parse(localStorage.getItem(roguelikeRunHistoryKey())||'null'))||roguelikeEmptyRunHistory()}catch{return roguelikeEmptyRunHistory()}}
function saveRoguelikeRunHistory(history){if(typeof localStorage==='undefined')return false;const clean=normalizeRoguelikeRunHistory(history);if(!clean)return false;try{localStorage.setItem(roguelikeRunHistoryKey(),JSON.stringify(clean));return true}catch{return false}}
function roguelikeArchiveCompletedRun(draft){
 const entry=roguelikeRunHistoryEntry(draft);if(!entry)return false;
 const history=loadRoguelikeRunHistory(),existing=history.entries.find(x=>x.runId===entry.runId);
 if(existing)return JSON.stringify(existing)===JSON.stringify(entry);
 history.entries.unshift(entry);history.entries=history.entries.slice(0,24);
 return saveRoguelikeRunHistory(history)
}
function roguelikeRunArchiveText(draft=null){
 const history=loadRoguelikeRunHistory(),currentId=draft?.status==='completed'?draft.runId:null,currentStored=currentId&&history.entries.some(x=>x.runId===currentId);
 if(!history.entries.length)return draft?.status==='completed'?'<b class="red">완료 아카이브 · 이번 런 기록 저장 대기</b>':'완료 아카이브 · 아직 기록 없음';
 const latest=history.entries[0],path=latest.regionNames.length?latest.regionNames.join(' → '):'공통 시작',count=latest.finalDeck.cards.length;
 return`<b class="${currentStored?'cyan':'gold'}">완료 아카이브 · 누적 ${history.entries.length}회</b>${currentStored?' · 이번 런 보관 완료':''}<br>최근 기록 · ${latest.starterName} · ${path} → 널워드 · ${latest.battleWins}승 · 네임드 ${latest.namedCount}/${count} · 교체 ${latest.deckRevision}회`
}
function roguelikeRunCompletionText(draft){"""
    text = replace_once(text, anchor, history, 'run-history insertion anchor')

    old = "<br>완료 기록과 최종 덱을 저장했습니다. 최종 덱으로 실험전을 하거나 스타터를 선택해 새 런을 시작할 수 있습니다."
    new = "<br>${roguelikeRunArchiveText(draft)}<br>완료 상태와 최종 덱을 저장했습니다. 최종 덱으로 실험전을 하거나 스타터를 선택해 새 런을 시작할 수 있습니다."
    text = replace_once(text, old, new, 'completion archive summary')

    old = "const draft=loadRoguelikeRunDraft(),route=typeof roguelikeBattleProgress==='function'?"
    new = "const draft=loadRoguelikeRunDraft();if(draft?.status==='completed')roguelikeArchiveCompletedRun(draft);const route=typeof roguelikeBattleProgress==='function'?"
    text = replace_once(text, old, new, 'picker archive hook')

    old = "if(typeof renderRoguelikeRegionPicker==='function')renderRoguelikeRegionPicker(draft);if(status)status.innerHTML=roguelikeRunDraftText(draft);if(prepare)"
    new = "if(typeof renderRoguelikeRegionPicker==='function')renderRoguelikeRegionPicker(draft);if(status){status.innerHTML=roguelikeRunDraftText(draft);const archive=loadRoguelikeRunHistory();if(archive.entries.length&&draft?.status!=='completed')status.innerHTML+=`<br>${roguelikeRunArchiveText()}`;}if(prepare)"
    text = replace_once(text, old, new, 'active-run archive summary')

    index.write_text(text, encoding='utf-8')


test = Path('tests/m11a-run-completion.mjs')
t = test.read_text(encoding='utf-8')
if "completion saves run state and one archive record" not in t:
    t = replace_once(
        t,
        "assert.equal(writeCount,beforeCompletionWrites+1,'completion and its last reward use exactly one successful write');",
        "assert.equal(writeCount,beforeCompletionWrites+2,'completion saves run state and one archive record');",
        'completion write-count assertion'
    )
    marker = "assert.equal(completed.status,'completed');assert.equal(completed.version,8);assert.equal(completed.runId,created.runId);"
    insert = marker + "\n const archive=JSON.parse(storage.get('rummyDuelRoguelikeRunHistoryV1'));const archived=archive.entries.find(x=>x.runId===completed.runId);\n assert.ok(archived,'completed run is archived');assert.equal(archived.finalDeckSignature,ctx.roguelikeRunDeckSignature(completed.runDeck));assert.equal(archived.rewards.filter(x=>x.source==='battle').length,14);assert.deepEqual(archived.regionPath,completed.regionPath);\n const archiveWrites=writeCount;render();assert.equal(writeCount,archiveWrites,'rerender does not duplicate an archived run');"
    t = replace_once(t, marker, insert, 'archive assertions')
    test.write_text(t, encoding='utf-8')


road = Path('ROADMAP.md')
r = road.read_text(encoding='utf-8')
archive_bullet = "- [x] 완료 런 아카이브 v1 — 최종 보상 처리로 `completed`가 된 런을 별도 `rummyDuelRoguelikeRunHistoryV1` 저장소에 runId 기준 1회 보관. 방문 경로·14전투 승리·수령/건너뛰기 이력·최종 30장 청사진/지문·교체 횟수를 최대 24개까지 보존하고, 진행 화면에서 누적 완료 수와 최근 기록을 표시한다. 일반 대전 클리어/레벨/해금 및 M12 표본 저장은 변경하지 않으며 아카이브 저장 실패가 런 완료 자체를 되돌리지 않는다."
if archive_bullet not in r:
    needle = "- [ ] 상점·이벤트 결제/조건 연결"
    r = replace_once(r, needle, archive_bullet + "\n" + needle, 'roadmap archive bullet')
    r = r.replace("일반 클리어/해금과 완료 아카이브·메타 보상은 별개이며 14연전의 난도/승률은 미확정.", "일반 클리어/해금과 메타 보상은 별개이며, 완료 아카이브는 아래 v1 저장으로 분리했다. 14연전의 난도/승률은 미확정.", 1)
    road.write_text(r, encoding='utf-8')


doc = Path('docs/ROGUELIKE_MASTER_PLAN.md')
d = doc.read_text(encoding='utf-8')
if "## 26. 완료 런 아카이브 v1" not in d:
    d += r"""

## 26. 완료 런 아카이브 v1

2026-09-02 구현. 25절의 최종 보상 처리로 런이 `completed`가 된 뒤, 현재 런 저장과 별개인 `rummyDuelRoguelikeRunHistoryV1`에 완료 기록을 보관한다. 새 런을 시작해 현재 draft가 교체되어도 이전 클리어 요약과 최종 덱은 남는다.

- 아카이브는 `runId` 기준 멱등 저장이다. 완료 화면이 다시 렌더되어도 같은 런을 중복 추가하거나 저장 횟수를 늘리지 않는다. 최신 기록이 앞에 오며 최대 24개를 보존한다.
- 한 기록에는 완료 시각, 스타터 ID/표시명, 두 분기 지역 ID/표시명, 실전 승리 수, 보상 수령/건너뛰기 수, 최종 덱 revision, 네임드 수, 최종 30장 `runDeck` 청사진과 덱 지문, 각 보상 sequence/source/status/선택 카드/전투 노드를 저장한다. 따라서 이후 통계·리플레이/최종 덱 재사용 기능의 입력으로 확장할 수 있다.
- 저장값을 읽을 때 날짜·중복 runId·보상 sequence/status·전투 영수증 수·최종 덱 정규화·덱 지문을 다시 검사한다. 손상된 아카이브는 현재 런 진행을 깨뜨리지 않고 빈 기록처럼 취급한다.
- 런 완료 저장과 아카이브 저장은 서로 다른 키다. 마지막 보상과 `completed` 상태 저장이 먼저 성공한 뒤 UI에서 아카이브를 보장하며, 아카이브 쪽 저장 실패가 이미 확정된 런 완료를 롤백하지 않는다. 다음 완료 화면 렌더에서 다시 보관을 시도한다.
- 완료 화면은 누적 완료 횟수와 최근 스타터/경로/승리/최종 네임드 수/교체 횟수를 표시한다. 새 런 진행 중에도 기존 완료 기록이 있으면 같은 요약을 진행 화면 아래에 표시한다.
- 일반 대전의 `totalClears`, 캐릭터 레벨/해금, 덱빌더 진행도 및 별도 M12 표본 저장은 건드리지 않는다. 메타 보상은 계속 미확정이다.
- 검증은 `tests/m11a-run-completion.mjs`의 12개 지역 순서 전체 완료 루프에 아카이브 저장·최종 덱/14전투 영수증·경로 일치·재렌더 중복 방지를 추가해 수행한다.
"""
    doc.write_text(d, encoding='utf-8')
