# 我的 Rime 配置

基于 [雾凇拼音](https://github.com/iDvel/rime-ice)，整合虎码形码，支持全平台同步使用。

## 输入方案

| 方案 | 说明 |
|------|------|
| 虎码单字 (`tiger`) | 虎码形码，纯单字模式 |
| 自然码双拼 (`double_pinyin`) | 自然码双拼，词库基于雾凇拼音 |

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

> **字体**：鼠须管皮肤 `mac_light` / `mac_dark` 用的是 Inter（英文）+ MiSans（中文），需要先装到系统里，否则会退回系统默认字体。
> - Inter：`brew install --cask font-inter`（开源 OFL）
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

在 PowerShell 中执行：

```powershell
git clone https://github.com/InsHomePgup/MyRimeConfig.git
cd MyRimeConfig
.\deploy.ps1
```

脚本同步到 `%APPDATA%\Rime\` 并调用 `WeaselDeployer.exe /deploy` 重新部署；找不到小狼毫安装目录时，请右键系统托盘小狼毫图标 → **重新部署**。

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

将本 repo 全部文件导入元书的 Rime 用户目录，并保留 `yuanshu.yaml`。导入后在元书内执行一次**重新部署**即可。

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
git pull && ./deploy.sh          # macOS / Linux
git pull; .\deploy.ps1           # Windows（PowerShell）
```

iOS 在仓输入法内手动触发同步或等待 iCloud 自动同步。

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
├── rime_ice.schema.yaml       # 雾凇拼音词库（自然码双拼的词库来源）
├── deploy.sh          # 部署脚本（macOS / Linux）
└── deploy.ps1         # 部署脚本（Windows）
```

## 常用快捷键

| 按键 | 功能 |
|------|------|
| `F4` / `Ctrl+\`` / `Ctrl+F8` | 切换输入方案 |
| `` ` `` | 虎码中切换自然码双拼反查 |
| `Shift` | 临时切换中/英文，上屏已输入内容 |
| `Caps Lock` | 清空输入并切换英文 |
