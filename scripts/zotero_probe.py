#!/usr/bin/env python3
"""
zotero_probe.py — 探测 Zotero 本地 API 的真实字段结构。

在写任何自动化脚本之前先跑这个。它回答三个问题：
  (a) citation key 在 JSON 里的确切字段路径
  (b) annotation 颜色是什么格式，紫色对应什么值
  (c) 日期字段长什么样

全程只读。不碰 ~/Zotero/zotero.sqlite。
只用 Python 标准库，不需要 pip install 任何东西。

用法：
    python3 zotero_probe.py
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "http://127.0.0.1:23119"
OUT = Path(__file__).parent / "probe_sample.json"

# Zotero 标准高亮调色板（待本脚本实测确认）
KNOWN_COLORS = {
    "#ffd400": "黄 yellow",
    "#ff6666": "红 red",
    "#5fb236": "绿 green",
    "#2ea8e5": "蓝 blue",
    "#a28ae5": "紫 purple",
    "#e56eee": "洋红 magenta",
    "#f19837": "橙 orange",
    "#aaaaaa": "灰 gray",
}


def get(path, timeout=15):
    url = API + path
    req = urllib.request.Request(url, headers={"User-Agent": "zotero-probe/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", errors="replace")
    return json.loads(body) if body.strip() else None


def die(msg, hints):
    print(f"\n✗ {msg}\n")
    print("排查步骤：")
    for i, h in enumerate(hints, 1):
        print(f"  {i}. {h}")
    sys.exit(1)


def find_keys(obj, needle, path="", hits=None):
    """递归找出所有字段名里含 needle 的路径。"""
    if hits is None:
        hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if needle.lower() in k.lower():
                hits.append((p, v))
            find_keys(v, needle, p, hits)
    elif isinstance(obj, list) and obj:
        find_keys(obj[0], needle, f"{path}[0]", hits)
    return hits


def main():
    sample = {}

    # ---------- 1. 连通性 ----------
    print("=" * 60)
    print("1. 连通性")
    print("=" * 60)
    try:
        try:
            items = get("/api/users/0/items/top?limit=5")
        except Exception:
            items = None
        if not items:
            pool = get("/api/users/0/items?limit=100")
            skip = {"attachment", "note", "annotation"}
            items = [it for it in pool
                     if it.get("data", {}).get("itemType") not in skip][:5]
    except urllib.error.URLError as e:
        die(
            f"连不上 Zotero 本地 API（{e}）",
            [
                "Zotero 桌面版是不是没开？打开它。",
                "Settings → Advanced → 勾选 "
                '"Allow other applications on this computer to communicate with Zotero"',
                "勾完重启 Zotero。",
                f"浏览器直接打开 {API}/api/users/0/items?limit=1 看有没有返回。",
            ],
        )
    except json.JSONDecodeError:
        die(
            "API 返回的不是 JSON",
            ["确认 Zotero 版本 ≥ 7；旧版本的本地 API 路径不同。"],
        )

    print(f"✓ 本地 API 可达，取到 {len(items)} 个条目")
    sample["items_raw"] = items

    # ---------- 2. 条目字段 ----------
    print()
    print("=" * 60)
    print("2. 前 5 个条目")
    print("=" * 60)
    for it in items:
        d = it.get("data", {})
        print(f"\n  key         : {d.get('key')}")
        print(f"  itemType    : {d.get('itemType')}")
        print(f"  title       : {str(d.get('title'))[:70]}")
        print(f"  date (原始) : {d.get('date')!r}")
        if d.get("extra"):
            print(f"  extra       : {str(d.get('extra'))[:70]!r}")

    # ---------- 3. citation key 在哪 ----------
    print()
    print("=" * 60)
    print("3. citation key 字段定位")
    print("=" * 60)
    ck_hits = []
    for it in items:
        for needle in ("citation", "citekey"):
            ck_hits += find_keys(it, needle)
    ck_hits = [(p, v) for p, v in ck_hits if v not in (None, "", {}, [])]

    if ck_hits:
        seen = set()
        for p, v in ck_hits:
            if p in seen:
                continue
            seen.add(p)
            print(f"  ✓ {p}  =  {v!r}")
        answer_a = sorted(seen)[0]
    else:
        legacy = [
            it["data"]["extra"]
            for it in items
            if "Citation Key" in str(it.get("data", {}).get("extra", ""))
        ]
        if legacy:
            print("  ⚠ 没找到原生字段，但 extra 里有旧式 'Citation Key:'")
            print(f"     例：{legacy[0][:60]!r}")
            answer_a = "data.extra 里的 'Citation Key: xxx'（旧式）"
        else:
            kinds = {it.get("data", {}).get("itemType") for it in items}
            print("  ✗ 这 5 个样本里没有 citation key")
            print(f"     样本类型：{kinds}")
            if kinds <= {"attachment", "note", "annotation"}:
                print("     → 取到的都是子条目，不是论文本身。这是取样问题，不是配置问题。")
                answer_a = "取样不含顶层条目，无法判定"
            else:
                print("     → 检查 Better BibTeX 是否装好、是否做过全库刷新（手册 A4）")
                answer_a = "未找到"

    # ---------- 4. 标注 ----------
    print()
    print("=" * 60)
    print("4. 标注（annotations）")
    print("=" * 60)
    try:
        anns = get("/api/users/0/items?itemType=annotation&limit=50")
    except Exception as e:
        print(f"  ✗ 拉标注失败：{e}")
        anns = []

    sample["annotations_raw"] = anns
    print(f"  取到 {len(anns)} 条标注\n")

    colors = {}
    for a in anns:
        d = a.get("data", {})
        c = d.get("annotationColor")
        if c:
            colors[c] = colors.get(c, 0) + 1

    for a in anns[:5]:
        d = a.get("data", {})
        print(f"  type  : {d.get('annotationType')}")
        print(f"  color : {d.get('annotationColor')!r}")
        print(f"  page  : {d.get('annotationPageLabel')!r}")
        print(f"  text  : {str(d.get('annotationText', ''))[:60]!r}")
        print(f"  tags  : {[t.get('tag') for t in d.get('tags', [])]}")
        print()

    print("  颜色分布：")
    if colors:
        for c, n in sorted(colors.items(), key=lambda x: -x[1]):
            print(f"    {c}  ×{n}   {KNOWN_COLORS.get(c.lower(), '?? 未知')}")
    else:
        print("    （没有标注，先去标几条再跑）")

    unknown = [c for c in colors if c.lower() not in KNOWN_COLORS]
    if unknown:
        print(f"\n  ⚠ 非标准调色板的颜色：{unknown}")
        print("     多半是从别的 PDF 阅读器导入的标注，不影响使用。")
    purple = [c for c in colors if c.lower() == "#a28ae5"]
    answer_b = purple[0] if purple else "库里还没有紫色标注（标一条再跑本脚本确认）"

    # ---------- 5. 日期 ----------
    print()
    print("=" * 60)
    print("5. 日期字段")
    print("=" * 60)
    dates = [(it["data"].get("title", "")[:40], it["data"].get("date"))
             for it in items if it.get("data", {}).get("date")]
    for t, d in dates:
        print(f"  {d!r:28} ← {t}")
    answer_c = (
        "date 字段是自由文本，格式不统一；working paper 的 'This draft' 日期"
        "Zotero 通常不单独存，需要你手填 draft_date"
    )

    # ---------- dump ----------
    OUT.write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print("=" * 60)
    print("结论")
    print("=" * 60)
    print(f"(a) citation key 字段路径 : {answer_a}")
    print(f"(b) 紫色的实际值          : {answer_b}")
    print(f"(c) 日期                  : {answer_c}")
    print()
    print(f"完整原始 JSON 已写入：{OUT}")
    print("→ 把 (b) 的值填进 export_purple.py 的 PURPLE 常量（如果和默认值不同）")


if __name__ == "__main__":
    main()
