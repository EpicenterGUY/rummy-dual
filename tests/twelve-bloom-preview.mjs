import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,b=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){b=i;break}}let d=0;for(let i=b;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function declaration(name,next){const a=script.indexOf(`const ${name}=`),b=script.indexOf(next,a);if(a<0||b<0)throw new Error(`missing declaration ${name}`);return script.slice(a,b)}
function card(uid,suit,rank,owner='player',extra={}){return{uid,suit,rank,slot:suit==='J'?'J':suit+rank,owner,name:'preview',themeId:null,twelveBloomLeapMonth:null,twelveBloomLeapOwner:null,...extra}}
function meld(cards,type='RUN'){return{type,cards:[...cards],chain:0,status:{},themeMeta:{}}}
function ctxFor({publicCards=[],enemyCards=[],knownTheme=false,selected=[],target=null,recovery=null,canAttach=true,meldType='SET'}={}){
 const state={turnToken:20,turnNo:4,turn:'player',phase:'action',gameOver:false,target,player:{hand:[...selected],deck:[],spent:[],melds:[meld(publicCards)]},enemy:{hand:[],deck:[],spent:[],melds:enemyCards.length?[meld(enemyCards)]:[]},discard:[]};
 if(knownTheme)state.player.deck.push(card(900,'C','Q','player',{themeId:'twelve-bloom'}));
 const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math,state,SUIT_SYMBOL:{S:'♠',H:'♥',D:'♦',C:'♣',J:'★'}});
 vm.runInContext(declaration('TWELVE_BLOOM_MONTH_BY_RANK','\nconst TWELVE_BLOOM_SEASON_DEFS='),ctx);
 vm.runInContext(declaration('TWELVE_BLOOM_SEASON_DEFS','\nconst TWELVE_BLOOM_PICTURE_DEFS='),ctx);
 vm.runInContext(declaration('TWELVE_BLOOM_PICTURE_DEFS','\nconst THEME_GROUPS='),ctx);
 for(const n of ['sideObj','other','meldsOf','twelveBloomAllKnownCards','twelveBloomPublicEntries','twelveBloomPublicCards','twelveBloomIsPublicCard','twelveBloomCardMonth','twelveBloomExactSlot','twelveBloomMatchSnapshotFromCards','twelveBloomMatchSnapshot','twelveBloomMatchDiff','twelveBloomPreviewRelevant','twelveBloomMatchName','twelveBloomSlotText','twelveBloomAffectedMatchKeys','twelveBloomProjectedPlayerAction'])vm.runInContext(source(n),ctx);
 ctx.selectedCards=()=>selected;
 ctx.recoverPlan=()=>recovery;
 ctx.canAttachTo=()=>canAttach;
 ctx.meldType=()=>meldType;
 ctx.newMeldAccess=()=>({allowed:true});
 return{ctx,state}
}

new Function(script);
ok(html.includes('id="twelveBloomPreview" class="twelveBloomPreview" hidden'),'battle UI contains a hidden-by-default TWELVE-BLOOM preview surface');
ok(script.includes("c?.themeId==='twelve-bloom'||c?.twelveBloomPreview===true"),'preview relevance is demand-gated by future theme material or an explicit test flag');
ok(source('renderTargetHint').includes("renderTwelveBloomPreview()"),'normal selection refresh path also refreshes contextual bloom preview');
ok(source('renderTwelveBloomPreview').includes("if(!data){el.hidden=true")&&source('renderTwelveBloomPreview').includes("if(!chips.length){el.hidden=true"),'preview hides itself when no relevant or useful match information exists');
ok(html.includes('.twelveBloomPreviewChips{display:flex;gap:4px;flex-wrap:wrap}'),'preview chips wrap instead of widening long RUN layouts');
ok(!source('cardHTML').includes('twelveBloom')&&!source('renderMelds').includes('월</span>'),'normal cards and melds receive no permanent month/picture labels');

{
 const {ctx}=ctxFor({publicCards:[card(1,'C','A'),card(2,'D','2')]});
 ok(ctx.twelveBloomProjectedPlayerAction()===null,'ordinary non-theme battle gets no TWELVE-BLOOM preview data');
}

{
 const a=card(10,'C','A'),two=card(11,'D','2'),three=card(12,'S','3'),f1=card(13,'H','5'),f2=card(14,'C','7');
 const {ctx}=ctxFor({publicCards:[a,two],knownTheme:true,selected:[three,f1,f2],meldType:'SET'});
 const data=ctx.twelveBloomProjectedPlayerAction();
 ok(data.action==='새 조합 후'&&data.changed===true,'three-card legal build is projected as a new-meld action');
 ok(data.diff.newlyCompleted.includes('season:spring'),'projected new meld reports spring newly completed');
}

{
 const a=card(20,'C','A'),two=card(21,'D','2'),three=card(22,'H','3');
 const target={side:'player',index:0};
 const {ctx}=ctxFor({publicCards:[a,two],knownTheme:true,selected:[three],target,canAttach:true});
 const data=ctx.twelveBloomProjectedPlayerAction();
 ok(data.action==='붙이기 후'&&data.diff.newlyCompleted.includes('season:spring'),'legal attach preview can report a newly completed season');
}

{
 const a=card(30,'C','A'),two=card(31,'D','2'),three=card(32,'S','3');
 const publicCards=[a,two,three];
 const recovery={card:three,side:'player',meld:{type:'RUN'}};
 const {ctx}=ctxFor({publicCards,knownTheme:true,recovery});
 const data=ctx.twelveBloomProjectedPlayerAction();
 ok(data.action==='회수 후'&&data.diff.broken.includes('season:spring'),'recovery preview reports a match that would be broken');
}

{
 const a=card(40,'C','A'),two=card(41,'D','2'),f1=card(42,'H','5'),f2=card(43,'S','7');
 const selected=[two,f1,f2];
 const {ctx}=ctxFor({publicCards:[a],knownTheme:true,selected,meldType:'RUN'});
 const data=ctx.twelveBloomProjectedPlayerAction();
 const near=data.near.find(x=>x.key==='season:spring');
 ok(near?.progress==='2/3'&&near?.missing==='3월 필요','affected near-match preview shows 2/3 and the one missing month');
}

{
 const ha=card(50,'H','A'),h2=card(51,'H','2'),h3=card(52,'H','3');
 const {ctx}=ctxFor({publicCards:[ha,h2],knownTheme:true,selected:[h3],target:{side:'player',index:0},canAttach:true});
 const data=ctx.twelveBloomProjectedPlayerAction();
 ok(data.diff.newlyCompleted.includes('picture:redRibbon'),'exact picture completion is projected from printed slots');
}

{
 const ha=card(60,'H','A'),h2=card(61,'H','2'),f1=card(62,'S','5'),f2=card(63,'C','7');
 const {ctx}=ctxFor({publicCards:[ha],knownTheme:true,selected:[h2,f1,f2],meldType:'SET'});
 const near=ctx.twelveBloomProjectedPlayerAction().near.find(x=>x.key==='picture:redRibbon');
 ok(near?.progress==='2/3'&&near?.missing==='3♥ 필요','exact picture near-match names the missing printed slot');
}


{
 const longRun=Array.from({length:10},(_,i)=>card(100+i,'C',i===0?'A':String(i+1)));
 const {ctx}=ctxFor({publicCards:longRun,knownTheme:true});
 const snap=ctx.twelveBloomMatchSnapshot('player');
 const complete=[...Object.values(snap.seasons),...Object.values(snap.pictures)].filter(x=>x.complete);
 ok(complete.length<=9,'long RUN snapshot remains match-aggregated instead of creating per-card UI rows');
 ok(html.includes('.meldCardRow{gap:4px;overflow-x:auto;overflow-y:hidden'),'long public RUN keeps local horizontal scrolling');
 ok(html.includes('.twelveBloomPreviewChips{display:flex;gap:4px;flex-wrap:wrap}'),'TWELVE-BLOOM preview chips wrap independently of long RUN width');
 const affected=ctx.twelveBloomAffectedMatchKeys(snap,snap);
 ok(affected.length===0,'unchanged long RUN produces no redundant preview-change chips');
}

console.log('TWELVE-BLOOM contextual preview regression passed.');
