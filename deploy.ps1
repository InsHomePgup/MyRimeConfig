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
$Excludes = @('.git', 'deploy.sh', 'deploy.ps1', 'LICENSE', '*.md')

Get-ChildItem -Path $RepoDir | Where-Object {
    $name = $_.Name
    -not ($Excludes | Where-Object { $name -like $_ })
} | ForEach-Object {
    $dest = Join-Path $RimeDir $_.Name
    if ($_.PSIsContainer) {
        Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
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

Write-Host ">>> 请在系统托盘右键小狼毫图标，点击「重新部署」"
