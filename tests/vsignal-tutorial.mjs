import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
new Function(script);
ok(script.includes("'v-signal':Object.freeze({themeId:'v-signal',startStep:'vsEncore',live:true})"),'V-SIGNAL tutorial registry is live and points to the Encore scenario');
ok(script.includes("{id:'vsEncore',themeId:'v-signal',title:'앙코르 재입장'")&&script.includes("expectAttachTag:'vEncore'")&&script.includes('expectRecoveredSameTurn:true'),'V-SIGNAL tutorial step requires the real Encore and same-turn recovered reuse');
ok(script.includes("makeTutorialNamed('VSH5','vsEncoreCard')")&&script.includes("makeTutorialCard('S','5','board','enemy'),makeTutorialCard('D','5','board','enemy'),makeTutorialCard('C','5','board','enemy')"),'scenario uses the live V-SIGNAL H5 variant and an ordinary opponent 5 SET');
ok(script.includes('if(step.expectRecoveredSameTurn&&!context.cards?.some(c=>c.recoveredToken===state.turnToken))return false'),'tutorial completion gate verifies the card was recovered this same turn');
ok(script.includes('V-SIGNAL 체험 완료! 전용 자원 없이 회수 → 다른 공개 조합 재입장 → 버스트'),'completion copy teaches the actual V-SIGNAL loop without a theme-only resource');

// Reproduce the tutorial board with live legality helpers: ordinary recovered cards are blocked,
// while Encore receives a one-turn destination-bound exception and can complete the enemy 5 SET.
{
 const rank={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
 let uid=0;const card=(suit,r,extra={})=>({uid:`vs-${++uid}`,suit,rank:String(r),owner:'player',named:false,themeId:null,tag:null,recoveredToken:null,recoverReturnOverrideToken:null,recoverReturnTargets:null,...extra});
 const encore=card('H','5',{named:true,themeId:'v-signal',tag:'vEncore',name:'앙코르',recoveredToken:41,encoreGrantToken:null});
 const sourceRun={type:'RUN',cards:[encore,card('H','6'),card('H','7'),card('H','8')],chain:1,createdToken:null,lastAttachToken:null};
 const destSet={type:'SET',cards:[card('S','5',{owner:'enemy'}),card('D','5',{owner:'enemy'}),card('C','5',{owner:'enemy'})],chain:0,createdToken:null,lastAttachToken:null};
 const player={melds:[sourceRun],returnedSwitchThisTurn:false},enemy={melds:[destSet],returnedSwitchThisTurn:false};
 const state={turnNo:5,turnToken:41,switchTarget:'neutral',player,enemy,field:null};
 const ctx=vm.createContext({console,Math,Set,Map,Array,Object,Number,state,RANK_VALUE:rank});
 ctx.sideObj=w=>w==='player'?player:enemy;ctx.other=w=>w==='player'?'enemy':'player';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=()=>true;ctx.canContinueReturnedRun=()=>false;ctx.log=()=>{};
 install(ctx,'isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','legalRecoveryReturnTargets','grantRecoveryReturnOverride','handleVSignalThemeEvent','recoveredCardCanReturn');
 ok(ctx.runValid(sourceRun.cards)&&ctx.setValid(destSet.cards),'tutorial source RUN and ordinary destination SET are both real legal melds');
 const ordinary={...encore,uid:'ordinary',themeId:null,tag:null,recoveredToken:41,recoverReturnOverrideToken:null,recoverReturnTargets:null};
 ok(ctx.recoveredCardCanReturn(ordinary,41,destSet)===false,'base recovery rule blocks ordinary same-turn BURST/CHAIN return reuse');
 ok(ctx.handleVSignalThemeEvent({event:'onRecover',actor:'player',card:encore,meld:sourceRun,turnToken:41})===true,'live Encore recovery handler grants the tutorial exception');
 ok(ctx.recoveredCardCanReturn(encore,41,destSet)===true,'Encore can re-enter the authorized ordinary destination in the same turn');
 ok(ctx.recoveredCardCanReturn(encore,41,sourceRun)===false,'Encore exception remains destination-bound and cannot return to its source meld');
 ok(ctx.meldType(destSet.cards.concat(encore))==='SET','Encore preserves its normal H5 slot identity and completes the opponent 5 SET');
}

ok(road.includes('- [x] V-SIGNAL 등 실제 구현된 테마군 체험전 — 첫 live 테마 체험으로 `앙코르 재입장`'),'ROADMAP marks the first real theme experience complete');
console.log('V-SIGNAL tutorial experience regression passed.');
