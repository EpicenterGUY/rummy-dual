import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const resolve=source('resolveEffects'),submit=source('submitNewMeld'),extReq=source('requestExtortChoice'),meldReq=source('requestOpponentMeldChoice'),extMove=source('moveExtortedCard'),extCandidates=source('extortionCandidates');
ok(resolve.includes("case'extortion':if(ctx.isNew)")&&resolve.includes('requestExtortChoice(w,ctx.meld,resume)'),'Extortion target selection lives inside resumable named-effect resolution');
ok(!submit.includes('autoExtortToNewMeld')&&!html.includes('function autoExtortToNewMeld('),'legacy eager first-candidate Extortion path is removed');
ok(extCandidates.includes('meldFixedActive(om)')&&extCandidates.includes('protectedByConstruction(om,c)')&&extCandidates.includes("meldType(remain)!==om.type")&&extCandidates.includes("meldType(added)!==m.type"),'Extortion only offers legal movable cards that preserve both melds');
ok(extMove.includes('insuranceBlocks(w,foe,om,c)')&&extMove.indexOf('insuranceBlocks(w,foe,om,c)')<extMove.indexOf('om.cards.splice'),'interference protection resolves before the chosen Extortion card moves');
ok(extReq.includes("candidates.length>1")&&extReq.includes('requestEffectChoice')&&!extReq.includes('allowSkip:true'),'human Extortion chooses among multiple legal cards and the mandatory move cannot be skipped');
ok(resolve.includes("case'heldBonus':if(c.age>=1)")&&resolve.includes('requestOpponentMeldChoice'),'charged Sleeper routes its opponent-meld target through shared choice handling');
ok(meldReq.includes("candidates.length>1")&&meldReq.includes('requestEffectChoice')&&meldReq.includes('lockMeldRecovery(m,foe)'),'Sleeper presents multiple opponent melds to the human and fixes the exact chosen meld');
ok(html.includes("'DJ':{n:'강탈자'")&&html.includes("'S9':{n:'잠복자'"),'target-choice cards remain in the live named-card pool');
ok(fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8').includes('Target-choice pass: Extortion'),'roadmap records the target-choice pass');
console.log('M8 named target-choice regression passed.');
