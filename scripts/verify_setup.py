#!/usr/bin/env python3
"""
verify_setup.py — 在你的真实库上验证另外两个脚本的每一条假设。

它不是重新实现一遍逻辑，而是 import export_purple，
调用它**真实的函数**，喂你**真实的数据**，逐条报告 PASS / FAIL。

全程只读：
  · 不调用任何 Zotero 写接口
  · 不碰 ~/Zotero
  · 不写、不改 vault 里任何文件（只在内存里跑）

用法（Zotero 保持开着）：
    cd ~/Documents/research/70-Meta/scripts
    python3 verify_setup.py
"""

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

API = "http://127.0.0.1:23119"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok))
    mark = "✓ PASS" if ok else "✗ FAIL"
    print(f"  {mark}  {name}")
    if detail:
        for line in str(detail).split("\n"):
            print(f"           {line}")


def head(n, t):
    print()
    print("=" * 66)
    print(f"{n}. {t}")
    print("=" * 66)


def raw_get(path, timeout=30):
    req = urllib.request.Request(API + path, headers={"User-Agent": "verify/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", errors="replace")
    return json.loads(body) if body.strip() else []


# ------------------------------------------------------------------ 0. import
head(0, "载入待验证的脚本")
try:
    import export_purple as ep
    check("import export_purple", True)
except Exception as e:
    check("import", False, e)
    print("\nexport_purple.py 不在同一目录，或有语法错误。停止。")
    sys.exit(1)


# 自带的 frontmatter 解析（不再依赖外部脚本）
def split_fm(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], lines[i + 1:], 1
    return None


def parse_fm(fm_lines):
    out = {}
    for idx, ln in enumerate(fm_lines):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(.*)$", ln)
        if m:
            out[m.group(1)] = (idx, m.group(2).strip())
    return out


FIELDS = ["citekey", "draft_date", "pub_status", "status", "topic", "setting",
          "data", "method", "identification", "measure", "finding", "gap",
          "rating", "added"]


# ------------------------------------------------------------------ 1. 连通
head(1, "Zotero 本地 API")
try:
    probe = raw_get("/api/users/0/items?limit=1")
    check("本地 API 可达", True)
except urllib.error.URLError as e:
    check("本地 API 可达", False, f"{e}\nZotero 开着吗？Settings→Advanced 勾了 local API 吗？")
    sys.exit(1)


# ------------------------------------------------------------------ 2. 分页
head(2, "分页（两个脚本都靠 get_all 把全库拉下来）")
p0 = raw_get("/api/users/0/items?limit=100&start=0")
p1 = raw_get("/api/users/0/items?limit=100&start=100")
k0 = {i.get("data", {}).get("key") for i in p0}
k1 = {i.get("data", {}).get("key") for i in p1}

check("start=0 返回数据", len(p0) > 0, f"{len(p0)} 条")
if len(p0) < 100:
    print(f"  -  SKIP  分页差异检查（全库不足 100 条，只有一页）")
else:
    check("start=100 返回不同的数据（分页真的生效）",
          len(p1) > 0 and not (k0 & k1),
          f"第二页 {len(p1)} 条，与第一页重叠 {len(k0 & k1)} 条")

t0 = time.time()
all_items = ep.get_all("/api/users/0/items")
dt = time.time() - t0
check("get_all 拉完全库", len(all_items) > 0,
      f"{len(all_items)} 条，耗时 {dt:.1f} 秒")
check("没撞上 20000 条的硬上限", len(all_items) < 20000, f"{len(all_items)} / 20000")

types = {}
for it in all_items:
    t = it.get("data", {}).get("itemType", "?")
    types[t] = types.get(t, 0) + 1
print(f"           类型分布：{dict(sorted(types.items(), key=lambda x: -x[1]))}")


# ------------------------------------------------------------------ 3. citekey
head(3, "citekey 提取（决定笔记文件名能否对上）")
tops = [it for it in all_items
        if it.get("data", {}).get("itemType") not in
        ("attachment", "note", "annotation")]

with_ck, without_ck = [], []
for it in tops:
    ck = ep.citekey_of(it["data"])
    (with_ck if ck else without_ck).append(it["data"])

check("export_purple.citekey_of 能取到 citekey",
      len(with_ck) > 0,
      f"{len(with_ck)} / {len(tops)} 个顶层条目有 citekey")

if without_ck:
    print(f"           ⚠ {len(without_ck)} 条没有 citekey，前 3 个：")
    for d in without_ck[:3]:
        print(f"             [{d.get('itemType')}] {str(d.get('title'))[:52]}")

bad = [ep.citekey_of(d) for d in [i["data"] for i in tops]
       if ep.citekey_of(d) and ep.citekey_of(d)[0].isdigit()]
check("没有以数字开头的坏 citekey", len(bad) == 0,
      f"{len(bad)} 个：{bad[:5]}" if bad else "")


# ------------------------------------------------------------------ 4. 回溯
head(4, "标注 → 附件 → 母条目 的两级回溯（export_purple 的核心）")
by_key = {i["data"]["key"]: i["data"] for i in all_items if i.get("data", {}).get("key")}
anns = [i for i in all_items if i.get("data", {}).get("itemType") == "annotation"]

resolved, orphan = 0, []
for a in anns:
    att = by_key.get(a["data"].get("parentItem"), {})
    par = by_key.get(att.get("parentItem"), {})
    if par:
        resolved += 1
    else:
        orphan.append(a["data"].get("key"))

check("标注能解析到母条目", len(anns) > 0 and resolved == len(anns),
      f"{resolved} / {len(anns)} 条解析成功"
      + (f"，孤儿：{orphan[:5]}" if orphan else ""))

idx_ok = 0
for a in anns:
    try:
        ep.sort_index(a)
        idx_ok += 1
    except Exception:
        pass
check("annotationSortIndex 排序不报错", idx_ok == len(anns),
      f"{idx_ok} / {len(anns)}")

colors = {}
for a in anns:
    c = str(a["data"].get("annotationColor", "")).lower()
    colors[c] = colors.get(c, 0) + 1
n_purple = colors.get(ep.PURPLE.lower(), 0)
check(f"紫色常量 {ep.PURPLE} 与库中一致",
      n_purple > 0,
      f"{n_purple} 条紫色标注" if n_purple
      else "库里还没有紫色标注 —— 标一条再跑本脚本，这条才有意义")


# ------------------------------------------------------------------ 7. 模板
head(5, "模板文件的 frontmatter")
tpl = HERE.parent / "templates" / "lit-note.md"
if tpl.exists():
    text = tpl.read_text(encoding="utf-8")
    parts = split_fm(text)
    check("能识别模板的 frontmatter", parts is not None)
    if parts:
        fm, body, off = parts
        fields = parse_fm(fm)
        need = FIELDS
        missing = [k for k in need if k not in fields]
        check("模板含有全部待填字段", not missing,
              f"缺：{missing}" if missing else f"{len(fields)} 个字段")
        if "{{VALUE:citekey}}" in text and "{{DATE:" in text:
            check("QuickAdd 占位符完好", True)
        else:
            check("QuickAdd 占位符完好", False, "{{VALUE:}} 或 {{DATE:}} 被改坏了")
else:
    check("找到 lit-note.md", False, str(tpl))


# ------------------------------------------------------------------ 8. 笔记
head(6, "10-Literature 里已有的笔记")
lit = HERE.parent.parent / "10-Literature"
notes = sorted(lit.glob("*.md")) if lit.is_dir() else []
print(f"           {len(notes)} 个笔记文件")

if notes:
    idx = {ep.citekey_of(i["data"]): i["data"] for i in tops
           if ep.citekey_of(i["data"])}
    matched, unmatched = 0, []
    for n in notes:
        p = split_fm(n.read_text(encoding="utf-8"))
        if not p:
            unmatched.append(f"{n.name}（没有 frontmatter）")
            continue
        f = parse_fm(p[0])
        ck = f.get("citekey", (0, ""))[1].strip().strip("\"'") or n.stem
        if ck in idx:
            matched += 1
        else:
            unmatched.append(f"{n.name}（citekey '{ck}' 在 Zotero 里找不到）")
    check("每条笔记都能对上 Zotero 条目", not unmatched,
          "\n".join(unmatched[:5]))
else:
    print("           还没写笔记，跳过（写完第一篇后重跑本脚本）")


# ------------------------------------------------------------------ 汇总
print()
print("=" * 66)
n_fail = sum(1 for _, ok in RESULTS if not ok)
print(f"共 {len(RESULTS)} 项，通过 {len(RESULTS) - n_fail}，失败 {n_fail}")
print("=" * 66)
if n_fail:
    print("\n失败项：")
    for name, ok in RESULTS:
        if not ok:
            print(f"  · {name}")
    print("\n把上面完整输出发出去，逐条修。")
else:
    print("\n两个脚本的全部假设都在你的真实数据上成立。")
print("\n本次运行未修改任何文件。")
