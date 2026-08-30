import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const roadmap=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(c,m){if(!c)throw new Error(m);console.log(`PASS: ${m}`)}
new Function(script);
ok(script.includes("id:'rummy'")&&script.includes("scenario:'rummy'")&&script.includes("expectReload:6")&&script.includes("completeOn:'rummy'")&&script.includes("completeOn:'rummy',stopAfter:true"),'RUMMY lesson is deterministic, requires six-card reload, and remains the basic segment endpoint');
ok(script.includes("makeTutorialCard('S','K','rummyLast')")&&script.includes("p.deck=[makeTutorialCard('C','2','rummyReload')"),'RUMMY scenario has one last card and a fixed six-card deck');
ok(script.includes("tutorialCheckProgress('rummy',{beforeHand:beforeReloadHand,reload,afterHand:s.hand.length})"),'real triggerRummy reports actual reload result');
ok(script.includes("if(step.expectReload&&context.afterHand!==step.expectReload)return false"),'tutorial only completes on actual six-card reload');
ok(script.includes("progress.tutorialCompleted=true;saveProgress()"),'final RUMMY lesson persists tutorial completion');
ok(script.includes("tutorialState.textContent=progress.tutorialCompleted?'다시 보기':'시작'"),'completed tutorial becomes replayable in start menu');
ok(script.includes("if(step.stopAfter&&state.tutorialSegmentDone){showStartScreen();return}"),'completed tutorial segment can return to main menu through the shared endpoint contract');
ok(!html.includes('고정 패 실습은 순차 추가 중입니다.'),'start screen no longer says core tutorial is still being added');
ok(roadmap.includes('- [x] 러미 튜토리얼')&&roadmap.includes('- [x] 튜토리얼 완료 상태 저장')&&roadmap.includes('- [x] 튜토리얼 다시 보기'),'roadmap records RUMMY completion and replay state');
console.log('RUMMY//DUEL deterministic RUMMY tutorial regressions passed.');
