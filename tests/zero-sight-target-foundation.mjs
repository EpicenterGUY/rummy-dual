import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const theme=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function ctx(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}
function install(c,...names){for(const n of names)vm.runInContext(source(n),c)}

ok(script.includes('function ensureMeldThemeMeta'),'target metadata helper exists');
ok(script.includes('function setZeroSightTarget'),'target setter exists');
ok(script.includes('function clearZeroSightTarget'),'target clear helper exists');
ok(script.includes('zeroSightTag'),'target has a public-board visual marker');

{
 const a={type:'SET',cards:[1,2,3]},b={type:'RUN',cards:[1,2,3]},c={type:'SET',cards:[1,2,3]};
 const player={melds:[a,b]},enemy={melds:[c]};
 const state={turnNo:5,player,enemy};
 const box=ctx({state,log:()=>{}});
 box.meldsOf=w=>w==='player'?player.melds:enemy.melds;
 install(box,'ensureMeldThemeMeta','isZeroSightTarget','zeroSightTargetMeld','clearZeroSightTarget','setZeroSightTarget');
 ok(box.setZeroSightTarget('player',a,{silent:true})===true,'player can designate a public meld');
 ok(box.isZeroSightTarget('player',a),'designated meld is marked for player');
 ok(box.setZeroSightTarget('player',c,{silent:true})===true,'player can move target across board sides');
 ok(!box.isZeroSightTarget('player',a)&&box.isZeroSightTarget('player',c),'new target clears only player previous target');
 ok(box.setZeroSightTarget('enemy',c,{silent:true})===true,'enemy can independently target same public meld');
 ok(box.isZeroSightTarget('player',c)&&box.isZeroSightTarget('enemy',c),'both sides can independently mark one meld');
 ok(box.setZeroSightTarget('enemy',b,{silent:true})===true,'enemy can move only its own target');
 ok(box.isZeroSightTarget('player',c)&&!box.isZeroSightTarget('enemy',c)&&box.isZeroSightTarget('enemy',b),'enemy retarget does not erase player target');
 ok(box.clearZeroSightTarget('player',{silent:true})===1&&!box.isZeroSightTarget('player',c),'clear removes exactly actor-owned target');
}

{
 const m={type:'SET',cards:[{uid:1,owner:'player',tag:null}],themeMeta:{zeroSight:{targetedBy:{player:true,enemy:true},targetedTurn:{player:3,enemy:4}}}};
 const player={melds:[m],hand:[],deck:[],spent:[]},enemy={melds:[],hand:[],deck:[],spent:[]};
 const state={turnNo:6,turnToken:60,player,enemy};
 const seen=[];
 const box=ctx({state,log:()=>{},cardText:()=>'',emitEffectEvent:(e,p)=>seen.push({e,targetedBy:{...p.themeMeta.zeroSight.targetedBy}})});
 box.meldsOf=w=>w==='player'?player.melds:enemy.melds; box.sideObj=w=>w==='player'?player:enemy;
 install(box,'retireMeld');
 box.retireMeld('player',0,'표적 정리');
 ok(seen.length===1&&seen[0].e==='onRetire','retire still emits onRetire');
 ok(seen[0].targetedBy.player===true&&seen[0].targetedBy.enemy===true,'onRetire observes target ownership before removal');
 ok(m.themeMeta.zeroSight.targetedBy.player===false&&m.themeMeta.zeroSight.targetedBy.enemy===false,'removed meld target metadata is cleared after retirement');
 ok(player.melds.length===0,'targeted meld physically retires normally');
}

const submit=source('submitNewMeld');
ok(submit.includes('themeMeta:{zeroSight:{targetedBy:{player:false,enemy:false}'),'new melds initialize target metadata');
const render=source('renderMelds');
ok(render.includes("isZeroSightTarget('player',m)")&&render.includes("isZeroSightTarget('enemy',m)"),'UI renders each side target independently');
ok(!source('meldType').includes('zeroSight')&&!source('setValid').includes('zeroSight')&&!source('runValid').includes('zeroSight'),'target metadata does not restrict normal SET/RUN legality');
ok(road.includes('- [x] 공개 조합 단위 표적 메타데이터 및 1개 제한 구현'),'ROADMAP marks target metadata complete');
ok(theme.includes('- [x] 공개 조합 단위 `표적` 메타데이터 설계')&&theme.includes('- [x] 표적 1개 제한 / 이전 / 조합 정리 시 해제 처리'),'canonical theme doc locks target lifecycle');
console.log('ZERO-SIGHT target foundation regression passed.');
