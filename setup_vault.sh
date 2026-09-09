#!/usr/bin/env bash
# setup_vault.sh — 一次性搭好 Obsidian 研究 vault 的全部骨架。
#
# 用法：
#   把本文件和 zotero_probe.py / export_purple.py / fill_frontmatter.py /
#   backup_zotero.sh 放在同一个文件夹里，然后：
#
#       bash setup_vault.sh ~/Documents/research
#
# 幂等：已存在的文件不会被覆盖，重复跑安全。

set -euo pipefail

VAULT="${1:-$HOME/Documents/research}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "→ vault 位置：$VAULT"

case "$VAULT" in
  *[Ii]cloud*|*"Mobile Documents"*)
    echo "✗ 拒绝在 iCloud 目录里建 vault。"
    echo "  Obsidian 的 .obsidian 配置目录会被 iCloud 反复覆盖，是已知的踩坑点。"
    echo "  换个位置，同步用 git。"
    exit 1 ;;
esac

mkdir -p "$VAULT"
cd "$VAULT"

# ---------------------------------------------------------------- 1. 目录
mkdir -p 00-Inbox 10-Literature 15-Sources \
         20-Concepts/{methods,measures,theories,data} \
         30-Streams 40-Projects 50-Ideas 60-Courses \
         70-Meta/{templates,scripts,prompts,exports} 90-Attachments
echo "✓ 目录结构"

# 说明文件，防止空目录被 git 忽略、也提醒自己每层放什么
write_if_absent() {  # $1=路径  stdin=内容
  if [ -e "$1" ]; then echo "  · 跳过已存在 $1"; else cat > "$1"; echo "  + $1"; fi
}

write_if_absent 15-Sources/README.md <<'EOF'
# 15-Sources —— 机器写的，不要手改

这个目录里的文件由 ZotFlow 自动生成，并且会被它**持续重新渲染**。
你在这里写的任何东西迟早会被覆盖。

你的判断、质疑、延伸，一律写在 `10-Literature/` 里。
那边的文件插件永不触碰。

这里的内容全部可以一键重建；那边的不能。
EOF

write_if_absent 20-Concepts/README.md <<'EOF'
# 20-Concepts —— 记忆宫殿的房间

文献笔记是砖，这里是房间。每个文件 = 一个可复用的单元：

- methods/   staggered-did.md, iv-design.md, ml-measurement.md
- measures/  abnormal-accruals.md, tone-textual.md
- theories/  agency.md, voluntary-disclosure.md
- data/      edgar-fulltext.md, boardex.md, incentive-lab.md

data/ 尤其重要：把踩过的坑、写过的脚本位置记下来，两年后价值极高。
EOF

# ---------------------------------------------------------------- 2. 模板
write_if_absent 70-Meta/templates/lit-note.md <<'EOF'
---
citekey: {{VALUE:citekey}}
title: 
authors: 
year: 
journal: 
draft_date: 
pub_status: wp
status: skim
topic: []
setting: 
data: []
method: 
identification: 
measure: 
finding: 
gap: 
rating: 
added: {{DATE:YYYY-MM-DD}}
---

> 原始条目与全部标注：[[{{VALUE:citekey}}-source]]

## 一句话


## 设计
- 样本 / 期间：
- 识别策略：
- 关键变量：
- 主结果（Table ?）：

## 我的评价
- **说服我的**：
- **没说服我的**：
- **如果我来做**：

## 关联
- 方法：
- 支持 / 反驳：
- 流：
EOF

write_if_absent 70-Meta/templates/stream.md <<'EOF'
# {{VALUE:流的名字}}

## 这场对话在争什么


争议点：
1. 
2. 

## 演化线


## 用到的工具


## 我认为的空白

EOF

write_if_absent 70-Meta/templates/concept.md <<'EOF'
# {{VALUE:概念名}}

## 是什么


## 什么时候用 / 什么时候不能用


## 常见做法与各自的批评


## 我读过的用例


## 我自己踩过的坑

EOF

# ---------------------------------------------------------------- 3. 台账
write_if_absent 30-Streams/_台账.md <<'EOF'
# 全部文献

```dataview
TABLE year, journal, method, status, finding, pub_status
FROM "10-Literature"
SORT added DESC
```

## 需要回头核对版本的 working paper

引用之前扫一眼，看有没有已经发表、改了结论、或者撤回的。

```dataview
TABLE draft_date, finding
FROM "10-Literature"
WHERE pub_status = "wp" AND rating >= 3
SORT draft_date ASC
```

## 读了但还没消化的（gap 空着的高分论文）

```dataview
TABLE year, method, finding
FROM "10-Literature"
WHERE rating >= 4 AND (gap = null OR gap = "")
```

## 待确认的机器猜测

frontmatter 里带 "?" 前缀的值是 fill_frontmatter.py 猜的，需要你确认后删掉前缀。

```dataview
TABLE method, setting, identification
FROM "10-Literature"
WHERE contains(string(method), "?") OR contains(string(setting), "?")
   OR contains(string(identification), "?")
```
EOF

# ---------------------------------------------------------------- 4. prompts
write_if_absent 70-Meta/prompts/01-读完一篇后.md <<'EOF'
# 读完一篇后（贴进 Claude 对话，连同你的高亮）

以下是我从一篇会计/金融论文里摘出的高亮，按颜色分组：
黄=核心结论 红=识别策略 绿=可复用方法 蓝=制度背景 紫=我的质疑

<粘贴高亮>

请做三件事，不要复述论文内容：

1. 用两句话说清这篇的识别策略到底靠什么变异，以及这个变异的最大威胁是什么
2. 我的紫色质疑里，哪些是我没读懂（指出我该重读哪一段），
   哪些是文献确实没解决的
3. 如果我要在这篇基础上做一个延伸，最省力且最可能有贡献的方向是什么，
   需要什么数据

如果这篇的贡献其实很薄，直接说，不要找补。
EOF

write_if_absent 70-Meta/prompts/02-紫色标注分析.md <<'EOF'
# 紫色标注分析（每月一次，连同 70-Meta/exports/紫-*.md）

这是我在 N 篇会计/金融论文里标记的全部疑问（紫色 = 我不认同或没想通的地方）。

请：

1. 找出反复出现的模式 —— 同一类质疑在不同论文里出现了几次，分别是哪几篇
2. 把它们分成两类：
   (a) 我当时没读懂 —— 指出我该去读什么补上
   (b) 文献里确实没解决
3. 从 (b) 里挑最多 3 个，判断够不够得上一篇 paper。
   每个说清：需要什么数据、识别策略可能是什么、最大的障碍是什么
4. 明确指出哪些质疑其实已经有文献回答了，我应该去读哪篇

不要安慰我，不要把每一条都说成有潜力。
按经验大部分应该落在 (a)。如果确实没有够格的选题，直接说没有。
EOF

write_if_absent 70-Meta/prompts/03-台账体检.md <<'EOF'
# 台账体检（每月一次，把 10-Literature/ 全部文件拖进对话）

这是我读过的全部论文笔记，每个文件的 frontmatter 是结构化字段。

1. 按 topic × method 做交叉表，标出每格的论文数
2. 指出空格和只有 1 篇的格。区分两种情况，不确定就说不确定：
   - 文献里真的没人做
   - 只是我还没读到
3. 列出 gap 非空且 rating >= 4 的论文，按 gap 的相似度聚类，
   每一类给一个概括
4. 找出 pub_status 是 wp 且 draft_date 早于 18 个月前的，
   这些我需要回去查是否已发表、改了结论、或撤回
5. 指出我的阅读结构上的偏食：方法过于集中在哪、哪类证据我几乎没读过

不要给"建议多读文献"这类话。给具体的格子和具体的论文。
EOF

write_if_absent 70-Meta/prompts/04-写作前.md <<'EOF'
# 写 literature review 之前

附件是我某个 stream 的全部文献笔记。

1. 把它们排成一条演化线：谁提出、谁反驳、谁改进、现在卡在哪
2. 指出这条线上被反复引用但我笔记里没有的论文（可能是我漏读的经典）
3. 起草 literature review 的段落结构 —— 只要结构和每段的论点，
   不要替我写正文
4. 指出我的 finding 字段里有没有互相矛盾的记录，如果有，
   告诉我该回去核对哪两篇

引用一律用 citekey，不要写作者全名。
EOF

echo "✓ 模板、台账、prompts"

# ---------------------------------------------------------------- 5. 脚本
for s in zotero_probe.py export_purple.py fill_frontmatter.py backup_zotero.sh; do
  if [ -f "$SRC/$s" ]; then
    if [ -e "70-Meta/scripts/$s" ]; then
      echo "  · 跳过已存在 70-Meta/scripts/$s"
    else
      cp "$SRC/$s" "70-Meta/scripts/$s"
      chmod +x "70-Meta/scripts/$s"
      echo "  + 70-Meta/scripts/$s"
    fi
  else
    echo "  ⚠ 没在 $SRC 找到 $s，跳过"
  fi
done

# ---------------------------------------------------------------- 6. git
if [ ! -d .git ]; then
  git init -q
  cat > .gitignore <<'EOF'
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.DS_Store
.trash/
70-Meta/scripts/__pycache__/
70-Meta/scripts/probe_sample.json
EOF
  git add -A
  if git config user.email > /dev/null 2>&1 || git config --global user.email > /dev/null 2>&1; then
    git commit -qm "init: vault skeleton"
    echo "✓ git 仓库已初始化并首次提交"
  else
    echo "⚠ git 仓库已初始化，但没提交 —— git 身份还没配。"
    echo "  跑这两行，然后 git commit -m 'init'："
    echo "    git config --global user.name  \"你的名字\""
    echo "    git config --global user.email \"你的邮箱\""
    GIT_PENDING=1
  fi
else
  echo "  · git 仓库已存在，跳过"
fi

echo
echo "════════════════════════════════════════════"
echo "完成。接下来手动做这几件（GUI，脚本代不了）："
echo "  1. Obsidian 打开这个文件夹作为 vault"
echo "  2. 装插件：ZotFlow / Dataview / QuickAdd / Obsidian Git / Excalidraw"
echo "  3. ZotFlow 填 API key，source note 输出目录设为 15-Sources"
echo "  4. QuickAdd 绑定 lit-note.md 模板到 Cmd+Shift+L"
echo "详见随附的《攻略》第二部分。"
