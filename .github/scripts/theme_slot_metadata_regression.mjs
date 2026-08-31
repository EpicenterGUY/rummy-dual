import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('index.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync('ROADMAP.md','utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function literal(name,next){const a=script.indexOf(`const ${name}=`);if(a<0)throw new Error(`missing ${name}`);const b=script.indexOf(next,a);if(b<0)throw new Error(`missing end ${name}`);return script.slice(a+`const ${name}=`.length,b).trim().replace(/;$/,'')}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}

const ctx=context();
vm.runInContext(`globalThis.NAMED=${literal('NAMED','\nconst CHARACTERS=')};globalThis.THEME_GROUPS=${literal('THEME_GROUPS','\nconst THEME_BUILD_PROFILES=')};globalThis.THEME_BUILD_PROFILES=${literal('THEME_BUILD_PROFILES','\nconst effectEventSubscribers=')};globalThis.RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};${source('namedSlot')}`,ctx);
const named=ctx.NAMED,groups=ctx.THEME_GROUPS,profiles=ctx.THEME_BUILD_PROFILES;
const themeCards=Object.entries(named).filter(([,v])=>v.themeId);
ok(themeCards.length>=9,'live/development theme variants are present at meaningful scale');
for(const[id,c]of themeCards){
  ok(!!groups[c.themeId],`${id} themeId resolves to registered theme metadata`);
  ok(typeof groups[c.themeId].displayName==='string'&&groups[c.themeId].displayName.length>0,`${id} theme has a visible display name`);
  const slot=ctx.namedSlot(id);
  ok(/^[SHDC](A|[2-9]|10|J|Q|K)$/.test(slot),`${id} remains bound to one canonical regular rank+suit slot`);
  ok(slot===(c.slot||id),`${id} theme identity does not rewrite its canonical slot`);
}

// Profiles and card theme IDs use the same stable namespace.
for(const[id,p]of Object.entries(profiles))if(id!=='mixed'&&p.themeId){
  ok(groups[p.themeId]?.id===p.themeId,`${id} build profile resolves through the same stable themeId namespace`);
  ok(p.displayName===groups[p.themeId].displayName,`${id} build profile and card metadata share one display name`);
}

// At least one physical slot has ordinary + theme alternatives, but sampling is still slot-exclusive.
const bySlot=new Map();
for(const[id,c]of Object.entries(named)){if(id[0]==='J')continue;const slot=ctx.namedSlot(id);if(!bySlot.has(slot))bySlot.set(slot,[]);bySlot.get(slot).push(id)}
const shared=[...bySlot.entries()].filter(([,ids])=>ids.length>1&&ids.some(id=>named[id].themeId));
ok(shared.length>=5,'multiple physical slots now contain ordinary/theme alternate identities');
for(const[slot,ids]of shared)ok(new Set(ids.map(id=>ctx.namedSlot(id))).size===1,`${slot} alternatives all collapse to exactly one physical slot key`);

// ZERO-SIGHT and POINT-BLANK meld metadata coexist without touching cards/slot identity.
{
 const state={turnNo:9,turnToken:4};
 const player={melds:[]},enemy={melds:[]};
 const meld={type:'RUN',cards:[{uid:1,slot:'C2',owner:'player'},{uid:2,slot:'C3',owner:'enemy'},{uid:3,slot:'C4',owner:'enemy'}]};enemy.melds.push(meld);
 const c=context({state,log:()=>{},emitEffectEvent:()=>null,sideObj:w=>w==='player'?player:enemy,other:w=>w==='player'?'enemy':'player',meldsOf:w=>w==='player'?player.melds:enemy.melds,meldOwnerSide:m=>enemy.melds.includes(m)?'enemy':'player'});
 for(const n of['ensureMeldThemeMeta','isZeroSightTarget','zeroSightTargetMeld','clearZeroSightTarget','setZeroSightTarget','ensurePointBlankMeta','isPointBlankClash','pointBlankClashMeld','setPointBlankClash'])vm.runInContext(source(n),c);
 ok(c.setZeroSightTarget('player',meld,{silent:true})===true,'ZERO-SIGHT target can be written to shared meld metadata');
 ok(c.setPointBlankClash('player',meld,{silent:true})===true,'POINT-BLANK clash can coexist on the same opponent meld');
 ok(c.isZeroSightTarget('player',meld)&&c.isPointBlankClash('player',meld),'target and clash metadata coexist independently');
 ok(meld.cards[0].slot==='C2'&&meld.cards[0].owner==='player','meld metadata writes do not mutate card slot or ownership identity');
}

ok(road.includes('테마 ID/표시명/전용 조합 메타데이터 ↔ 동일 랭크+무늬 슬롯 불변식 검증'),'ROADMAP closes the theme slot/metadata compatibility gate');
console.log('Theme ID, slot, and meld-metadata invariant regression passed.');
