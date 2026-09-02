import {makeGame} from './live-game.mjs';

export function fresh(){
 const g=makeGame(),s=g.state;
 Object.assign(s,{turn:'player',phase:'action',turnNo:5,turnToken:10,switchPower:20,switchTarget:'player',discard:[],gameOver:false});
 for(const w of ['player','enemy'])Object.assign(s[w],{status:g.blankStatus(),effectReservations:[],melds:[],spent:[],hand:[plain(g,'H','K',w)],deck:['A','2','3','4','5','6','7','8','9','10','J','Q','K'].map(r=>plain(g,'D',r,w)),shield:0,hp:40,maxHp:60,cores:3,turnStarts:3,newMeldCount:0,returnedSwitchThisTurn:false,recoveredThisTurn:false});
 return g;
}
export function plain(g,suit,rank,owner='player'){return g.makeCard(suit,String(rank),false,owner)}
export function named(g,id,owner='player'){const d=g.NAMED[id],slot=d.slot||id;return g.makeCard(slot[0],slot.slice(1),true,owner,id)}
export function meld(g,owner,cards,type='RUN',extra={}){
 const m={type,cards,chain:0,createdTurn:g.state.turnNo-1,createdToken:g.state.turnToken-1,lastAttachToken:null,status:g.blankMeldStatus(),...extra};
 g.state[owner].melds.push(m);return m;
}
export function run(g,owner,suit,ranks,extra={}){return meld(g,owner,ranks.map(r=>plain(g,suit,r,owner)),'RUN',extra)}
export function nextTurn(g,actor='player'){
 g.state.turn=actor;g.state.turnToken++;g.state.turnNo++;g.state[actor].turnStarts++;g.state[actor].returnedSwitchThisTurn=false;g.state[actor].recoveredThisTurn=false;
}
