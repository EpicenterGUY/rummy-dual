import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

// Attach bias: target/clash/V-SIGNAL are small contextual bonuses; live ZERO-SIGHT finishers get their actual expected values.
{
 const target={id:'target'},clash={id:'clash'},plain={id:'plain'};
 const state={switchPower:40};
 const ctx=context({state,other:w=>w==='enemy'?'player':'enemy',isZeroSightTarget:(w,m)=>m===target,isPointBlankClash:(w,m)=>m===clash,coreShieldDeficit:()=>10});
 install(ctx,'themeAIAttachBias');
 ok(ctx.themeAIAttachBias('enemy','player',target,[{tag:'zsBallistics'}],10)===14,'AI values own target plus exact Ballistics lethal deficit');
 state.switchPower=50;
 ok(ctx.themeAIAttachBias('enemy','player',target,[{tag:'zsOneShot'}],10)===22,'AI values a ready ONE SHOT as target context + actual +18');
 state.switchPower=49;
 ok(ctx.themeAIAttachBias('enemy','player',target,[{tag:'zsOneShot'}],10)===-2,'AI discounts a premature ONE SHOT because of its self-seal risk');
 ok(ctx.themeAIAttachBias('enemy','player',clash,[{}],10)===4,'AI values re-entering its own POINT-BLANK clash');
 ok(ctx.themeAIAttachBias('enemy','player',plain,[{themeId:'v-signal'}],10)===2,'AI gives a small RAID-style bonus to V-SIGNAL opponent-meld entry');
 ok(ctx.themeAIAttachBias('enemy','enemy',plain,[{themeId:'v-signal'}],10)===0,'V-SIGNAL RAID-style bonus is not applied to own melds');
}

// Recovery bias: free recovery, Encore re-entry, and clash recycling can stack, but ordinary recovery stays neutral.
{
 const clash={id:'clash'},plain={id:'plain'};
 const ctx=context({recoveryAccess:(w,side,m,c)=>({free:!!c.free}),legalRecoveryReturnTargets:(w,c,m)=>c.encore?[{}]:[],isPointBlankClash:(w,m)=>m===clash});
 install(ctx,'themeAIRecoveryBias');
 ok(ctx.themeAIRecoveryBias('enemy','player',plain,{free:true})===5,'AI values a free recovery without inventing extra reward');
 ok(ctx.themeAIRecoveryBias('enemy','player',plain,{themeId:'v-signal',tag:'vEncore',encore:true})===9,'AI values Encore recovery when a legal re-entry destination exists');
 ok(ctx.themeAIRecoveryBias('enemy','player',clash,{free:true,themeId:'v-signal',tag:'vEncore',encore:true})===17,'free + Encore + clash recovery context stacks predictably');
 ok(ctx.themeAIRecoveryBias('enemy','player',plain,{})===0,'ordinary recovery receives no artificial theme bonus');
}

const ext=source('bestExtensionFromHand'),rec=source('bestRecoverAI');
ok(ext.includes("sc+=opponentMeldAttachBias(w,targetSide,m,combined,k)"),'M10 opponent-board scoring remains intact');
ok(ext.includes('const powerGain=sc')&&ext.includes('themeAIAttachBias(w,targetSide,m,cs,powerGain)'),'extension scoring adds theme context only after preserving raw power gain');
ok(ext.indexOf('opponentMeldAttachBias')<ext.indexOf('themeAIAttachBias'),'theme AI bias is additive after the established M10 board-risk layer');
ok(rec.includes('themeAIRecoveryBias(w,targetSide,m,c)'),'recovery planning consumes the shared theme recovery bias');
ok(rec.includes("c.tag==='pbQuickReload'")&&rec.includes('bestNewMeldForTurn(w,hyp)'),'existing Quick Reload and new-meld recovery logic remain present');
ok(road.includes('AI 표적·접전·상대 조합 사용·회수 최소 휴리스틱 추가'),'ROADMAP closes the minimum theme-aware AI item');
ok(themeDoc.includes('AI는 테마 전용 별도 규칙을 만들지 않고 이미 합법인 행동의 점수에만 작은 테마 보정을 더한다'),'canonical design locks additive-only theme AI policy');
console.log('Cross-theme AI heuristic regression passed.');
