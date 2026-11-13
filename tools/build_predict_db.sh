#!/usr/bin/env bash
# 生成联想底库 predict-zhs.db：librime-predict 官方数据（繁体）→ OpenCC t2s 转简体 → 重新编译
#
# 用法（Debian / Ubuntu，包括 WSL，不需要 sudo）：
#   tools/build_predict_db.sh            # 结果写到仓库根目录的 predict-zhs.db
#
# 做的事：
# 1. 下载官方 data-1.0 的 predict.txt（上文 ⇥ 下文 ⇥ 权重，约 54 万条）
# 2. apt-get download 取 librime / OpenCC 及其开发包，解压到临时目录（不安装）
# 3. 编译 librime-predict 自带的 build_predict 工具；先用官方数据重编一次，
#    确认和官方发布的 predict.db 逐字节相同，证明工具没问题
# 4. OpenCC t2s 转换后合并重复条目（繁体不同、简体相同的词权重相加），按权重排序后编译
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$(mktemp -d)}"
OUT="$REPO_DIR/predict-zhs.db"
DATA_URL="https://github.com/rime/librime-predict/releases/download/data-1.0"
SRC_URL="https://raw.githubusercontent.com/rime/librime-predict/master"
LIBRIME_TAG="1.13.1"   # 只用它的 darts.h，和 Debian trixie 的 librime 版本一致

echo ">>> 工作目录: $WORK"
mkdir -p "$WORK/debs" "$WORK/root" "$WORK/src/src" "$WORK/src/tools"
cd "$WORK"

curl -fsSL -o predict.txt "$DATA_URL/predict.txt"
curl -fsSL -o predict-official.db "$DATA_URL/predict.db"

(cd debs && apt-get download \
    librime1t64 librime-dev opencc libopencc1.1 libopencc-data \
    libmarisa0 libmarisa-dev libyaml-cpp0.8 libleveldb1d \
    libgoogle-glog0v6t64 libgoogle-glog-dev libgflags2.2 libgflags-dev libunwind8 libsnappy1v5 \
    libboost1.83-dev libboost-locale1.83.0 libboost-regex1.83.0)
for f in debs/*.deb; do dpkg -x "$f" root; done
ROOT="$WORK/root"
LIB="$ROOT/usr/lib/x86_64-linux-gnu"
export LD_LIBRARY_PATH="$LIB"

curl -fsSL -o src/darts.h "https://raw.githubusercontent.com/rime/librime/$LIBRIME_TAG/include/darts.h"
for f in src/predict_db.cc src/predict_db.h tools/build_predict.cc; do
    curl -fsSL -o "src/$f" "$SRC_URL/$f"
done
g++ -std=c++17 -O2 -I"$ROOT/usr/include" -I"$ROOT/usr/include/x86_64-linux-gnu" -Isrc -Isrc/src \
    src/tools/build_predict.cc src/src/predict_db.cc -o build_predict \
    -L"$LIB" -lrime -lglog -lmarisa -Wl,-rpath,"$LIB"

echo ">>> 校验 build_predict：重编官方数据"
./build_predict rebuilt.db < predict.txt 2>/dev/null
cmp predict-official.db rebuilt.db
echo "    与官方 predict.db 一致"

echo ">>> 繁转简并合并"
"$ROOT/usr/bin/opencc" -c "$ROOT/usr/share/opencc/t2s.json" -i predict.txt -o predict-t2s.txt
python3 - predict-t2s.txt predict-zhs.txt <<'EOF'
import sys
from collections import defaultdict
src, dst = sys.argv[1], sys.argv[2]
data = defaultdict(lambda: defaultdict(int))
for line in open(src, encoding="utf-8"):
    key, text, weight = line.rstrip("\n").split("\t")
    data[key][text] += int(weight)
n = 0
with open(dst, "w", encoding="utf-8") as f:
    for key in sorted(data):
        for text, weight in sorted(data[key].items(), key=lambda x: -x[1]):
            f.write(f"{key}\t{text}\t{weight}\n")
            n += 1
print(f"    {len(data)} 个上文，{n} 条联想")
EOF

./build_predict "$OUT" < predict-zhs.txt 2>/dev/null
echo ">>> 已生成 $OUT"
