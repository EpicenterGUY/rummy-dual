from pathlib import Path

p=Path('index.html')
s=p.read_text()

def rep(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    s=s.replace(old,new,1)

old="function recoverRedundantGapRun(targetSide,m){for(let i=m.cards.length-1;i>=0;i--){const c=m.cards[i];if(c.tag!=='gapRun'||cardFixedActive(c))continue;const remain=m.cards.filter((_,j)=>j!==i);if(remain.length<3||meldType(remain)!==m.type)continue;m.cards.splice(i,1);if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);sideObj(c.owner).hand.push(c);c.suppressEffectToken=state.turnToken;c.recoveredToken=state.turnToken;c.recoverReturnOverrideToken=null;c.age=0;markSetCompletion(m,targetSide);log(`${c.name}: 빠진 실제 카드가 채워져 무료 회수${m.type==='RUN'?' · CHAIN -1':''}.`,'good');return c}return null}"
new="""function simpleGapMissingRank(cards,gapCard){if(!gapCard||gapCard.tag!=='gapRun'||cards.length<3)return null;if(cards.some(c=>isJoker(c)||c.tag==='counterfeiter'||c.tag==='smugglerBridge'||isSuitFlexible(c)||c.suit!==gapCard.suit))return null;const base=cards.map(c=>RANK_VALUE[c.rank]);for(const vals of[base,base.map(v=>v===1?14:v)]){const u=[...new Set(vals)].sort((a,b)=>a-b);if(u.length!==vals.length)continue;let missing=null,bad=false;for(let i=1;i<u.length;i++){const d=u[i]-u[i-1];if(d===2&&missing==null)missing=u[i-1]+1;else if(d!==1){bad=true;break}}if(!bad&&missing!=null)return missing===14?1:missing}return null}
function recoverRedundantGapRun(targetSide,m,beforeCards,newCards){for(let i=m.cards.length-1;i>=0;i--){const c=m.cards[i];if(c.tag!=='gapRun'||cardFixedActive(c))continue;const missing=simpleGapMissingRank(beforeCards,c);if(missing==null||!newCards.some(n=>n.suit===c.suit&&RANK_VALUE[n.rank]===missing))continue;const remain=m.cards.filter((_,j)=>j!==i);if(remain.length<3||meldType(remain)!==m.type)continue;m.cards.splice(i,1);if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);sideObj(c.owner).hand.push(c);c.suppressEffectToken=state.turnToken;c.recoveredToken=state.turnToken;c.recoverReturnOverrideToken=null;c.age=0;markSetCompletion(m,targetSide);log(`${c.name}: 빠진 실제 카드가 채워져 무료 회수${m.type==='RUN'?' · CHAIN -1':''}.`,'good');return c}return null}"""
rep(old,new,'gap helper')

rep("const beforeLen=m.cards.length,beforeChain=m.chain||0,combined=m.cards.concat(cards),type=meldType(combined);",
    "const beforeCards=[...m.cards],beforeLen=m.cards.length,beforeChain=m.chain||0,combined=m.cards.concat(cards),type=meldType(combined);",
    'attach before snapshot')
rep("recoverRedundantGapRun(targetSide,m);middleManagerReturnPlaceholder(targetSide,m,cards);replaceRedundantJokers(targetSide,m,w);",
    "recoverRedundantGapRun(targetSide,m,beforeCards,cards);middleManagerReturnPlaceholder(targetSide,m,cards);replaceRedundantJokers(targetSide,m,w);",
    'gap resolver args')
p.write_text(s)

# Strengthen the M8 audit to lock the exact-fill semantics.
t=Path('tests/named-card-audit.mjs')
a=t.read_text()
old_test="ok(script.includes('function recoverRedundantGapRun('),'Gap Run has an explicit redundant-card recovery resolver');"
new_test="""ok(script.includes('function simpleGapMissingRank('),'Gap Run records the exact simple one-card hole before recovery');
ok(script.includes('function recoverRedundantGapRun('),'Gap Run has an explicit redundant-card recovery resolver');
ok(script.includes('missing==null||!newCards.some(n=>n.suit===c.suit&&RANK_VALUE[n.rank]===missing)'),'Gap Run only auto-recovers when a newly attached card fills the recorded missing rank');"""
if a.count(old_test)!=1:
    raise SystemExit(f'named audit gap assertion: expected 1, got {a.count(old_test)}')
a=a.replace(old_test,new_test,1)
a=a.replace("recoverRedundantGapRun(targetSide,m);middleManagerReturnPlaceholder(targetSide,m,cards);replaceRedundantJokers",
            "recoverRedundantGapRun(targetSide,m,beforeCards,cards);middleManagerReturnPlaceholder(targetSide,m,cards);replaceRedundantJokers")
t.write_text(a)
