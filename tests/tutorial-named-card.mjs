import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}

new Function(script);
ok(script.includes("'H8':{n:'응급 보호구',t:'emergencyGear',d:'조합에 들어갈 때 보호막 20. SWITCH가 나를 향하면 보호막 32.'}"),'Emergency Gear remains the live H8 named variant');
ok(script.includes("{id:'namedCard',title:'네임드 카드'")&&script.includes("expectAttachTag:'emergencyGear'")&&script.includes("expectShieldGain:20"),'advanced tutorial declares a real Emergency Gear named-card step');
ok(script.includes("makeTutorialNamed('H8','namedCard')"),'named-card scenario instantiates the live H8 variant instead of a fake tutorial card');
ok(script.includes("makeTutorialCard('S','8','board','player'),makeTutorialCard('D','8','board','player'),makeTutorialCard('C','8','board','player')"),'named-card scenario uses the ordinary missing-suit 8 SET structure');
ok(script.includes("일반 8♥와 같은 세트 재료")&&script.includes("네임드는 기존 랭크·무늬 슬롯의 조합 역할"),'tutorial copy explains slot identity plus added named effect');
ok(script.includes("고급 튜토리얼 · 회수/정비/상태/조커/네임드"),'start screen advertises named cards as part of the advanced tutorial');

// The exact live effect used by the tutorial: H8 enters a meld while SWITCH is neutral, so it adds 20 shield.
{
 const player={hand:[],shield:0,status:{}},enemy={hand:[],shield:0,status:{}};
 const state={turnToken:7,turnNo:1,switchTarget:'neutral'};
 const ctx=vm.createContext({console,Math,Set,Array,Object,state});
 ctx.sideObj=w=>w==='player'?player:enemy;
 ctx.other=w=>w==='player'?'enemy':'player';
 ctx.consumeOfficialStatus=()=>0;
 ctx.addShield=(w,n)=>{ctx.sideObj(w).shield+=Math.max(0,Math.round(n*4));return Math.max(0,Math.round(n*4))};
 ctx.log=()=>{};
 vm.runInContext(source('resolveEffects'),ctx);
 const card={uid:'tutorial-h8',named:true,name:'응급 보호구',tag:'emergencyGear',suppressEffectToken:null};
 const result=ctx.resolveEffects('player',[card],'SET',{willReturn:true,isAttach:true,targetOwner:'player',meld:{type:'SET',cards:[]},totalLength:4,effectSeen:new Set()});
 ok(result.pending===false&&player.shield===20,'live Emergency Gear resolution grants exactly 20 shield in the tutorial neutral-SWITCH setup');
 state.switchTarget='player';player.shield=0;
 ctx.resolveEffects('player',[{...card,uid:'tutorial-h8-threat'}],'SET',{willReturn:true,isAttach:true,targetOwner:'player',meld:{type:'SET',cards:[]},totalLength:4,effectSeen:new Set()});
 ok(player.shield===32,'the same live named effect still preserves its stronger 32-shield incoming-SWITCH branch');
}

ok(road.includes('- [x] 네임드 카드 설명 — 고급 튜토리얼 마지막에 8♥ `응급 보호구`'),'ROADMAP marks named-card explanation complete with the executable tutorial scenario');
console.log('Named-card tutorial regression passed.');
