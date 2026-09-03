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
const wave3=[
 ['SSD5','D5','표준 규격','ssStandardSpec'],
 ['SSC4','C4','임시 용접','ssTempWeld'],
 ['SSH2','H2','자석 회수기','ssMagnetRetriever'],
 ['SSS10','S10','과열 부품','ssOverheatedPart']
];
for(const [id,slot,name,tag] of wave3){
 ok(script.includes(`'${id}':{slot:'${slot}',themeId:'scrap-shift',n:'${name}',t:'${tag}'`),`${name} is defined in SCRAP-SHIFT wave3`);
 ok(source('resolveEffects').includes(`case'${tag}'`),`${tag} has a live resolver branch`);
}
ok(script.includes("themeId:'scrap-shift',live:false"),'wave3 remains DEV-only and does not prematurely release SCRAP-SHIFT');

{
 const old={uid:1,owner:'enemy',name:'묵은 카드',age:7};
 const fresh={uid:2,owner:'enemy',name:'새 카드',age:0};
 const side={hand:[old],deck:[fresh]};let draws=0,bottomed=null;
 const state={turn:'enemy',turnToken:21};
 const ctx=context({state,sideObj:()=>side,drawOne:()=>{draws++;side.hand.push(fresh);return fresh},scrapShiftCardTurnLocked:()=>false,bottomSpecificHandCard:(w,c)=>{bottomed=c;side.hand=side.hand.filter(x=>x!==c);side.deck.unshift(c);return true},cardText:c=>c.name});
 install(ctx,'requestScrapShiftDrawBottom');
 ok(ctx.requestScrapShiftDrawBottom('enemy',{name:'표준 규격'})===false,'standard spec resolves synchronously for AI');
 ok(draws===1&&bottomed===old,'standard spec draws one then bottoms the oldest eligible hand card');
}

{
 const a={uid:10,owner:'enemy',name:'A'},b={uid:11,owner:'enemy',name:'B'},part={uid:12,owner:'enemy',name:'부품',scrapShiftPart:true};
 const meld={type:'RUN',cards:[a,b,part]};let protection=null;
 const state={turn:'enemy'};
 const ctx=context({state,applyOfficialStatus:(scope,target,key,n)=>{protection={scope,target,key,n}},log:()=>{},cardText:c=>c.name});
 install(ctx,'scrapShiftProtectCandidates','requestScrapShiftProtectChoice');
 ok(ctx.scrapShiftProtectCandidates('enemy',meld).length===3,'temporary weld only offers owned cards from its run');
 ctx.requestScrapShiftProtectChoice('enemy',{name:'임시 용접'},meld);
 ok(protection?.scope==='card'&&protection?.target===a&&protection?.key==='protect'&&protection?.n===1,'temporary weld applies protect 1 to one owned run card');
}

{
 const part={uid:20,owner:'enemy',name:'회수 부품',scrapShiftPart:true,enteredMeldToken:null};
 const x={uid:21,owner:'enemy'},y={uid:22,owner:'enemy'},z={uid:23,owner:'enemy'};
 const meld={type:'RUN',cards:[x,y,z,part],chain:2};
 const enemy={melds:[meld],hand:[]},player={melds:[],hand:[]};
 const state={turn:'enemy',turnToken:31};let recovered=null;
 const ctx=context({state,other:w=>w==='enemy'?'player':'enemy',meldsOf:w=>w==='enemy'?enemy.melds:player.melds,freeRecoverCandidates:()=>[part],isScrapShiftPart:(c,o)=>!!c?.scrapShiftPart&&(!o||c.owner===o),recoverSpecificFromMeld:(w,m,c,opts)=>{recovered={w,m,c,opts};return c},cardText:c=>c.name});
 install(ctx,'scrapShiftRecoverCandidates','requestScrapShiftRecoverChoice');
 const list=ctx.scrapShiftRecoverCandidates('enemy');
 ok(list.length===1&&list[0].card===part,'magnet retriever finds an owned part that is legally recoverable');
 ctx.requestScrapShiftRecoverChoice('enemy',{name:'자석 회수기'});
 ok(recovered?.c===part&&recovered?.opts?.label.includes('자석 회수기'),'magnet retriever routes the part through shared free recovery');
}

{
 const part={uid:30,owner:'enemy',scrapShiftPart:true},otherCard={uid:31,owner:'enemy'};
 const meld={type:'SET',cards:[part,otherCard]};let status=null;
 const ctx=context({isScrapShiftPart:(c,o)=>!!c?.scrapShiftPart&&(!o||c.owner===o),other:w=>w==='enemy'?'player':'enemy',sideObj:w=>({side:w}),applyOfficialStatus:(scope,target,key,n,opts)=>{status={scope,target,key,n,opts}},log:()=>{}});
 install(ctx,'scrapShiftMeldHasOwnedPart','applyScrapShiftOverheat');
 ok(ctx.applyScrapShiftOverheat('enemy',meld,{name:'과열 부품'})===true,'overheated part activates when the returning meld contains an owned part');
 ok(status?.scope==='player'&&status?.key==='vulnerable'&&status?.n===1&&status?.opts?.actor==='enemy','overheated part gives vulnerable 1 to the opponent');
 status=null;
 ok(ctx.applyScrapShiftOverheat('enemy',{type:'SET',cards:[{uid:32,owner:'enemy'}]},{name:'과열 부품'})===false&&status===null,'overheated part does nothing without an owned part');
}

const resolver=source('resolveEffects');
ok(resolver.includes("case'ssStandardSpec':if(type==='SET'")&&resolver.includes('isScrapShiftPart(c,w)'),'standard spec is gated by SET entry while the source card is a part');
ok(resolver.includes("case'ssTempWeld':if(ctx.isAttach&&type==='RUN'")&&resolver.includes('scrapShiftMeldHasOwnedPart(w,ctx.meld)'),'temporary weld requires attaching to a run containing an owned part');
ok(resolver.includes("case'ssMagnetRetriever':")&&resolver.includes('requestScrapShiftRecoverChoice'),'magnet retriever uses the shared recovery helper');
ok(resolver.includes("case'ssOverheatedPart':if(isReturning&&ctx.meld)"),'overheated part only checks on SWITCH-return resolution');
ok(road.includes('3차 유틸리티 슬라이스 4장 — 5♦ 표준 규격 / 4♣ 임시 용접 / 2♥ 자석 회수기 / 10♠ 과열 부품'),'ROADMAP records SCRAP-SHIFT wave3');
ok(themeDoc.includes('3차 유틸리티 슬라이스 — 5♦ `표준 규격` / 4♣ `임시 용접` / 2♥ `자석 회수기` / 10♠ `과열 부품`'),'canonical theme doc records wave3');
ok(poolDoc.includes('24장 미라이브 · 12장 DEV 구현 완료(행동 4 + 반응 4 + 유틸리티 4)'),'full-pool policy records twelve DEV cards while keeping the theme non-live');
ok(road.includes('- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현'),'full 24-card implementation remains open');
console.log('SCRAP-SHIFT wave3 utility regression passed.');
