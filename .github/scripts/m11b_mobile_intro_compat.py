from pathlib import Path

paths=[Path('tests/m11b-rank-choice-ui.mjs'),Path('.github/scripts/m11b_rank_choice_ui_regression.mjs')]
old="ok(road.includes('- [ ] 모바일에서 상·하단 숫자가 다른 카드가 단순 오타처럼 보이지 않도록 최초 획득/튜토리얼 설명 설계'),'mobile/onboarding explanation remains the final M11B UI item');"
new="ok(road.includes('- [x] 모바일에서 상·하단 숫자가 다른 카드가 단순 오타처럼 보이지 않도록 최초 획득/튜토리얼 설명 설계'),'mobile/onboarding explanation is completed after the rank-choice UI phase');"
for p in paths:
    s=p.read_text()
    if old in s:
        s=s.replace(old,new,1)
        p.write_text(s)
    elif new not in s:
        raise SystemExit(f'M11B prior UI regression anchor missing: {p}')
print('Prior M11B UI regression aligned with completed mobile onboarding')
