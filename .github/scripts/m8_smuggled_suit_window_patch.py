from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing {label}')
    s=s.replace(old,new,1)

once('fromDiscard:false,smuggledActive:false,enteredMeldToken:null,',
     'fromDiscard:false,smuggledActive:false,smuggledTurnToken:null,enteredMeldToken:null,',
     'card smuggled timing state')
once("c.outlawFreeRecoverAt=null;c.smuggledActive=false;c.age=0;",
     "c.outlawFreeRecoverAt=null;c.smuggledActive=false;c.smuggledTurnToken=null;c.age=0;",
     'full recirculation smuggled reset')
once("function acquireDiscardCard(w,indexFromTop=0){const s=sideObj(w),idx=state.discard.length-1-indexFromTop;if(idx<0)return null;const[c]=state.discard.splice(idx,1),oldOwner=c.owner;c.owner=w;c.contractActive=false;",
     "function acquireDiscardCard(w,indexFromTop=0){const s=sideObj(w),idx=state.discard.length-1-indexFromTop;if(idx<0)return null;const[c]=state.discard.splice(idx,1),oldOwner=c.owner;c.owner=w;c.contractActive=false;if(c.tag==='smuggledSuit'){c.smuggledTurnToken=state.turnToken;c.smuggledActive=false}",
     'discard acquisition timing stamp')
once("const c=s.deck.pop();if(!c)return null;c.fromDiscard=false;c.contractActive=false;c.age=0;s.hand.push(c);",
     "const c=s.deck.pop();if(!c)return null;c.fromDiscard=false;c.contractActive=false;if(c.tag==='smuggledSuit'){c.smuggledTurnToken=null;c.smuggledActive=false}c.age=0;s.hand.push(c);",
     'fresh deck draw smuggled reset')
once("function cardText(c){return c.suit==='J'?'JOKER':`${c.rank}${SUIT_SYMBOL[c.suit]}`}function isJoker(c){return c.suit==='J'}function isSuitFlexible(c){return c.tag==='flexSuit'||c.tag==='smugglerBridge'||(c.tag==='smuggledSuit'&&c.smuggledActive)}",
     "function cardText(c){return c.suit==='J'?'JOKER':`${c.rank}${SUIT_SYMBOL[c.suit]}`}function isJoker(c){return c.suit==='J'}function isSuitFlexible(c){return c.tag==='flexSuit'||c.tag==='smugglerBridge'||(c.tag==='smuggledSuit'&&(c.smuggledActive||c.smuggledTurnToken===state.turnToken))}",
     'Smuggled Goods turn-scoped flexibility')
once("if(c.tag==='discardContract')c.contractActive=true;if(c.tag==='smuggledSuit')c.smuggledActive=true;if(c.tag==='fencePeek')",
     "if(c.tag==='discardContract')c.contractActive=true;if(c.tag==='smuggledSuit'){c.smuggledTurnToken=state.turnToken;c.smuggledActive=false}if(c.tag==='fencePeek')",
     'discard draw Smuggled Goods timing')

# Once legally committed to a RUN during its acquisition turn, preserve that role while it stays in that public RUN.
once("const m={type,cards:[...cards],chain:0,createdTurn:state.turnNo,createdToken:state.turnToken,lastAttachToken:null,extraAttachGrantedToken:null,lastTouchedOwnerStart:s.turnStarts,status:blankMeldStatus()};meldsOf(w).push(m);if(cards.some(c=>c.tag==='extortion'))",
     "const m={type,cards:[...cards],chain:0,createdTurn:state.turnNo,createdToken:state.turnToken,lastAttachToken:null,extraAttachGrantedToken:null,lastTouchedOwnerStart:s.turnStarts,status:blankMeldStatus()};meldsOf(w).push(m);if(type==='RUN')for(const c of cards)if(c.tag==='smuggledSuit'&&c.smuggledTurnToken===state.turnToken)c.smuggledActive=true;if(cards.some(c=>c.tag==='extortion'))",
     'new RUN locks Smuggled Goods role')
once("m.cards.push(...cards);\n  m.lastAttachToken=state.turnToken;",
     "m.cards.push(...cards);\n  if(type==='RUN')for(const c of cards)if(c.tag==='smuggledSuit'&&c.smuggledTurnToken===state.turnToken)c.smuggledActive=true;\n  m.lastAttachToken=state.turnToken;",
     'RUN attach locks Smuggled Goods role')

# Any ordinary recovery/retirement back out of the meld ends the locked role.
once("s.hand.push(c);s.rummyRecoveryPending=false;if(!freeReason)s.recoveredThisTurn=true;",
     "s.hand.push(c);if(c.tag==='smuggledSuit')c.smuggledActive=false;s.rummyRecoveryPending=false;if(!freeReason)s.recoveredThisTurn=true;",
     'player recovery clears locked role')
once("m.cards.splice(i,1);if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);sideObj(w).hand.push(c);sideObj(w).rummyRecoveryPending=false;",
     "m.cards.splice(i,1);if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);sideObj(w).hand.push(c);if(c.tag==='smuggledSuit')c.smuggledActive=false;sideObj(w).rummyRecoveryPending=false;",
     'free recovery clears locked role')
once("s.hand.push(c);s.rummyRecoveryPending=false;if(!freeReason)s.recoveredThisTurn=true;else{",
     "s.hand.push(c);if(c.tag==='smuggledSuit')c.smuggledActive=false;s.rummyRecoveryPending=false;if(!freeReason)s.recoveredThisTurn=true;else{",
     'AI recovery clears locked role')
once("else sideObj(c.owner).spent.push(c)}log(`${owner==='player'?'내':'상대'} ${m.type} 정리",
     "else{if(c.tag==='smuggledSuit')c.smuggledActive=false;sideObj(c.owner).spent.push(c)}}log(`${owner==='player'?'내':'상대'} ${m.type} 정리",
     'meld retirement clears locked role')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
anchor='- [x] Fix Golden Hand source check so any discard-acquired card in the same meld action can enable its cycle, not only Golden Hand itself\n'
line='- [x] Fix Smuggled Goods duration: free-suit legality lasts only for the discard-acquisition turn in hand, while a role legally committed to a RUN stays valid until that card leaves the meld\n'
if line not in r:
    if anchor not in r: raise SystemExit('missing M8 Smuggled Goods roadmap anchor')
    r=r.replace(anchor,anchor+line,1)
road.write_text(r,encoding='utf-8')

t=Path('tests/named-smuggled-suit-window.mjs')
t.write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;if(body<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const state={turnToken:7};const ctx=vm.createContext({state});vm.runInContext(source('isSuitFlexible'),ctx);
let c={tag:'smuggledSuit',smuggledActive:false,smuggledTurnToken:7};
ok(ctx.isSuitFlexible(c),'Smuggled Goods is suit-flexible on the turn it is acquired from discard');
state.turnToken=8;ok(!ctx.isSuitFlexible(c),'an unplayed Smuggled Goods loses suit flexibility on the next turn');
c.smuggledActive=true;ok(ctx.isSuitFlexible(c),'a Smuggled Goods already committed to a RUN keeps its locked meld role');
const submit=source('submitNewMeld'),attach=source('attachCards'),recover=source('playerRecover'),free=source('freeRecoverFromMeld'),retire=source('retireMeld');
ok(submit.includes("if(type==='RUN')for(const c of cards)if(c.tag==='smuggledSuit'&&c.smuggledTurnToken===state.turnToken)c.smuggledActive=true"),'new RUN locks the current-turn Smuggled Goods role');
ok(attach.includes("if(type==='RUN')for(const c of cards)if(c.tag==='smuggledSuit'&&c.smuggledTurnToken===state.turnToken)c.smuggledActive=true"),'RUN attachment locks the current-turn Smuggled Goods role');
ok(recover.includes("if(c.tag==='smuggledSuit')c.smuggledActive=false")&&free.includes("if(c.tag==='smuggledSuit')c.smuggledActive=false")&&retire.includes("if(c.tag==='smuggledSuit')c.smuggledActive=false"),'leaving the public meld clears the locked Smuggled Goods role');
ok(html.includes("c.smuggledTurnToken=state.turnToken;c.smuggledActive=false"),'discard acquisition stamps the current-turn permission instead of permanent flexibility');
console.log('M8 Smuggled Goods timing regression passed.');
''',encoding='utf-8')
