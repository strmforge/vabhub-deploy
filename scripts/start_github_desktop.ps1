# GitHub Desktop 启动脚本
Write-Host "正在启动 GitHub Desktop..." -ForegroundColor Green

$githubDesktopPath = "C:\Users\$env:USERNAME\AppData\Local\GitHubDesktop\GitHubDesktop.exe"

if (Test-Path $githubDesktopPath) {
    Start-Process $githubDesktopPath
    Write-Host "GitHub Desktop 已启动！" -ForegroundColor Green
} else {
    Write-Host "未找到 GitHub Desktop，请检查安装路径" -ForegroundColor Red
}

Write-Host ""
Write-Host "GitHub Desktop 安装位置：" -ForegroundColor Yellow
Write-Host $githubDesktopPath -ForegroundColor Cyan