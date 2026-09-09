#!/usr/bin/env python3
"""
fill_frontmatter.py — 批量补全 10-Literature/ 里空的 frontmatter 字段。

分工原则：
  事实字段（title/authors/year/journal/pub_status）→ 直接从 Zotero 取，不经过模型
  判断字段（setting/data/method/identification/measure）→ 可选地调本地 LLM，
    且值前面加 "?" 前缀，表示待你确认

安全设计：
  · 默认 dry-run，必须显式 --apply 才写盘
  · 绝不覆盖任何已有的非空字段
  · 绝不改动 frontmatter 以外的正文（按行编辑，不做 YAML 重排）
  · --apply 前检查 git 工作区是否干净
  · 只读 Zotero，不碰 zotero.sqlite

用法：
    python3 fill_frontmatter.py                  # 预览将要改什么
    python3 fill_frontmatter.py --apply          # 只填事实字段
    python3 fill_frontmatter.py --llm --apply    # 加上模型推断字段
    python3 fill_frontmatter.py --llm --model qwen2.5:14b --apply
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ZOTERO = "http://127.0.0.1:23119"
OLLAMA = "http://127.0.0.1:11434"

VAULT = Path(__file__).resolve().parent.parent.parent
LITDIR = VAULT / "10-Literature"

FACT_FIELDS = ["title", "authors", "year", "journal", "pub_status"]
LLM_FIELDS = ["setting", "data", "method", "identification", "measure"]

JOURNAL_HINT = {
    "journal of accounting research": "JAR",
    "the accounting review": "TAR",
    "journal of accounting and economics": "JAE",
    "review of accounting studies": "RAST",
    "contemporary accounting research": "CAR",
    "journal of finance": "JF",
    "journal of financial economics": "JFE",
    "review of financial studies": "RFS",
}


# ---------------------------------------------------------------- frontmatter

def split_fm(text):
    """返回 (frontmatter行列表, 正文, 起始行号)。不是 frontmatter 就返回 None。"""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], lines[i + 1:], 1
    return None


def parse_fm(fm_lines):
    """极简解析：只认顶层 'key: value'。返回 {key: (行号, 原始值字符串)}。"""
    out = {}
    for idx, ln in enumerate(fm_lines):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(.*)$", ln)
        if m:
            out[m.group(1)] = (idx, m.group(2).strip())
    return out


def is_empty(val):
    return val in ("", "[]", '""', "''", "~", "null")


def yaml_escape(s):
    s = str(s).replace("\n", " ").strip()
    if re.search(r'[:#\[\]{}",]|^\s|\s$', s) or s == "":
        return '"' + s.replace('"', '\\"') + '"'
    return s


# ---------------------------------------------------------------- zotero

def zget(path, timeout=30):
    req = urllib.request.Request(ZOTERO + path,
                                 headers={"User-Agent": "fill-fm/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", errors="replace")
    return json.loads(body) if body.strip() else []


def zget_all(path, page=100, cap=20000):
    out, start = [], 0
    while start < cap:
        sep = "&" if "?" in path else "?"
        chunk = zget(f"{path}{sep}limit={page}&start={start}")
        if not chunk:
            break
        out += chunk
        if len(chunk) < page:
            break
        start += page
    return out


def citekey_of(d):
    for k in ("citationKey", "citekey", "citation_key"):
        if d.get(k):
            return d[k]
    m = re.search(r"Citation Key:\s*(\S+)", str(d.get("extra", "")))
    return m.group(1) if m else None


def build_index():
    items = zget_all("/api/users/0/items")
    idx = {}
    for it in items:
        d = it.get("data", {})
        ck = citekey_of(d)
        if ck:
            idx[ck] = d
    return idx


def facts_from(d):
    out = {}
    if d.get("title"):
        out["title"] = d["title"]

    creators = [c for c in d.get("creators", []) if c.get("creatorType") == "author"]
    names = [c.get("lastName") or c.get("name", "") for c in creators]
    names = [n for n in names if n]
    if names:
        out["authors"] = ", ".join(names)

    m = re.search(r"\b(1[89]\d{2}|20\d{2})\b", str(d.get("date", "")))
    if m:
        out["year"] = m.group(1)

    pub = d.get("publicationTitle") or d.get("repository") or ""
    if pub:
        out["journal"] = JOURNAL_HINT.get(pub.strip().lower(), pub.strip())

    it = d.get("itemType", "")
    if it in ("preprint", "manuscript", "report"):
        out["pub_status"] = "wp"
    elif it == "journalArticle" and d.get("publicationTitle"):
        out["pub_status"] = "published"

    return out


# ---------------------------------------------------------------- ollama

def ollama_up():
    try:
        urllib.request.urlopen(OLLAMA + "/api/tags", timeout=5)
        return True
    except Exception:
        return False


def ask_llm(model, title, abstract, need):
    prompt = (
        "You are extracting structured metadata from an accounting/finance "
        "research paper. Return ONLY a JSON object, no prose, no code fences.\n\n"
        f"Fields to fill: {', '.join(need)}\n"
        "Definitions:\n"
        "  setting = sample and period, e.g. 'US public firms 2010-2024'\n"
        "  data = data sources as a short comma-separated list\n"
        "  method = main empirical method, e.g. 'DiD', 'IV', 'RDD', 'OLS'\n"
        "  identification = the source of identifying variation, one clause\n"
        "  measure = the key constructed variable\n"
        "If a field cannot be determined from the text, use an empty string.\n"
        "Keep every value under 15 words.\n\n"
        f"TITLE: {title}\n\nTEXT:\n{abstract[:6000]}\n"
    )
    body = json.dumps({
        "model": model, "prompt": prompt, "stream": False,
        "options": {"temperature": 0},
    }).encode()
    req = urllib.request.Request(
        OLLAMA + "/api/generate", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.loads(r.read().decode())
    raw = resp.get("response", "").strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.M).strip()
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return {}
    try:
        got = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}
    return {k: v for k, v in got.items() if k in need and str(v).strip()}


# ---------------------------------------------------------------- main

def git_clean(root):
    try:
        r = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                           capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            return None
        return r.stdout.strip() == ""
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真的写盘（默认只预览）")
    ap.add_argument("--llm", action="store_true", help="用本地模型填判断字段")
    ap.add_argument("--model", default="qwen2.5:14b")
    ap.add_argument("--dir", default=str(LITDIR))
    args = ap.parse_args()

    litdir = Path(args.dir)
    if not litdir.is_dir():
        print(f"✗ 找不到目录 {litdir}")
        sys.exit(1)

    if args.apply:
        clean = git_clean(litdir)
        if clean is False:
            print("✗ git 工作区不干净。先 commit 当前状态再跑 --apply：")
            print(f"    git -C {litdir.parent} add -A && "
                  'git -C . commit -m "before fill_frontmatter"')
            sys.exit(1)
        elif clean is None:
            print("⚠ 这个目录不在 git 仓库里，出错无法回滚。")
            if input("  继续？[y/N] ").strip().lower() != "y":
                sys.exit(0)

    print("读取 Zotero…", flush=True)
    try:
        idx = build_index()
    except urllib.error.URLError as e:
        print(f"✗ 连不上 Zotero：{e}\n  → Zotero 开着吗？local API 勾了吗？")
        sys.exit(1)
    print(f"  {len(idx)} 个条目带 citekey")

    if args.llm:
        if not ollama_up():
            print(f"✗ Ollama 没在 {OLLAMA} 上响应。先 `ollama serve`。")
            sys.exit(1)
        print(f"  本地模型：{args.model}")

    files = sorted(litdir.glob("*.md"))
    print(f"  {len(files)} 个笔记文件\n")

    n_changed = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        parts = split_fm(text)
        if not parts:
            continue
        fm_lines, _, offset = parts
        fields = parse_fm(fm_lines)

        ck = fields.get("citekey", (None, ""))[1].strip().strip("\"'")
        if not ck:
            ck = f.stem
        d = idx.get(ck)
        if not d:
            print(f"  ? {f.name:40} citekey '{ck}' 在 Zotero 里找不到")
            continue

        empties = [k for k in FACT_FIELDS
                   if k in fields and is_empty(fields[k][1])]
        fills = {k: v for k, v in facts_from(d).items() if k in empties}

        if args.llm:
            need = [k for k in LLM_FIELDS if k in fields and is_empty(fields[k][1])]
            if need:
                abstract = d.get("abstractNote", "")
                if abstract.strip():
                    try:
                        got = ask_llm(args.model, d.get("title", ""), abstract, need)
                        for k, v in got.items():
                            fills[k] = f"?{v}"
                    except Exception as e:
                        print(f"  ! {f.name}: 模型调用失败 {e}")

        if not fills:
            continue

        n_changed += 1
        print(f"  ✎ {f.name}")
        for k, v in fills.items():
            print(f"      {k}: {str(v)[:60]}")

        if args.apply:
            new_fm = list(fm_lines)
            for k, v in fills.items():
                i = fields[k][0]
                new_fm[i] = f"{k}: {yaml_escape(v)}"
            lines = text.split("\n")
            lines[offset:offset + len(fm_lines)] = new_fm
            f.write_text("\n".join(lines), encoding="utf-8")

    print()
    if not args.apply:
        print(f"[DRY-RUN] {n_changed} 个文件将被修改。确认无误后加 --apply 重跑。")
    else:
        print(f"✓ 已修改 {n_changed} 个文件。")
        print("  带 '?' 前缀的值是模型猜的，确认后把 '?' 删掉。")
        print("  不满意就 git checkout . 回滚。")


if __name__ == "__main__":
    main()
