from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, got {count}")
    return text.replace(old, new, 1)

p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = replace_once(s, '<span class="menuState">PLAY</span>', '<span class="menuState">시작</span>', 'localize battle menu state')
s = replace_once(s, '<span class="menuState">OPEN</span>', '<span class="menuState">열기</span>', 'localize codex menu state')
s = replace_once(s, "const state={sessionMode:'menu',player:null,enemy:null,", "const state={sessionMode:'menu',battleId:0,player:null,enemy:null,", 'add battle session id')
s = replace_once(s, "function newGame(){state.sessionMode='battle';uidSeq=1;", "function newGame(){state.sessionMode='battle';state.battleId++;uidSeq=1;", 'increment battle session id')
s = replace_once(
    s,
    "function endPlayerTurn(){settleContracts('player');turnEnd('player');state.phase='wait';state.turn='enemy';state.player.hand.forEach(c=>c.age++);render();if(!state.gameOver)setTimeout(aiTurn,430)}",
    "function endPlayerTurn(){settleContracts('player');turnEnd('player');state.phase='wait';state.turn='enemy';state.player.hand.forEach(c=>c.age++);render();if(!state.gameOver){const battleId=state.battleId;setTimeout(()=>{if(state.sessionMode==='battle'&&state.battleId===battleId&&!state.gameOver)aiTurn()},430)}}",
    'guard delayed AI turn',
)
s = replace_once(
    s,
    "function checkGameOver(){if(state.gameOver)return;if((state.player?.cores||0)<=0||(state.enemy?.cores||0)<=0){state.gameOver=true;state.phase='over';const win=(state.enemy?.cores||0)<=0;setTimeout(()=>showResult(win),1400)}}",
    "function checkGameOver(){if(state.gameOver)return;if((state.player?.cores||0)<=0||(state.enemy?.cores||0)<=0){state.gameOver=true;state.phase='over';const win=(state.enemy?.cores||0)<=0,battleId=state.battleId;setTimeout(()=>{if(state.sessionMode==='battle'&&state.battleId===battleId&&state.gameOver)showResult(win)},1400)}}",
    'guard delayed result overlay',
)

p.write_text(s, encoding='utf-8')
