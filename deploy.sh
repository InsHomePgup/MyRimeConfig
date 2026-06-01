#!/usr/bin/env bash
# 将此 repo 的配置部署到当前平台的 Rime 配置目录
# 用法: ./deploy.sh [macos|linux-ibus|linux-fcitx5]

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# 自动检测平台（也可手动传参）
detect_platform() {
    case "$OSTYPE" in
        darwin*) echo "macos" ;;
        linux*)
            if pgrep -x ibus-daemon &>/dev/null || [ -d ~/.config/ibus/rime ]; then
                echo "linux-ibus"
            else
                echo "linux-fcitx5"
            fi
            ;;
        msys*|cygwin*|win32) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

PLATFORM="${1:-$(detect_platform)}"

case "$PLATFORM" in
    macos)
        RIME_DIR="$HOME/Library/Rime"
        REDEPLOY_CMD="/Library/Input Methods/Squirrel.app/Contents/MacOS/Squirrel --reload"
        ;;
    linux-ibus)
        RIME_DIR="$HOME/.config/ibus/rime"
        REDEPLOY_CMD="ibus restart"
        ;;
    linux-fcitx5)
        RIME_DIR="$HOME/.local/share/fcitx5/rime"
        REDEPLOY_CMD="fcitx5-remote -r"
        ;;
    windows)
        echo "Windows 请在 PowerShell 中运行 deploy.ps1"
        exit 1
        ;;
    *)
        echo "未知平台: $PLATFORM"
        echo "用法: $0 [macos|linux-ibus|linux-fcitx5]"
        exit 1
        ;;
esac

echo ">>> 部署平台: $PLATFORM"
echo ">>> 目标目录: $RIME_DIR"

mkdir -p "$RIME_DIR"

# 同步文件（排除 .git、部署脚本本身、LICENSE）
rsync -av --delete \
    --exclude='.git/' \
    --exclude='deploy.sh' \
    --exclude='deploy.ps1' \
    --exclude='LICENSE' \
    --exclude='*.md' \
    --exclude='build/' \
    "$REPO_DIR/" "$RIME_DIR/"

echo ">>> 文件同步完成"

# 重新部署
if command -v "$REDEPLOY_CMD" &>/dev/null 2>&1 || [ -f "${REDEPLOY_CMD%% *}" ]; then
    echo ">>> 触发重新部署..."
    eval "$REDEPLOY_CMD" 2>/dev/null || echo "    (请手动点击「重新部署」)"
else
    echo ">>> 请手动触发 Rime 重新部署"
fi

echo ">>> 完成！"
