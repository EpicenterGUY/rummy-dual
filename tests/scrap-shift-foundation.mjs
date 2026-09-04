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

ok(script.includes("'scrap-shift':Object.freeze({id:'scrap-shift',name:'SCRAP-SHIFT',displayName:'SCRAP-SHIFT',concept:'부품 · 해체 · 이식 · 재조립',live:true})"),'SCRAP-SHIFT exists in the live theme registry');
for(const event of ['onPartSet','onDismantle','onReassemble'])ok(script.includes(`'${event}'`),`${event} is a shared effect event`);
ok(script.includes("dismantle:Object.freeze(['onDismantle','onTargetMeldChange','onClashMeldChange'])"),'dismantle reaction order is explicitly locked');
ok(source('makeCard').includes('scrapShiftPart:false')&&source('makeCard').includes('scrapShiftReassembledToken:null'),'new cards initialize part and reassembly state');
ok(script.includes('class=\"scrapPartMark\">부품</div>')&&html.includes('.scrapPartMark{'),'part state has a physical card marker independent of theme identity');

{
 const events=[];const card={uid:1,owner:'player',name:'일반 카드',scrapShiftPart:false};
 const player={hand:[card],spent:[],deck:[],melds:[]},enemy={hand:[],spent:[],deck:[],melds:[]};
 const state={turnToken:10,turnNo:4,discard:[],player,enemy};
 const ctx=context({state,sideObj:w=>w==='player'?player:enemy,other:w=>w==='player'?'enemy':'player',meldsOf:w=>(w==='player'?player:enemy).melds,emitEffectEvent:(event,p)=>{events.push([event,p]);return p},log:()=>{},cardText:c=>String(c.uid)});
 install(ctx,'isScrapShiftPart','scrapShiftPartZone','setScrapShiftPart');
 ok(ctx.setScrapShiftPart('player',card,{silent:true})===true&&card.scrapShiftPart===true,'ordinary/non-theme owned hand card can become a part');
 ok(events.length===1&&events[0][0]==='onPartSet'&&events[0][1].zone==='hand','first part assignment emits exactly one onPartSet event');
 ok(ctx.setScrapShiftPart('player',card,{silent:true})===true&&events.length===1,'reassigning the same part is non-stacking and does not re-emit');
 player.hand=[];player.spent=[card];card.scrapShiftPart=false;
 ok(ctx.setScrapShiftPart('player',card,{silent:true})===false&&card.scrapShiftPart===false,'spent card cannot be newly designated as a part');
}

{
 const order=[];const part={uid:4,owner:'player',name:'부품',scrapShiftPart:true},a={uid:1,owner:'player'},b={uid:2,owner:'player'},c={uid:3,owner:'player'};
 const meld={type:'RUN',cards:[a,b,c,part],chain:3};
 const player={hand:[],spent:[],deck:[],melds:[meld]},enemy={hand:[],spent:[],deck:[],melds:[]};
 const state={turnToken:20,turnNo:7,discard:[],player,enemy};
 const ctx=context({state,sideObj:w=>w==='player'?player:enemy,other:w=>w==='player'?'enemy':'player',meldsOf:w=>(w==='player'?player:enemy).melds,meldOwnerSide:m=>player.melds.includes(m)?'player':enemy.melds.includes(m)?'enemy':null,meldType:cards=>cards.length>=3?'RUN':null,meldFixedActive:()=>false,cardFixedActive:()=>false,isScrapShiftPart:(x,o=null)=>!!x?.scrapShiftPart&&(!o||x.owner===o),clearCardActiveRank:()=>{},clearMailRouteCard:()=>{},markSetCompletion:()=>{},zeroSightTargetActors:()=>['player'],emitEffectEvent:(event,p)=>{order.push(event);return p},emitZeroSightTargetChange:()=>order.push('target'),refreshPointBlankClashMeld:()=>order.push('clash'),log:()=>{},cardText:x=>String(x.uid)});
 install(ctx,'scrapShiftDismantleAccess','dismantleScrapShiftPart');
 const out=ctx.dismantleScrapShiftPart('player',meld,part,{silent:true});
 ok(!!out&&player.spent[0]===part&&part.scrapShiftPart===true,'dismantle moves owned part from a legal meld to own spent while preserving part mark');
 ok(meld.cards.length===3&&meld.chain===2,'dismantling from RUN preserves a legal meld and lowers chain by one');
 ok(order.join('>')==='onDismantle>target>clash','dismantle resolves derived part event before target and clash refresh');
 const tiny={type:'RUN',cards:[a,b,part],chain:1};player.melds=[tiny];player.spent=[];
 ok(ctx.scrapShiftDismantleAccess('player',tiny,part).allowed===false,'dismantle cannot invalidate a 3-card source meld');
}

{
 const events=[];const part={uid:9,owner:'player',name:'재조립 대상',scrapShiftPart:true,scrapShiftPartSetToken:2,scrapShiftReassembledToken:null,blockedUntilTurn:null};
 const player={hand:[],spent:[part],deck:[],melds:[]},enemy={hand:[],spent:[],deck:[],melds:[]};
 const state={turnToken:30,turnNo:11,discard:[],player,enemy};
 const ctx=context({state,sideObj:w=>w==='player'?player:enemy,isScrapShiftPart:(x,o=null)=>!!x?.scrapShiftPart&&(!o||x.owner===o),enterHand:(w,x)=>(w==='player'?player:enemy).hand.push(x),emitEffectEvent:(event,p)=>{events.push(event);return p},log:()=>{},cardText:x=>String(x.uid)});
 install(ctx,'clearScrapShiftPart','reassembleScrapShiftPart','scrapShiftCardTurnLocked');
 const out=ctx.reassembleScrapShiftPart('player',part,{silent:true});
 ok(!!out&&player.spent.length===0&&player.hand[0]===part,'reassembly moves an owned spent part to hand');
 ok(part.scrapShiftPart===false&&part.blockedUntilTurn===11&&part.scrapShiftReassembledToken===30,'reassembly consumes part mark and applies current-turn lock');
 ok(ctx.scrapShiftCardTurnLocked(part)===true&&events[0]==='onReassemble','reassembled card exposes shared lock and onReassemble event');
 state.turnToken=31;ok(ctx.scrapShiftCardTurnLocked(part)===false,'reassembly token lock expires on the next action turn token');
}

for(const [fn,needle,label] of [
 ['pushDiscard',"clearScrapShiftPart(c,'공용 버림패',true)",'public discard clears part'],
 ['recycleIfNeeded',"clearScrapShiftPart(c,'개인 덱 재순환',true)",'spent/discard recycle into personal deck clears part'],
 ['fullRecirculation',"clearScrapShiftPart(c,'전체 재순환',true)",'full recirculation clears part'],
 ['bottomSpecificHandCard',"clearScrapShiftPart(chosen,'덱 아래',true)",'bottoming a hand card clears part'],
 ['performMaintenance',"clearScrapShiftPart(c,'정비·개인 덱',true)",'maintenance deck entry clears part'],
 ['acquireDiscardCard',"clearScrapShiftPart(c,'공용 버림패 획득',true)",'discard acquisition defensively clears stale part'],
 ['drawOne',"clearScrapShiftPart(c,'개인 덱 획득',true)",'deck draw defensively clears stale part']
]) ok(source(fn).includes(needle),label);

ok(source('performMaintenance').includes('scrapShiftCardTurnLocked'),'maintenance rejects same-turn reassembled cards');
ok(source('playerDiscard').includes('재조립한 카드는 이번 턴 버릴 수 없습니다.'),'player cannot voluntarily discard a same-turn reassembled card');
ok(source('chooseAIDiscard').includes('scrapShiftCardTurnLocked')&&source('chooseAIMaintenanceCards').includes('scrapShiftCardTurnLocked'),'AI discard/maintenance respects reassembly lock');
ok(!/scrap(?:Point|Count|Resource|Gauge)|고철 (?:포인트|점수)/i.test(source('setScrapShiftPart')+source('dismantleScrapShiftPart')+source('reassembleScrapShiftPart')),'foundation introduces no numeric scrap resource');

ok(road.includes('## M8SS — SCRAP-SHIFT 24/24 풀 카드군 · 완료'),'ROADMAP tracks SCRAP-SHIFT as a completed live theme');
ok(road.includes('- [x] 24장 / 수트별 6장 정의 및 실제 효과 구현')&&road.includes('- [ ] 해금·도감·자동 테마 빌드·체험전 연결 후 일반 보상 승격'),'24-card effects are complete while live release integration remains explicitly unfinished');
ok(themeDoc.includes('공용 엔진 기반 구현을 시작했지만, 24장 카드는 아직 라이브 카드군이 아니다'),'canonical theme doc distinguishes foundation from live card pool');
ok(themeDoc.includes('`onDismantle → 표적 변화 → 접전 변화`'),'canonical cross-theme order includes dismantle');
ok(poolDoc.includes('24/24 라이브 구현 완료'),'full-pool policy records the completed live SCRAP-SHIFT pool');
ok(poolDoc.includes('28/28 라이브 구현 완료'),'full-pool policy no longer calls completed MAIL-ROUTE non-live');

console.log('SCRAP-SHIFT engine foundation regression passed.');
