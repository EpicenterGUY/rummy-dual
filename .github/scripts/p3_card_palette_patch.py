from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()
anchor='/* UX1 P2 · switch movement + RUMMY feedback */'
if s.count(anchor)!=1:
    raise SystemExit(f'P3 card palette CSS anchor mismatch: {s.count(anchor)}')
block=r'''
/* UI3 P3 · card surface / named frame palette */
:root{--card-paper:#f1eadf;--card-paper-low:#e4d8c7;--card-ink:#2d3537;--card-red:#b95f64;--card-edge:#6e665a;--card-line:#b5a387;--card-named:#9f875f;--card-named-soft:#d7c5a5}
.card{border-color:var(--card-edge);background:linear-gradient(180deg,var(--card-paper),var(--card-paper-low));box-shadow:0 0 0 1px #c3b49c inset,0 3px 7px #0003;color:var(--card-ink)}
.card:before{border-color:var(--card-line)}.centerSuit:not(.suitRed){color:#30383a}.suitRed{color:var(--card-red)}
.card.named{border-color:#766951;background:linear-gradient(180deg,#f2eadc,#dfd0ba);box-shadow:0 0 0 1px var(--card-named) inset,0 3px 7px #0003}.card.named:before{border-color:var(--card-named)}
.namedMark{width:84%;bottom:14px;padding:3px 3px 2px;border-color:var(--card-named);color:#4e473c;background:linear-gradient(180deg,transparent,#9f875f14);letter-spacing:-.02em}
.named:after{content:"◆";right:5px;top:5px;min-width:14px;width:14px;height:14px;padding:0;display:grid;place-items:center;border:1px solid #75684f;border-radius:3px;background:#b79d6b;color:#273034;font-size:7px;line-height:1;box-shadow:0 1px 0 #fff5 inset}
.joker{background:linear-gradient(180deg,#eee8dc,#ddd0bb)}.joker .centerSuit{color:#746f83}
.meldMiniCard .named:after,.codexMini .named:after{right:3px;top:3px;min-width:10px;width:10px;height:10px;border-radius:2px;font-size:5px}
.cardBtn.selected .card{outline-color:#6f9690}.cardBtn.attachable:not(.selected) .card{outline-color:#7f9683}
'''
s=s.replace(anchor,block+'\n'+anchor,1)
old='- [ ] 카드 아이콘/네임드 프레임과 새 UI 팔레트 통일'
new='- [x] 카드 아이콘/네임드 프레임과 새 UI 팔레트 통일 — 크림 카드 본체는 유지하되 검정/빨강 무늬를 전술 보드 톤으로 조정하고, 네임드는 옛 자주색 `N` 배지 대신 황동 `◆` 표식 + 따뜻한 이중 프레임/이름선으로 통일. 손패·공개 조합·도감 미니카드가 같은 카드 시각 언어를 공유'
if r.count(old)!=1:
    raise SystemExit(f'P3 roadmap card palette anchor mismatch: {r.count(old)}')
r=r.replace(old,new,1)
index.write_text(s)
road.write_text(r)
print('P3 card palette installed')
