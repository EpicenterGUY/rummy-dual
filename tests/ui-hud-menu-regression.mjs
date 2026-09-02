import fs from 'node:fs';
import assert from 'node:assert/strict';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const readme = fs.readFileSync(new URL('../README.md', import.meta.url), 'utf8');
const roadmap = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');

assert.ok(html.includes('/* UI4 P1 · HUD menu stacking fix */'), 'HUD stacking marker missing');
assert.ok(html.includes('.topbar{z-index:120}'), 'topbar must stack above .main');
assert.ok(html.includes('.hudMenuPanel{z-index:122}'), 'HUD menu panel stacking guard missing');
assert.ok(html.includes('새 3장 조합(세트/런)은 둘을 합쳐 기본 턴당 최대 2회'), 'rules overlay must explain the combined new-meld limit');
assert.ok(html.includes('방금 반환한 같은 런은 계속 연장 가능하며, 다른 버스트/체인 반환은 불가합니다.'), 'returned-SWITCH phase must preserve same-RUN continuation');
assert.ok(!html.includes('스위치 반환 1회 완료. 추가 공격 없이'), 'obsolete no-more-attack copy must be removed');
assert.ok(readme.includes('SET or RUN combined'), 'README must document combined new-meld limit');
assert.ok(roadmap.includes('Base new-meld limit: SET/RUN combined'), 'ROADMAP M0 must lock combined new-meld limit');

console.log('HUD menu stacking and turn-rule clarity regression passed.');
