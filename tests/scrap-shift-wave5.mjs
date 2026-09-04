import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const poolDoc=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

new Function(script);
const wave5=[
 ['SSD9','D9','교환 규격','ssExchangeSpec'],
 ['SSC10','C10','모듈 버스','ssModuleBus'],
 ['SSH10','H10','리퍼비시','ssRefurbish'],
 ['SSS3','S3','볼트 커터','ssBoltCutter']
];
const resolver=source('resolveEffects');
for(const [id,slot,name,tag] of wave5){
 ok(script.includes(`'${id}':{slot:'${slot}',themeId:'scrap-shift',n:'${name}',t:'${tag}'`),`${name} is defined in SCRAP-SHIFT wave5`);
 ok(resolver.includes(`case'${tag}'`),`${tag} is registered on the named resolver surface`);
}
ok(script.includes("themeId:'scrap-shift',live:false"),'wave5 remains DEV-only and does not release SCRAP-SHIFT early');

// 9♦ Exchange Spec: only part maintenance opens one additional draw-bottom circulation.
{
 const sourceCard={uid:1,name:'교환 규격',tag:'ssExchangeSpec'};
 let cycles=0;
 const ctx=context({
  scrapShiftPublicCards:(w,tag)=>tag==='ssExchangeSpec'?[sourceCard]:[],
  scrapShiftPassiveDrawBottom:()=>{cycles++;return true},
  log:()=>{}
 });
 install(ctx,'triggerScrapShiftExchangeSpec');
 ok(ctx.triggerScrapShiftExchangeSpec('player',false)===false&&cycles===0,'Exchange Spec ignores maintenance with no part card');
 ok(ctx.triggerScrapShiftExchangeSpec('player',true)===true&&cycles===1,'Exchange Spec adds exactly one post-maintenance circulation when a part was bottomed');
 const maintenance=source('performMaintenance');
 ok(maintenance.includes('const hadScrapPart=')&&maintenance.indexOf('const hadScrapPart=')<maintenance.indexOf("clearScrapShiftPart(c,'정비·개인 덱'"),'maintenance snapshots part state before deck entry clears the marker');
 ok(maintenance.indexOf("for(let i=0;i<valid.length;i++){const x=drawOne")<maintenance.indexOf("triggerScrapShiftExchangeSpec(w,true)"),'Exchange Spec resolves only after normal maintenance replacement draws');
}

// 10♣ Module Bus: recovery and transplant from the same surviving part RUN grant shield 10 once per turn.
{
 const bus={uid:10,owner:'player',themeId:'scrap-shift',tag:'ssModuleBus',name:'모듈 버스',themeTurnGates:{}};
 const part={uid:11,owner:'player',scrapShiftPart:true};
 const recovered={uid:12,owner:'player',scrapShiftPart:false};
 const run={type:'RUN',cards:[bus,part,{uid:13,owner:'player'},{uid:14,owner:'player'}]};
 const gates=new Set();let shield=0;
 const key=(c,k,t)=>`${c.uid}:${k}:${t}`;
 const state={turnToken:30};
 const ctx=context({
  state,
  sideObj:()=>({}),other:w=>w==='player'?'enemy':'player',
  isScrapShiftPart:(c,o)=>!!c?.scrapShiftPart&&(!o||c.owner===o),
  scrapShiftMeldHasOwnedPart:(w,m)=>(m.cards||[]).some(c=>!!c.scrapShiftPart&&c.owner===w),
  themeTurnGateUsed:(c,k,t)=>gates.has(key(c,k,t)),
  claimThemeTurnGate:(c,k,t)=>{const x=key(c,k,t);if(gates.has(x))return false;gates.add(x);return true},
  scrapShiftPublicCards:()=>[],scrapShiftPassiveCycle:()=>false,scrapShiftPassiveDrawBottom:()=>false,
  addShield:(w,n)=>{shield+=n},heal:()=>{},scrapShiftSealTarget:()=>null,log:()=>{}
 });
 install(ctx,'scrapShiftModuleBusSource','applyScrapShiftModuleBus','handleScrapShiftThemeEvent');
 ok(ctx.handleScrapShiftThemeEvent({event:'onRecover',actor:'player',card:recovered,meld:run,turnToken:30})===true,'Module Bus reacts when an own card leaves a surviving part RUN by recovery');
 ok(shield===2.5,'Module Bus uses exact shield 10 through the shared recovery unit scale');
 ok(ctx.handleScrapShiftThemeEvent({event:'onRecover',actor:'player',card:recovered,meld:run,turnToken:30})===false&&shield===2.5,'Module Bus is capped to once per turn');
 state.turnToken=31;
 ok(ctx.handleScrapShiftThemeEvent({event:'onMeldMove',actor:'player',card:part,sourceMeld:run,targetMeld:{type:'SET',cards:[]},reason:'scrapShiftTransplant',turnToken:31})===true,'Module Bus also reacts to a real part transplant out of its RUN');
 ok(shield===5,'Module Bus transplant reaction grants one more shield 10 on the new turn');
}

// 10♥ Refurbish: player RUMMY pauses for an optional spent-part choice before turn finish.
{
 const sourceCard={uid:20,owner:'player',themeId:'scrap-shift',tag:'ssRefurbish',name:'리퍼비시',themeTurnGates:{}};
 const p1={uid:21,owner:'player',scrapShiftPart:true,name:'부품1'},p2={uid:22,owner:'player',scrapShiftPart:true,name:'부품2'};
 const gates=new Set();let choice=null,reassembled=null,resumed=0;
 const state={turn:'player',turnToken:40};
 const key=(c,k,t)=>`${c.uid}:${k}:${t}`;
 const ctx=context({
  state,
  scrapShiftPublicCards:(w,tag)=>tag==='ssRefurbish'?[sourceCard]:[],
  scrapShiftReassembleCandidates:()=>[p1,p2],
  themeTurnGateUsed:(c,k,t)=>gates.has(key(c,k,t)),
  claimThemeTurnGate:(c,k,t)=>{const x=key(c,k,t);if(gates.has(x))return false;gates.add(x);return true},
  requestEffectChoice:spec=>{choice=spec;return true},
  reassembleScrapShiftPart:(w,c)=>{reassembled=c;return{card:c}},
  cardText:c=>c.name
 });
 install(ctx,'requestScrapShiftRummyRefurbish');
 ok(ctx.requestScrapShiftRummyRefurbish('player',()=>{resumed++})===true,'Refurbish opens a real optional choice during player RUMMY');
 ok(choice?.allowSkip===true&&choice.options.length===2&&reassembled===null,'Refurbish exposes all current spent parts and allows skipping');
 choice.onChoose(choice.options[1]);
 ok(reassembled===p2&&resumed===1,'Refurbish reassembles the chosen part before RUMMY flow resumes');
 const rummy=source('triggerRummy');
 ok(rummy.includes("requestScrapShiftRummyRefurbish(w,finishAfterRefurbish)")&&rummy.includes("if(paused)return'choice'"),'RUMMY completion explicitly pauses for Refurbish instead of ending the turn under the choice overlay');
}

// 3♠ Bolt Cutter: hostile movement/spend consumes its granted protect through the existing interference gate.
{
 const cutter={uid:30,owner:'player',themeId:'scrap-shift',tag:'ssBoltCutter',name:'볼트 커터',themeTurnGates:{}};
 const part={uid:31,owner:'player',scrapShiftPart:true,protect:0};
 const meld={type:'RUN',cards:[part,{uid:32},{uid:33},{uid:34}]};
 const state={turnToken:50};
 const gates=new Set();const key=(c,k,t)=>`${c.uid}:${k}:${t}`;
 const side={spent:[]};
 const ctx=context({
  state,
  isScrapShiftPart:(c,o)=>!!c?.scrapShiftPart&&(!o||c.owner===o),
  scrapShiftPublicCards:(w,tag)=>tag==='ssBoltCutter'?[cutter]:[],
  themeTurnGateUsed:(c,k,t)=>gates.has(key(c,k,t)),
  claimThemeTurnGate:(c,k,t)=>{const x=key(c,k,t);if(gates.has(x))return false;gates.add(x);return true},
  officialStatusValue:(scope,c,k)=>scope==='card'&&k==='protect'?(c.protect||0):0,
  applyOfficialStatus:(scope,c,k,n)=>{if(scope==='card'&&k==='protect')c.protect=(c.protect||0)+n;return c.protect},
  consumeOfficialStatus:(scope,c,k)=>{if(scope==='card'&&k==='protect'&&(c.protect||0)>0){c.protect--;return true}return false},
  sideObj:()=>side,meldType:()=> 'RUN',noteScrapShiftPartSpent:()=>{},cardText:()=> '부품',log:()=>{}
 });
 install(ctx,'scrapShiftBoltCutterProtect','insuranceBlocks');
 ok(ctx.insuranceBlocks('enemy','player',meld,part)===true&&part.protect===0,'Bolt Cutter grants protect and the shared interference gate consumes it to block the hostile effect');
 ok(ctx.insuranceBlocks('enemy','player',meld,part)===false,'Bolt Cutter cannot block a second hostile effect in the same turn');
 const fresh={uid:35,owner:'player',scrapShiftPart:true,protect:1};
 const freshCutter={...cutter,uid:36,themeTurnGates:{}};
 gates.clear();ctx.scrapShiftPublicCards=(w,tag)=>tag==='ssBoltCutter'?[freshCutter]:[];
 ok(ctx.insuranceBlocks('enemy','player',{type:'RUN',cards:[fresh,{uid:37},{uid:38},{uid:39}]},fresh)===true,'existing card protect blocks first without needing a new Bolt Cutter layer');
 ok(!gates.has(key(freshCutter,'ssBoltCutter',50)),'Bolt Cutter preserves its once-per-turn gate when the target was already protected');
}

const wave5Sources=['triggerScrapShiftExchangeSpec','applyScrapShiftModuleBus','requestScrapShiftRummyRefurbish','scrapShiftBoltCutterProtect'].map(source).join('\n');
ok(!wave5Sources.includes('grantExtraAttach')&&!wave5Sources.includes('extraAttachRemaining'),'wave5 does not bypass the simplified one-base-attach contract');

ok(road.includes('5차 교차행동 슬라이스 4장 — 9♦ 교환 규격 / 10♣ 모듈 버스 / 10♥ 리퍼비시 / 3♠ 볼트 커터'),'ROADMAP records SCRAP-SHIFT wave5');
ok(themeDoc.includes('5차 교차행동 슬라이스 — 9♦ `교환 규격` / 10♣ `모듈 버스` / 10♥ `리퍼비시` / 3♠ `볼트 커터`'),'canonical theme doc records wave5');
ok(poolDoc.includes('24장 미라이브 · 20장 DEV 구현 완료(행동 4 + 반응 4 + 유틸리티 4 + 수명주기 4 + 교차행동 4)'),'full-pool policy records twenty DEV cards while keeping SCRAP-SHIFT non-live');
ok(road.includes('- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현'),'final 24-card implementation remains open after wave5');

console.log('SCRAP-SHIFT wave5 cross-action regression passed.');
