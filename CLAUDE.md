# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

个人 Rime 输入法配置：雾凇拼音（rime-ice）+ 虎码单字，全平台共用同一套文件。安装、平台说明见 README.md。

## 架构

- `default.yaml` 的 `schema_list` 只启用两个方案：`tiger`（虎码单字，主力）和 `double_pinyin`（自然码双拼，即雾凇方案）。其余 schema 都是被借用的依赖，不直接出现在方案列表里。
- 两个方案来自不同上游，写法不同，不要混用：
  - **虎码**（`tiger.*`、`core2022.*`、`easy_english.*`、`stroke.*`）：Lua 组件在 `rime.lua` 里注册为全局变量，schema 里写 `lua_filter@name`。
  - **雾凇**（`double_pinyin`、`rime_ice`、`melt_eng`、`radical_pinyin`、`cn_dicts/`、`en_dicts/`）：写 `lua_filter@*name`，直接按模块名 require，不经过 `rime.lua`。
- 虎码借用了别的方案的词库：`` ` `` 双拼反查用 `rime_ice` 词库 + `double_pinyin` prism；无前缀英文用 `melt_eng`（优先，拼写运算自带大写派生）和 `easy_english`。被借用的方案必须写进 `schema/dependencies`，否则它的 prism 不会被编译，翻译器查不到东西。
- 虎码的英文逻辑：关掉了 4 码顶屏，`auto_clear: none`。`lua/tiger_english_filter.lua` 负责在 4 码以内有虎码候选时隐藏英文，然后交给雾凇的 `autocap_filter` 处理大小写。
- `squirrel.yaml` / `weasel.yaml` / `hamster.yaml` / `yuanshu.yaml` 是各前端的外观配置，互不影响。Android 端以 submodule 形式打包进 InsHomePgup/trime fork，不走部署脚本。

## 部署与验证

没有构建或测试命令，“构建”就是 Rime 的重新部署：

- macOS / Linux：`./deploy.sh`（自动判断平台，也可传 `macos` / `linux-ibus` / `linux-fcitx5`）
- Windows：`.\deploy.ps1`。在 WSL 里要用 PowerShell 7：`pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$(wslpath -w deploy.ps1)"`。Windows PowerShell 5.1 会把这个 UTF-8 脚本读成乱码。
- 部署是否成功以 Rime 日志为准，要看到 `finished updating schemas: N success, 0 failure`。小狼毫的日志在 `%TEMP%\rime.weasel\`。
- 想不装输入法就验证行为或性能：可以下载 Debian 的 librime、librime-dev、librime-plugin-lua、rime-prelude 包解压到本地，写个几十行的 C 程序调用 `rime_api.h` 的 `simulate_key_sequence` 和 `get_context` 打印候选。

## 改动时注意

- **换行符**：虎码系文件（`tiger.*`、`easy_english.*`、`stroke.*`、`core2022.dict.yaml`、`rime.lua`，以及 `lua/calculator_translator.lua`、`lua/unicode_display.lua`）是 CRLF，其余是 LF。编辑时保持原样，用 Python 改写的话要加 `newline=''`。
- **Lua filter 不要遍历整个候选流**：候选是惰性生成的，短码的英文补全可能有几万条。只丢弃不 yield 的循环会把它们全部拉一遍，之前就因此每次按键卡了约 0.4 秒。能确定后面没有需要的候选时就 `break`。
- **仓库是公开的**：`*.userdb`、`installation.yaml`、`user.yaml`、`sync/` 不能提交。部署脚本已经把它们排除，不会覆盖或删除。
- **分支**：直接在当前分支提交，不要自己建分支。分支由用户管理。
