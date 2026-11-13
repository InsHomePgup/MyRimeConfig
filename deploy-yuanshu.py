#!/usr/bin/env python3
"""通过元书输入法的「WiFi 传输」把本仓库配置和电脑的用户词库推到 iPhone。

用法:
    python3 deploy-yuanshu.py <手机地址> [--dry-run] [--no-userdb] [--sync-dir 路径] [--skin]

    <手机地址>   元书 WiFi 传输页面显示的地址，如 192.168.1.23 或 http://192.168.1.23:80
                 也可以用环境变量 YUANSHU_HOST 提供。

做两件事：
1. 配置：比对仓库里已跟踪的文件和手机 RimeUserData/ 下的同名文件，只上传有变化的。
   手机上的 *.userdb、user.yaml、installation.yaml、build/ 不会被动到；
   手机上多出来的文件只列出来，不删除。
2. 用户词库：把电脑同步目录（Google Drive 的 RimeSync）里各设备导出的 *.userdb.txt
   快照传到手机的 RimeUserData/sync/<设备名>/。传完在元书里点「同步」才会合并。
   同步目录默认从本机 Rime 的 installation.yaml 里的 sync_dir 读取。
3. 加 --skin 时：用 yuanshu-skin/build.py 生成键盘皮肤，传到手机的 Skins/<皮肤名>/，
   传完在元书的「键盘皮肤」里选中它（已选中的要重新点一下才会重新加载）。

传完后要在元书里先「重新部署」，再「同步」。

只用 Python 标准库，macOS / Linux / Windows / WSL 都能跑。
"""

import argparse
import fnmatch
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
REMOTE_ROOT = "RimeUserData"

# 和 deploy.sh 一致：这些不是 Rime 配置，不传到手机
EXCLUDES = [".gitignore", ".release-it.json", "deploy.sh", "deploy.ps1",
            "deploy-yuanshu.py", "LICENSE", "*.md"]
# 这些目录不是 Rime 配置（键盘皮肤单独用 --skin 上传）
EXCLUDE_DIRS = ["yuanshu-skin/"]
SKIN_ROOT = "Skins"


class FileBrowser:
    """元书的 WiFi 传输是 File Browser（无需登录），这里只用到它的几个 API。"""

    def __init__(self, base):
        if not re.match(r"^https?://", base):
            base = "http://" + base
        self.base = base.rstrip("/")
        req = urllib.request.Request(self.base + "/api/login", data=b"{}", method="POST")
        self.token = urllib.request.urlopen(req, timeout=10).read().decode()

    def _open(self, method, url, data=None):
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"X-Auth": self.token})
        return urllib.request.urlopen(req, timeout=300).read()

    def _url(self, api, path, query="", root=REMOTE_ROOT):
        return "%s/api/%s/%s/%s%s" % (self.base, api, root,
                                      urllib.parse.quote(path), query)

    def list_dir(self, path):
        """返回 {相对路径: 大小}，子目录的值为 None。目录不存在返回 None。"""
        try:
            data = self._open("GET", self._url("resources", path + "/" if path else ""))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise
        out = {}
        for item in json.loads(data).get("items", []):
            p = (path + "/" if path else "") + item["name"]
            out[p] = None if item["isDir"] else item["size"]
        return out

    def read(self, path):
        data = self._open("GET", self._url("raw", path))
        # 这个 File Browser 的 raw 接口会把单个文件也打成 zip 返回
        if data[:4] == b"PK\x03\x04":
            try:
                z = zipfile.ZipFile(io.BytesIO(data))
                names = z.namelist()
                if len(names) == 1:
                    return z.read(names[0])
            except zipfile.BadZipFile:
                pass
        return data

    def write(self, path, data, root=REMOTE_ROOT):
        self._open("POST", self._url("resources", path, "?override=true", root), data)


def tracked_files():
    out = subprocess.check_output(["git", "-C", REPO_DIR, "ls-files", "-z"])
    files = []
    for f in out.decode("utf-8").split("\0"):
        if (f and not any(fnmatch.fnmatch(os.path.basename(f), p) for p in EXCLUDES)
                and not any(f.startswith(d) for d in EXCLUDE_DIRS)):
            files.append(f)
    return files


def sync_config(fb, dry_run):
    print(">>> 比对配置文件...")
    files = tracked_files()
    remote = {}
    for d in sorted({os.path.dirname(f) for f in files}):
        listing = fb.list_dir(d)
        if listing:
            remote.update(listing)

    changed = []
    for f in files:
        local = os.path.join(REPO_DIR, f)
        size = os.path.getsize(local)
        if remote.get(f) != size:
            changed.append(f)
            continue
        with open(local, "rb") as fh:
            if fb.read(f) != fh.read():
                changed.append(f)

    tracked = set(files)
    subdirs = {f.split("/")[0] for f in files if "/" in f}
    extra = sorted(p for p, size in remote.items()
                   if size is not None and p not in tracked and p.split("/")[0] in subdirs)

    if not changed:
        print(">>> 配置已是最新")
    for f in changed:
        if dry_run:
            print("    [dry-run] 将上传 %s" % f)
        else:
            with open(os.path.join(REPO_DIR, f), "rb") as fh:
                fb.write(f, fh.read())
            print("    已上传 %s" % f)
    if extra:
        print(">>> 手机上有仓库里没有的文件（未删除，需要的话在 WiFi 传输页面手动删）:")
        for p in extra:
            print("    %s" % p)
    return len(changed)


# ---------- 用户词库 ----------

def is_wsl():
    return "microsoft" in platform.uname().release.lower()


def windows_appdata_from_wsl():
    try:
        out = subprocess.check_output(["cmd.exe", "/c", "echo %APPDATA%"],
                                      stderr=subprocess.DEVNULL, cwd="/mnt/c")
        win = out.decode("utf-8", "replace").strip()
        return subprocess.check_output(["wslpath", "-u", win]).decode().strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def local_rime_dirs():
    home = os.path.expanduser("~")
    if sys.platform == "darwin":
        return [os.path.join(home, "Library", "Rime")]
    if sys.platform == "win32":
        return [os.path.join(os.environ.get("APPDATA", ""), "Rime")]
    dirs = []
    if is_wsl():
        appdata = windows_appdata_from_wsl()
        if appdata:
            dirs.append(os.path.join(appdata, "Rime"))
    dirs += [os.path.join(home, ".local", "share", "fcitx5", "rime"),
             os.path.join(home, ".config", "ibus", "rime")]
    return dirs


def parse_sync_dir(text):
    m = re.search(r"^sync_dir:\s*(.+?)\s*$", text, re.M)
    if not m:
        return None
    v = m.group(1)
    if v.startswith('"') and v.endswith('"'):
        v = v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    elif v.startswith("'") and v.endswith("'"):
        v = v[1:-1].replace("''", "'")
    return v


def find_sync_dir():
    for d in local_rime_dirs():
        p = os.path.join(d, "installation.yaml")
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as fh:
                v = parse_sync_dir(fh.read())
            if v:
                return v
    return None


def copy_snapshots_via_powershell(win_dir, dest):
    """WSL 里看不到 Google Drive 挂载的盘符，借 Windows 的 PowerShell 把快照复制出来。"""
    win_dest = subprocess.check_output(["wslpath", "-w", dest]).decode().strip()
    q = lambda s: "'" + s.replace("'", "''") + "'"
    script = (
        "$src = %s; $dst = %s;"
        "Get-ChildItem -LiteralPath $src -Directory | ForEach-Object {"
        "  $files = Get-ChildItem -LiteralPath $_.FullName -Filter '*.userdb.txt' -File;"
        "  if ($files) {"
        "    $d = Join-Path $dst $_.Name; New-Item -ItemType Directory -Force $d | Out-Null;"
        "    $files | Copy-Item -Destination $d"
        "  }"
        "}" % (q(win_dir), q(win_dest)))
    exe = shutil.which("pwsh.exe") or shutil.which("powershell.exe") or "powershell.exe"
    subprocess.check_call([exe, "-NoProfile", "-Command", script], cwd="/mnt/c")


def collect_snapshots(sync_dir, tmp):
    """返回 [(设备名, 文件名, 本地路径)]。"""
    root = sync_dir
    if is_wsl() and re.match(r"^[A-Za-z]:\\", sync_dir):
        root = os.path.join(tmp, "snapshots")
        os.makedirs(root)
        copy_snapshots_via_powershell(sync_dir, root)
    if not os.path.isdir(root):
        sys.exit("!!! 找不到同步目录: %s" % sync_dir)
    out = []
    for dev in sorted(os.listdir(root)):
        ddir = os.path.join(root, dev)
        if not os.path.isdir(ddir):
            continue
        for name in sorted(os.listdir(ddir)):
            if name.endswith(".userdb.txt"):
                out.append((dev, name, os.path.join(ddir, name)))
    return out


def remote_installation_id(fb):
    try:
        text = fb.read("installation.yaml").decode("utf-8", "replace")
    except urllib.error.HTTPError:
        return None
    m = re.search(r'^installation_id:\s*"?([^"\n]+?)"?\s*$', text, re.M)
    return m.group(1) if m else None


def sync_userdb(fb, sync_dir, dry_run):
    sync_dir = sync_dir or find_sync_dir()
    if not sync_dir:
        print(">>> 本机 installation.yaml 没有设置 sync_dir，跳过用户词库（可用 --sync-dir 指定）")
        return 0
    print(">>> 用户词库来源: %s" % sync_dir)
    own_id = remote_installation_id(fb)
    tmp = tempfile.mkdtemp(prefix="yuanshu-")
    try:
        snaps = collect_snapshots(sync_dir, tmp)
        n = 0
        for dev, name, path in snaps:
            if dev == own_id:  # 手机自己导出的快照不要拿回去覆盖
                continue
            with open(path, "rb") as fh:
                data = fh.read()
            if dry_run:
                print("    [dry-run] 将上传 sync/%s/%s" % (dev, name))
            else:
                fb.write("sync/%s/%s" % (dev, name), data)
                print("    已上传 sync/%s/%s" % (dev, name))
            n += 1
        if not n:
            print(">>> 同步目录里没有可用的 *.userdb.txt 快照")
        return n
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------- 键盘皮肤 ----------

def sync_skin(fb, dry_run):
    sys.path.insert(0, os.path.join(REPO_DIR, "yuanshu-skin"))
    import build
    skin_dir, _ = build.build()
    name = os.path.basename(skin_dir)
    print(">>> 上传键盘皮肤 %s/%s/" % (SKIN_ROOT, name))
    n = 0
    for root, _, files in os.walk(skin_dir):
        for f in sorted(files):
            full = os.path.join(root, f)
            rel = "%s/%s" % (name, os.path.relpath(full, skin_dir).replace(os.sep, "/"))
            if dry_run:
                print("    [dry-run] 将上传 %s/%s" % (SKIN_ROOT, rel))
            else:
                with open(full, "rb") as fh:
                    fb.write(rel, fh.read(), root=SKIN_ROOT)
            n += 1
    if not dry_run:
        print("    已上传 %d 个文件" % n)
    return n


def main():
    ap = argparse.ArgumentParser(description="把配置和电脑的用户词库推到元书输入法（WiFi 传输）")
    ap.add_argument("host", nargs="?", default=os.environ.get("YUANSHU_HOST"),
                    help="元书 WiFi 传输地址，如 192.168.1.23；也可用环境变量 YUANSHU_HOST")
    ap.add_argument("--dry-run", action="store_true", help="只列出要上传的文件，不实际上传")
    ap.add_argument("--no-userdb", action="store_true", help="只同步配置，不传用户词库")
    ap.add_argument("--sync-dir", help="用户词库同步目录（默认读本机 installation.yaml 的 sync_dir）")
    ap.add_argument("--skin", action="store_true", help="同时生成并上传键盘皮肤（yuanshu-skin/）")
    args = ap.parse_args()
    if not args.host:
        ap.error("请提供元书 WiFi 传输地址，或设置环境变量 YUANSHU_HOST")

    try:
        fb = FileBrowser(args.host)
        fb.list_dir("")
    except (urllib.error.URLError, OSError) as e:
        sys.exit("!!! 连不上 %s：%s\n    确认手机和电脑在同一网络，且元书的 WiFi 传输页面开着" % (args.host, e))

    print(">>> 目标: %s/%s" % (fb.base, REMOTE_ROOT))
    changed = sync_config(fb, args.dry_run)
    uploaded = 0 if args.no_userdb else sync_userdb(fb, args.sync_dir, args.dry_run)
    skin = sync_skin(fb, args.dry_run) if args.skin else 0

    if args.dry_run:
        print(">>> dry-run 结束，没有上传任何文件")
        return
    print(">>> 完成！")
    if changed:
        print("    在元书里点「重新部署」加载新配置")
    if uploaded:
        print("    再点「同步」把电脑学到的词合并进来")
    if skin:
        print("    在「键盘皮肤」里选中 MyRime（已选中的话重新点一下）")


if __name__ == "__main__":
    main()
