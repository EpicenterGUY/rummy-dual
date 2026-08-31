from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label,count=1):
    global s
    if s.count(old)<count:
        raise SystemExit(f'missing {label}: {s.count(old)}/{count}')
    s=s.replace(old,new,count)

# Existing regressions intentionally extract individual functions into isolated VMs.
# New hand-prep helpers therefore remain optional dependencies from legacy functions.
rep("for(const c of list)if(s.hand.some(x=>x.uid===c.uid))leaveHandPreparation(w,c);s.hand=s.hand.filter", "for(const c of list)if(s.hand.some(x=>x.uid===c.uid)&&typeof leaveHandPreparation==='function')leaveHandPreparation(w,c);s.hand=s.hand.filter", 'removeFromHand optional prep')
rep("c.fromDiscard=true;c.age=0;enterHand(w,c);return c}", "c.fromDiscard=true;c.age=0;if(typeof enterHand==='function')enterHand(w,c);else s.hand.push(c);return c}", 'acquire fallback')
rep("c.age=0;enterHand(w,c);if(!s.deck.length)", "c.age=0;if(typeof enterHand==='function')enterHand(w,c);else s.hand.push(c);if(!s.deck.length)", 'draw fallback')
rep("enterHand(w,c);if(c.tag==='smuggledSuit')c.smuggledActive=false;", "if(typeof enterHand==='function')enterHand(w,c);else sideObj(w).hand.push(c);if(c.tag==='smuggledSuit')c.smuggledActive=false;", 'free recover fallback')
rep("enterHand(c.owner,c);c.suppressEffectToken=state.turnToken;", "if(typeof enterHand==='function')enterHand(c.owner,c);else sideObj(c.owner).hand.push(c);c.suppressEffectToken=state.turnToken;", 'owned auto return fallback',2)
rep("enterHand(j.owner,j);j.suppressEffectToken=state.turnToken;", "if(typeof enterHand==='function')enterHand(j.owner,j);else sideObj(j.owner).hand.push(j);j.suppressEffectToken=state.turnToken;", 'joker return fallback')
rep("enterHand(home,c);log(`${opts.preserveLabel||'보존'}:", "if(typeof enterHand==='function')enterHand(home,c);else sideObj(home).hand.push(c);log(`${opts.preserveLabel||'보존'}:", 'preserve fallback')
rep("enterHand(home,c);c.flexSuitOffSuit=false;", "if(typeof enterHand==='function')enterHand(home,c);else sideObj(home).hand.push(c);c.flexSuitOffSuit=false;", 'understudy fallback')
rep("[c]=m.cards.splice(plan.ci,1);enterHand('player',c);if(c.tag==='smuggledSuit')", "[c]=m.cards.splice(plan.ci,1);if(typeof enterHand==='function')enterHand('player',c);else s.hand.push(c);if(c.tag==='smuggledSuit')", 'player recover fallback')
rep("const [back]=state.discard.splice(ri,1);back.fromDiscard=false;enterHand(w,back);log", "const [back]=state.discard.splice(ri,1);back.fromDiscard=false;if(typeof enterHand==='function')enterHand(w,back);else s.hand.push(back);log", 'ignored return fallback')
rep("const [ph]=s.spent.splice(pi,1);enterHand(w,ph);ph.phoenixReturned=true;", "const [ph]=s.spent.splice(pi,1);if(typeof enterHand==='function')enterHand(w,ph);else s.hand.push(ph);ph.phoenixReturned=true;", 'phoenix fallback')
rep("[c]=m.cards.splice(plan.ci,1);enterHand(w,c);if(c.tag==='smuggledSuit')", "[c]=m.cards.splice(plan.ci,1);if(typeof enterHand==='function')enterHand(w,c);else s.hand.push(c);if(c.tag==='smuggledSuit')", 'AI recover fallback')
rep("c.smuggledTurnToken=null;c.age=0;resetHandPreparation(c);if(c.flexSuitOffSuit)", "c.smuggledTurnToken=null;c.age=0;if(typeof resetHandPreparation==='function')resetHandPreparation(c);if(c.flexSuitOffSuit)", 'recirculation optional prep')
rep("const prep=c.prepRequired>0?ensureHandPreparation(c):null,prepText=prep?", "const prep=c.prepRequired>0?(typeof ensureHandPreparation==='function'?ensureHandPreparation(c):(c.handPrep||(c.handPrep={turns:0,exitTurns:0,exitTurnToken:null,exitOwner:null}))):null,prepText=prep?", 'render optional prep')

p.write_text(s,encoding='utf-8')
