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
Write-Host ">>> 请在系统托盘右键小狼毫图标，点击「重新部署」"
