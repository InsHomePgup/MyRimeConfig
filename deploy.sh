#!/usr/bin/env bash
# 将此 repo 的配置部署到当前平台的 Rime 配置目录
# 用法: ./deploy.sh [macos|linux-ibus|linux-fcitx5|windows]
# Windows 在 Git Bash 里运行

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
        if ! command -v cygpath &>/dev/null || [ -z "$APPDATA" ]; then
            echo "windows 平台需要在 Git Bash 里运行"
            exit 1
        fi
        RIME_DIR="$(cygpath -u "$APPDATA")/Rime"
        ;;
    *)
        echo "未知平台: $PLATFORM"
        echo "用法: $0 [macos|linux-ibus|linux-fcitx5|windows]"
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
        --exclude='.release-it.json' \
        --exclude='deploy.sh' \
        --exclude='deploy-yuanshu.py' \
        --exclude='LICENSE' \
        --exclude='*.md' \
        --exclude='build/' \
        --exclude='yuanshu-skin/' \
        --exclude='tools/' \
        --exclude='double_pinyin.custom.yaml' \
        --exclude='predict-zhs.db' \
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
        --exclude='./.release-it.json' \
        --exclude='./deploy.sh' \
        --exclude='./deploy-yuanshu.py' \
        --exclude='./LICENSE' \
        --exclude='*.md' \
        --exclude='./build' \
        --exclude='./yuanshu-skin' \
        --exclude='./tools' \
        --exclude='./double_pinyin.custom.yaml' \
        --exclude='./predict-zhs.db' \
        --exclude='./sync' \
        --exclude='*.userdb' \
        --exclude='*.userdb.txt' \
        --exclude='./user.yaml' \
        --exclude='./installation.yaml' \
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
            # installation.yaml 设了 sync_dir 才同步用户词库（合并其他设备学到的词）
            if grep -q '^sync_dir:' "$RIME_DIR/installation.yaml" 2>/dev/null; then
                echo ">>> 同步用户词库..."
                "$SQUIRREL" --sync
            fi
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
    windows)
        # Git Bash 会把 /v、/deploy 这类参数当成路径改写，调用 Windows 程序时要关掉
        export MSYS_NO_PATHCONV=1
        WEASEL_ROOT=""
        for key in 'HKLM\SOFTWARE\WOW6432Node\Rime\Weasel' 'HKLM\SOFTWARE\Rime\Weasel'; do
            WEASEL_ROOT="$(reg query "$key" /v WeaselRoot 2>/dev/null | sed -n 's/.*REG_SZ[[:space:]]*//p' | tr -d '\r')"
            [ -n "$WEASEL_ROOT" ] && break
        done
        DEPLOYER=""
        [ -n "$WEASEL_ROOT" ] && DEPLOYER="$(cygpath -u "$WEASEL_ROOT")/WeaselDeployer.exe"
        if [ -n "$DEPLOYER" ] && [ -f "$DEPLOYER" ]; then
            echo ">>> 触发重新部署..."
            "$DEPLOYER" /deploy
            # installation.yaml 设了 sync_dir 才同步用户词库（合并其他设备学到的词）
            if grep -q '^sync_dir:' "$RIME_DIR/installation.yaml" 2>/dev/null; then
                echo ">>> 同步用户词库..."
                "$DEPLOYER" /sync
            fi
        else
            echo ">>> 未找到小狼毫，请在系统托盘右键小狼毫图标，点击「重新部署」"
        fi
        ;;
esac

echo ">>> 完成！"
