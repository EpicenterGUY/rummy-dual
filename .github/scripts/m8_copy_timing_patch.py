from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing {label}')
    s=s.replace(old,new,1)

# Clarify that copy cards mirror an effect that is actually eligible in the same action.
once("'CA':{n:'재귀 함수',t:'repeatNumeric',d:'같은 행동의 다른 네임드가 연결자면 1장 뽑기, 응급 보호구면 보호막 12, 갈아끼우기면 무료 회수 1회를 반복한다. 누적 위력은 복사하지 않는다.'}",
     "'CA':{n:'재귀 함수',t:'repeatNumeric',d:'같은 행동의 다른 네임드 중 실제 발동 조건을 만족한 효과 하나를 복제한다. 연결자면 1장 뽑기, 응급 보호구면 보호막 12, 갈아끼우기면 무료 회수 1회. 누적 위력은 복사하지 않는다.'}",
     'Recursive Function text')
once("'C8':{n:'복사기',t:'copier',d:'같은 행동의 다른 네임드가 응급 보호구면 보호막 20, 연결자면 1장 뽑기를 복사한다.'}",
     "'C8':{n:'복사기',t:'copier',d:'같은 행동의 다른 네임드 중 실제 발동 조건을 만족한 효과 하나를 복제한다. 응급 보호구면 보호막 20, 연결자면 1장 뽑기.'}",
     'Copier text')

marker='function resolveEffects(w,cards,type,ctx={})'
helper="function firstCopyEffectSource(cards,self,tags){const allow=new Set(tags||[]);return cards.find(x=>x.uid!==self.uid&&x.named&&allow.has(x.tag))||null}\n"
if 'function firstCopyEffectSource(' not in s:
    if marker not in s: raise SystemExit('missing resolveEffects marker')
    s=s.replace(marker,helper+marker,1)

old_repeat="case'repeatNumeric':{const prior=cards.find(x=>x.uid!==c.uid&&x.named);if(prior&&prior.tag==='run4Draw')drawOne(w,false);else if(prior&&prior.tag==='emergencyGear')addShield(w,3);else if(prior&&prior.tag==='freeSwapRecover')freeRecoverFromMeld(w,ctx.meld,cards,{allowReturnReuse:true});break}"
new_repeat="case'repeatNumeric':{const eligible=['emergencyGear'];if(type==='RUN'&&ctx.totalLength>=4)eligible.push('run4Draw');if(ctx.isAttach&&ctx.targetOwner===w)eligible.push('freeSwapRecover');const prior=firstCopyEffectSource(cards,c,eligible);if(prior?.tag==='run4Draw')drawOne(w,false);else if(prior?.tag==='emergencyGear')addShield(w,3);else if(prior?.tag==='freeSwapRecover')freeRecoverFromMeld(w,ctx.meld,cards,{allowReturnReuse:true});break}"
once(old_repeat,new_repeat,'Recursive Function implementation')

old_copier="case'copier':{const prior=cards.find(x=>x.uid!==c.uid&&x.named);if(prior&&prior.tag==='emergencyGear')addShield(w,5);else if(prior&&prior.tag==='run4Draw')drawOne(w,false);break}"
new_copier="case'copier':{const eligible=['emergencyGear'];if(type==='RUN'&&ctx.totalLength>=4)eligible.push('run4Draw');const prior=firstCopyEffectSource(cards,c,eligible);if(prior?.tag==='emergencyGear')addShield(w,5);else if(prior?.tag==='run4Draw')drawOne(w,false);break}"
once(old_copier,new_copier,'Copier implementation')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
anchor='- [x] Second correctness pass: activate Death Sentence discard targeting, Tuner cross-meld recovery, role-sensitive Understudy retirement, and executable Doppelganger SET support coverage\n'
line='- [x] Third timing pass: Recursive Function / Copier ignore unrelated named cards and only copy effects whose current action trigger conditions are actually satisfied\n'
if line not in r:
    if anchor not in r: raise SystemExit('missing M8 roadmap anchor')
    r=r.replace(anchor,anchor+line,1)
road.write_text(r,encoding='utf-8')

t=Path('tests/named-copy-timing.mjs')
t.write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const ctx=vm.createContext({Set});vm.runInContext(source('firstCopyEffectSource'),ctx);
const self={uid:'copy',named:true,tag:'copier'},noise={uid:'noise',named:true,tag:'marketMaker'},connector={uid:'link',named:true,tag:'run4Draw'},gear={uid:'gear',named:true,tag:'emergencyGear'};
ok(ctx.firstCopyEffectSource([self,noise,connector],self,['run4Draw','emergencyGear'])===connector,'copy cards skip unrelated named cards instead of fizzling on the first named card');
ok(ctx.firstCopyEffectSource([self,connector,gear],self,['emergencyGear'])===gear,'an ineligible Connector is skipped and a later eligible Emergency Gear can be copied');
const fx=source('resolveEffects');
ok(fx.includes("case'repeatNumeric':{const eligible=['emergencyGear'];if(type==='RUN'&&ctx.totalLength>=4)eligible.push('run4Draw');if(ctx.isAttach&&ctx.targetOwner===w)eligible.push('freeSwapRecover')"),'Recursive Function gates Connector and Free Swap copies by the original effect trigger conditions');
ok(fx.includes("case'copier':{const eligible=['emergencyGear'];if(type==='RUN'&&ctx.totalLength>=4)eligible.push('run4Draw')"),'Copier only offers Connector as a copy source when Connector would actually trigger');
ok(html.includes('실제 발동 조건을 만족한 효과 하나를 복제한다'),'copy-card text explains the timing rule');
console.log('M8 copy/timing regression passed.');
''',encoding='utf-8')
