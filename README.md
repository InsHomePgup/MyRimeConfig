# 我的 Rime 配置

基于 [雾凇拼音](https://github.com/iDvel/rime-ice)，整合了虎码方案，支持全平台同步使用。

## 输入方案

| 方案 | 说明 |
|------|------|
| 虎码官方词库 (`tigress`) | 虎码形码，单字 + 词组，**日常推荐** |
| 虎码官方单字 (`tiger`) | 虎码形码，纯单字模式 |
| 自然码双拼 (`double_pinyin`) | 自然码双拼方案 |
| 雾凇拼音 (`rime_ice`) | 全拼方案 |
| 中文九键 (`t9`) | 九宫格，仓输入法 / 元书专用 |

在虎码方案中，按 `` ` `` 键可切换为**自然码双拼反查**，用拼音检索虎码编码。

## 平台支持

| 平台 | 前端 | 前端配置文件 |
|------|------|-------------|
| macOS | 鼠须管 (Squirrel) | `squirrel.yaml` |
| Windows | 小狼毫 (Weasel) | `weasel.yaml` |
| Linux | ibus-rime | — |
| iOS | 仓输入法 (Hamster) | `hamster.yaml` |

所有 schema、词典、Lua 脚本、OpenCC 文件全平台通用，各平台前端配置文件互不干扰。

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

### Linux（ibus-rime）

```bash
git clone https://github.com/InsHomePgup/MyRimeConfig.git
cd MyRimeConfig
./deploy.sh linux-ibus
```

脚本同步到 `~/.config/ibus/rime/` 并执行 `ibus restart`。

若修改了 schema 或词库，还需手动触发 Rime 重新部署：右键 ibus 托盘图标 → **部署**，或：

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

脚本同步到 `%APPDATA%\Rime\`。完成后右键系统托盘小狼毫图标 → **重新部署**。

### iOS（仓输入法）

仓输入法支持通过 iCloud 同步配置，推荐以下两种方式：

**方式一：iCloud 同步（推荐）**

1. 在仓输入法 → 设置 → 输入方案 → iCloud 同步中开启同步
2. 在 Mac 上打开 Finder，进入 `iCloud 云盘 / Hamster / RIME/Rime/`
3. 将本 repo 中所有文件复制到该目录（覆盖）
4. 回到仓输入法 → 重新部署

**方式二：Git 同步（仓输入法 ≥ 2.x）**

仓输入法内置 Git 支持，可直接填入本 repo 地址自动拉取。

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
├── hamster.yaml       # iOS 前端配置
├── tiger.schema.yaml  # 虎码单字方案
├── tigress.schema.yaml# 虎码词组方案
├── double_pinyin.schema.yaml  # 自然码双拼方案
├── rime_ice.schema.yaml       # 雾凇拼音方案
├── deploy.sh          # 部署脚本（macOS / Linux）
└── deploy.ps1         # 部署脚本（Windows）
```

## 常用快捷键

| 按键 | 功能 |
|------|------|
| `F4` 或 `Ctrl+grave` | 切换输入方案 |
| `` ` `` | 虎码中切换自然码双拼反查 |
| `Shift` | 临时切换中/英文，上屏已输入内容 |
| `Caps Lock` | 清空输入并切换英文 |
