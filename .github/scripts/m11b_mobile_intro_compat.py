from pathlib import Path

choice_paths=[Path('tests/m11b-rank-choice-ui.mjs'),Path('.github/scripts/m11b_rank_choice_ui_regression.mjs')]
old_choice="ok(road.includes('- [ ] 모바일에서 상·하단 숫자가 다른 카드가 단순 오타처럼 보이지 않도록 최초 획득/튜토리얼 설명 설계'),'mobile/onboarding explanation remains the final M11B UI item');"
new_choice="ok(road.includes('- [x] 모바일에서 상·하단 숫자가 다른 카드가 단순 오타처럼 보이지 않도록 최초 획득/튜토리얼 설명 설계'),'mobile/onboarding explanation is completed after the rank-choice UI phase');"
for p in choice_paths:
    s=p.read_text()
    if old_choice in s:
        s=s.replace(old_choice,new_choice,1)
        p.write_text(s)
    elif new_choice not in s:
        raise SystemExit(f'M11B prior UI regression anchor missing: {p}')

frame_paths=[Path('tests/m11b-rank-ui.mjs'),Path('.github/scripts/m11b_rank_ui_regression.mjs')]
old_frame="ok(unresolvedHtml.includes('↕ 3/7'),'unresolved X/Y card displays a compact two-choice marker');"
new_frame="ok(unresolvedHtml.includes('↕ 선택')&&unresolvedHtml.includes('>3<br>♠')&&unresolvedHtml.includes('>7<br>♠'),'unresolved X/Y card combines distinct printed corners with an explicit selectable-rank marker');"
for p in frame_paths:
    s=p.read_text()
    if old_frame in s:
        s=s.replace(old_frame,new_frame,1)
        p.write_text(s)
    elif new_frame not in s:
        raise SystemExit(f'M11B frame regression anchor missing: {p}')

print('Prior M11B UI regressions aligned with completed mobile onboarding and semantic rank marker')
