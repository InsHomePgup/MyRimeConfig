# 更新日志

## [1.1.1](https://github.com/InsHomePgup/MyRimeConfig/compare/v1.1.0...v1.1.1) (2026-11-27)

### 修复

* 恢复元书皮肤纵向候选展开面板，移除上屏后联想功能 ([4debc9b](https://github.com/InsHomePgup/MyRimeConfig/commit/4debc9b17bee2c5cdff6c629b2a89185f4b2feee))

## [1.1.0](https://github.com/InsHomePgup/MyRimeConfig/compare/v1.0.0...v1.1.0) (2026-11-26)

### 新功能

* Windows 改用 Git Bash 运行 deploy.sh，移除 deploy.ps1 ([d0e275b](https://github.com/InsHomePgup/MyRimeConfig/commit/d0e275b25d85e8a0a1c00311252f455cf1773e53))
* 元书上开启联想（librime-predict + 简体联想词库），电脑不同步 ([1385815](https://github.com/InsHomePgup/MyRimeConfig/commit/1385815b0e2838c352238d7468fb6ea88048a286))
* 元书皮肤去掉 Emoji 键，改用 iOS 自带的 Emoji 键盘 ([18d8ec3](https://github.com/InsHomePgup/MyRimeConfig/commit/18d8ec32028d8ecfedd473f4d1ea0cd21aa9b4ab))
* 元书皮肤字体改为英文 Maple Mono、中文 MiSans，中英键的“英”改回黑色 ([7ea6c81](https://github.com/InsHomePgup/MyRimeConfig/commit/7ea6c813751bb5b76caedcfee52d19a8d71b7812))
* 元书皮肤移除纵向候选面板，逗号键支持长按上滑选句号 ([3b7563c](https://github.com/InsHomePgup/MyRimeConfig/commit/3b7563c8bf16023f1fd3af7ac3cc0ec5ce24d069))
* 元书皮肤符号键盘对齐微信，新增更多符号页和分类栏 ([18c954c](https://github.com/InsHomePgup/MyRimeConfig/commit/18c954cbfbf37638c501d7b3e6d4d3c0f2f1c083))
* 元书联想改用 17 万上文的简体底库，并从输入习惯学习联想 ([4ab9b31](https://github.com/InsHomePgup/MyRimeConfig/commit/4ab9b31be6bb58dc7c2cf0ce6a19c7d1efb5348d))
* 小狼毫加入 Rime Skin Studio 的 45 套预设配色，默认高级灰 · 紫 ([f705254](https://github.com/InsHomePgup/MyRimeConfig/commit/f70525420a2204ed6709d0150150eaef728966ec))
* 小狼毫默认改用 macOS 风格皮肤，重做微信输入法皮肤，字体换成 Maple Mono + MiSans ([f9cf5d4](https://github.com/InsHomePgup/MyRimeConfig/commit/f9cf5d451525aaac29b9526599e1f05975602a87))
* 新增元书 WiFi 部署脚本，同步配置和电脑用户词库 ([b2ca401](https://github.com/InsHomePgup/MyRimeConfig/commit/b2ca401d860ccf95365bf179b5a15607efb79e0d))
* 新增元书键盘皮肤 MyRime（仿微信布局、iOS 原生液态玻璃风格），deploy-yuanshu.py 加 --skin 上传 ([d8adb3f](https://github.com/InsHomePgup/MyRimeConfig/commit/d8adb3fe9df8008b882d16e424c7fae771175afc))
* 新增自建汽车词库，覆盖品牌车型、底盘、三电、智驾等 ([57b628f](https://github.com/InsHomePgup/MyRimeConfig/commit/57b628ffc23a775025e255a650423a6d6aa2de8b))
* 新增自然码双拼繁体方案（通用 / 港澳 / 台湾），用方案选单切换 ([9fc4d62](https://github.com/InsHomePgup/MyRimeConfig/commit/9fc4d6258c82f5fa695823ab9b47ee2ad6115502))
* 方案列表把自然码双拼排到第一，部署后默认是双拼 ([8337e13](https://github.com/InsHomePgup/MyRimeConfig/commit/8337e13c4e2cddf3bb35d36508f1cd9980b53c7b))
* 部署后自动同步用户词库，README 补充多设备同步说明 ([874353f](https://github.com/InsHomePgup/MyRimeConfig/commit/874353fe1f8a7f59a643d679dd21a894df3331a7))
* 鼠须管字体换成 Maple Mono + MiSans ([9d3247a](https://github.com/InsHomePgup/MyRimeConfig/commit/9d3247a6ea4c4a97591981b55b349b71110da3ae))

### 修复

* deploy.sh 的 tar 分支补上用户词库、同步目录等排除项 ([35af68f](https://github.com/InsHomePgup/MyRimeConfig/commit/35af68f9155e8f66544fb31b2a76ebe2814be4a9))
* 元书皮肤更多符号页的分类栏写明每格宽度，右侧不再留空隙 ([6c14a73](https://github.com/InsHomePgup/MyRimeConfig/commit/6c14a7313c146cd17649a114b586d63461a0a664))
* 元书皮肤更多符号页第三行按实际符号个数均分宽度，去掉末尾空格 ([9bee3d1](https://github.com/InsHomePgup/MyRimeConfig/commit/9bee3d1eac15f74d437341c83017c76e14da0456))
* 元书皮肤的 123 改为进符号键盘，符号键盘的「12/34」再进九宫格数字键盘（同微信） ([0578cf9](https://github.com/InsHomePgup/MyRimeConfig/commit/0578cf9da8b8bf3f6b09d490d3fe99aa3fd610aa))
* 元书皮肤的 123 符号页改用自定义键盘类型，点符号后停留在当前页，不再自动回主键盘 ([1c4b34b](https://github.com/InsHomePgup/MyRimeConfig/commit/1c4b34bf847a0fbde43b9aa4acf68cc3edee3780))
* 元书皮肤符号键上的全角中文标点水平居中 ([0c367c8](https://github.com/InsHomePgup/MyRimeConfig/commit/0c367c808da211dcb51ba2b31b1a5f38374c874b))
* 元书皮肤第三行两端功能键（Shift / 删除 / 符号 / 123）键帽统一宽度 ([fbcb142](https://github.com/InsHomePgup/MyRimeConfig/commit/fbcb1420738dd2ab437968aada58bd3f8b34be50))
* 元书皮肤逗号键长按改为单行横向滑动选择（换行/。/？/！/@/…） ([2397970](https://github.com/InsHomePgup/MyRimeConfig/commit/23979707107734d8ea8507b5f3ff3f12c63cb7a1))
* 删除词库中无法编码的词条（--、——、飚升） ([eef0489](https://github.com/InsHomePgup/MyRimeConfig/commit/eef0489c79f1bf8d7a5773090a002ebb712c67e6))
* 双拼删除与中文冲突的英文自定义短语（go、todo、hugo 等），中文优先 ([2f13f04](https://github.com/InsHomePgup/MyRimeConfig/commit/2f13f043050c8470a1e7f556104069de39465a7c))
* 所有窗口共用同一个方案，切换窗口不再回到旧方案 ([3294e62](https://github.com/InsHomePgup/MyRimeConfig/commit/3294e62e9822686c169939fbfaea0be5944b6b8d))
* 消除部署日志里的警告 ([a7ab9f4](https://github.com/InsHomePgup/MyRimeConfig/commit/a7ab9f48ccc56a64933b1e6b415456f62932dd78))
* 联想学习防止来回点联想词刷次数，删除改为写删除标记以免同步时恢复 ([57db734](https://github.com/InsHomePgup/MyRimeConfig/commit/57db734e648764c94a63fc16dc58d3167b3316ca))

### 回退

* 元书皮肤不再打包字体，字体改在元书的「键盘字体」里设置 ([e45adb4](https://github.com/InsHomePgup/MyRimeConfig/commit/e45adb458b76d093adee14fb9419a2906863e0ae))

### 文档

* CLAUDE.md 写明改动只针对简体双拼，虎码和繁体保持现状 ([8684ee8](https://github.com/InsHomePgup/MyRimeConfig/commit/8684ee802d800ad51cc8fa8cbea84e0602f0d868))
* 新增元书皮肤文档 yuanshu-skin/README.md，build.py 生成时自动检查布局、引用和宽度 ([58b52a6](https://github.com/InsHomePgup/MyRimeConfig/commit/58b52a6a7cb4a533dc740eb84acb2ddcaa837983))
* 新增公开词库目录，汇总搜狗细胞词库和 THUOCL 供挑选 ([8c123b0](https://github.com/InsHomePgup/MyRimeConfig/commit/8c123b0d8582b62c08b3ed0c8a694ebd5b2b868d))

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
