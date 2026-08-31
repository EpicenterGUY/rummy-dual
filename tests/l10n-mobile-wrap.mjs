import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}

ok(html.includes('/* L10N · long Korean copy mobile wrap safety */'),'dedicated Korean long-copy wrap safety block exists');
ok(html.includes('.combatBanner{max-width:94%;white-space:normal;text-align:center;line-height:1.25;overflow-wrap:anywhere;word-break:keep-all}'),'combat banners may wrap Korean copy instead of clipping');
ok(/@media\(max-width:390px\)\{[\s\S]*?\.combatBanner\{max-width:calc\(100vw - 28px\);padding:7px 9px;font-size:14px\}/.test(html),'390px combat banner is bounded to the viewport');
ok(html.includes('.effectChoiceTitle,.effectChoiceText,.effectChoiceBtn,.effectChoiceBtn small{min-width:0;white-space:normal;overflow-wrap:anywhere;word-break:keep-all}'),'effect-choice text and actions are flex-shrink/wrap safe');
ok(html.includes('.effectChoiceBtn{align-items:flex-start;flex-wrap:wrap}')&&html.includes('.effectChoiceBtn small{flex:1 1 100%;line-height:1.35}'),'390px effect-choice details can fall onto their own line');
ok(html.includes('.fieldStrip>span{min-width:0}')&&html.includes('.fieldStrip>span:last-child{text-align:right;overflow-wrap:anywhere;word-break:keep-all}')&&html.includes('.fieldStrip>span:last-child{max-width:62%}'),'field name/effect row cannot force horizontal overflow on narrow screens');
ok(html.includes('.phaseText,.initiativeRule,.switchAlert,.practiceCoachText,.startResumeNote{overflow-wrap:anywhere;word-break:keep-all}'),'battle guidance and warning surfaces wrap long Korean phrases');
ok(html.includes('.startMenuBtn>span:first-child{min-width:0}')&&html.includes('.startMenuBtn small{white-space:normal;overflow-wrap:anywhere;word-break:keep-all}'),'start-menu explanatory copy can shrink and wrap beside the state label');
ok(html.includes('.progressFooter .pixelBtn,.developerActions .pixelBtn,.modalBtns .pixelBtn{min-width:0;white-space:normal;overflow-wrap:anywhere;word-break:keep-all}'),'modal action buttons wrap long Korean labels safely');
ok(html.includes('.namedMark{')&&html.includes('text-overflow:ellipsis')&&html.includes('#charBadge{max-width:142px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'),'intentional compact card-name and character-badge ellipsis remain intact');
ok(road.includes('- [x] 모바일 UI에서 긴 한국어 표현 잘림 점검'),'ROADMAP marks broad Korean mobile clipping audit complete');
console.log('Korean mobile long-copy wrap regression passed.');
