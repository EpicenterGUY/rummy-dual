import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run,nextTurn} from './helpers/v3-fixture.mjs';

{
 const g=fresh(),m=run(g,'player','H',[4,5,6]);
 for(const actor of ['player','enemy'])assert.equal(g.applyOfficialStatus('meld',m,'mark',1,{actor}),1);
 assert.equal(g.officialStatusValue('meld',m,'mark'),2);
 assert.equal(g.consumeOfficialStatus('meld',m,'mark'),0,'a mark requires an explicit owner to consume');
 assert.equal(g.consumeMeldMark(m,'player'),1);assert.equal(g.meldMarkValue(m,'enemy'),1);
 g.applyOfficialStatus('meld',m,'mark',1,{actor:'enemy'});assert.equal(g.meldMarkValue(m,'enemy'),1);
 assert.match(g.meldStatusText(m),/상대 표식/);
 g.applyOfficialStatus('meld',m,'protect',1,{silent:true});
 assert.equal(g.applyOfficialStatus('meld',m,'fracture',Infinity,{actor:'enemy'}),0);assert.equal(m.status.protect,1,'invalid status does not spend protection');
 assert.equal(g.applyOfficialStatus('meld',m,'fracture',1,{actor:'enemy'}),0);assert.equal(m.status.protect,0);
 assert.equal(g.applyOfficialStatus('meld',m,'fracture',1,{actor:'enemy'}),1);assert.match(g.meldStatusText(m),/균열/);
 assert.equal(g.applyOfficialStatus('meld',{cards:[]},'fracture',1,{actor:'player'}),0,'detached targets are rejected');
 assert.equal(g.applyOfficialStatus('card',m.cards[0],'mark',1,{actor:'player'}),0,'card marks are not shipped yet');
 const hp=g.state.player.hp;g.retireMeld('player',0);assert.equal(g.state.player.hp,hp);assert.equal(m.status.fracture,0);assert.equal(g.officialStatusValue('meld',m,'mark'),0,'whole retirement drops both marks');
}
// All successful departure routes consume one fracture, after the card has moved.
for(const route of ['basic','free','move','spend']){
 const g=fresh(),m=run(g,'player','H',[4,5,6,7]),c=m.cards.at(-1);
 g.applyOfficialStatus('meld',m,'fracture',1,{actor:'enemy'});
 let seen=0;g.subscribeEffectEvent(p=>{if(p.fractureTriggered){seen++;assert.ok(!m.cards.includes(c)||route==='spend');assert.equal(m.status.fracture,0)}});
 if(route==='basic'){g.state.boardSelected.add(c.uid);g.playerRecover()}
 if(route==='free')assert.equal(g.recoverSpecificFromMeld('player',m,c),c);
 if(route==='move'){const dst=run(g,'enemy','H',[8,9,10]);assert.ok(g.moveCardBetweenMelds('player',c,m,dst));assert.ok(dst.cards.includes(c))}
 if(route==='spend')assert.ok(g.spendPointBlankMeldCard('player',m));
 assert.equal(g.state.player.hp,34,`${route}: exactly six ordinary damage`);assert.equal(seen,1);
 g.emitEffectEvent('onRecover',{actor:'player',meld:m,card:c,targetSide:'player'});assert.equal(g.state.player.hp,34,'the status is already gone');
}
{
 const g=fresh(),m=run(g,'player','H',[4,5,6,7]),c=m.cards.at(-1);g.state.player.hp=2;g.state.player.cores=1;
 g.applyOfficialStatus('meld',m,'fracture',1,{actor:'enemy'});g.recoverSpecificFromMeld('player',m,c);
 assert.equal(g.state.gameOver,true);assert.equal(g.state.player.hand.filter(x=>x.uid===c.uid).length,1);assert.ok(!m.cards.includes(c),'a lethal fracture cannot leave a half-completed recovery');
}
{
 const g=fresh(),c=named(g,'S4'),m=run(g,'enemy','S',[1,2,3].map(r=>r===1?'A':r));
 g.state.lastEnemyUsedDiscard=true;g.state.player.hand.push(c);assert.equal(g.attachCards('player',[c],'enemy',0),true);assert.equal(m.status.fracture,1);assert.equal(g.state.player.hand.length,1,'bait no longer performs a recovery');
}
{
 const g=fresh(),c=named(g,'S7B'),m=run(g,'enemy','S',[4,5,6]);g.state.player.hand.push(c);
 assert.equal(g.attachCards('player',[c],'enemy',0),true);assert.equal(m.status.fracture,1);
 const power=g.state.switchPower;nextTurn(g);assert.equal(g.recoverSpecificFromMeld('player',m,c),c);
 assert.equal(g.state.enemy.hp,34);assert.equal(g.state.player.status.loaded,12);assert.equal(g.state.switchPower,power,'the fuse stores loading instead of adding power immediately');
 assert.equal(g.recoveredCardCanReturn(c,g.state.turnToken),false);
}
for(const owner of ['player','enemy']){
 const g=fresh(),c=named(g,'H4B'),m=meld(g,owner,[c,...[5,6,7].map(r=>plain(g,'H',r,owner))]);
 assert.equal(g.recoverSpecificFromMeld('player',m,c),c);assert.equal(g.state.player.hp,48);assert.equal(g.state.player.status.endure||0,owner==='enemy'?8:0);assert.equal(g.state.player.shield,0);
}
{
 const g=fresh(),c=named(g,'VSDJ'),m=run(g,'player','D',[8,9,10]);g.state.player.hand.push(c);
 g.setOfficialStatus('meld',m,'seal',3);g.applyMeldFixed(m,'player');g.applyOfficialStatus('meld',m,'fracture',1,{actor:'enemy'});
 assert.equal(g.attachCards('player',[c],'player',0),'choice');assert.equal(m.status.seal,3,'own meld seal does not suppress Manager');
 g.resolveEffectChoice('seal');assert.equal(m.status.seal,0);assert.equal(m.status.fracture,1);assert.equal(g.meldFixedActive(m),true,'only the chosen status is removed');
}
{
 const g=fresh(),c=named(g,'VSDJ'),m=run(g,'player','D',[8,9,10]);g.state.player.hand.push(c);g.state.player.status.seal=1;
 assert.equal(g.attachCards('player',[c],'player',0),true);assert.equal(m.status.protect,0,'player seal still suppresses Manager');
}
console.log('Shared board statuses: ownership, protection, all departure paths, lethal atomicity and four common/theme cards passed');
