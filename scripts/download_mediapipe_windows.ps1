# MediaPipe库下载脚本 (Windows PowerShell)
# 用法: .\scripts\download_mediapipe_windows.ps1

$ErrorActionPreference = "Stop"

# 版本信息（使用最新版本，如果特定版本不存在）
$VERSIONS = @{
    'hands' = '0.4.1675469404'  # 如果此版本不存在，会尝试 'latest' 或 '0.4'
    'camera_utils' = '0.3.1675466867'  # 如果此版本不存在，会尝试 'latest' 或 '0.3'
    'drawing_utils' = '0.3.1620248257'  # 如果此版本不存在，会尝试 'latest' 或 '0.3'
}

# 备用版本策略
$FALLBACK_VERSIONS = @{
    'hands' = @('latest', '0.4')
    'camera_utils' = @('latest', '0.3')
    'drawing_utils' = @('latest', '0.3')
}

# CDN地址（多个备选）
$CDN_SOURCES = @(
    @{
        name = 'jsdelivr'
        base_url = 'https://cdn.jsdelivr.net/npm/@mediapipe'
    },
    @{
        name = 'unpkg'
        base_url = 'https://unpkg.com/@mediapipe'
    }
)

# 获取项目根目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$TargetDir = Join-Path $ProjectRoot "static\lib\mediapipe"

# 创建目标目录
Write-Host "创建目录: $TargetDir" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

# 下载文件的函数
function Download-File {
    param(
        [string]$Url,
        [string]$TargetPath
    )
    
    try {
        Write-Host "  正在下载: $Url" -ForegroundColor Yellow
        Write-Host "  保存到: $TargetPath" -ForegroundColor Gray
        
        # 使用Invoke-WebRequest下载
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $TargetPath -UseBasicParsing
        
        # 检查文件大小
        $fileInfo = Get-Item $TargetPath
        $fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
        
        if ($fileInfo.Length -gt 0) {
            Write-Host "  ✅ 下载成功 ($fileSizeMB MB)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ❌ 文件大小为0，下载可能失败" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "  ❌ 下载失败: $($_.Exception.Message)" -ForegroundColor Red
        # 删除可能的不完整文件
        if (Test-Path $TargetPath) {
            Remove-Item $TargetPath -Force
        }
        return $false
    }
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "  MediaPipe库下载工具 (Windows)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "目标目录: $TargetDir" -ForegroundColor Cyan
Write-Host ""

# 需要下载的核心文件
$CoreFiles = @(
    @{
        package = 'hands'
        file = 'hands.js'
        version = $VERSIONS['hands']
    },
    @{
        package = 'camera_utils'
        file = 'camera_utils.js'
        version = $VERSIONS['camera_utils']
    },
    @{
        package = 'drawing_utils'
        file = 'drawing_utils.js'
        version = $VERSIONS['drawing_utils']
    }
)

$SuccessCount = 0
$FailedFiles = @()

# 下载核心文件
foreach ($fileInfo in $CoreFiles) {
    $package = $fileInfo.package
    $filename = $fileInfo.file
    $version = $fileInfo.version
    
    Write-Host "📦 下载 $package ($filename)..." -ForegroundColor Cyan
    
    $targetPath = Join-Path $TargetDir $filename
    $downloaded = $false
    
    # 尝试每个CDN，如果指定版本失败，尝试备用版本
    $versionsToTry = @($version) + $FALLBACK_VERSIONS[$package]
    
    foreach ($tryVersion in $versionsToTry) {
        foreach ($cdn in $CDN_SOURCES) {
            $url = "$($cdn.base_url)/$package@$tryVersion/$filename"
            Write-Host "  尝试从 $($cdn.name) CDN 下载 (版本: $tryVersion)..." -ForegroundColor Gray
            
            if (Download-File -Url $url -TargetPath $targetPath) {
                $downloaded = $true
                $SuccessCount++
                if ($tryVersion -ne $version) {
                    Write-Host "  ⚠️ 使用了备用版本 $tryVersion 替代 $version" -ForegroundColor Yellow
                }
                break
            }
        }
        
        if ($downloaded) {
            break
        }
    }
    
    if (-not $downloaded) {
        Write-Host "  ❌ $filename 下载失败（所有CDN都无法访问）" -ForegroundColor Red
        $FailedFiles += $filename
    }
}

# 下载MediaPipe Hands的依赖文件
Write-Host ""
Write-Host "📦 下载MediaPipe Hands依赖文件..." -ForegroundColor Cyan

$DependencyFiles = @(
    'hands_solution_packed_assets.data',
    'hands_solution_packed_assets_loader.js',
    'hands.binarypb',
    'hands_wasm_internal.js',
    'hands_wasm_internal.wasm',
    'hands_landmark_full.tflite'
)

foreach ($depFile in $DependencyFiles) {
    $targetPath = Join-Path $TargetDir $depFile
    
    if (Test-Path $targetPath) {
        Write-Host "  ✓ $depFile 已存在，跳过" -ForegroundColor Green
        continue
    }
    
    $downloaded = $false
    foreach ($cdn in $CDN_SOURCES) {
        $url = "$($cdn.base_url)/hands@$($VERSIONS['hands'])/$depFile"
        Write-Host "  下载 $depFile..." -ForegroundColor Gray
        if (Download-File -Url $url -TargetPath $targetPath) {
            $downloaded = $true
            break
        }
    }
    
    if (-not $downloaded) {
        Write-Host "  ⚠️ $depFile 下载失败，但不影响基本功能" -ForegroundColor Yellow
    }
}

# 总结
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  下载完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

if ($SuccessCount -eq $CoreFiles.Count) {
    Write-Host "✅ 所有核心文件下载成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "文件保存在: $TargetDir" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "下一步操作：" -ForegroundColor Yellow
    Write-Host "1. 检查文件: git status" -ForegroundColor White
    Write-Host "2. 添加到Git: git add static/lib/mediapipe/" -ForegroundColor White
    Write-Host "3. 提交: git commit -m 'Add MediaPipe libraries'" -ForegroundColor White
    Write-Host "4. 推送: git push" -ForegroundColor White
} else {
    Write-Host "⚠️ $SuccessCount/$($CoreFiles.Count) 个核心文件下载成功" -ForegroundColor Yellow
    if ($FailedFiles.Count -gt 0) {
        Write-Host "失败的文件: $($FailedFiles -join ', ')" -ForegroundColor Red
        Write-Host ""
        Write-Host "建议：" -ForegroundColor Yellow
        Write-Host "1. 检查网络连接" -ForegroundColor White
        Write-Host "2. 尝试使用VPN或更换网络环境" -ForegroundColor White
        Write-Host "3. 手动下载文件（参见 MEDIAPIPE_DOWNLOAD.md）" -ForegroundColor White
    }
}

