# 简化版MediaPipe下载脚本 - 使用最新版本
# 如果指定版本不存在，使用此脚本

$ErrorActionPreference = "Stop"

# 使用 latest 版本（更可靠）
$VERSIONS = @{
    'hands' = 'latest'  # 或使用 '0.4' 获取最新的 0.4.x 版本
    'camera_utils' = 'latest'  # 或使用 '0.3'
    'drawing_utils' = 'latest'  # 或使用 '0.3'
}

$CDN_SOURCES = @(
    @{ name = 'jsdelivr'; base_url = 'https://cdn.jsdelivr.net/npm/@mediapipe' }
    @{ name = 'unpkg'; base_url = 'https://unpkg.com/@mediapipe' }
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$TargetDir = Join-Path $ProjectRoot "static\lib\mediapipe"

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

function Download-File {
    param([string]$Url, [string]$TargetPath)
    
    try {
        Write-Host "  下载: $(Split-Path -Leaf $TargetPath)" -ForegroundColor Yellow
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $TargetPath -UseBasicParsing
        $fileSizeMB = [math]::Round((Get-Item $TargetPath).Length / 1MB, 2)
        Write-Host "  ✅ 成功 ($fileSizeMB MB)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  ❌ 失败: $($_.Exception.Message)" -ForegroundColor Red
        if (Test-Path $TargetPath) { Remove-Item $TargetPath -Force }
        return $false
    }
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "  MediaPipe库下载 (使用最新版本)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$Files = @(
    @{ package = 'hands'; file = 'hands.js'; version = $VERSIONS['hands'] }
    @{ package = 'camera_utils'; file = 'camera_utils.js'; version = $VERSIONS['camera_utils'] }
    @{ package = 'drawing_utils'; file = 'drawing_utils.js'; version = $VERSIONS['drawing_utils'] }
)

$SuccessCount = 0

foreach ($fileInfo in $Files) {
    Write-Host "📦 $($fileInfo.file)..." -ForegroundColor Cyan
    $targetPath = Join-Path $TargetDir $fileInfo.file
    $downloaded = $false
    
    foreach ($cdn in $CDN_SOURCES) {
        $url = "$($cdn.base_url)/$($fileInfo.package)@$($fileInfo.version)/$($fileInfo.file)"
        if (Download-File -Url $url -TargetPath $targetPath) {
            $downloaded = $true
            $SuccessCount++
            break
        }
    }
    
    if (-not $downloaded) {
        Write-Host "  ❌ 下载失败" -ForegroundColor Red
    }
}

Write-Host ""
if ($SuccessCount -eq $Files.Count) {
    Write-Host "✅ 所有文件下载成功！" -ForegroundColor Green
    Write-Host "文件位置: $TargetDir" -ForegroundColor Cyan
} else {
    Write-Host "⚠️ $SuccessCount/$($Files.Count) 个文件下载成功" -ForegroundColor Yellow
}

