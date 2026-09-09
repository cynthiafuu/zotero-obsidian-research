#!/usr/bin/env python3
"""
export_purple.py — 导出全库紫色标注（= 你的质疑），按论文分组成 markdown。

紫色标注是选题的原料。每月跑一次，把输出丢给 Claude 做模式分析
（prompt 见 70-Meta/prompts/02-purple-analysis.md）。

全程只读。只用标准库。

用法：
    python3 export_purple.py                    # 默认导紫色
    python3 export_purple.py --color "#ff6666"  # 导别的颜色
    python3 export_purple.py --all-colors       # 全部颜色，按色分组
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

API = "http://127.0.0.1:23119"
PURPLE = "#a28ae5"          # 若 probe 显示不同，改这里
OUTDIR = Path(__file__).parent.parent / "exports"

COLOR_NAMES = {
    "#ffd400": "yellow-key-finding",
    "#ff6666": "red-identification",
    "#5fb236": "green-reusable-method",
    "#2ea8e5": "blue-institutional",
    "#a28ae5": "purple-my-doubts",
    "#e56eee": "magenta",
    "#f19837": "orange",
    "#aaaaaa": "gray",
}


def get(path, timeout=30):
    req = urllib.request.Request(API + path,
                                 headers={"User-Agent": "export-purple/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", errors="replace")
    return json.loads(body) if body.strip() else []


def get_all(path_tmpl, page=100, cap=20000):
    """分页拉全部结果。path_tmpl 里用 {start} 占位。"""
    out, start = [], 0
    while start < cap:
        sep = "&" if "?" in path_tmpl else "?"
        chunk = get(f"{path_tmpl}{sep}limit={page}&start={start}")
        if not chunk:
            break
        out += chunk
        if len(chunk) < page:
            break
        start += page
    return out


def citekey_of(data):
    """Zotero 8+ 原生字段优先，退回 extra 里的旧式写法。"""
    for k in ("citationKey", "citekey", "citation_key"):
        if data.get(k):
            return data[k]
    m = re.search(r"Citation Key:\s*(\S+)", str(data.get("extra", "")))
    return m.group(1) if m else None


def sort_index(a):
    """annotationSortIndex 形如 '00003|000512|00019'，按数值排。"""
    raw = a.get("data", {}).get("annotationSortIndex", "")
    try:
        return tuple(int(x) for x in raw.split("|"))
    except ValueError:
        return (0,)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--color", default=PURPLE)
    ap.add_argument("--all-colors", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    try:
        print("拉取全部条目…", flush=True)
        items = get_all("/api/users/0/items")
    except urllib.error.URLError as e:
        print(f"✗ 连不上 Zotero 本地 API：{e}")
        print("  → Zotero 开着吗？Settings → Advanced 勾了 local API 吗？")
        sys.exit(1)

    by_key = {it["data"]["key"]: it["data"] for it in items if it.get("data", {}).get("key")}
    print(f"  {len(by_key)} 个条目")

    print("筛选标注…", flush=True)
    anns = [it for it in items if it.get("data", {}).get("itemType") == "annotation"]
    print(f"  {len(anns)} 条标注")

    if not args.all_colors:
        want = args.color.lower()
        anns = [a for a in anns
                if str(a["data"].get("annotationColor", "")).lower() == want]
        print(f"  其中 {COLOR_NAMES.get(want, want)}：{len(anns)} 条")

    if not anns:
        print("\n没有符合条件的标注。先去标几条，或用 --all-colors 看看有什么。")
        sys.exit(0)

    # annotation → 附件 → 母条目
    groups = {}
    for a in anns:
        d = a["data"]
        att = by_key.get(d.get("parentItem"), {})
        parent = by_key.get(att.get("parentItem"), {})
        if not parent:
            parent = {"title": "（找不到母条目）", "key": "orphan"}
        gk = parent.get("key")
        groups.setdefault(gk, {"parent": parent, "anns": []})["anns"].append(a)

    outdir = OUTDIR
    outdir.mkdir(parents=True, exist_ok=True)
    tag = "all" if args.all_colors else COLOR_NAMES.get(
        args.color.lower(), args.color).split("-")[0]
    out = Path(args.out) if args.out else outdir / f"{tag}-{date.today()}.md"

    lines = [
        f"# Annotation export — {tag}",
        "",
        f"- 导出日期：{date.today()}",
        f"- 论文数：{len(groups)}",
        f"- 标注数：{len(anns)}",
        "",
        "---",
        "",
    ]

    def sort_group(kv):
        p = kv[1]["parent"]
        return (citekey_of(p) or "zzz", p.get("title", ""))

    for _, g in sorted(groups.items(), key=sort_group):
        p = g["parent"]
        ck = citekey_of(p) or "(无 citekey)"
        year = ""
        m = re.search(r"\b(1[89]\d{2}|20\d{2})\b", str(p.get("date", "")))
        if m:
            year = f" ({m.group(1)})"
        lines.append(f"## {ck} — {p.get('title', '(无标题)')}{year}")
        lines.append("")
        for a in sorted(g["anns"], key=sort_index):
            d = a["data"]
            page = d.get("annotationPageLabel") or "?"
            text = " ".join(str(d.get("annotationText", "")).split())
            comment = " ".join(str(d.get("annotationComment", "")).split())
            tags = [t.get("tag") for t in d.get("tags", []) if t.get("tag")]
            if args.all_colors:
                cname = COLOR_NAMES.get(
                    str(d.get("annotationColor", "")).lower(), "?")
                lines.append(f"- **[{cname}] p.{page}** {text}")
            else:
                lines.append(f"- **p.{page}** {text}")
            if comment:
                lines.append(f"  - 我的批注：{comment}")
            if tags:
                lines.append(f"  - tags: {', '.join(tags)}")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ 写入 {out}")
    print(f"  {len(groups)} 篇论文，{len(anns)} 条标注")
    print("\n下一步：把这个文件连同 70-Meta/prompts/02-purple-analysis.md 一起丢给 Claude")


if __name__ == "__main__":
    main()
