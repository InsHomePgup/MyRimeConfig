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
            if pgrep -x fcitx5 &>/dev/null; then
                echo "linux-fcitx5"
            elif pgrep -x ibus-daemon &>/dev/null || [ -d ~/.config/ibus/rime ]; then
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
        ;;
    linux-ibus)
        RIME_DIR="$HOME/.config/ibus/rime"
        ;;
    linux-fcitx5)
        RIME_DIR="$HOME/.local/share/fcitx5/rime"
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

# 同步文件。--delete 会清掉 repo 里已删除的文件，
# 但被 exclude 的路径不会被删，用户词库、同步目录等都靠这里保住
if command -v rsync &>/dev/null; then
    rsync -a --delete \
        --exclude='.git/' \
        --exclude='.gitignore' \
        --exclude='deploy.sh' \
        --exclude='deploy.ps1' \
        --exclude='LICENSE' \
        --exclude='*.md' \
        --exclude='build/' \
        --exclude='sync/' \
        --exclude='*.userdb/' \
        --exclude='*.userdb.txt' \
        --exclude='user.yaml' \
        --exclude='installation.yaml' \
        "$REPO_DIR/" "$RIME_DIR/"
else
    # 没有 rsync 时只覆盖、不删除
    echo ">>> 未找到 rsync，改用 tar 直接复制（repo 中已删除的文件不会从目标目录移除）"
    tar -C "$REPO_DIR" -cf - \
        --exclude='./.git' \
        --exclude='./.gitignore' \
        --exclude='./deploy.sh' \
        --exclude='./deploy.ps1' \
        --exclude='./LICENSE' \
        --exclude='*.md' \
        --exclude='./build' \
        . | tar -xf - -C "$RIME_DIR"
fi

echo ">>> 文件同步完成"

# 重新部署
SQUIRREL="/Library/Input Methods/Squirrel.app/Contents/MacOS/Squirrel"
case "$PLATFORM" in
    macos)
        if [ -x "$SQUIRREL" ]; then
            echo ">>> 触发重新部署..."
            "$SQUIRREL" --reload
        else
            echo ">>> 未找到鼠须管，请手动点击「重新部署」"
        fi
        ;;
    linux-ibus)
        if command -v ibus &>/dev/null; then
            echo ">>> 重启 ibus（ibus-rime 启动时会重新部署有变动的文件）..."
            ibus restart
        else
            echo ">>> 未找到 ibus，请手动重新部署"
        fi
        ;;
    linux-fcitx5)
        if command -v fcitx5-remote &>/dev/null; then
            echo ">>> 重新加载 fcitx5..."
            fcitx5-remote -r
        else
            echo ">>> 未找到 fcitx5-remote，请手动重新部署"
        fi
        ;;
esac

echo ">>> 完成！"
