import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const doc=fs.readFileSync(new URL('../docs/ASYMMETRIC_RANK_PROTOTYPE.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
new Function(script);

for(const n of ['playerRankChoiceRequired','playerLegalRankPlans','playerRankChoiceHint','requestPlayerRankChoice','executePlayerMeld','executePlayerAttach'])ok(script.includes(`function ${n}(`),`M11B player-choice helper exists: ${n}`);
ok(html.includes('/* M11B UI2 · player asymmetric-rank legality and choice preview */'),'player rank-choice UI has a dedicated CSS layer');
ok(source('renderEffectChoiceModal').includes("q.kicker||'효과 선택'"),'shared choice modal supports a rank-choice kicker without changing normal effect default');
ok(source('renderEffectChoiceModal').includes("o.kind==='rankPlan'?' rankPlanChoice':''"),'rank-plan options receive a distinct but shared-modal presentation class');
ok(source('canAttachTo').includes("legalRankChoicePlansForAttach(m,cards)"),'player attach legality checks all asymmetric rank projections');
ok(source('attachPreview').includes("plans[0]?.projected||cards"),'attach preview labels use a legal projected rank plan instead of unresolved base rank');
ok(source('playerMeld').includes('requestPlayerRankChoice(cs,null')&&source('executePlayerMeld').includes("submitNewMeld('player',cs,rankPlan)"),'player new-meld path explicitly chooses and forwards a rank plan');
ok(source('playerAttach').includes('requestPlayerRankChoice(cs,m')&&source('executePlayerAttach').includes("attachCards('player',cs,target.side,target.index,rankPlan)"),'player attach path explicitly chooses and forwards a rank plan');
ok(source('updateButtons').includes('legalRankChoicePlansForNewMeld(cs)')&&source('updateButtons').includes('사용값 선택'),'new-meld button enablement and label are projection-aware');
ok(source('renderTargetHint').includes("playerRankChoiceHint(cs,tm||null)"),'selection strip exposes rank-plan legality for the current target');

const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
const SUIT_SYMBOL={S:'♠',H:'♥',D:'♦',C:'♣',J:'★'};
let uid=1;
const card=(suit,base,top=base,bottom=base)=>({uid:uid++,suit,rank:base,baseRank:base,topRank:top,bottomRank:bottom,activeRank:null,rankOrientation:null,named:false,name:'시험',themeId:null,tag:null});
const state={field:null,battleId:9,turnToken:5,turn:'player',phase:'action',turnNo:2,player:{hand:[],melds:[],returnedSwitchThisTurn:false},enemy:{hand:[],melds:[],returnedSwitchThisTurn:false}};
const ctx=vm.createContext({console,Math,Number,Object,Array,Set,Map,RANK_VALUE,SUIT_SYMBOL,state});
ctx.isJoker=c=>c?.suit==='J';ctx.isSuitFlexible=()=>false;ctx.sideObj=w=>w==='player'?state.player:state.enemy;ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.cardText=c=>`${c.rank}${SUIT_SYMBOL[c.suit]}`;
install(ctx,'normalizePrototypeRank','ensureRankPrototype','cardPrintedRanks','isAsymmetricRankCard','rankChoiceOptions','rankChoicePlans','projectRankChoiceCards','rankChoicePlanLabel','runSequenceOK','setValid','runValid','meldType','legalRankChoicePlansForNewMeld','legalRankChoicePlansForAttach','rankChoicePreview','playerRankChoiceRequired','playerLegalRankPlans','playerRankChoiceHint','requestPlayerRankChoice');

const asym=card('S','7','3','7'),h3=card('H','3'),d3=card('D','3');
state.player.hand=[asym,h3,d3];
let hint=ctx.playerRankChoiceHint([asym,h3,d3],null);
ok(hint.includes('사용값 1안')&&hint.includes('1번 위 3 → 세트'),'new-meld selection hint shows the only legal printed side and resulting SET');
ok(!hint.includes('아래 7 → 세트'),'selection hint omits illegal printed-side outcomes instead of implying both are valid');
const run={type:'RUN',cards:[card('S','4'),card('S','5'),card('S','6')],chain:0,createdToken:null};state.enemy.melds=[run];
hint=ctx.playerRankChoiceHint([asym],run);
ok(hint.includes('사용값 2안')&&hint.includes('위 3 → 런')&&hint.includes('아래 7 → 런'),'attach hint exposes both legal orientations when either end of a RUN can be extended');

let modal=null,chosen=null;ctx.requestEffectChoice=spec=>{modal=spec;return true};
state.enemy.melds=[];
ok(ctx.requestPlayerRankChoice([asym,h3,d3],null,{title:'시험 선택',onChoose:(plan,type)=>{chosen={plan,type}}})===true,'unresolved asymmetric action opens the shared rank-choice modal');
ok(modal?.kicker==='사용값 선택'&&modal?.options?.length===1,'even one legal plan still requires explicit player confirmation');
ok(modal.options[0].kind==='rankPlan'&&modal.options[0].detail.includes('세트'),'rank-choice option explains projected meld type before action commit');
modal.onChoose(modal.options[0]);
ok(chosen?.type==='SET'&&chosen.plan[0].rank==='3'&&chosen.plan[0].orientation==='top','confirmed UI option forwards the exact top-rank plan');
ok(asym.activeRank===null&&asym.rank==='7','preview and modal confirmation remain non-mutating until the real action commits');

const ordinary=[card('S','9'),card('H','9'),card('D','9')];state.player.hand=ordinary;modal=null;
ok(ctx.playerRankChoiceRequired(ordinary)===false&&ctx.requestPlayerRankChoice(ordinary,null,{onChoose:()=>{}})===false,'ordinary X/X actions bypass the rank-choice modal entirely');

// stale guard: same option cannot commit after the hand/turn snapshot changes.
state.player.hand=[asym,h3,d3];state.turnToken=8;modal=null;chosen=null;ctx.requestPlayerRankChoice([asym,h3,d3],null,{onChoose:(plan,type)=>{chosen={plan,type}}});
state.turnToken=9;modal.onChoose(modal.options[0]);
ok(chosen===null,'rank choice is discarded if its battle/turn snapshot is stale before confirmation');

const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('const FIELDS=',namedStart),namedBlock=script.slice(namedStart,namedEnd);
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'player choice UI still ships with zero live asymmetric card definitions');
ok(doc.includes('UI 프로토타입 단계 2')&&doc.includes('합법 plan이 1개뿐이어도 자동 선택하지 않는다'),'prototype document locks explicit player direction choice');
ok(road.includes('- [x] 손패에서 비대칭 카드 선택 시 두 사용값과 각각의 합법 세트/런 후보를 미리보기로 표시'),'ROADMAP closes the hand rank-choice preview item');
ok(road.includes('- [ ] 모바일에서 상·하단 숫자가 다른 카드가 단순 오타처럼 보이지 않도록 최초 획득/튜토리얼 설명 설계'),'mobile/onboarding explanation remains the final M11B UI item');
console.log('M11B player asymmetric-rank choice UI regression passed.');
