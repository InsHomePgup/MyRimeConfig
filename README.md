# 我的 Rime 配置

基于 [雾凇拼音](https://github.com/iDvel/rime-ice)，整合虎码形码，支持全平台同步使用。

## 输入方案

| 方案 | 说明 |
|------|------|
| 虎码单字 (`tiger`) | 虎码形码，纯单字模式 |
| 自然码双拼 (`double_pinyin`) | 自然码双拼，词库基于雾凇拼音 |
| 自然码双拼·繁 / ·港 / ·台 (`double_pinyin_trad` / `_hk` / `_tw`) | 打简出繁：通用繁体 / 港澳繁体 / 台湾繁体（含用词转换），用 Ctrl+` 方案选单切换 |

在虎码方案中，按 `` ` `` 键可切换为**自然码双拼反查**，用拼音检索虎码编码。

## 平台支持

| 平台 | 前端 | 前端配置文件 |
|------|------|-------------|
| macOS | 鼠须管 (Squirrel) | `squirrel.yaml` |
| Windows | 小狼毫 (Weasel) | `weasel.yaml` |
| Linux | ibus-rime | — |
| iOS | 仓输入法 (Hamster) | `hamster.yaml` |
| iOS | 元书输入法 | `yuanshu.yaml` |
| Android | [Trime 自定义（个人版）](https://github.com/InsHomePgup/trime) | 内嵌为 APK，装完即用 |

所有 schema、词典、Lua 脚本、OpenCC 文件全平台通用，各平台前端配置文件互不干扰。

Android 端不走 `deploy.sh` 这套流程：本仓库以 git submodule 的形式接入个人 fork
[InsHomePgup/trime](https://github.com/InsHomePgup/trime)，随 APK 一起编译打包。改了配置后，
在 trime 仓库执行 `git submodule update --remote` 并打 tag，GitHub Actions 会自动出新 APK，
发布在 [trime 仓库的 Releases 页面](https://github.com/InsHomePgup/trime/releases)。仅供个人
使用，不是公开发布的输入法应用。

---

## 安装 / 部署

### macOS（鼠须管）

```bash
git clone https://github.com/InsHomePgup/MyRimeConfig.git
cd MyRimeConfig
./deploy.sh
```

脚本会自动同步到 `~/Library/Rime/` 并触发重新部署。

如未自动部署，点击菜单栏鼠须管图标 → **重新部署**。

> **字体**：鼠须管皮肤 `mac_light` / `mac_dark` 用的是 Maple Mono（英文）+ MiSans（中文），需要先装到系统里，否则会退回系统默认字体。
> - Maple Mono：`brew install --cask font-maple-mono`（开源 OFL）
> - MiSans：从 [小米官网](https://hyperos.mi.com/font) 下载，双击 `MiSans-Regular.ttf` 安装。MiSans 的授权不允许再分发，所以字体文件不放进本仓库。

### Linux（ibus-rime）

```bash
git clone https://github.com/InsHomePgup/MyRimeConfig.git
cd MyRimeConfig
./deploy.sh linux-ibus
```

脚本同步到 `~/.config/ibus/rime/` 并执行 `ibus restart`（ibus-rime 启动时会重新部署有变动的文件）。

如果用的是 fcitx5-rime，执行 `./deploy.sh linux-fcitx5`，同步到 `~/.local/share/fcitx5/rime/` 并执行 `fcitx5-remote -r`。
不带参数时脚本会自动判断（fcitx5 在运行就用 fcitx5，否则用 ibus）。不确定自己用的是哪个，可以执行：

```bash
pgrep -a 'fcitx5|ibus-daemon'
```

若部署后没有生效，手动触发 Rime 重新部署：右键托盘图标 → **部署**，或：

```bash
rm -rf ~/.config/ibus/rime/build && ibus restart
```

### Windows（小狼毫）

**前置条件**（新装的 Windows 先准备好）：

- [小狼毫](https://rime.im/download/)
- [Git for Windows](https://git-scm.com/download/win)（或 `winget install Git.Git`），自带 Git Bash，部署脚本在 Git Bash 里运行
- 字体：`weasel.yaml` 用的是 Maple Mono（英文）+ MiSans（中文），没装会退回其他字体，但不影响部署。
  - Maple Mono：从 [GitHub Releases](https://github.com/subframe7536/maple-font/releases) 下载安装（开源 OFL）
  - MiSans：从 [小米官网](https://hyperos.mi.com/font) 下载安装

**部署**：在 Git Bash 中执行：

```bash
git clone https://github.com/InsHomePgup/MyRimeConfig.git
cd MyRimeConfig
./deploy.sh
```

脚本同步到 `%APPDATA%\Rime\` 并调用 `WeaselDeployer.exe /deploy` 重新部署。Git Bash 没有 rsync，脚本会改用 tar 复制：只覆盖不删除，repo 里删掉的文件要自己到 `%APPDATA%\Rime\` 里清理；找不到小狼毫安装目录时，请右键系统托盘小狼毫图标 → **重新部署**。

部署是否成功看 `%TEMP%\rime.weasel\` 下的日志，出现 `finished updating schemas: N success, 0 failure` 即可。

### iOS（仓输入法 / 元书输入法）

仓输入法与元书输入法都可以直接导入普通 Rime 配置目录。

仓输入法支持通过 iCloud 同步配置，推荐以下两种方式：

**方式一：iCloud 同步（推荐）**

1. 在仓输入法 → 设置 → 输入方案 → iCloud 同步中开启同步
2. 在 Mac 上打开 Finder，进入 `iCloud 云盘 / Hamster / RIME/Rime/`
3. 将本 repo 中所有文件复制到该目录（覆盖）
4. 回到仓输入法 → 重新部署

**方式二：Git 同步（仓输入法 ≥ 2.x）**

仓输入法内置 Git 支持，可直接填入本 repo 地址自动拉取。

### iOS（元书输入法）

在元书里打开 **WiFi 传输**，记下页面上显示的地址，然后在电脑上运行（电脑和手机要在同一个局域网）：

```bash
python3 deploy-yuanshu.py 192.168.x.x            # 地址换成 WiFi 传输页面上显示的
python3 deploy-yuanshu.py 192.168.x.x --dry-run  # 只看要传哪些文件
```

脚本只用 Python 标准库，macOS、Linux、Windows、WSL 都能跑。它会：

1. 比对仓库里已跟踪的配置文件和手机 `RimeUserData/` 里的同名文件，只上传有变化的。手机上的用户词库、`user.yaml`、`installation.yaml` 不会被动到；手机上多出来的文件只列出来，不会删除。
2. 把电脑同步目录里各设备导出的用户词库快照（`*.userdb.txt`）传到手机的 `RimeUserData/sync/<设备名>/`，见下面的[用户词库同步](#用户词库同步各设备学到的词)。同步目录默认从本机 Rime 的 `installation.yaml` 读 `sync_dir`；也可以用 `--sync-dir` 指定，或用 `--no-userdb` 跳过。在 WSL 里看不到 Google Drive 的盘符，脚本会借 PowerShell 复制快照。

传完后在元书里先点**重新部署**，再点**同步**，把电脑学到的词合并进来。也可以手动在 WiFi 传输页面上传文件，效果一样。

**键盘皮肤**：`yuanshu-skin/build.py` 生成仿微信输入法布局的皮肤 `MyRime`。字母键不绑划动、点击区域铺满整个格子，不容易误触；底行是 123 / 表情 / 逗号（上划句号）/ 空格 / 中英 / 回车。加 `--skin` 会生成皮肤并传到手机的 `Skins/MyRime/`，然后在元书的键盘皮肤里选中它：

```bash
python3 deploy-yuanshu.py 192.168.x.x --skin
python3 yuanshu-skin/demo.py   # 在电脑上画预览图到 yuanshu-skin/build/（需要 Pillow）
```

配色、尺寸、布局都是 `build.py` 开头的常量。生成结果在 `yuanshu-skin/build/`，不提交；里面的 `MyRime.cskin` 也可以隔空投送到手机导入。目前只做了 iPhone 竖屏，横屏和 iPad 暂时沿用竖屏布局。

这是单向的：电脑上新学的词，要先在电脑上同步一次，再运行一次脚本才能到元书；元书学到的词也不会回到电脑，因为元书的同步目录不在 Google Drive 里。

如果元书使用的是独立共享目录，需确保本仓库依赖的所有 schema、dict、lua、opencc 文件一并导入，不能只单独导入某一个方案文件。

部署脚本只覆盖 repo 里的配置文件，Rime 目录下的用户词库（`*.userdb`）、`user.yaml`、`installation.yaml`、`sync/` 不会被删除或覆盖。

---

## 日常同步工作流

在任意平台修改配置后：

```bash
git add .
git commit -m "描述修改内容"
git push
```

其他平台同步：

```bash
git pull && ./deploy.sh          # macOS / Linux / Windows（Git Bash）
```

iOS：仓输入法内手动触发同步或等待 iCloud 自动同步；元书运行 `python3 deploy-yuanshu.py <手机地址>`。

### 用户词库同步（各设备学到的词）

git 只同步配置和词库文件。输入法根据选词学到的词和词频（`*.userdb`）每台设备各一份，用 Rime 自带的「同步用户数据」合并，经由 Google Drive 的 `RimeSync` 文件夹中转。用户词库带个人输入习惯，**不要放进本仓库**。

每台设备在 Rime 用户目录的 `installation.yaml` 里设置（这个文件不进仓库，部署脚本也不会覆盖）：

```yaml
installation_id: "macos"   # 每台设备取不同的名字，同步目录下会生成同名子文件夹
sync_dir: "<Google Drive 路径>/RimeSync"
```

| 平台 | `installation_id` | `sync_dir` |
|------|------|------|
| macOS | `macos` | `/Users/<用户名>/Library/CloudStorage/GoogleDrive-<邮箱>/我的云端硬盘/RimeSync` |
| Windows | `windows` | `G:\\我的云端硬盘\\RimeSync`（盘符以 Google Drive 实际挂载的为准） |

改完后重新部署一次让设置生效。之后：

- `deploy.sh` 在 macOS 和 Windows 上部署后会自动同步一次（只在设置了 `sync_dir` 时）。
- 手动同步：鼠须管菜单栏 / 小狼毫托盘 → **同步用户数据**；macOS 命令行是 `"/Library/Input Methods/Squirrel.app/Contents/MacOS/Squirrel" --sync`。
- 每次同步会导出本机学到的词，并合并其他设备的词。在一台设备上用了一段时间后同步一次，再到另一台设备同步，两边就一致了。
- 同步时 Rime 也会把配置文件备份到自己的子文件夹，这是正常的；本机删掉的方案文件，备份里不会自动删除，可以手动清理。

---

## 目录结构

```
MyRimeConfig/
├── cn_dicts/          # 中文词典
├── en_dicts/          # 英文词典
├── lua/               # Lua 脚本（雾凇 + 虎码）
├── opencc/            # OpenCC 转换文件（含虎码拆分 hu_cf）
├── default.yaml       # 全局配置（方案列表、快捷键等）
├── rime.lua           # 虎码 Lua 入口
├── squirrel.yaml      # macOS 前端配置
├── weasel.yaml        # Windows 前端配置
├── hamster.yaml       # iOS 仓输入法前端配置
├── yuanshu.yaml       # iOS 元书输入法前端配置
├── tiger.schema.yaml          # 虎码单字方案
├── double_pinyin.schema.yaml  # 自然码双拼方案
├── double_pinyin_{trad,hk,tw}.schema.yaml  # 自然码双拼的繁体版（继承 double_pinyin，只换 OpenCC 配置）
├── rime_ice.schema.yaml       # 雾凇拼音词库（自然码双拼的词库来源）
├── deploy.sh          # 部署脚本（macOS / Linux / Windows Git Bash）
├── deploy-yuanshu.py  # 部署脚本（iOS 元书，经 WiFi 传输）
└── yuanshu-skin/      # 元书键盘皮肤生成脚本
```

## 常用快捷键

| 按键 | 功能 |
|------|------|
| `F4` / `Ctrl+\`` / `Ctrl+F8` | 切换输入方案 |
| `` ` `` | 虎码中切换自然码双拼反查 |
| `Shift` | 临时切换中/英文，上屏已输入内容 |
| `Caps Lock` | 清空输入并切换英文 |
