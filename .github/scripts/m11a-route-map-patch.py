from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'missing {label}')
    return text.replace(old, new, 1)


index = Path('index.html')
text = index.read_text(encoding='utf-8')

if 'id="roguelikeRouteMap"' not in text:
    old = '<div id="roguelikeStarterGrid" class="charGrid"></div><div id="roguelikeRegionPicker"></div>'
    new = '<div id="roguelikeStarterGrid" class="charGrid"></div><div id="roguelikeRouteMap" class="roguelikeRouteMap" aria-label="로그라이크 런 경로"></div><div id="roguelikeRegionPicker"></div>'
    text = replace_once(text, old, new, 'route-map mount')

if '.roguelikeRouteMap{' not in text:
    css = r'''
.roguelikeRouteMap{margin:8px 0;padding:8px;border:2px solid #000;background:#0d1420;box-shadow:0 0 0 2px #34445e inset}.roguelikeMapHead{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:7px;font-size:8px;color:var(--soft)}.roguelikeMapHead b{font-size:9px;color:var(--text)}.roguelikeMapTrack{display:flex;gap:5px;overflow-x:auto;padding:2px 2px 6px;scrollbar-width:none;scroll-snap-type:x proximity}.roguelikeMapTrack::-webkit-scrollbar{display:none}.roguelikeMapNode,.roguelikeMapGate{flex:0 0 78px;min-height:63px;padding:6px;border:2px solid #000;background:#151c29;box-shadow:0 0 0 1px #3b475d inset;scroll-snap-align:center}.roguelikeMapNode.done{background:#16251e;box-shadow:0 0 0 1px #4d765e inset}.roguelikeMapNode.pending{background:#2b2515;box-shadow:0 0 0 2px var(--gold) inset}.roguelikeMapNode.current{background:#13272b;box-shadow:0 0 0 2px var(--cyan) inset}.roguelikeMapNode.locked{opacity:.45;filter:grayscale(.35)}.roguelikeMapNode.boss{border-bottom-color:var(--gold)}.roguelikeMapNode.final-boss{border-bottom-color:var(--red)}.roguelikeMapIndex{font-size:6px;color:var(--soft);line-height:1.25}.roguelikeMapName{margin-top:4px;font-size:8px;font-weight:900;line-height:1.3}.roguelikeMapState{margin-top:5px;font-size:6px;line-height:1.3}.roguelikeMapNode.done .roguelikeMapState{color:var(--green)}.roguelikeMapNode.pending .roguelikeMapState{color:var(--gold)}.roguelikeMapNode.current .roguelikeMapState{color:var(--cyan)}.roguelikeMapGate{border-style:dashed;background:#111824}.roguelikeMapGate.ready{box-shadow:0 0 0 2px var(--violet) inset}.roguelikeMapGate .roguelikeMapState{color:var(--soft)}.roguelikeMapGate.ready .roguelikeMapState{color:var(--violet)}.roguelikeMapLegend{margin-top:3px;font-size:7px;color:#7f8ca5;line-height:1.45}
'''
    text = replace_once(text, '</style>', css + '</style>', 'style terminator')

if 'function roguelikeRouteMapState(' not in text:
    anchor = 'function renderRoguelikeRegionPicker(draft){'
    js = r'''function roguelikeRouteMapState(index,progress,draft){
 const completed=Math.max(0,Number(progress?.completed)||0),pending=progress?.pending?.source==='battle';
 if(draft?.status==='completed')return'done';
 if(pending&&index===completed-1)return'pending';
 if(index<completed-(pending?1:0))return'done';
 if(!pending&&progress?.current&&index===completed)return'current';
 return'locked'
}
function roguelikeRouteMapGate(draft,progress){
 const path=Array.isArray(draft?.regionPath)?draft.regionPath:[];
 if(!draft||draft.status==='completed'||path.length>=ROGUELIKE_ROUTE_LIMITS.regionVisits)return null;
 const visit=path.length+1,ready=!!progress?.awaitingRegion;
 return{visit,ready,label:`지역 ${visit} 선택`,detail:ready?'선택 가능':visit===1?'공통 시작 3전투 보상 완료 후':'첫 지역 중간 보스 보상 완료 후'}
}
function roguelikeRouteMapZoneName(zone){
 if(!zone||zone===ROGUELIKE_COMMON_START_ZONE)return'공통 시작';
 if(zone===ROGUELIKE_ENDGAME.id)return ROGUELIKE_ENDGAME.name;
 return ROGUELIKE_REGIONS.find(r=>r.id===zone)?.name||zone
}
function roguelikeRouteMapPrototypeTotal(){
 const first=ROGUELIKE_REGIONS[0],perRegion=first?roguelikeRegionRoute([first.id]).length:0;
 return ROGUELIKE_COMMON_START_ROUTE.length+perRegion*ROGUELIKE_ROUTE_LIMITS.regionVisits+ROGUELIKE_ENDGAME.nodes.length
}
function renderRoguelikeRouteMap(draft=loadRoguelikeRunDraft()){
 const host=document.getElementById('roguelikeRouteMap');if(!host)return;
 if(!draft){host.innerHTML='<div class="roguelikeMapHead"><b>RUN MAP</b><span>런 덱 없음</span></div><div class="roguelikeMapLegend">런 덱을 만들면 공통 시작부터 현재 경로를 표시합니다. 지역은 실제로 선택한 뒤에만 지도에 확정됩니다.</div>';return}
 const progress=roguelikeBattleProgress(draft),route=roguelikeRunRoute(draft.regionPath||[]),prototypeTotal=roguelikeRouteMapPrototypeTotal(),gate=roguelikeRouteMapGate(draft,progress),stateText={done:'보상 처리 완료',pending:'승리 · 보상 대기',current:'다음 전투',locked:'잠김'};
 const nodes=route.map((node,index)=>{const state=roguelikeRouteMapState(index,progress,draft),zone=roguelikeRouteMapZoneName(node.zone),name=String(node.label||node.id).replace(`${zone} · `,''),kind=node.kind==='final-boss'?'final-boss':node.kind==='boss'?'boss':'';return`<div class="roguelikeMapNode ${state} ${kind}" data-run-map-node="${node.id}" data-run-map-state="${state}"><div class="roguelikeMapIndex">${index+1} · ${zone}</div><div class="roguelikeMapName">${name}</div><div class="roguelikeMapState">${stateText[state]}</div></div>`}).join('');
 const gateHtml=gate?`<div class="roguelikeMapGate ${gate.ready?'ready':''}" data-run-map-gate="${gate.visit}"><div class="roguelikeMapIndex">분기 관문</div><div class="roguelikeMapName">${gate.label}</div><div class="roguelikeMapState">${gate.detail}</div></div>`:'';
 const status=draft.status==='completed'?'RUN COMPLETE':progress.pending?.source==='battle'?'REWARD WAIT':progress.awaitingRegion?'ROUTE CHOICE':'IN PROGRESS';
 host.innerHTML=`<div class="roguelikeMapHead"><b>RUN MAP · ${status}</b><span>승리 ${progress.completed}/${prototypeTotal}</span></div><div class="roguelikeMapTrack">${nodes}${gateHtml}</div><div class="roguelikeMapLegend">초록 완료 · 금색 보상 대기 · 청록 다음 전투 · 점선 지역 선택 · 잠긴 노드는 아직 진행할 수 없습니다.</div>`
}
'''
    text = replace_once(text, anchor, js + anchor, 'route-map functions')

if "typeof renderRoguelikeRouteMap==='function'" not in text:
    old = "if(typeof renderRoguelikeRegionPicker==='function')renderRoguelikeRegionPicker(draft);if(status)"
    new = "if(typeof renderRoguelikeRouteMap==='function')renderRoguelikeRouteMap(draft);if(typeof renderRoguelikeRegionPicker==='function')renderRoguelikeRegionPicker(draft);if(status)"
    text = replace_once(text, old, new, 'route-map render hook')

index.write_text(text, encoding='utf-8')


test = Path('tests/m11a-route-map.mjs')
if not test.exists():
    test.write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const src=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function fn(name,next){const start=src.indexOf(`function ${name}(`);if(start<0)throw new Error(`missing ${name}`);const end=src.indexOf(`function ${next}(`,start);if(end<0)throw new Error(`missing next ${next}`);return src.slice(start,end)}
ok(src.includes('id="roguelikeRouteMap"'),'route map mount exists in the run UI');
ok(src.includes('.roguelikeMapNode.pending')&&src.includes('.roguelikeMapNode.current')&&src.includes('.roguelikeMapGate.ready'),'route map has distinct pending/current/route-choice visuals');
ok(src.includes("if(typeof renderRoguelikeRouteMap==='function')renderRoguelikeRouteMap(draft)"),'starter picker renders the route map through a compatibility guard');
const stateSrc=fn('roguelikeRouteMapState','roguelikeRouteMapGate');
const ctx={};vm.createContext(ctx);vm.runInContext(`${stateSrc};this.state=roguelikeRouteMapState`,ctx);
const current={completed:0,pending:null,current:{id:'common-1'}};
assert.equal(ctx.state(0,current,{status:'prepared'}),'current');assert.equal(ctx.state(1,current,{status:'prepared'}),'locked');
const pending={completed:3,pending:{source:'battle'},current:{id:'region-1'}};
assert.equal(ctx.state(0,pending,{status:'prepared'}),'done');assert.equal(ctx.state(1,pending,{status:'prepared'}),'done');assert.equal(ctx.state(2,pending,{status:'prepared'}),'pending');assert.equal(ctx.state(3,pending,{status:'prepared'}),'locked');
const gateWait={completed:3,pending:null,current:null,awaitingRegion:true};
assert.equal(ctx.state(0,gateWait,{status:'prepared'}),'done');assert.equal(ctx.state(2,gateWait,{status:'prepared'}),'done');
assert.equal(ctx.state(13,{completed:14,pending:null,current:null},{status:'completed'}),'done');
ok(true,'route map state distinguishes completed, reward-pending, current, and locked nodes');
const gateSrc=fn('roguelikeRouteMapGate','roguelikeRouteMapZoneName');
const gateCtx={ROGUELIKE_ROUTE_LIMITS:{regionVisits:2}};vm.createContext(gateCtx);vm.runInContext(`${gateSrc};this.gate=roguelikeRouteMapGate`,gateCtx);
let gate=gateCtx.gate({status:'prepared',regionPath:[]},{awaitingRegion:false});assert.equal(gate.visit,1);assert.equal(gate.ready,false);assert.match(gate.detail,/공통 시작/);
gate=gateCtx.gate({status:'prepared',regionPath:['neon-arc']},{awaitingRegion:true});assert.equal(gate.visit,2);assert.equal(gate.ready,true);assert.equal(gate.detail,'선택 가능');
assert.equal(gateCtx.gate({status:'prepared',regionPath:['neon-arc','red-zone']},{awaitingRegion:false}),null);assert.equal(gateCtx.gate({status:'completed',regionPath:['neon-arc','red-zone']},{awaitingRegion:false}),null);
ok(true,'route-choice gate appears only before each unresolved region choice');
const renderSrc=fn('renderRoguelikeRouteMap','renderRoguelikeRegionPicker');
ok(renderSrc.includes('roguelikeBattleProgress(draft)')&&renderSrc.includes('roguelikeRunRoute(draft.regionPath||[])'),'route map reads the canonical progress and route helpers');
ok(renderSrc.includes("'승리 · 보상 대기'")&&renderSrc.includes("'다음 전투'")&&renderSrc.includes('RUN COMPLETE'),'route map exposes the required player-facing states');
ok(!renderSrc.includes('saveRoguelikeRunDraft')&&!renderSrc.includes('localStorage.setItem'),'route map is read-only and cannot mutate run progress');
console.log('M11A route map regression passed.');
''', encoding='utf-8')


road = Path('ROADMAP.md')
r = road.read_text(encoding='utf-8')
bullet = "  - [x] 런 경로 지도 v1 — 현재 저장된 전투 영수증과 기존 경로 계산만 읽어 공통 시작→선택 지역→널워드의 진행을 가로 지도에 표시. 완료/승리 후 보상 대기/다음 전투/잠금/지역 선택 관문을 분리하고, 아직 고르지 않은 지역은 미리 확정하지 않는다. 전투 수·보상·상점·이벤트·경제 규칙은 변경하지 않음"
if bullet not in r:
    anchor = "  - [x] 공통 시작 구역 3연전 실전 슬라이스"
    pos = r.find(anchor)
    if pos < 0:
        raise SystemExit('missing roadmap map parent child anchor')
    line_end = r.find('\n', pos)
    r = r[:line_end+1] + bullet + '\n' + r[line_end+1:]
    road.write_text(r, encoding='utf-8')


doc = Path('docs/ROGUELIKE_MASTER_PLAN.md')
d = doc.read_text(encoding='utf-8')
if '## 27. 런 경로 지도 v1' not in d:
    d += r'''

## 27. 런 경로 지도 v1

2026-09-02 구현. 이미 플레이 가능한 14전투 프로토타입을 새로운 규칙 없이 읽기 쉽게 보여 주는 진행 지도다. 지도는 `roguelikeBattleProgress()`와 `roguelikeRunRoute()`의 결과만 사용하며 런 저장을 직접 수정하지 않는다.

- 공통 시작, 실제로 선택한 1·2지역, 널워드 노드를 방문 순서대로 가로 스크롤 카드로 표시한다. 아직 고르지 않은 지역은 지도에 임의로 확정하지 않고 `지역 1/2 선택` 관문 하나만 표시하며 기존 지역 선택 UI가 실제 선택을 담당한다.
- 전투 상태는 `보상 처리 완료 / 승리·보상 대기 / 다음 전투 / 잠김` 네 단계로 분리한다. 전투 승리 영수증이 생겼지만 해당 카드 보상이 pending이면 그 노드는 완료색으로 넘기지 않고 별도 보상 대기 상태를 유지한다.
- 완료 런은 확정된 14개 전투를 모두 완료로 표시하고 헤더를 `RUN COMPLETE`로 전환한다. 진행 중에는 누적 승리 수와 현재 프로토타입 전체 전투 수를 함께 보여 준다.
- 지도는 읽기 전용이다. 전투 시작, 보상 수령/건너뛰기, 지역 선택, 덱 교체, 저장 함수는 지도 자체에서 호출하지 않는다. 따라서 기존 전투/보상/지역/완료 계약과 일반 진행도·M12 표본은 바뀌지 않는다.
- 상점·이벤트·엘리트 노드 위치나 비율은 아직 확정하지 않는다. 후속 맵 확장에서 실제 노드 종류가 추가되면 같은 상태 표현을 확장하되, 이번 v1을 경제/런 길이 확정 근거로 사용하지 않는다.
- `tests/m11a-route-map.mjs`는 현재·잠금, 승리 후 보상 대기, 지역 선택 관문 2회, 완료 상태와 읽기 전용 조건을 회귀로 고정한다.
'''
    doc.write_text(d, encoding='utf-8')
