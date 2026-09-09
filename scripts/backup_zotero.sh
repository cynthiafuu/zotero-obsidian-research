#!/usr/bin/env bash
# backup_zotero.sh — 安全打包 Zotero 数据目录。
#
# 比裸 tar 多做三件事：
#   1. 检查 Zotero 是否在运行（运行时打包会得到损坏的数据库，且你不会立刻发现）
#   2. 检查产物体积，异常小就报警
#   3. 自动清理超过 90 天的旧备份，只保留最近 3 份
#
# 用法：
#   bash backup_zotero.sh                 # 存到桌面
#   bash backup_zotero.sh /Volumes/外置盘  # 存到指定位置

set -euo pipefail

DATA_DIR="$HOME/Zotero"
DEST="${1:-$HOME/Desktop}"
STAMP="$(date +%F)"
OUT="$DEST/zotero-backup-$STAMP.tar.gz"

# ---- 1. Zotero 必须是关闭的 ----
if pgrep -x "Zotero" > /dev/null 2>&1 || pgrep -f "Zotero.app" > /dev/null 2>&1; then
  echo "✗ Zotero 正在运行。"
  echo ""
  echo "  数据库正在被写入时打包，得到的副本可能已损坏，"
  echo "  而且损坏往往要到你真正需要恢复时才发现。"
  echo ""
  echo "  请先按 Cmd+Q 完全退出 Zotero（关窗口不算），再重跑。"
  exit 1
fi

# ---- 2. 目录得存在 ----
if [ ! -d "$DATA_DIR" ]; then
  echo "✗ 找不到 $DATA_DIR"
  echo "  如果你改过数据目录位置："
  echo "  Zotero → Settings → Advanced → Files and Folders 看实际路径，"
  echo "  然后改本脚本顶部的 DATA_DIR。"
  exit 1
fi

if [ ! -f "$DATA_DIR/zotero.sqlite" ]; then
  echo "✗ $DATA_DIR 里没有 zotero.sqlite，这不像是 Zotero 数据目录。"
  exit 1
fi

mkdir -p "$DEST"

if [ -e "$OUT" ]; then
  OUT="$DEST/zotero-backup-$STAMP-$(date +%H%M).tar.gz"
fi

echo "→ 打包 $DATA_DIR"
echo "  目标 $OUT"
echo "  （库大的话要几分钟）"

tar -czf "$OUT" -C "$HOME" "$(basename "$DATA_DIR")"

# ---- 3. 体积检查 ----
BYTES=$(stat -f%z "$OUT" 2>/dev/null || stat -c%s "$OUT")
HUMAN=$(du -h "$OUT" | cut -f1)

echo ""
if [ "$BYTES" -lt 1048576 ]; then
  echo "⚠ 警告：产物只有 $HUMAN，小得可疑。"
  echo "  确认一下 $DATA_DIR 里是不是真的有东西。"
  exit 1
fi
echo "✓ 完成，$HUMAN"

# ---- 4. 轮换 ----
COUNT=$(ls -1t "$DEST"/zotero-backup-*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
if [ "$COUNT" -gt 3 ]; then
  echo ""
  echo "  清理旧备份（保留最近 3 份）："
  ls -1t "$DEST"/zotero-backup-*.tar.gz | tail -n +4 | while read -r old; do
    echo "    删除 $(basename "$old")"
    rm -f "$old"
  done
fi

echo ""
echo "记得把它拖进云盘或外置硬盘 —— 放在同一块盘上的备份不算备份。"
