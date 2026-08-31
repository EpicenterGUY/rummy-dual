import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const audit=fs.readFileSync(new URL('named-card-audit.mjs',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,Infinity,...extra})}

ok(script.includes("'ZSSK':{slot:'SK',themeId:'zero-sight',n:'ONE SHOT',t:'zsOneShot'"),'ONE SHOT is a live ZERO-SIGHT K-spade variant');
ok(script.includes("{id:'zs7',label:'전체 7클리어 · ZERO-SIGHT',kind:'theme',when:p=>p.totalClears>=7,items:['ZSSK'],fields:[]}"),'ONE SHOT unlocks independently at seven clears');
ok(script.includes("zsOneShot:['pressure','control','status']"),'ONE SHOT uses ordinary open-deck tendencies');
ok(script.includes("이 행동 전 기존 누적 위력이 50 이상"),'ONE SHOT card text makes the 50 threshold timing explicit');

// Success: only an actual return through the actor's opponent target at pre-action 50+ reserves +18 and target clear.
{
  const resolve=source('resolveEffects');
  const target={type:'RUN',cards:[]};
  const side={hand:[]};
  const state={turnToken:11,switchPower:50};
  const ctx=context({state,sideObj:()=>side,other:()=> 'enemy',consumeOfficialStatus:()=>0,isZeroSightTarget:(w,m)=>w==='player'&&m===target});
  vm.runInContext(`${resolve};globalThis.__r=resolveEffects`,ctx);
  const card={uid:1,named:true,tag:'zsOneShot',name:'ONE SHOT'};
  const action={isNew:false,isAttach:true,targetOwner:'enemy',meld:target,totalLength:4,effectSeen:new Set(),willReturn:true};
  const out=ctx.__r('player',[card],'RUN',action);
  ok(out.bonus===18,'ONE SHOT success adds exactly +18');
  ok(action.fxState?.zeroSightClearTargetAfterReturn===target,'ONE SHOT success defers exact target clearing');
  ok(!action.fxState?.zeroSightSelfSealAfterReturn,'successful ONE SHOT schedules no self seal');
}

// Failure: 49 is below threshold, gives no +18, does not clear immediately, and defers one self-seal.
{
  const resolve=source('resolveEffects');
  const target={type:'SET',cards:[]};
  const side={hand:[]};
  const state={turnToken:12,switchPower:49};
  let clears=0,seals=0;
  const ctx=context({state,sideObj:()=>side,other:()=> 'enemy',consumeOfficialStatus:()=>0,isZeroSightTarget:()=>true,clearZeroSightTarget:()=>{clears++},applyOfficialStatus:()=>{seals++}});
  vm.runInContext(`${resolve};globalThis.__r=resolveEffects`,ctx);
  const card={uid:2,named:true,tag:'zsOneShot',name:'ONE SHOT'};
  const action={isNew:false,isAttach:true,targetOwner:'enemy',meld:target,totalLength:4,effectSeen:new Set(),willReturn:true};
  const out=ctx.__r('player',[card],'SET',action);
  ok(out.bonus===0,'failed ONE SHOT grants no direct power');
  ok(action.fxState?.zeroSightSelfSealAfterReturn===1,'failed ONE SHOT defers exactly one self seal');
  ok(!action.fxState?.zeroSightClearTargetAfterReturn,'failed ONE SHOT preserves its target for a later attempt');
  ok(clears===0&&seals===0,'resolver itself does not clear or seal, avoiding same-action order dependence');
}

// Wrong board context: own meld or non-target gets no reward/risk.
{
  const resolve=source('resolveEffects');
  const target={type:'RUN',cards:[]},side={hand:[]},state={turnToken:13,switchPower:80};
  const ctx=context({state,sideObj:()=>side,other:()=> 'enemy',consumeOfficialStatus:()=>0,isZeroSightTarget:()=>true});
  vm.runInContext(`${resolve};globalThis.__r=resolveEffects`,ctx);
  const card={uid:3,named:true,tag:'zsOneShot',name:'ONE SHOT'};
  const action={isNew:false,isAttach:true,targetOwner:'player',meld:target,totalLength:4,effectSeen:new Set(),willReturn:true};
  const out=ctx.__r('player',[card],'RUN',action);
  ok(out.bonus===0&&!action.fxState?.zeroSightClearTargetAfterReturn&&!action.fxState?.zeroSightSelfSealAfterReturn,'ONE SHOT ignores own-meld returns even at high power');
}

// Deferred resolver performs success clear OR failure seal after the action, exactly once.
{
  const fn=source('resolveZeroSightPostReturn');
  const meld={};let clears=0,seals=0;
  const side={};
  const ctx=context({sideObj:()=>side,isZeroSightTarget:()=>true,clearZeroSightTarget:()=>{clears++},applyOfficialStatus:(scope,target,key,n)=>{if(scope==='player'&&target===side&&key==='seal')seals+=n},log:()=>{}});
  vm.runInContext(`${fn};globalThis.__post=resolveZeroSightPostReturn`,ctx);
  const success={zeroSightClearTargetAfterReturn:meld};
  ok(ctx.__post('player',meld,success)===true&&clears===1&&seals===0,'post-return success clears the exact target and does not seal');
  ok(success.zeroSightClearTargetAfterReturn===null,'success clear token is consumed');
  const fail={zeroSightSelfSealAfterReturn:1};
  ok(ctx.__post('player',meld,fail)===true&&seals===1,'post-return failure applies official player seal 1');
  ok(fail.zeroSightSelfSealAfterReturn===0,'failure seal token is consumed');
}

// Target-aware reactions must observe the target before ONE SHOT clears it.
{
  const attach=source('attachCards');
  const onAttach=attach.indexOf("emitEffectEvent('onAttach'");
  const targetChange=attach.indexOf("emitZeroSightTargetChange('attach'",onAttach);
  const post=attach.indexOf("resolveZeroSightPostReturn(w,m,ctx.fxState||{})",targetChange);
  ok(onAttach>=0&&targetChange>onAttach&&post>targetChange,'ONE SHOT cleanup runs after attach and target-change reaction packets');
}

ok(audit.includes("'zsBallistics','zsOneShot'"),'direct-power audit counts both live ZERO-SIGHT power modifiers');
ok(road.includes('K♠ `ONE SHOT` 라이브 구현'),'ROADMAP records live ONE SHOT timing and risk');
ok(themeDoc.includes('행동 전 기존 누적 위력')&&themeDoc.includes('반환 후 자신에게 봉인 1'),'canonical ONE SHOT wording locks threshold and failure timing');
ok(themeDoc.includes('K♠ `ONE SHOT` 라이브 구현'),'canonical ZERO-SIGHT checklist records the live finisher');
console.log('ZERO-SIGHT ONE SHOT finisher regression passed.');
