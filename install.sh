#!/bin/bash
# OpenClaw Skills 一键安装脚本
# 用法: bash install.sh

set -e

SKILLS_DIR="$HOME/.openclaw/workspace/skills"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== OpenClaw Skills 安装器 ==="
echo ""

# 创建 skills 目录
mkdir -p "$SKILLS_DIR"

# 安装每个 skill
for skill_dir in "$SCRIPT_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    
    # 跳过隐藏目录和非 skill 目录
    if [[ "$skill_name" == .* ]] || [[ ! -f "$skill_dir/SKILL.md" ]]; then
        continue
    fi
    
    echo "安装 $skill_name ..."
    
    # 复制 skill 到目标目录
    rm -rf "$SKILLS_DIR/$skill_name"
    cp -r "$skill_dir" "$SKILLS_DIR/$skill_name"
    
    echo "  ✅ $skill_name 安装完成"
done

echo ""

# 检查 Python 依赖
echo "检查 Python 依赖..."
if command -v python3 &> /dev/null; then
    echo "  ✅ Python3 已安装"
else
    echo "  ❌ 缺少 Python3，请先安装"
    exit 1
fi

# 安装 Python 包
echo "安装 Python 包..."
pip3 install tushare pandas --break-system-packages -q 2>/dev/null || pip3 install tushare pandas -q 2>/dev/null || echo "  ⚠️ pip 安装失败，请手动安装 tushare 和 pandas"

echo ""
echo "=== 安装完成！==="
echo ""
echo "还需要配置 API Keys："
echo "  export TAVILY_API_KEY=\"你的key\""
echo "  export TUSHARE_TOKEN=\"你的token\""
echo ""
echo "配置好后重启 OpenClaw："
echo "  openclaw gateway restart"
