#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""投喂提示词结构自检（V6.9 小说三阶段接入版）。"""
from __future__ import annotations
import json, os, re, sys
from collections import Counter
from typing import List, Tuple, Dict

LIMITS={"2.5":30,"2.0":15}
MAX_CHARS_STANDARD=4500
MAX_CHARS_NOVEL_WARN=4500
MAX_CHARS_NOVEL_FAIL=8000
TIME_RE=re.compile(r"(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?\s*[-~～→]\s*(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?|(?<!\w)(\d+(?:\.\d+)?)\s*s\s*[-~～→]\s*(\d+(?:\.\d+)?)\s*s",re.I)
EXPLICIT_SECONDS_RE=re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(?:秒|s\b)",re.I)
BEAT_COUNT_RE=re.compile(r"(?:停顿|保持|停留)\s*[一二三四五六七八九十两0-9]+\s*拍")
SHOT_RE=re.compile(r"\[镜头\s*(\d+)\]")
SEVEN=["【画幅风格】","【场景资产】","【核心人物】","【站位声明】","【时间轴分镜】","【音效】","【强制禁止项】"]
GORE=["鲜血","血喷","血肉模糊","喷血","断肢","断臂","断头","碎尸","内脏","脑浆","割喉","虐杀","凌迟","开膛破肚","伤口","裸体","露点","床戏","自杀","自残","割腕","上吊","吸毒"]

def ranges(text:str)->List[Tuple[float,float,int]]:
    out=[]
    for i,line in enumerate(text.splitlines(),1):
        for m in TIME_RE.finditer(line):
            if m.group(1) is not None:
                a=int(m.group(1))*60+int(m.group(2))+int(m.group(3) or 0)/100
                b=int(m.group(4))*60+int(m.group(5))+int(m.group(6) or 0)/100
            else:a,b=float(m.group(7)),float(m.group(8))
            out.append((round(a,2),round(b,2),i))
    return out

def section(text,h,nexts):
    a=text.find(h)
    if a<0:return ""
    a+=len(h); es=[text.find(n,a) for n in nexts]; es=[e for e in es if e>=0]
    return text[a:min(es) if es else len(text)]

def shared(text,model,issues,warns):
    style=section(text,"【画幅风格】",["【场景资产】"])
    if not re.search(r"aspect_ratio\s*=",text) and not re.search(r"16:9|9:16|21:9|1:1",style):issues.append("C6 缺画幅回填")
    missing=[x for x in SEVEN if x not in text]
    if missing:issues.append(f"C7 七段式缺栏 {missing}")
    else:
        ps=[text.index(x) for x in SEVEN]
        if ps!=sorted(ps):issues.append("C7 七段式段序错误")
    if "【时间轴分镜】" in text and "【接续状态】" not in text:issues.append("C11 缺【接续状态】")
    if model=="2.0" and re.search(r"首尾帧|first_last_frame",text,re.I):issues.append("C8 Seedance 2.0 禁用首尾帧")
    hits=[w for w in GORE if w in text]
    if hits:issues.append(f"C9 平台高危词 {hits}")

def validate_standard(text,model,mode):
    issues=[]; warns=[]; tr=ranges(text); dur=max((b for a,b,l in tr),default=0)
    if tr:
        if dur>LIMITS[model]+.01:issues.append(f"C1 时长 {dur}s 超上限")
        for a,b,l in tr:
            if b<=a:issues.append(f"C3 第{l}行时间倒挂")
            elif b-a<3:warns.append(f"C2 第{l}行碎切风险")
            elif b-a>6:warns.append(f"C10 第{l}行长镜风险")
    else:warns.append("C1-C3 未识别时间轴")
    if len(text)>MAX_CHARS_STANDARD:issues.append(f"C4 字符数 {len(text)} 超预算")
    shared(text,model,issues,warns)
    return issues,warns,{"profile":"standard","duration_s":dur,"shots":len(tr),"chars":len(text)}

def validate_novel(text,model):
    issues=[]; warns=[]
    if model!="2.5":issues.append("N1 novel-2.5-ntc 只允许 Seedance 2.5")
    shared(text,model,issues,warns)
    tr=ranges(text)
    secs=[(m.group(0),text[:m.start()].count("\n")+1) for m in EXPLICIT_SECONDS_RE.finditer(text)]
    beats=[(m.group(0),text[:m.start()].count("\n")+1) for m in BEAT_COUNT_RE.finditer(text)]
    if tr:issues.append(f"N3 禁止时间码：{len(tr)}处")
    if secs:issues.append("N3 禁止数字秒数："+", ".join(f"第{l}行 {v}" for v,l in secs[:5]))
    if beats:issues.append("N3 禁止数字拍数："+", ".join(f"第{l}行 {v}" for v,l in beats[:5]))
    shots=[int(x) for x in SHOT_RE.findall(text)]
    if not shots:issues.append("N4 未识别镜头编号")
    else:
        if len(shots)!=len(set(shots)):issues.append("N4 镜头编号重复")
        if shots!=list(range(1,len(shots)+1)):issues.append(f"N4 镜头编号不连续 {shots}")
    st=section(text,"【站位声明】",["【时间轴分镜】"])
    if st:
        if not re.search(r"画面|左|右|前景|中景|后景|中央",st):issues.append("N5 站位缺画面位置")
        if "朝向" not in st and not re.search(r"朝左|朝右|面向|侧身|背向",st):issues.append("N5 站位缺朝向")
        if "距离" not in st and not re.search(r"相距|一步|两步|三步|一臂|隔着",st):warns.append("N5 未显式写人物距离")
    if not re.search(r"Seedance\s*2\.5|seedance-2\.5|model\s*=\s*seedance-2\.5",text,re.I):issues.append("N6 未明确 Seedance 2.5")
    if len(text)>MAX_CHARS_NOVEL_FAIL:issues.append(f"N8 字符数 {len(text)} 超硬上限")
    elif len(text)>MAX_CHARS_NOVEL_WARN:warns.append(f"N8 字符数 {len(text)} 超建议清洁线")
    return issues,warns,{"profile":"novel-2.5-ntc","duration_s":None,"shots":len(shots),"chars":len(text)}

def validate(text,model="2.5",mode="new",profile="standard"):
    return validate_novel(text,model) if profile=="novel-2.5-ntc" else validate_standard(text,model,mode)

def selftest():
    novel='''【画幅风格】\n9:16竖屏，Seedance 2.5，全能参考模式。\n【场景资产】\n@SCN-服装店。\n【核心人物】\n@CHR-白厄；@CHR-千仞雪。\n【站位声明】\n白厄位于画面右后柜台内，身体朝向千仞雪；千仞雪位于画面左前货架旁，侧身朝右；两人隔柜台相距约两步。\n【时间轴分镜】\n[镜头1] 双人中景 · 斜侧平视 · 固定。千仞雪举起衣服，白厄同步看向衣服。声音：<布料声>。台词：无。\n[镜头2] 中近景 · 千仞雪观察侧 · 固定。千仞雪挥手，白厄收拢衣服。声音：<衣架声>。台词：无。\n【接续状态】\n千仞雪仍在货架旁；白厄留在柜台内。\n【音效】\n环境声低于对白。\n【强制禁止项】\n画面：禁止新增人物；文字：禁止字幕；声音：禁止新增台词。'''
    i,_,_=validate(novel,"2.5",profile="novel-2.5-ntc")
    if i:print("FAIL novel",i);return 1
    bad=novel.replace("[镜头1]","00:00-00:05 [镜头1]")
    i,_,_=validate(bad,"2.5",profile="novel-2.5-ntc")
    if not any("N3" in x for x in i):print("FAIL no timecode");return 1
    print("[+] self-test PASSED");return 0

def main():
    a=sys.argv[1:]
    if "--self-test" in a:sys.exit(selftest())
    files=[x for x in a if not x.startswith("-")]
    if not files:print(__doc__);sys.exit(2)
    def opt(k,d):return a[a.index(k)+1] if k in a else d
    model=opt("--model","2.5"); profile=opt("--profile","standard"); mode=opt("--mode","new")
    text=open(files[0],encoding="utf-8").read(); issues,warns,stats=validate(text,model,mode,profile)
    if "--json" in a:print(json.dumps({"issues":issues,"warnings":warns,"stats":stats},ensure_ascii=False,indent=2))
    else:
        print(f"[+] profile={profile} model={model} shots={stats['shots']} chars={stats['chars']}")
        for x in warns:print("[!] WARN:",x)
        for x in issues:print("[-] FAIL:",x)
        print("[+] PASSED" if not issues else f"[-] {len(issues)} error(s)")
    sys.exit(1 if issues else 0)
if __name__=="__main__":main()
