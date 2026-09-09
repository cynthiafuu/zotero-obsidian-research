# 研究工作流使用手册

日常操作手册。搭建过程已结束，这份只讲怎么用。
系统状态：Zotero 9.0.6 · Obsidian vault `~/Documents/research` · 18/18 验证通过
最后更新：2026-09-07

---

## 目录

- [0. 速查卡](#0-速查卡)
- [1. 读一篇论文的完整流程](#1-读一篇论文的完整流程)
- [2. iPad 上读](#2-ipad-上读)
- [3. Boox 上读](#3-boox-上读)
- [4. 写笔记：三档](#4-写笔记三档)
- [5. 记忆宫殿：概念卡与文献流](#5-记忆宫殿概念卡与文献流)
- [6. 每周整理](#6-每周整理)
- [7. 每月复盘](#7-每月复盘)
- [8. Claude 与 Claude Code 辅助](#8-claude-与-claude-code-辅助)
- [9. 脚本参考](#9-脚本参考)
- [10. 写作时](#10-写作时)
- [11. RA 项目](#11-ra-项目)
- [12. 排障](#12-排障)
- [13. 定期维护](#13-定期维护)

---

## 0. 速查卡

打印这一页贴在显示器边上。

### 快捷键

| 键 | 作用 |
|---|---|
| `Cmd+Shift+L` | 新建文献笔记（输 citekey） |
| `Cmd+O` | 快速打开任意文件（输 `@citekey` 直达 source note） |
| `Cmd+P` | 命令面板（ZotFlow 的所有命令都在这） |
| `Cmd+E` | 编辑/预览切换 |

### 高亮颜色（写死，永不改）

| 颜色 | 含义 |
|---|---|
| 黄 | 核心结论 |
| 红 | 识别策略、关键假设 |
| 绿 | 可复用方法、变量构造、数据源 |
| 蓝 | 制度背景 |
| **紫** | **我的质疑** ← 最值钱，是选题的原料 |

紫色的十六进制值是 `#a28ae5`，已验证与脚本一致。

### 目录职责

| 目录 | 谁写 | 单位 |
|---|---|---|
| `10-Literature/` | **只有你** | 一篇论文一个文件，名 = citekey |
| `15-Sources/My Library/` | ZotFlow 自动，**不要手改** | 名 = `@citekey` |
| `20-Concepts/` | 你 | 一个方法/测度/理论 |
| `30-Streams/` | 你 | 一场学术对话 |
| `50-Ideas/` | 你 | 一个想法 |
| `70-Meta/` | 你 + 脚本 | 模板、脚本、prompt、导出 |

---

## 1. 读一篇论文的完整流程

以 `kim2024bloated` 为例，走一遍全程。

### 1.1 打开

**不要在 Zotero Tree View 里翻**，几百条滚不动。用：

`Cmd+O` → 输 `@kim2024` → 回车

打开的是 `15-Sources/My Library/@kim2024bloated.md`，里面有元数据和附件链接，点附件进阅读器。

或者 `Cmd+P` → `ZotFlow` → 用它的搜索命令按标题找。

### 1.2 三遍法

**不要每篇都精读。** 95% 的论文停在第一遍。

| 遍 | 时间 | 做什么 |
|---|---|---|
| P1 | 10 分钟 | 标题、摘要、intro 最后两段、所有表格标题。判断值不值得往下 |
| P2 | 40 分钟 | identification strategy、关键变量构造、Table 1–3。**全部在 PDF 上用颜色高亮完成，不写外部笔记** |
| P3 | 2 小时+ | 只给和你方向直接相关的。读完必须回答：**"如果让我重做这篇，我会改什么？"** |

P3 那个问题是你未来 idea 的主要来源。答不出来说明这篇对你没用，降级成 P1。

### 1.3 标高亮

在 ZotFlow 的阅读器里标，8–12 处，**至少一处紫色**。

标注实时双向同步回 Zotero，也会同步到 iPad 和 Boox。

紫色标什么：你不认同的、逻辑跳跃的、样本可疑的、结论超出证据的、"这里应该做个稳健性检验但他们没做"的。**不要因为怕标错而不标**——半年后这批紫色标注会被 `export_purple.py` 汇总成选题清单，错的那些自然会在复盘时被筛掉。

### 1.4 建笔记

`Cmd+Shift+L` → 输入 citekey（如 `kim2024bloated`）→ 回车

笔记生成在 `10-Literature/`，第一行的 `[[@kim2024bloated]]` 自动链到 source note。

### 1.5 填 frontmatter

```yaml
citekey: kim2024bloated
title:                    # 留空，脚本会从 Zotero 自动补
authors:                  # 留空
year: 2024
journal: SSRN
draft_date: 2024-01-30    # 我读的是哪一版 ← 手填，Zotero 不存这个
pub_status: wp            # wp / forthcoming / published
status: read              # skim / read / deep
topic: [disclosure, AI-measure]
setting: US public firms 2010-2024
data: [EDGAR, transcripts]
method: DiD
identification: staggered adoption of X
measure: LLM-based tone score
finding: 一句话，因果方向写清楚
gap: 他们没做好的地方
rating: 4
added: 2026-09-07         # 自动
```

**`title` 和 `authors` 一定留空。** 攒够 30 篇后 `fill_frontmatter.py` 会从 Zotero 批量补，手打是浪费。

`draft_date` 和 `pub_status` **必须手填**——已验证 Zotero 不单独存 "This draft" 日期。你库里有 31 篇 working paper，这两个字段是防止你把未定稿的结论当定论引用的唯一保险。

### 1.6 写正文

```markdown
## 一句话
LLM 摘要显著降低了信息处理成本，长披露的信息含量被高估。

## 设计
- 样本 / 期间：
- 识别策略：
- 关键变量：
- 主结果（Table ?）：

## 我的评价
- **说服我的**：
- **没说服我的**：作者挂了 CAVEAT NOTICE，说数据、方法、
  结论正在重新评估。引用前必须回去核对最新版。
- **如果我来做**：

## 关联
- 方法：[[llm-as-measure]]
- 支持 / 反驳：[[loughran2011when]]
- 流：[[llm-information-cost]]
```

**正文只写你自己的话，禁止摘抄。** 原文留在 Zotero 高亮里，笔记只放你的判断。摘抄会让你产生"读懂了"的错觉。

「没说服我的」要和 PDF 里的紫色高亮对应。

### 1.7 验收

- 点开头的 `[[@kim2024bloated]]`，能跳到 source note
- 打开 `30-Streams/_ledger.md`，这篇出现在「All Literature」表里
- 如果 `pub_status: wp` 且 `rating >= 3`，它还会出现在「Working papers to re-check」表里

### 1.8 存档

装了 Obsidian Git 就不用管，每 30 分钟自动提交。手动的话：

```bash
cd ~/Documents/research && git add -A && git commit -m "note: kim2024bloated" && git push
```

---

## 2. iPad 上读

### 用什么

**只用 Zotero 官方 app。** 不要用 PDF Expert / MarginNote / GoodNotes——它们的批注不回流 Zotero，链条断在这里，你会白标。

### 流程

1. Zotero app 里找到论文（和桌面版同一个账号，自动同步）
2. Apple Pencil 按同一套颜色约定标
3. 回 Mac，Obsidian 里 `Cmd+P` → ZotFlow → Sync All
4. `Cmd+Shift+L` 建笔记

### 适合什么

精读（P2/P3）。Pencil 划线比鼠标准，适合逐段抠 identification。

### 不适合什么

写笔记。**Obsidian 移动端别装**——git 同步在 iOS 上要额外配 SSH key，收益不抵折腾。iPad 只读只标，笔记回 Mac 写。

### 离线

出门前在 app 里把要读的论文点开一次，PDF 会下到本地。飞机上照样标，落地联网自动同步。

---

## 3. Boox 上读

### 装什么

Zotero 官方 Android APK，从 `zotero.org/download/android/` 直接下（Boox 没有 Play Store）。配 Obtainium 可以自动更新。

移动端 app 版本独立，**可以随便更新**，不受"桌面版暂时不升 Zotero 10"那条限制。

### 适合什么

- 泛读（P1）：一口气扫十篇摘要和表格
- 教材、长 working paper
- 长时间阅读，护眼

### 不适合什么

- 需要精细定位的高亮（e-ink 触控延迟）
- 图表密集的论文

### 双栏 PDF 的痛点

Boox 屏幕上读双栏 JAR/TAR 很痛苦。Zotero 10 的 **Reading Mode** 能把 PDF 重排成可调字号的单栏，且重排视图里仍可高亮——这是升级 Zotero 10 的主要动机。

**但现在别升**（见第 13 节）。当前的替代方案：横屏 + 放大 + 单栏滚动，或者把这类论文留给 iPad。

---

## 4. 写笔记：三档

**所有读过的论文都建文件**，但成本必须分级，否则两个月后你会开始逃避读论文。

| `status` | 时间 | 填什么 |
|---|---|---|
| `skim` | 3 分钟 | 只填 `finding` 一行，正文全空。**就这样，不要有负罪感** |
| `read` | 15 分钟 | 补 `identification` `measure` `gap` + 「设计」段 |
| `deep` | 1 小时 | 全填，尤其「如果我来做」 |

### 为什么 skim 也要建文件

半年后你搜"谁用过 Incentive Lab 做 X"，靠的是 frontmatter 能被 Dataview 查到，不是靠你记得读过。

一个只有 `finding` 一行的 skim 笔记，成本 3 分钟，价值是让这篇论文永远可检索。

### 升级机制

笔记不是一次写完的。今天 skim 的论文，三个月后发现它和你的方向相关，就打开来补成 read 或 deep，把 `status` 改掉。

台账里「Read but not digested」那个查询专门抓这种：`rating >= 4` 但 `gap` 空着的——高分说明你当时觉得重要，`gap` 空着说明你还没想清楚它的价值。

---

## 5. 记忆宫殿：概念卡与文献流

文献笔记是砖，不是宫殿。**宫殿是 `20-Concepts/` 和 `30-Streams/`。**

### 5.1 概念卡（`20-Concepts/`）

每个文件 = 一个可复用单元。模板在 `70-Meta/templates/concept.md`。

```
20-Concepts/
├── methods/     staggered-did.md · iv-design.md · llm-as-measure.md
├── measures/    abnormal-accruals.md · tone-textual.md
├── theories/    agency.md · voluntary-disclosure.md
└── data/        edgar-fulltext.md · boardex.md · incentive-lab.md
```

内容结构：

```markdown
# Staggered DiD

## 是什么

## 什么时候用 / 什么时候不能用

## 常见做法与各自的批评
Goodman-Bacon 之后该怎么做，有哪些替代 estimator

## 我读过的用例
[[kim2024bloated]] · [[chen2024conducting]]

## 我自己踩过的坑
```

**什么时候建**：同一个方法在三篇不同论文里出现过，就建卡，把三篇都链进来。

**为什么这才是宫殿**：半年后你搜"staggered DiD"，看到的不是 30 篇论文，而是一张你自己写的、被 30 篇论文支撑的方法卡。

**`data/` 尤其重要**。你已经有 SEC filings、earnings-call transcripts、BoardEx、Compustat、Incentive Lab 的构建经验，那些踩过的坑、写过的脚本在哪，全写进 `data/` 卡片。两年后价值极高，而且是别人拿不走的资产。

### 5.2 文献流（`30-Streams/`）

一个文件 = 你给一场学术对话画的地图。模板在 `70-Meta/templates/stream.md`。

```markdown
# LLM 与信息处理成本

## 这场对话在争什么
核心命题：信息处理成本是不是信息不对称的真实来源？
如果 LLM 能近乎零成本地把冗长披露压缩成有用摘要，
那"披露冗余"本身就是一个可被技术消解的摩擦。

争议点：
1. LLM 摘要的信息含量，是抽取出来的还是生成出来的？
2. 用 GPT 做历史样本，有没有 look-ahead 污染？

## 演化线
词典法 [[loughran2011when]]
  → 有监督 ML [[li2010information]]
  → 生成式摘要 [[kim2024bloated]] ⚠️ 作者标注结论正在重估
  → ？

## 用到的工具
[[llm-as-measure]] · [[tone-textual]] · [[edgar-fulltext]]

## 我认为的空白
- 这批研究都在美国大公司样本上做，制度差异没被利用
- → [[idea-2026-09-07]]
```

**什么时候建**：读到某主题第 5–8 篇、发现它们在互相引用互相反驳时。硬凑出来的是空壳。

**自检信号**：写不出「这场对话在争什么」，说明你还没读懂这个流。这时候该回去重读，不是继续加论文。

**「演化线」和「我认为的空白」是全 vault 最值钱的两段**：前者是 literature review 的骨架，后者是 dissertation 的种子。

**数量**：第一年撑死 3–5 个 stream。多了说明在广撒网而不是找方向。

### 5.3 想法池（`50-Ideas/`）

一个想法一个文件，命名 `idea-2026-09-07.md` 或描述性名字。

每条至少写清四件事：

```markdown
# 制度差异下的 LLM 披露效应

## 观察
现有研究全在美国大公司样本上做

## 为什么没人做
可能是数据难拿，也可能是有人做过我没读到 ← 待查

## 可行的数据
中国 A 股年报全文 + 同期 LLM 可得性

## 卡在哪
identification：LLM 普及是全球同时发生的，
没有天然的处理组/对照组
```

**「卡在哪」这一栏最重要。** 大部分 idea 死在这里，写下来能让你判断值不值得继续。

### 5.4 可视化

用 Excalidraw 画文献流的关系图（谁反驳谁、identification 怎么演化），画完嵌进 stream 文件。

比在脑子里想清楚得多，而且半年后还能看懂。

---

## 6. 每周整理

**周五 30 分钟。** 固定时间，别拖到"有空的时候"。

1. **清空 Zotero 的 `00-Inbox` collection** —— 这周抓的论文归到 Streams 或 Courses
2. **清空 Obsidian 的 `00-Inbox` 目录** —— 碎片想法归位到 `50-Ideas` 或相应笔记
3. **补完本周 `deep` 档的笔记** —— 尤其「如果我来做」那一栏
4. **看台账的「Read but not digested」表** —— 高分但 `gap` 空着的，补上或者降 rating
5. **确认 git 已推送**：

```bash
cd ~/Documents/research && git status && git log --oneline -5
```

---

## 7. 每月复盘

### 7.1 紫色标注 → 选题

```bash
cd ~/Documents/research/70-Meta/scripts
python3 export_purple.py
```

输出：`70-Meta/exports/purple-<日期>.md`，按论文分组，带页码、你的批注和 tag。

把这个文件连同 `70-Meta/prompts/02-purple-analysis.md` 一起丢给 Claude。

那个 prompt 里有一句「不要安慰我，不要把每一条都说成有潜力」——**别删**。不加这句，模型会把你四十条随手记的疑惑全捧成研究空白。

其他用法：

```bash
python3 export_purple.py --all-colors          # 全部颜色，按色标注
python3 export_purple.py --color "#5fb236"     # 只导绿色（可复用方法）
```

绿色那条在你要写方法部分、或者建 `20-Concepts/methods/` 卡片时很有用。

### 7.2 台账体检 → 找空格

把 `10-Literature/` 全部文件拖进 Claude 对话，配 `70-Meta/prompts/03-ledger-audit.md`。

它会做 topic × method 交叉表并指出空格。**空格就是选题。**

同时会揪出 `pub_status: wp` 且 `draft_date` 超过 18 个月的——那 31 篇 working paper 里，肯定有已经发表、改了结论、甚至撤回的。

### 7.3 复跑验证

```bash
cd ~/Documents/research/70-Meta/scripts && python3 verify_setup.py
```

第 8 项会检查你所有笔记的 citekey 能否对上 Zotero。有对不上的，说明某处 citekey 被改过或论文被删了。

---

## 8. Claude 与 Claude Code 辅助

分工原则：**Claude Code 动文件，Claude 对话动脑子。**

### 8.1 Claude 对话（用 `70-Meta/prompts/` 里的四个）

| prompt | 什么时候用 | 附带什么 |
|---|---|---|
| `01-after-reading.md` | 读完一篇 deep 档 | 那篇的全部高亮 |
| `02-purple-analysis.md` | 每月 | `exports/purple-*.md` |
| `03-ledger-audit.md` | 每月 | `10-Literature/` 全部文件 |
| `04-before-writing.md` | 写 lit review 前 | 某个 stream 的全部笔记 |

这四个文件在 vault 里，随时可以改。改的时候保留那些约束性句子（"不要安慰我"、"指出不确定的地方"），它们是防止模型讨好你的。

### 8.2 Claude Code（在 vault 目录下启动）

**动文件前先 commit。** 这是让 agent 碰你笔记的前提条件，出问题 `git checkout .` 一键回滚。

几个可复用的 prompt：

**批量整理 frontmatter 格式**

```
工作目录 ~/Documents/research

扫描 10-Literature/ 下所有 .md，检查 frontmatter 的一致性问题：
1. 字段顺序和 70-Meta/templates/lit-note.md 不一致的
2. topic 字段写成字符串而不是数组的
3. pub_status 值不在 {wp, forthcoming, published} 里的
4. year 不是四位数字的
5. 缺字段或多出模板里没有的字段的

只报告，不修改。输出成表格，每行一个文件一个问题。

硬约束：不修改任何文件，不碰 ~/Zotero。
```

**从笔记反向生成概念卡骨架**

```
工作目录 ~/Documents/research

读 10-Literature/ 下所有笔记的 frontmatter，统计 method 字段的取值分布。

对出现 3 次以上的 method，检查 20-Concepts/methods/ 下有没有对应的卡片。
没有的话，列出来，并告诉我哪几篇笔记用了这个方法。

只报告，不要替我创建卡片 —— 概念卡必须我自己写，
那是我的判断，不是汇总。
```

**找断链**

```
工作目录 ~/Documents/research

检查所有 [[wiki链接]] 是否指向真实存在的文件。
列出所有断链，注明出现在哪个文件的第几行。

注意：15-Sources/ 下的文件名带 @ 前缀，
10-Literature/ 下的不带，别把这个当成错误。

只报告，不修复。
```

### 8.3 硬约束模板

给 Claude Code 的每个 prompt 都带上：

```
硬约束：
- 绝不修改 ~/Zotero 下任何内容
- 绝不直接读写 zotero.sqlite（Zotero 运行时会损坏数据库），
  需要 Zotero 数据一律走本地 API http://127.0.0.1:23119
- 修改 10-Literature/ 前先 git commit
- 不安装任何依赖
- 不 git push
```

### 8.4 什么不要交给 AI

- **概念卡的正文** —— 那是你的判断，代写等于没有
- **「如果我来做」那一栏** —— 这是你 idea 的来源，外包了就没有 idea
- **stream 的「这场对话在争什么」** —— 写不出来说明没读懂，让 AI 写只会掩盖这一点

AI 适合做的是汇总、检查一致性、找模式、指出空格。**判断必须是你的。**

---

## 9. 脚本参考

全部在 `70-Meta/scripts/`。**都只读 Zotero，不碰 `zotero.sqlite`。**

### `verify_setup.py`

```bash
python3 verify_setup.py
```

18 项检查，验证其他脚本的全部假设在你真实数据上是否成立。
换电脑后、Zotero 大版本升级后、脚本改动后跑一次。全程只读。

### `export_purple.py`

```bash
python3 export_purple.py                    # 紫色（默认）
python3 export_purple.py --all-colors       # 全部颜色
python3 export_purple.py --color "#5fb236"  # 指定颜色
```

每月跑。输出到 `70-Meta/exports/`。

### `fill_frontmatter.py`

**攒够 30 篇笔记后才用。** 提前用你不知道该抽哪些字段。

```bash
python3 fill_frontmatter.py                 # 预览，不写盘
python3 fill_frontmatter.py --apply         # 只填事实字段（不需要模型）
python3 fill_frontmatter.py --llm --apply   # 加上模型推断（需要 Ollama）
```

分工：
- `title` / `authors` / `year` / `journal` / `pub_status` → **直接从 Zotero 取，不经过模型**
- `setting` / `data` / `method` / `identification` / `measure` → 只有 `--llm` 才填，且值前加 `?` 前缀

`?` 前缀让你一眼分清哪些是机器猜的。确认后删掉 `?`，台账第四个查询会自动把它移出待确认列表。

安全设计（已实测）：默认 dry-run；绝不覆盖非空字段；**绝不改动 frontmatter 以外的正文**；`--apply` 前检查 git 是否干净；重复跑幂等。

⚠️ `--llm` 那条路径是唯一没被验证过的部分（需要 Ollama）。9/22 之后先 dry-run。

### `backup_zotero.sh`

```bash
bash backup_zotero.sh                  # 存到桌面
bash backup_zotero.sh /Volumes/外置盘   # 存到指定位置
```

Zotero 在运行会直接拒绝（运行时打包得到的是损坏副本）。自动保留最近 3 份。

**每学期一次，或每次批量操作前跑一次。** 打完拖进云盘——放在同一块盘上的备份不算备份。

### `zotero_probe.py`

诊断工具。Zotero 升级后、脚本行为异常时跑，看字段结构有没有变。

---

## 10. 写作时

### 引用

`70-Meta/library.bib` 由 BBT 自动保持更新（勾了 Keep updated），Zotero 里加一篇它就自动同步。

- **Overleaf**：把 `library.bib` 传上去，或者用 Overleaf 的 GitHub 同步直接连你的 repo
- **Pandoc**：`--bibliography=70-Meta/library.bib`
- **Word**：Zotero 的 Word 插件，不走 bib

在 Obsidian 里写作时，ZotFlow 支持 `@@` 触发引用自动补全，可以插入 Pandoc 格式 `[@kim2024bloated]` 或 wikilink 格式。

### 引用前的检查

**每次引用 working paper 前，打开台账的「Working papers to re-check」表。** 你库里有 31 篇 wp，两年前存的那些现在很可能已经发表、改了结论。

把 working paper 的结论当定论引用，是 PhD 前两年最常见的翻车方式。

### 写 literature review

1. 打开对应的 stream 文件，「演化线」就是骨架
2. 用 `70-Meta/prompts/04-before-writing.md`，附上该 stream 的全部笔记
3. 让它给结构和每段论点，**正文自己写**

---

## 11. RA 项目

### Group library

每个 RA 项目让教授开一个 Zotero group library，你加入。

好处：
- 文献和高亮共享，不用来回发 PDF
- 你的贡献可见
- ZotFlow 支持多库，Sync 设置里可以给每个库单独设 Bidirectional / Read-Only / Ignored

ZotFlow 的路径模板是 `15-Sources/{{libraryName}}/...`，所以 group library 的 source note 会自动进 `15-Sources/<项目名>/`，和个人库分开。这就是当初保留 `{{libraryName}}` 那一段的原因。

### 项目笔记

`40-Projects/<项目名>/` 下建目录，放会议记录、任务清单、代码位置索引。

**教授的未公开草稿、项目原始数据不要上传到你的 GitHub repo。** 你的 vault 是 private 的，但仍然建议敏感材料只放本地——在 `.gitignore` 里加一行：

```
40-Projects/*/confidential/
```

---

## 12. 排障

| 症状 | 原因 / 处理 |
|---|---|
| 台账四个表全空 | 笔记不在 `10-Literature/`。检查 QuickAdd 的 Folder 设置 |
| 单篇笔记不出现在台账 | frontmatter 的 `---` 必须在**文件第一行**；或字段名拼错 |
| Dataview 数组字段查不到 | `topic: [a, b]` 要用 `contains(topic, "a")`，不能用 `topic = "a"` |
| 新建笔记文件名带空格 | QuickAdd 的 File Name Format 里有多余空格，全选删掉重输 `{{VALUE:citekey}}` |
| `[[@citekey]]` 是灰的 | source note 没生成，或 citekey 拼错。`Cmd+P` → ZotFlow → Sync All |
| Obsidian 标注没回到 Zotero | 该库在 ZotFlow 里被设成 Read-Only，改成 Bidirectional |
| ZotFlow 里 PDF 打不开 | Zotero 附件没同步上去；检查 Zotero → Settings → Sync 的存储用量 |
| 脚本报连不上 Zotero | Zotero 没开；或 Settings → Advanced 的 local API 没勾；勾完要重启 Zotero |
| `export_purple.py` 导出 0 条 | 该颜色没有标注。用 `--all-colors` 看实际分布 |
| `fill_frontmatter.py` 拒绝运行 | git 工作区不干净，先 commit |
| citekey 变了导致链接断 | 你全库刷新了 key。**永远只刷改动过的单条** |
| Zotero 自动升到 10 | 先测 BBT 还能不能用。不能就只是暂时失去 `.bib` 自动导出，笔记和链接不受影响 |

### 万能回滚

```bash
cd ~/Documents/research
git status                    # 看改了什么
git checkout .                # 丢弃所有未提交的改动
git log --oneline -10         # 看历史
git checkout <commit> -- 路径  # 恢复某个文件到某个版本
```

---

## 13. 定期维护

### 每学期

```bash
bash ~/Documents/research/70-Meta/scripts/backup_zotero.sh
```

打完拖进云盘。

### 隔几周查一次

去 `github.com/retorquere/zotero-better-bibtex/releases` 看最新发版说明。

**当它明确写出支持 Zotero 10 时，才升级 Zotero。** 当前（v9.0.63, 2026-08-26）措辞仍是"兼容 Zotero 8 和 Zotero 9 beta"。

升级后能拿到：PDF Reading Mode（重排单栏，解决 Boox 读双栏的痛点）、标注级高级搜索（嵌套条件、按结果层级检索）。

### 换电脑 / 大升级后

```bash
cd ~/Documents/research/70-Meta/scripts && python3 verify_setup.py
```

18/18 才继续用脚本。

### 9/22 Mac mini 到货后

**在此之前不要做。**

1. 迁移 Zotero 数据目录 + 整个 vault，Mac mini 做主机，笔记本走 Zotero Sync + `git pull`
2. 装 Ollama。**选配置时直接上 32GB** —— 统一内存出厂不可加装，16GB 只能舒服跑 7–8B，喂整篇论文的长上下文会撞内存墙
3. 装 Obsidian 插件 **Smart Connections**，本地 embedding 把 `10-Literature` + `20-Concepts` 向量化 → 全库语义检索
4. 笔记攒到 30 篇以上后，用 `fill_frontmatter.py --llm`

本地 vs 云端分工：

| 任务 | 跑在哪 |
|---|---|
| 全库语义检索（embedding） | 本地，模型很小 |
| 批量抽字段填 frontmatter | 本地 |
| 教授的未公开草稿、RA 原始数据 | **必须本地** |
| 手写推导、seminar 录音转录 | 本地 |
| 跨 30 篇的综合、identification 批判 | Claude |
| gap analysis、写作、写脚本 | Claude |

---

## 附：一句话总结

**每天**：读 → 标（至少一处紫色）→ `Cmd+Shift+L` → 按三档填

**每周五**：清 inbox、补 deep 笔记、看「Read but not digested」

**每月**：`export_purple.py` → Claude 找选题；台账体检 → 找空格

**攒到 5–8 篇同主题**：建 stream

**同一方法出现 3 次**：建概念卡

系统的事到此为止。剩下的是读论文。
