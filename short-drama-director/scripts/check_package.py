#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
BASE=Path(__file__).resolve().parent.parent
bad=[]
def check(n,c):
 print(f"[{'PASS' if c else 'FAIL'}] {n}"); bad.append(n) if not c else None
check('V6.9 SKILL','V6.9 小说三阶段接入版' in (BASE/'SKILL.md').read_text('utf-8'))
refs=list((BASE/'references').rglob('*.md')); check('44 reference files',len(refs)==44)
req=['references/novel-entry/01_Chat原作影视化增补.md','references/novel-entry/02_Chat抖音剧情优化.md','references/novel-entry/03_Chat基础分镜架构.md','references/novel-entry/04_小说漫剧已改编入口与Work交接.md','references/novel-entry/05_Work技术施工与Seedance2.5无时间码流程.md','references/novel-entry/06_Seedance2.5七段式无时间码合同.md']
for r in req:check(r,(BASE/r).exists())
entry=(BASE/req[3]).read_text('utf-8'); check('P1-N','IMPORTED_AND_SATISFIED' in entry)
work=(BASE/req[4]).read_text('utf-8'); check('Work core','先位后机' in work and '先静后动' in work and '最终交付：禁止时间码' in work)
contract=(BASE/req[5]).read_text('utf-8'); check('seven sections',all(x in contract for x in ['【画幅风格】','【场景资产】','【核心人物】','【站位声明】','【时间轴分镜】','【接续状态】','【音效】','【强制禁止项】']))
check('unicode names',not any('#U2605' in p.name for p in BASE.rglob('*')))
r=subprocess.run([sys.executable,str(BASE/'scripts/validate_prompt.py'),'--self-test'],capture_output=True,text=True);check('validator selftest',r.returncode==0)
print('FAILED',bad if bad else 'none');sys.exit(1 if bad else 0)
