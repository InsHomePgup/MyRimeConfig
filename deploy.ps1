# Windows 小狼毫部署脚本
# 在 PowerShell 中运行: .\deploy.ps1

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RimeDir = "$env:APPDATA\Rime"

Write-Host ">>> 部署平台: Windows (小狼毫)"
Write-Host ">>> 目标目录: $RimeDir"

if (-not (Test-Path $RimeDir)) {
    New-Item -ItemType Directory -Path $RimeDir | Out-Null
}

# 排除不需要同步的文件
$Excludes = @('.git', '.gitignore', 'deploy.sh', 'deploy.ps1', 'LICENSE', '*.md')

Get-ChildItem -Path $RepoDir | Where-Object {
    $name = $_.Name
    -not ($Excludes | Where-Object { $name -like $_ })
} | ForEach-Object {
    $dest = Join-Path $RimeDir $_.Name
    if ($_.PSIsContainer) {
        # 目标目录已存在时 Copy-Item 会把源目录嵌套进去（lua\lua\），所以复制目录内容
        if (-not (Test-Path $dest)) {
            New-Item -ItemType Directory -Path $dest | Out-Null
        }
        Copy-Item -Path (Join-Path $_.FullName '*') -Destination $dest -Recurse -Force
    } else {
        Copy-Item -Path $_.FullName -Destination $dest -Force
    }
}

Write-Host ">>> 文件同步完成"

# 删除旧的 .custom.yaml 补丁（设置已合并进主文件）
$OldCustomFiles = @(
    "default.custom.yaml",
    "weasel.custom.yaml",
    "tiger.custom.yaml",
    "tigress.custom.yaml",
    "double_pinyin.custom.yaml"
)
foreach ($f in $OldCustomFiles) {
    $p = Join-Path $RimeDir $f
    if (Test-Path $p) {
        Remove-Item $p -Force
        Write-Host ">>> 已删除旧补丁: $f"
    }
}

# 清理以前部署时误嵌套出来的目录（如 lua\lua\）
foreach ($d in Get-ChildItem -Path $RepoDir -Directory) {
    $nested = Join-Path (Join-Path $RimeDir $d.Name) $d.Name
    if ((Test-Path $nested) -and -not (Test-Path (Join-Path $d.FullName $d.Name))) {
        Remove-Item $nested -Recurse -Force
        Write-Host ">>> 已清理误嵌套目录: $($d.Name)\$($d.Name)"
    }
}

# 重新部署
$WeaselRoot = $null
foreach ($key in @('HKLM:\SOFTWARE\WOW6432Node\Rime\Weasel', 'HKLM:\SOFTWARE\Rime\Weasel')) {
    $item = Get-ItemProperty -Path $key -ErrorAction SilentlyContinue
    if ($item -and $item.WeaselRoot) { $WeaselRoot = $item.WeaselRoot; break }
}
$Deployer = if ($WeaselRoot) { Join-Path $WeaselRoot 'WeaselDeployer.exe' }
if ($Deployer -and (Test-Path $Deployer)) {
    Write-Host ">>> 触发重新部署..."
    & $Deployer /deploy
} else {
    Write-Host ">>> 请在系统托盘右键小狼毫图标，点击「重新部署」"
}
