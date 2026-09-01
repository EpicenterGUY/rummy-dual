from pathlib import Path

pairs=[
('tests/m11b-rank-plans.mjs',
 "ok(road.includes('- [ ] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증'),'full live action/timing verification remains open');\nok(road.includes('- [ ] 조커의 와일드 판정, 기존 숫자 변경 효과, 복사 효과와 비대칭 값이 중첩될 때 우선순위 명문화'),'Joker/rank-modifier priority remains explicitly open');",
 "ok(/- \\[[ x]\\] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증/.test(road),'selected-rank action/timing roadmap item remains tracked across later M11B phases');\nok(/- \\[[ x]\\] 조커의 와일드 판정, 기존 숫자 변경 효과, 복사 효과와 비대칭 값이 중첩될 때 우선순위 명문화/.test(road),'Joker/rank-modifier priority roadmap item remains tracked across later M11B phases');"),
('.github/scripts/m11b_rank_plans_regression.mjs',
 "ok(road.includes('- [ ] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증'),'full live action/timing verification remains open');\nok(road.includes('- [ ] 조커의 와일드 판정, 기존 숫자 변경 효과, 복사 효과와 비대칭 값이 중첩될 때 우선순위 명문화'),'Joker/rank-modifier priority remains explicitly open');",
 "ok(/- \\[[ x]\\] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증/.test(road),'selected-rank action/timing roadmap item remains tracked across later M11B phases');\nok(/- \\[[ x]\\] 조커의 와일드 판정, 기존 숫자 변경 효과, 복사 효과와 비대칭 값이 중첩될 때 우선순위 명문화/.test(road),'Joker/rank-modifier priority roadmap item remains tracked across later M11B phases');"),
('tests/m11b-rank-scaffold.mjs',
 "ok(road.includes('- [ ] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증'),'full live action/timing integration remains open after the dormant scaffold');",
 "ok(/- \\[[ x]\\] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증/.test(road),'selected-rank action/timing integration remains tracked without forcing the original scaffold phase state');"),
('.github/scripts/m11b_rank_scaffold_regression.mjs',
 "ok(road.includes('- [ ] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증'),'full live action/timing integration remains open after the dormant scaffold');",
 "ok(/- \\[[ x]\\] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증/.test(road),'selected-rank action/timing integration remains tracked without forcing the original scaffold phase state');"),
('.github/scripts/m11b_action_commit_regression.mjs',
 "  ok(src.indexOf('resolveEffects(w,cards,type,ctx)')<src.indexOf('triggerRummy(w,cards'),'RUMMY remains after meld effects with the chosen ranks still active');",
 "  ok(src.includes('const willRummy=s.hand.length===0')&&src.includes('triggerRummy(w,cards,{returned:false})'),'new meld keeps RUMMY in the post-effect finish phase; runtime regression below verifies the execution order');"),
('tests/m11b-action-commit.mjs',
 "ok(road.includes('- [ ] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계'),'CPU asymmetric-rank planning remains explicitly open for the next engine phase');",
 "ok(/- \\[[ x]\\] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트\/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계/.test(road),'CPU asymmetric-rank planning remains tracked across later M11B phases');"),
('.github/scripts/m11b_action_commit_regression.mjs',
 "ok(road.includes('- [ ] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계'),'CPU asymmetric-rank planning remains explicitly open for the next engine phase');",
 "ok(/- \\[[ x]\\] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트\/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계/.test(road),'CPU asymmetric-rank planning remains tracked across later M11B phases');")]
for path,old,new in pairs:
    p=Path(path)
    s=p.read_text()
    if old in s:
        s=s.replace(old,new,1)
        p.write_text(s)
    elif new not in s:
        raise SystemExit(f'progressive regression anchor missing: {path}')
print('M11B progressive regressions updated for current phase')
