import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

ok(script.includes("const THEME_REACTION_ORDER=Object.freeze({attach:Object.freeze(['onAttach','onTargetMeldChange','onClashMeldChange','onArrival','postReturn'])"),'attach reaction order is explicitly declared');
ok(script.includes("recover:Object.freeze(['onRecover','onTargetMeldChange','onClashMeldChange','onReturnMail'])"),'recovery reaction order is explicitly declared');
ok(script.includes("move:Object.freeze(['onMeldMove','onTargetMeldChange:source','onTargetMeldChange:target','onClashMeldChange:source','onClashMeldChange:target','onArrival'])"),'movement source/target ordering is explicitly declared');

// Shared card-bound turn gate: one claim per key per turn token, independent keys coexist.
{
 const state={turnToken:7};const card={};
 const ctx=context({state});install(ctx,'ensureThemeTurnGates','themeTurnGateUsed','claimThemeTurnGate');
 ok(ctx.claimThemeTurnGate(card,'alpha',7)===true,'first theme reaction claim succeeds');
 ok(ctx.themeTurnGateUsed(card,'alpha',7)===true,'claimed reaction is visible for current token');
 ok(ctx.claimThemeTurnGate(card,'alpha',7)===false,'same reaction key cannot claim twice in one turn');
 ok(ctx.claimThemeTurnGate(card,'beta',7)===true,'different reaction keys coexist on the same card and turn');
 ok(ctx.claimThemeTurnGate(card,'alpha',8)===true,'same reaction key becomes available on a later turn token');
}

// Runtime source order matches the declared contract.
{
 const recover=source('emitRecoveryEvent');
 const base=recover.indexOf("emitEffectEvent('onRecover'");
 const target=recover.indexOf("emitZeroSightTargetChange('recover'",base);
 const clash=recover.indexOf("refreshPointBlankClashMeld(meld",target);
 ok(base>=0&&target>base&&clash>target,'recovery executes base event → target change → clash change');
}
{
 const move=source('emitMeldMoveEvent');
 const base=move.indexOf("emitEffectEvent('onMeldMove'");
 const targetOut=move.indexOf("emitZeroSightTargetChange('moveOut'",base);
 const targetIn=move.indexOf("emitZeroSightTargetChange('moveIn'",targetOut);
 const clash=move.indexOf("refreshPointBlankClashMeld(sourceMeld",targetIn);
 const clashTarget=move.indexOf("refreshPointBlankClashMeld(targetMeld",clash);
 ok(base>=0&&targetOut>base&&targetIn>targetOut&&clash>targetIn&&clashTarget>clash,'movement executes base → target source/target → clash source/target');
}
{
 const attach=source('attachCards');
 const base=attach.indexOf("emitEffectEvent('onAttach'");
 const target=attach.indexOf("emitZeroSightTargetChange('attach'",base);
 const clash=attach.indexOf("refreshPointBlankClashMeld(m",target);
 const post=attach.indexOf("resolveZeroSightPostReturn(w,m,ctx.fxState||{})",clash);
 ok(base>=0&&target>base&&clash>target&&post>clash,'attach executes base event → target change → clash change → deferred post-return cleanup');
}

// Encore: generic gate blocks a second grant even if its legacy compatibility token is cleared.
{
 const state={turnToken:31};const c={themeId:'v-signal',tag:'vEncore',name:'앙코르',encoreGrantToken:null};let grants=0;
 const ctx=context({state,grantRecoveryReturnOverride:()=>{grants++;return 1},log:()=>{}});install(ctx,'ensureThemeTurnGates','themeTurnGateUsed','claimThemeTurnGate','handleVSignalThemeEvent');
 ok(ctx.handleVSignalThemeEvent({event:'onRecover',actor:'player',card:c,meld:{},turnToken:31})===true,'Encore first eligible recovery reaction fires');
 c.encoreGrantToken=null;
 ok(ctx.handleVSignalThemeEvent({event:'onRecover',actor:'player',card:c,meld:{},turnToken:31})===false&&grants===1,'shared gate blocks duplicate Encore even if legacy token is absent');
}

// Quick Reload: same shared gate, while the legacy token remains populated for compatibility.
{
 const state={turnToken:41};const c={themeId:'point-blank',tag:'pbQuickReload',name:'퀵 리로드',quickReloadNewMeldToken:null};
 const ctx=context({state,isPointBlankClash:()=>true,log:()=>{}});install(ctx,'ensureThemeTurnGates','themeTurnGateUsed','claimThemeTurnGate','handlePointBlankThemeEvent');
 ok(ctx.handlePointBlankThemeEvent({event:'onRecover',actor:'player',card:c,meld:{},turnToken:41})===true,'Quick Reload first clash recovery reaction fires');
 ok(c.quickReloadNewMeldToken===41,'Quick Reload preserves its legacy compatibility token');
 c.quickReloadNewMeldToken=null;
 ok(ctx.handlePointBlankThemeEvent({event:'onRecover',actor:'player',card:c,meld:{},turnToken:41})===false,'shared gate blocks duplicate Quick Reload even if legacy token is cleared');
}

// Cover Swap shares the gate but still records the old used token expected by existing UI/tests.
{
 const state={turnToken:51};const target={uid:'t',owner:'player'},alt={uid:'a',owner:'player'};
 const cover={uid:'c',owner:'player',themeId:'point-blank',tag:'pbCoverSwap',name:'엄폐 교대',coverSwapUsedToken:null};
 const meld={cards:[target,cover,alt],themeMeta:{pointBlank:{clashBy:{player:true,enemy:false}}}};
 const ctx=context({state,addShield:()=>{},log:()=>{},cardText:c=>c.uid});install(ctx,'ensureThemeTurnGates','themeTurnGateUsed','claimThemeTurnGate','isPointBlankClash','pointBlankCoverSwapSource','pointBlankCoverSwapTarget');
 const first=ctx.pointBlankCoverSwapTarget('enemy',meld,target,[alt]);
 ok(first.redirected===true&&cover.coverSwapUsedToken===51,'Cover Swap first hostile reaction fires and preserves legacy token');
 cover.coverSwapUsedToken=null;
 const second=ctx.pointBlankCoverSwapTarget('enemy',meld,target,[alt]);
 ok(second.redirected===false&&second.source===null,'shared gate blocks duplicate Cover Swap even if legacy token is cleared');
}

ok(source('makeCard').includes('themeTurnGates:{}'),'new cards explicitly initialize shared theme-turn gate storage');
ok(road.includes('한 행동의 테마 반응 순서 + 턴당 1회 게이트 명문화'),'ROADMAP closes the shared reaction-order gate');
ok(themeDoc.includes('테마 반응의 턴당 1회 처리 공통화'),'canonical V-SIGNAL checklist closes common once-per-turn handling');
ok(themeDoc.includes('기본 행동 이벤트 → 표적 변화 반응 → 접전 변화 반응 → 반환 후 지연 처리'),'canonical theme principles document cross-theme ordering');
console.log('Theme reaction order and once-per-turn gate regression passed.');
