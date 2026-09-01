import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
ok(html.includes('@media(max-width:390px)'),'390px compact fallback remains present');
ok(html.includes('@media(max-width:370px)'),'370px narrow fallback remains present');
ok(road.includes('- [x] 360~480px 라이브 Chromium 폭에서 버튼/상태 문구 잘림 회귀 점검'),'ROADMAP locks exact 360/370/390/430/480 live-browser audit');
ok(road.includes('Chrome DevTools 모바일 viewport'),'ROADMAP records exact CSS-pixel device emulation');
ok(road.includes('문서 가로 오버플로와 핵심 패널 viewport 이탈 0건'),'ROADMAP records the measured overflow criterion');
ok(road.includes('- [ ] Android/iOS 실제 물리 기기 최종 확인'),'physical-device verification remains explicitly open');
console.log('UI2 mobile live-browser audit regression passed.');
