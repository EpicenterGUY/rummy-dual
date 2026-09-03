from pathlib import Path

script=Path(__file__).with_name('base-action-simplification-patch.py')
src=script.read_text(encoding='utf-8')
old="- 자기 공개 조합 3칸이 모두 찼다면, 당턴 생성/고정 조합을 제외하고 기본 `정리` 1회로 슬롯을 비울 수 있다. 정리는 위력 +0 / SWITCH 이동 없음.','UX switch basics')"
new="- 자기 공개 조합 3칸이 모두 찼다면, 당턴 생성/고정 조합을 제외하고 기본 `정리` 1회로 슬롯을 비울 수 있다. 정리는 위력 +0 / SWITCH 이동 없음.''','UX switch basics')"
if old not in src and new not in src:raise SystemExit('missing UX syntax correction anchor')
src=src.replace(old,new,1)
compile(src,str(script),'exec')
ns={'__file__':str(script),'__name__':'__main__'}
exec(compile(src,str(script),'exec'),ns,ns)
