from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing {label}')
    s=s.replace(old,new,1)

# Keep the previous DETONATE result alive through the owner's next action window.
once("lastDamageTaken:0,lastDetonateTaken:0,charId,", "lastDamageTaken:0,lastDetonateTaken:0,detonateMemory:0,charId,", 'side detonate memory')
once("s.lastDamageTaken=0;s.lastDetonateTaken=0;s.actedThisTurn=false;", "s.lastDamageTaken=0;s.lastDetonateTaken=0;s.detonateMemory=0;s.actedThisTurn=false;", 'tutorial detonate memory reset')
once("case'revenge3':if(side.lastDetonateTaken>0&&!c.revengeUsed){", "case'revenge3':if(side.detonateMemory>0&&!c.revengeUsed){", 'Revenge Blade detonate window')
once("case'heal2':if(side.lastDetonateTaken>0)heal(w,3);", "case'heal2':if(side.detonateMemory>0)heal(w,3);", 'Phoenix detonate window')

old_turn_start="function turnStart(w){state.turnToken++;const s=sideObj(w);s.turnStarts=(s.turnStarts||0)+1;if(s.shield>0){log(`${w==='player'?'YOU':'CPU'} 남은 보호막 ${s.shield} 소멸.`);s.shield=0}s.actedThisTurn=false;s.newMeldUsed=false;s.recoveredThisTurn=false;s.maintenanceUsed=false;s.returnedSwitchThisTurn=false;s.discardsRemaining=1;s.healedThisTurn=0;s.flags={shift:false,large:false,salvage:false,joker:false,festival:0,roundabout:false,casinoCycle:false,tuner:false};const ri=state.discard.findLastIndex?state.discard.findLastIndex(c=>c.owner===w&&c.tag==='returnIfIgnored'):(()=>{for(let i=state.discard.length-1;i>=0;i--)if(state.discard[i].owner===w&&state.discard[i].tag==='returnIfIgnored')return i;return-1})();if(ri>=0){const [back]=state.discard.splice(ri,1);back.fromDiscard=false;s.hand.push(back);log(`${back.name}: 버림패에서 손패로 돌아왔습니다.`,'good')}if(s.lastDetonateTaken>0){const pi=s.spent.findIndex(c=>c.tag==='heal2'&&!c.phoenixReturned);if(pi>=0){const [ph]=s.spent.splice(pi,1);s.hand.push(ph);ph.phoenixReturned=true;ph.suppressEffectToken=null;heal(w,3);log(`${ph.name}: 폭발 뒤 소모패에서 1회 귀환.`,'good')}}if(officialStatusValue('player',s,'regen')>0){const r=officialStatusValue('player',s,'regen');heal(w,r);consumeOfficialStatus('player',s,'regen')}s.lastDetonateTaken=0}"
new_turn_start="function turnStart(w){state.turnToken++;const s=sideObj(w);s.turnStarts=(s.turnStarts||0)+1;s.detonateMemory=Math.max(0,s.lastDetonateTaken||0);s.lastDetonateTaken=0;if(s.shield>0){log(`${w==='player'?'YOU':'CPU'} 남은 보호막 ${s.shield} 소멸.`);s.shield=0}s.actedThisTurn=false;s.newMeldUsed=false;s.recoveredThisTurn=false;s.maintenanceUsed=false;s.returnedSwitchThisTurn=false;s.discardsRemaining=1;s.healedThisTurn=0;s.flags={shift:false,large:false,salvage:false,joker:false,festival:0,roundabout:false,casinoCycle:false,tuner:false};const ri=state.discard.findLastIndex?state.discard.findLastIndex(c=>c.owner===w&&c.tag==='returnIfIgnored'):(()=>{for(let i=state.discard.length-1;i>=0;i--)if(state.discard[i].owner===w&&c.tag==='returnIfIgnored')return i;return-1})();if(ri>=0){const [back]=state.discard.splice(ri,1);back.fromDiscard=false;s.hand.push(back);log(`${back.name}: 버림패에서 손패로 돌아왔습니다.`,'good')}if(s.detonateMemory>0){const pi=s.spent.findIndex(c=>c.tag==='heal2'&&!c.phoenixReturned);if(pi>=0){const [ph]=s.spent.splice(pi,1);s.hand.push(ph);ph.phoenixReturned=true;ph.suppressEffectToken=null;ph.age=0;log(`${ph.name}: 직전 폭발 뒤 소모패에서 1회 귀환 · 이번 턴 사용하면 회복.`,'good')}}if(officialStatusValue('player',s,'regen')>0){const r=officialStatusValue('player',s,'regen');heal(w,r);consumeOfficialStatus('player',s,'regen')}}"
# Avoid hand-editing the long start function if its exact body drifts: use the current exact version above.
once(old_turn_start,new_turn_start,'turnStart detonate response window')
once("function turnEnd(w){if(typeof recordCirculationTurn==='function')recordCirculationTurn(w);const s=sideObj(w);s.creditDebt=false;", "function turnEnd(w){if(typeof recordCirculationTurn==='function')recordCirculationTurn(w);const s=sideObj(w);s.detonateMemory=0;s.creditDebt=false;", 'turnEnd detonate memory expiry')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
anchor='- [x] Third timing pass: Recursive Function / Copier ignore unrelated named cards and only copy effects whose current action trigger conditions are actually satisfied\n'
line='- [x] Repair previous-DETONATE action window so Revenge Blade and Phoenix can trigger on the following owner turn; Phoenix spent return no longer grants its heal before use\n'
if line not in r:
    if anchor not in r: raise SystemExit('missing M8 timing roadmap anchor')
    r=r.replace(anchor,anchor+line,1)
road.write_text(r,encoding='utf-8')

t=Path('tests/named-detonate-window.mjs')
t.write_text(r'''import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const start=source('turnStart'),end=source('turnEnd'),fx=source('resolveEffects');
ok(start.includes('s.detonateMemory=Math.max(0,s.lastDetonateTaken||0);s.lastDetonateTaken=0;'),'turn start transfers the previous DETONATE result into the current action window before clearing the pending value');
ok(start.includes('if(s.detonateMemory>0){const pi=s.spent.findIndex')&&start.includes('ph.phoenixReturned=true')&&!start.includes('ph.suppressEffectToken=null;heal(w,3)'),'Phoenix may return from spent after DETONATE without receiving its use-triggered heal for free');
ok(fx.includes("case'revenge3':if(side.detonateMemory>0&&!c.revengeUsed)"),'Revenge Blade checks the preserved previous-DETONATE window');
ok(fx.includes("case'heal2':if(side.detonateMemory>0)heal(w,3)"),'Phoenix heals only when actually used during the preserved previous-DETONATE window');
ok(end.includes('s.detonateMemory=0;'),'the previous-DETONATE action window expires when that owner turn ends');
ok(html.includes('lastDetonateTaken:0,detonateMemory:0,charId'),'new battle side state initializes the timing memory');
console.log('M8 previous-DETONATE timing regression passed.');
''',encoding='utf-8')
