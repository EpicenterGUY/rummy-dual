import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync('index.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync('ROADMAP.md','utf8');
const themeDoc=fs.readFileSync('docs/THEME_GROUPS.md','utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

ok(script.includes("'ZSCA':{slot:'CA',themeId:'zero-sight',n:'관측수',t:'zsObserver'"),'Observer is a live ZERO-SIGHT A-club variant');
ok(script.includes("'ZSC2':{slot:'C2',themeId:'zero-sight',n:'스코프 조정',t:'zsScopeAdjust'"),'Scope Adjustment is a live ZERO-SIGHT 2-club variant');
ok(script.includes("'zero-sight':Object.freeze({id:'zero-sight',displayName:'ZERO-SIGHT',short:'정밀 표적'")&&script.includes("themeId:'zero-sight',live:true"),'ZERO-SIGHT build profile is promoted to live');
ok(script.includes("items:['S6','H7','D8','C2','ZSCA','ZSC2','DA','D3']"),'both starter variants unlock at one clear');
ok(source('themeBuildLockText').includes("id==='zero-sight'")&&source('themeBuildLockText').includes('전체 1클리어부터'),'theme selection communicates the one-clear unlock timing');
ok(script.includes("zsObserver:['control','cycle','combo']")&&script.includes("zsScopeAdjust:['control','cycle','interact']"),'ZERO-SIGHT starters use ordinary open-deck tendencies');

// ZERO-SIGHT build remains open/mixed while prioritizing its live variants.
{
  const NAMED={ZSCA:{slot:'CA',themeId:'zero-sight',t:'zsObserver'},ZSC2:{slot:'C2',themeId:'zero-sight',t:'zsScopeAdjust'},N1:{slot:'S5',t:'x'},N2:{slot:'H5',t:'x'},N3:{slot:'D5',t:'x'},N4:{slot:'C5',t:'x'},N5:{slot:'S7',t:'x'},N6:{slot:'H7',t:'x'},N7:{slot:'D7',t:'x'},N8:{slot:'C7',t:'x'},N9:{slot:'S9',t:'x'}};
  const CHARACTERS={wanderer:{weights:{}}},TENDENCY_BY_TAG={zsObserver:['cycle'],zsScopeAdjust:['cycle'],x:['mix']};
  const math=Object.create(Math);math.random=()=>0.2;
  const ctx=context({NAMED,CHARACTERS,TENDENCY_BY_TAG,Math:math});
  install(ctx,'weightedPick','namedSlot','weightedVariantSample','cardWeightForChar','chooseNamedForBuild');
  const picked=[...ctx.chooseNamedForBuild(Object.keys(NAMED),'wanderer','zero-sight')];
  ok(picked.length===9,'ZERO-SIGHT build keeps the normal nine named slots');
  ok(picked.includes('ZSCA')&&picked.includes('ZSC2'),'ZERO-SIGHT build prioritizes both live starter variants');
  ok(picked.some(id=>!NAMED[id].themeId),'ZERO-SIGHT remains an open mixed build rather than theme-only');
}

const cycleFns=['zeroSightCycleCandidates','cycleSpecificHandCard','requestZeroSightCycle'];
const relocationFns=['zeroSightRelocationTargets','requestZeroSightRelocation'];
for(const n of [...cycleFns,...relocationFns])ok(script.includes(`function ${n}(`),`shared ZERO-SIGHT helper exists: ${n}`);

// Fallback: no target -> exact card cycle, no fake target creation.
{
  const sent={uid:1,name:'old',age:3,fromDiscard:true,contractActive:true},keep={uid:2,name:'keep',age:1},draw={uid:3,name:'draw',age:0};
  const enemy={hand:[sent,keep],deck:[draw]},player={hand:[],deck:[]};
  const state={turn:'enemy',turnToken:7};let setCalls=0;
  const ctx=context({state,sideObj:w=>w==='enemy'?enemy:player,other:w=>w==='enemy'?'player':'enemy',meldsOf:()=>[],zeroSightTargetMeld:()=>null,setZeroSightTarget:()=>{setCalls++;return true},requestEffectChoice:()=>false,cardText:c=>c.name,log:()=>{},flashPile:()=>{},drawOne:w=>{const s=w==='enemy'?enemy:player;const c=s.deck.pop();if(c)s.hand.push(c);return c}});
  install(ctx,...cycleFns,...relocationFns);
  const paused=ctx.requestZeroSightRelocation('enemy',{name:'스코프 조정'},{cards:[]});
  ok(paused===false,'targetless Scope Adjustment resolves without opening CPU choice UI');
  ok(setCalls===0,'targetless fallback does not invent a target');
  ok(enemy.hand.some(c=>c.uid===draw.uid)&&enemy.deck.some(c=>c.uid===sent.uid),'targetless starter cycles the oldest hand card into one replacement draw');
  ok(sent.fromDiscard===false&&sent.contractActive===false&&sent.age===0,'fallback cycle normalizes the bottomed card');
}

// Existing target + destination -> relocate, do not cycle.
{
  const current={type:'SET',cards:[1,2,3]},dest={type:'RUN',cards:[1,2,3]},own={type:'SET',cards:[1,2,3]};
  const enemy={hand:[{uid:9,age:4}],deck:[{uid:10,age:0}]},player={hand:[],deck:[]};
  const state={turn:'enemy',turnToken:8};let target=null,cycles=0;
  const ctx=context({state,sideObj:w=>w==='enemy'?enemy:player,other:w=>w==='enemy'?'player':'enemy',meldsOf:s=>s==='player'?[dest]:[current,own],zeroSightTargetMeld:()=>current,setZeroSightTarget:(w,m)=>{target=m;return true},requestEffectChoice:()=>false,cardText:c=>String(c.uid),log:()=>{},flashPile:()=>{},drawOne:()=>{cycles++;return null}});
  install(ctx,...cycleFns,...relocationFns);
  ctx.requestZeroSightRelocation('enemy',{name:'스코프 조정'},{cards:[]});
  ok(target===dest,'Scope Adjustment relocates to a different public meld when one exists');
  ok(cycles===0,'successful target relocation does not also grant fallback cycling');
}

// Resolver wiring: Observer always opens a target from its used meld; Scope uses resumable relocation helper.
{
  const resolve=source('resolveEffects');
  const meld={type:'RUN',cards:[]};let targeted=null,cycled=0;
  const state={turnToken:4};
  const ctx=context({state,sideObj:()=>({hand:[1]}),other:()=> 'enemy',consumeOfficialStatus:()=>0,setZeroSightTarget:(w,m)=>{targeted=m;return true},requestZeroSightCycle:()=>{cycled++;return false},requestZeroSightRelocation:()=>false});
  vm.runInContext(`${resolve};globalThis.__r=resolveEffects`,ctx);
  const c={uid:1,named:true,tag:'zsObserver',name:'관측수'};
  const out=ctx.__r('player',[c],'RUN',{isNew:true,isAttach:false,meld,totalLength:3,effectSeen:new Set(),willReturn:false});
  ok(targeted===meld&&cycled===1&&!out.pending,'Observer marks the exact used meld as target then gives its free cycle');
}
{
  const resolve=source('resolveEffects');let reloc=0;
  const state={turnToken:5};
  const ctx=context({state,sideObj:()=>({hand:[1]}),other:()=> 'enemy',consumeOfficialStatus:()=>0,requestZeroSightRelocation:()=>{reloc++;return false}});
  vm.runInContext(`${resolve};globalThis.__r=resolveEffects`,ctx);
  const c={uid:2,named:true,tag:'zsScopeAdjust',name:'스코프 조정'};
  const out=ctx.__r('player',[c],'RUN',{isNew:true,isAttach:false,meld:{type:'RUN',cards:[]},totalLength:3,effectSeen:new Set(),willReturn:false});
  ok(reloc===1&&!out.pending,'Scope Adjustment routes through the shared resumable relocation/fallback helper');
}

ok(road.includes('- [x] 표적 없이 잡힌 스타터의 대체 패순환 처리'),'ROADMAP closes the targetless starter fallback item');
ok(road.includes('ZERO-SIGHT 첫 라이브 스타터 페어'),'ROADMAP records the first live ZERO-SIGHT pair');
ok(themeDoc.includes('- [x] 표적 없이 잡힌 스타터의 대체 패순환 처리'),'canonical theme doc closes the fallback item');
ok(themeDoc.includes('첫 라이브 스타터 구현'),'canonical theme doc records the live starter pair');
ok(!script.includes('ZERO-SIGHT HYPE')&&!script.includes('zeroSightResource'),'ZERO-SIGHT starters add no dedicated resource');
console.log('ZERO-SIGHT starter targeting and targetless fallback regression passed.');
