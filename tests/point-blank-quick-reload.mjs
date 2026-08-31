import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const name of names)vm.runInContext(source(name),ctx)}

new Function(script);
ok(script.includes("'PBDJ':{slot:'DJ',themeId:'point-blank',n:'퀵 리로드',t:'pbQuickReload'"),'Quick Reload is a live POINT-BLANK J♦ named variant');
ok(script.includes('이미 새 조합을 만들었어도')&&script.includes('버스트/체인 반환 제한은 유지한다'),'Quick Reload text describes the non-redundant extra-new-meld rule and preserved return guard');

// Recovery from the actor's active clash grants one card-bound extra-new-meld token.
{
  const clash={type:'RUN',cards:[],themeMeta:{pointBlank:{clashBy:{player:true,enemy:false},clashTurn:{player:1,enemy:null},releaseAtTurnEndStart:{player:null,enemy:null}}}};
  const plain={type:'RUN',cards:[],themeMeta:{pointBlank:{clashBy:{player:false,enemy:false},clashTurn:{player:null,enemy:null},releaseAtTurnEndStart:{player:null,enemy:null}}}};
  const quick={uid:'qr',owner:'player',themeId:'point-blank',tag:'pbQuickReload',name:'퀵 리로드',quickReloadNewMeldToken:null,quickReloadConsumedToken:null};
  const ctx=vm.createContext({console,Object});ctx.log=()=>{};
  install(ctx,'isPointBlankClash','handlePointBlankThemeEvent');
  ok(ctx.handlePointBlankThemeEvent({event:'onRecover',actor:'player',card:quick,meld:plain,turnToken:40})===false,'Quick Reload does not arm when recovered from a non-clash meld');
  ok(quick.quickReloadNewMeldToken==null,'non-clash recovery leaves no extra-new-meld token');
  ok(ctx.handlePointBlankThemeEvent({event:'onRecover',actor:'player',card:quick,meld:clash,turnToken:41})===true,'Quick Reload arms when recovered from the actor’s active clash');
  ok(quick.quickReloadNewMeldToken===41&&quick.quickReloadConsumedToken==null,'Quick Reload stores a current-turn card-bound permission');
  ok(ctx.handlePointBlankThemeEvent({event:'onRecover',actor:'player',card:quick,meld:clash,turnToken:41})===false,'same recovery window cannot re-arm Quick Reload repeatedly');
}

// Base first-new-meld rule is unchanged; the exception exists only after that action was already spent.
{
  const side={newMeldUsed:false};
  const state={turnToken:77};
  const ctx=vm.createContext({console,Object,state});ctx.sideObj=()=>side;
  install(ctx,'quickReloadNewMeldCard','newMeldAccess');
  const normal=[{uid:'n1',owner:'player'},{uid:'n2',owner:'player'},{uid:'n3',owner:'player'}];
  let access=ctx.newMeldAccess('player',normal);
  ok(access.allowed===true&&access.extra===false,'ordinary first new meld remains allowed without Quick Reload');
  side.newMeldUsed=true;
  access=ctx.newMeldAccess('player',normal);
  ok(access.allowed===false,'ordinary second new meld remains blocked');
  const quick={uid:'q',owner:'player',themeId:'point-blank',tag:'pbQuickReload',quickReloadNewMeldToken:77,quickReloadConsumedToken:null};
  access=ctx.newMeldAccess('player',[quick,normal[0],normal[1]]);
  ok(access.allowed===true&&access.extra===true&&access.quickReloadCard===quick,'armed Quick Reload allows exactly the extra new meld that includes that card');
  quick.quickReloadConsumedToken=77;
  ok(ctx.newMeldAccess('player',[quick,normal[0],normal[1]]).allowed===false,'consumed Quick Reload cannot grant a second extra new meld in the same turn');
}

// AI/new-meld search only considers combinations that actually contain the armed card after the normal action is spent.
{
  const state={turnToken:9,turnNo:3};
  const quick={uid:'q',owner:'enemy',themeId:'point-blank',tag:'pbQuickReload',quickReloadNewMeldToken:9,quickReloadConsumedToken:null,group:'quick',named:true};
  const hand=[quick,{uid:'q2',owner:'enemy',group:'quick',named:false},{uid:'q3',owner:'enemy',group:'quick',named:false},{uid:'n1',owner:'enemy',group:'normal',named:true},{uid:'n2',owner:'enemy',group:'normal',named:true},{uid:'n3',owner:'enemy',group:'normal',named:true}];
  const side={newMeldUsed:true,hand};
  const ctx=vm.createContext({console,Math,Array,Object,Set,state});ctx.sideObj=()=>side;ctx.meldType=cards=>cards.length===3&&cards.every(c=>c.group===cards[0].group)?'SET':null;
  install(ctx,'combinations','bestNewMeld','quickReloadNewMeldCard','newMeldAccess','bestNewMeldForTurn');
  const best=ctx.bestNewMeldForTurn('enemy');
  ok(best&&best.cards.includes(quick),'after normal new-meld use, AI search only returns a legal combination containing armed Quick Reload');
  quick.quickReloadNewMeldToken=8;
  ok(ctx.bestNewMeldForTurn('enemy')===null,'expired Quick Reload permission cannot create an extra new-meld candidate');
}

// Actual submit path consumes the permission, creates a normal zero-return 3-card meld, and exposes the extra-action snapshot.
{
  const state={turnToken:55,turnNo:8,gameOver:false,lastPlayerMeldType:null};
  const quick={uid:'q',owner:'player',themeId:'point-blank',tag:'pbQuickReload',name:'퀵 리로드',quickReloadNewMeldToken:55,quickReloadConsumedToken:null,blockedUntilTurn:null,named:true,fromDiscard:false};
  const a={uid:'a',owner:'player',blockedUntilTurn:null,named:false,fromDiscard:false},b={uid:'b',owner:'player',blockedUntilTurn:null,named:false,fromDiscard:false},spare={uid:'s',owner:'player'};
  const side={hand:[quick,a,b,spare],melds:[],newMeldUsed:true,actedThisTurn:false,turnStarts:2};
  const events=[];
  const ctx=vm.createContext({console,Math,Array,Object,Set,state});
  ctx.sideObj=()=>side;ctx.meldsOf=()=>side.melds;ctx.meldType=cards=>cards.length===3?'SET':null;ctx.beforeNewMeld=()=>true;
  ctx.removeFromHand=(w,cards)=>{const ids=new Set(cards.map(c=>c.uid));side.hand=side.hand.filter(c=>!ids.has(c.uid))};ctx.blankMeldStatus=()=>({});ctx.markSetCompletion=()=>{};ctx.fieldAction=()=>0;ctx.resolveEffects=()=>({pending:false});ctx.characterActionBonus=()=>0;ctx.triggerOpponentHandTraps=()=>{};ctx.zeroSightTargetActors=()=>[];ctx.emitEffectEvent=(event,payload)=>{events.push({event,...payload});return payload};ctx.log=()=>{};
  install(ctx,'quickReloadNewMeldCard','newMeldAccess','submitNewMeld');
  const result=ctx.submitNewMeld('player',[quick,a,b]);
  ok(result===true&&side.melds.length===1&&side.melds[0].cards.includes(quick),'armed Quick Reload successfully builds the extra 3-card meld');
  ok(quick.quickReloadConsumedToken===55,'successful extra new meld consumes Quick Reload permission');
  const created=events.find(e=>e.event==='onMeldCreate');
  ok(created?.extraNewMeld===true&&created.quickReloadCard===quick,'onMeldCreate exposes that the meld used the Quick Reload extra action');
}

// Crucially, Quick Reload never bypasses the recovered-card BURST/CHAIN return guard.
{
  const quick={recoveredToken:66,recoverReturnOverrideToken:null,recoverReturnTargets:null,quickReloadNewMeldToken:66,quickReloadConsumedToken:null};
  const ctx=vm.createContext({console});install(ctx,'recoveredCardCanReturn');
  ok(ctx.recoveredCardCanReturn(quick,66,{})===false,'Quick Reload permission alone cannot reuse a recovered card for a same-turn returning attach');
  quick.recoverReturnOverrideToken=66;quick.recoverReturnTargets=[];
  ok(ctx.recoveredCardCanReturn(quick,66,{})===false,'destination-bound return override rules remain separate from Quick Reload');
}

const playerMeld=source('playerMeld'),buttons=source('updateButtons'),ai=source('continueAITurnAfterAcquisition'),bestFinish=source('bestFinishRunAI'),legal=source('hasAnyLegalAction');
ok(playerMeld.includes("newMeldAccess('player',cs)")&&playerMeld.includes('퀵 리로드가 있다면'),'player new-meld action recognizes only the explicit Quick Reload exception');
ok(buttons.includes("newMeldAccess('player',cs)")&&buttons.includes('퀵 리로드 · 추가'),'UI previews the extra new meld instead of saying the action is already spent');
ok(!ai.includes("nm=!state.enemy.newMeldUsed")&&!ai.includes("if(nm&&!state.enemy.newMeldUsed"),'AI new-meld loop no longer hard-blocks a valid Quick Reload extra action');
ok(!bestFinish.includes('if(s.newMeldUsed||'),'AI may finish a RUN to open a slot when a valid Quick Reload extra action exists');
ok(!legal.includes('if(!s.newMeldUsed&&'),'stuck-state legality recognizes a valid Quick Reload extra new meld');

ok(road.includes('- [x] `퀵 리로드` 회수 후 추가 새 조합 예외 구현'),'ROADMAP marks the non-redundant Quick Reload implementation complete');
ok(themeDoc.includes('기본 규칙이 회수 카드의 첫 새 조합 사용을 이미 허용하므로 효과를 비중복 형태로 수정'),'canonical card design records why Quick Reload was redesigned');
ok(themeDoc.includes('- [x] 회수 카드를 추가 새 조합 재료로만 허용하는 `퀵 리로드` 예외 처리'),'canonical POINT-BLANK checklist marks Quick Reload complete');
ok(themeDoc.includes('- [x] 일반 카드가 접전 조합에 붙어도 테마 엔진이 인식하도록 이벤트 설계'),'canonical POINT-BLANK checklist records the already-tested card-agnostic clash event path');

console.log('POINT-BLANK Quick Reload extra-new-meld regression passed.');
