# 更新日志

## 1.0.0 (2026-11-10)

### 新功能

* 双拼单按 a / e 时置顶「啊」「额」 ([578d4fd](https://github.com/InsHomePgup/MyRimeConfig/commit/578d4fdac57d059931055638216094d08d621f40))
* 虎码双拼反查词组显示编码，支持无前缀直接打英文 ([9128c5d](https://github.com/InsHomePgup/MyRimeConfig/commit/9128c5d917eb19a2b6f4f75f36d7b603da8370bb))
* 虎码无前缀英文支持大写开头 ([53308e1](https://github.com/InsHomePgup/MyRimeConfig/commit/53308e196b01437318d9b5caf1f9be5e320c8603))
* 连按 h 输出同样个数的「哈」 ([7f6af66](https://github.com/InsHomePgup/MyRimeConfig/commit/7f6af66ee566f14bce712ba763cd88fdceff29ba))
* 雾凇拼写运算适配自然码双拼，删除无效滤镜 ([fb5de6b](https://github.com/InsHomePgup/MyRimeConfig/commit/fb5de6b38b497e9e2b164ba04ed7fa2109f64c25))
* 鼠须管 macOS 皮肤改用 Inter + MiSans 字体，README 补充字体安装说明 ([e83d876](https://github.com/InsHomePgup/MyRimeConfig/commit/e83d876b291b02464b312f4c6b03a65b5e435072))
* 鼠须管新增仿 macOS 原生的浅色 / 深色皮肤，跟随系统切换 ([cfd164a](https://github.com/InsHomePgup/MyRimeConfig/commit/cfd164a251e7321caf2e78220a30cbbf9c322938))

### 修复

* 双拼反查改用 script_translator 以支持多字词组 ([dcc0112](https://github.com/InsHomePgup/MyRimeConfig/commit/dcc011262136a6bbc17e6965ff01e3f6ab55ae10))
* 字集过滤按词典名查找 core2022 反查库 ([ac47be0](https://github.com/InsHomePgup/MyRimeConfig/commit/ac47be004902e28a508725933601740c99f71d7e))
* 投资词库带字母的词移到自定义短语，修复双拼末尾单声母联想 ([4022a34](https://github.com/InsHomePgup/MyRimeConfig/commit/4022a3441ef6a83385ba4e6dacc07bd264e3b4f7))
* 支持双拼反查多字词组查询 ([f35a0b6](https://github.com/InsHomePgup/MyRimeConfig/commit/f35a0b6c73eb02fd8956e0c81f908f5e2473b1f8))
* 部署脚本保留用户词库并修复自动重新部署 ([9ec8fb6](https://github.com/InsHomePgup/MyRimeConfig/commit/9ec8fb6daba399611021bf6fa1e8aef56c3f7441))

### 回退

* 双拼反查改用 script_translator 会导致完全无法反查 ([ed15d1c](https://github.com/InsHomePgup/MyRimeConfig/commit/ed15d1caee79802bb56dc2a38c44451292667851))

### 文档

* mention Android APK via trime fork ([8da0973](https://github.com/InsHomePgup/MyRimeConfig/commit/8da0973f28f19f180a89809c317b385015d409a8))
* 添加 CLAUDE.md ([9202b85](https://github.com/InsHomePgup/MyRimeConfig/commit/9202b85f17b1004e148d4da664dc9c01b535bc8f))

### 杂项

* 用 release-it 管理版本号和 CHANGELOG ([2282477](https://github.com/InsHomePgup/MyRimeConfig/commit/2282477eff85b34630056c8a114433afe8a0023e))
* 虎码删除简繁和拼音滤镜 ([5ef33d8](https://github.com/InsHomePgup/MyRimeConfig/commit/5ef33d88bc0da1a2dbef108b6303b5658a91d0b8))
