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
  const ctx=vm.createContext({console,Object});ctx.state={turnToken:5};install(ctx,'hasQuickReloadExtraNewMeld');
  const q={uid:'q',owner:'player',tag:'pbQuickReload',quickReloadNewMeldToken:null,quickReloadConsumedToken:null};
  const a={uid:'a',owner:'player'};const b={uid:'b',owner:'player'};
  ok(ctx.hasQuickReloadExtraNewMeld('player',[q,a,b],false)===true,'ordinary first new meld remains allowed without Quick Reload');
  ok(ctx.hasQuickReloadExtraNewMeld('player',[q,a,b],true)===false,'ordinary second new meld remains blocked');
  q.quickReloadNewMeldToken=5;
  ok(ctx.hasQuickReloadExtraNewMeld('player',[q,a,b],true)===true,'armed Quick Reload allows exactly the extra new meld that includes that card');
  q.quickReloadConsumedToken=5;
  ok(ctx.hasQuickReloadExtraNewMeld('player',[q,a,b],true)===false,'consumed Quick Reload cannot grant a second extra new meld in the same turn');
}

// AI search remains turn-aware and only opens the second meld if the armed card is present.
{
  const ctx=vm.createContext({console,Math,Object,Set});ctx.state={turnToken:9};ctx.combos=arr=>{const out=[];for(let i=0;i<arr.length;i++)for(let j=i+1;j<arr.length;j++)for(let k=j+1;k<arr.length;k++)out.push([arr[i],arr[j],arr[k]]);return out};ctx.meldType=cs=>cs.map(c=>c.rank).join('')==='123'?'RUN':null;ctx.namedBoardBias=()=>0;ctx.themeAIAttachBias=()=>0;install(ctx,'hasQuickReloadExtraNewMeld','bestNewMeldForTurn');
  const q={uid:'q',rank:'1',owner:'enemy',tag:'pbQuickReload',quickReloadNewMeldToken:9,quickReloadConsumedToken:null};
  const a={uid:'a',rank:'2',owner:'enemy'},b={uid:'b',rank:'3',owner:'enemy'},x={uid:'x',rank:'7',owner:'enemy'};
  const best=ctx.bestNewMeldForTurn('enemy',[q,a,b,x],true);
  ok(best&&best.includes(q)&&best.length===3,'after normal new-meld use, AI search only returns a legal combination containing armed Quick Reload');
  q.quickReloadNewMeldToken=8;
  ok(ctx.bestNewMeldForTurn('enemy',[q,a,b,x],true)==null,'expired Quick Reload permission cannot create an extra new-meld candidate');
}

// Successful extra new meld consumes the card-bound token and reports that it used the exception.
{
  const player={hand:[],melds:[],newMeldUsed:true};const enemy={hand:[],melds:[],newMeldUsed:false};
  const q={uid:'q',rank:'5',suit:'H',owner:'player',tag:'pbQuickReload',quickReloadNewMeldToken:20,quickReloadConsumedToken:null};
  const a={uid:'a',rank:'5',suit:'S',owner:'player'},b={uid:'b',rank:'5',suit:'D',owner:'player'};player.hand=[q,a,b];
  const ctx=vm.createContext({console,Math,Object,Set,Array});ctx.state={turnToken:20,phase:'action',side:'player',actionMade:false};ctx.sideObj=w=>w==='player'?player:enemy;ctx.meldType=cs=>cs.length===3&&new Set(cs.map(c=>c.suit)).size===3&&cs.every(c=>c.rank==='5')?'SET':null;ctx.isTurnBlockedCard=()=>false;ctx.makeMeld=(type,cards,owner)=>({type,cards,owner,chain:0});ctx.resolveEffects=()=>({pending:false});ctx.emitEffectEvent=(event,p)=>{if(event==='onMeldCreate')ctx.packet=p};ctx.log=()=>{};ctx.render=()=>{};ctx.tutorialCheckProgress=()=>{};ctx.tryRummy=()=>false;install(ctx,'hasQuickReloadExtraNewMeld','submitNewMeld');
  ok(ctx.submitNewMeld('player',[q,a,b])===true,'armed Quick Reload successfully builds the extra 3-card meld');
  ok(q.quickReloadConsumedToken===20,'successful extra new meld consumes Quick Reload permission');
  ok(ctx.packet?.quickReloadExtra===true,'onMeldCreate exposes that the meld used the Quick Reload extra action');
}

// Quick Reload must never become a returning-attach override by itself.
{
  const ctx=vm.createContext({console,Object});ctx.state={turnToken:30};install(ctx,'recoveredCardsCanReturn');
  const q={uid:'q',recoveredTurnToken:30,quickReloadNewMeldToken:30,recoverReturnOverrideToken:null,recoverReturnAllowedMelds:null};
  const m={type:'RUN',cards:[]};
  ok(ctx.recoveredCardsCanReturn([q],m,30)===false,'Quick Reload permission alone cannot reuse a recovered card for a same-turn returning attach');
  q.recoverReturnOverrideToken=30;q.recoverReturnAllowedMelds=new Set([m]);
  ok(ctx.recoveredCardsCanReturn([q],m,30)===true,'destination-bound return override rules remain separate from Quick Reload');
}

ok(script.includes("const quickReloadExtra=hasQuickReloadExtraNewMeld('player',chosen,state.player.newMeldUsed);"),'player new-meld action recognizes only the explicit Quick Reload exception');
ok(script.includes("state.player.newMeldUsed?'퀵 리로드 추가 새 조합':'새 조합'"),'UI previews the extra new meld instead of saying the action is already spent');
ok(script.includes("const nm=bestNewMeldForTurn('enemy',a.hand,a.newMeldUsed);"),'AI new-meld loop no longer hard-blocks a valid Quick Reload extra action');
ok(script.includes('a.newMeldUsed&&hasQuickReloadNewMeldCandidateAI(w,a.hand)'),'AI may finish a RUN to open a slot when a valid Quick Reload extra meld exists');
ok(script.includes('if(bestNewMeldForTurn(w,hand,side.newMeldUsed))return true;'),'stuck-state legality recognizes a valid Quick Reload extra new meld');
ok(road.includes('- [x] `퀵 리로드` 회수 후 추가 새 조합 예외 구현'),'ROADMAP marks the non-redundant Quick Reload implementation complete');
ok(themeDoc.includes('기본 규칙이 회수 카드의 첫 새 조합 사용을 이미 허용하므로 효과를 비중복 형태로 수정'),'canonical card design records why Quick Reload was redesigned');
ok(themeDoc.includes('- [x] 회수 카드를 추가 새 조합 재료로만 허용하는 `퀵 리로드` 예외 처리'),'canonical POINT-BLANK checklist marks Quick Reload complete');
ok(themeDoc.includes('- [x] 일반 카드가 접전 조합에 붙어도 테마 엔진이 인식하도록 이벤트 설계'),'canonical POINT-BLANK checklist records the already-tested card-agnostic clash event path');
console.log('POINT-BLANK Quick Reload extra-new-meld regression passed.');