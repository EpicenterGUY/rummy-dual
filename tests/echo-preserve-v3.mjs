import assert from 'node:assert/strict';
import {fresh,named,plain,meld,nextTurn} from './helpers/v3-fixture.mjs';

function enduranceRun(g,actor='player'){
 const cards=['3','4','5','6','7','8','9','10','J','Q','K'].map(r=>r==='3'?named(g,'C3',actor):r==='8'?named(g,'H8',actor):r==='K'?named(g,'VSCK',actor):plain(g,'C',r,actor));
 const m=meld(g,actor,cards,'RUN',{chain:4});assert.ok(g.runValid(m.cards));return{m,gear:cards[5],source:cards.at(-1)};
}
for(const sealed of [false,true]){
 const g=fresh(),{m,gear}=enduranceRun(g);gear.originOwner='enemy';g.applyOfficialStatus('card',gear,'comeback',1,{silent:true});let retires=0,recoveries=0;
 g.subscribeEffectEvent(p=>{if(p.event==='onRetire')retires++;if(p.event==='onRecover')recoveries++});
 assert.equal(g.finishRun('player',0),'choice');assert.ok(g.state.player.melds.includes(m));assert.equal(retires,0);
 const q=g.state.pendingEffectChoice,option=q.options.find(o=>o.card===gear);assert.ok(!q.allowSkip);assert.equal(g.resolveEffectChoice('__skip__'),false);
 g.resolveEffectChoice(option.key);assert.equal(retires,1);assert.equal(recoveries,0);assert.ok(g.state.player.hand.includes(gear));assert.equal(gear.owner,'player');assert.equal(gear.officialStatus.comeback,1,'explicit preservation precedes comeback to origin owner');
 assert.equal(gear.echoOnNextPlacement,true);assert.equal(gear.officialStatus.echo,0);assert.equal(gear.blockedUntilTurn,g.state.turnNo);assert.equal(g.state.switchPower,20);
 assert.match(g.cardHTML(gear),/다음 배치 잔향/);g.renderDetail(gear);assert.match(g.document.getElementById('detail').innerHTML,/보존 예약.*다음 성공한 공개 배치/);
 q.onChoose(option);assert.equal(retires,1);assert.equal(g.state.player.hand.filter(c=>c===gear).length,1);
 const next=[gear,plain(g,'S','8'),plain(g,'D','8')];g.state.player.hand.push(...next.slice(1));assert.equal(g.submitNewMeld('player',next),false);assert.equal(gear.echoOnNextPlacement,true);
 nextTurn(g);assert.equal(g.submitNewMeld('player',[gear,next[1],plain(g,'D','7')]),false);assert.equal(gear.echoOnNextPlacement,true,'failed placement never consumes the reservation');
 if(sealed)g.applyOfficialStatus('card',gear,'seal',1,{silent:true});
 assert.equal(g.submitNewMeld('player',next),true);assert.equal(gear.echoOnNextPlacement,false);assert.equal(gear.officialStatus.echo,sealed?1:0);assert.equal(g.state.player.shield,sealed?0:48);
}
// The reservation cannot be spent by an earlier hand reaction; it belongs to this physical card.
{
 const g=fresh(),{m,source}=enduranceRun(g),heart=named(g,'HA');m.cards[0]=heart;heart.echoOnNextPlacement=true;g.state.player.melds=[];g.state.player.hand=[heart];
 const a=g.createNumericEffectAction('player');g.runEffectAction('addShield',{actor:'player',source:heart,action:a},{amount:4});
 assert.equal(g.state.player.shield,16);assert.equal(heart.echoOnNextPlacement,true);assert.equal(heart.officialStatus.echo,0);
 const unrelated=[plain(g,'S','3'),plain(g,'D','3'),plain(g,'C','3')];g.state.player.hand.push(...unrelated);assert.equal(g.submitNewMeld('player',unrelated),true);assert.equal(heart.echoOnNextPlacement,true);
 assert.equal(source.echoOnNextPlacement,false);
}
// Activation also precedes the named effect on a successful attachment and does not stack echo.
{
 const g=fresh(),gear=named(g,'H8');gear.echoOnNextPlacement=true;g.applyOfficialStatus('card',gear,'echo',1,{silent:true});g.state.player.hand.push(gear);
 const m=meld(g,'enemy',['S','D','C'].map(s=>plain(g,s,'8','enemy')),'SET');
 assert.equal(g.attachCards('player',[gear],'enemy',0),true);assert.equal(g.state.player.shield,48);assert.equal(gear.echoOnNextPlacement,false);assert.equal(gear.officialStatus.echo,0);assert.ok(g.state.player.spent.includes(gear));assert.equal(g.state.enemy.melds.length,0);
}
for(const failure of ['chain','silence','foreign','stale','moved-target']){
 const g=fresh(),{m,gear,source}=enduranceRun(g);
 if(failure==='chain')m.chain=3;
 if(failure==='silence')g.applyOfficialStatus('card',source,'silence',1,{actor:'player',silent:true});
 if(failure==='foreign')source.owner='enemy';
 const result=g.finishRun('player',0);
 if(['stale','moved-target'].includes(failure)){
  assert.equal(result,'choice');const q=g.state.pendingEffectChoice,o=q.options.find(o=>o.card===gear);
  if(failure==='stale')g.state.turnToken++;else gear.owner='enemy';g.resolveEffectChoice(o.key);assert.ok(g.state.player.melds.includes(m));
 }else if(failure==='chain')assert.equal(result,false);else{assert.equal(result,true);assert.ok(g.state.player.spent.includes(gear))}
 assert.equal(gear.echoOnNextPlacement,false);
}
{
 const g=fresh();g.state.turn='enemy';const {gear}=enduranceRun(g,'enemy');assert.equal(g.finishRun('enemy',0),true);assert.equal(g.state.pendingEffectChoice,null);assert.ok(g.state.enemy.hand.includes(gear));assert.equal(gear.echoOnNextPlacement,true,'CPU preserves a useful numeric card');
}
// Ordinary cards remain legal preservation targets, and optional Gather All stays independent.
{
 const g=fresh(),{m}=enduranceRun(g),ordinary=m.cards[1];assert.equal(ordinary.named,false);g.finishRun('player',0);g.resolveEffectChoice(String(ordinary.uid));assert.ok(g.state.player.hand.includes(ordinary));assert.equal(ordinary.echoOnNextPlacement,true);
}
{
 const g=fresh(),c=named(g,'VSD4'),m=meld(g,'player',[c,plain(g,'S','4'),plain(g,'H','4')],'SET'),last=plain(g,'C','4');g.state.player.hand.push(last);
 assert.equal(g.attachCards('player',[last],'player',0),'choice');assert.ok(g.state.pendingEffectChoice.allowSkip);g.resolveEffectChoice(String(c.uid));assert.ok(g.state.player.hand.includes(c));assert.equal(c.echoOnNextPlacement,false);
}
for(const end of ['victory','defeat','draw']){
 const g=fresh(),{gear}=enduranceRun(g);g.finishRun('player',0);g.resolveEffectChoice(String(gear.uid));assert.equal(gear.echoOnNextPlacement,true);
 const discarded=plain(g,'D','2');discarded.echoOnNextPlacement=true;g.state.discard.push(discarded);
 if(end==='draw')g.resolveCirculationStalemate();else{g.state[end==='victory'?'enemy':'player'].cores=0;g.checkGameOver()}
 assert.equal(g.state.gameOver,true);assert.equal(gear.echoOnNextPlacement,false);assert.equal(discarded.echoOnNextPlacement,false);
}
console.log('Echo preservation: mandatory one card, physical binding, next placement, silence/seal/failure, ordinary targets and CPU');
