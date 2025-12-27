# 图片互动应用部署脚本 (Windows PowerShell)
# 用法: .\deploy.ps1 [-Force] [-Logs] [-Help]

param(
    [switch]$Force,
    [switch]$Logs,
    [switch]$Help
)

# 错误处理
$ErrorActionPreference = "Stop"

# 显示帮助信息
if ($Help) {
    Write-Host "用法: .\deploy.ps1 [选项]" -ForegroundColor Cyan
    Write-Host "选项:"
    Write-Host "  -Force     强制重新构建（不使用缓存）" -ForegroundColor Yellow
    Write-Host "  -Logs      部署后查看日志" -ForegroundColor Yellow
    Write-Host "  -Help      显示帮助信息" -ForegroundColor Yellow
    exit 0
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "  图片互动应用部署脚本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 检查 docker-compose 是否安装
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "错误: 未找到 docker-compose 命令" -ForegroundColor Red
    Write-Host "请先安装 docker-compose"
    exit 1
}

# 检查 Dockerfile 是否存在
if (-not (Test-Path "Dockerfile")) {
    Write-Host "错误: 未找到 Dockerfile" -ForegroundColor Red
    Write-Host "请在项目根目录运行此脚本"
    exit 1
}

try {
    # 步骤 1: 停止当前容器
    Write-Host "[1/4] 停止当前容器..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✓ 容器已停止" -ForegroundColor Green
    Write-Host ""

    # 步骤 2: 重新构建镜像
    Write-Host "[2/4] 构建 Docker 镜像..." -ForegroundColor Yellow
    if ($Force) {
        Write-Host "  使用 --no-cache 强制重新构建..." -ForegroundColor Yellow
        docker-compose build --no-cache
    } else {
        docker-compose build
    }
    Write-Host "✓ 镜像构建完成" -ForegroundColor Green
    Write-Host ""

    # 步骤 3: 启动服务
    Write-Host "[3/4] 启动服务..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "✓ 服务已启动" -ForegroundColor Green
    Write-Host ""

    # 等待服务启动
    Write-Host "[4/4] 等待服务就绪..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3

    # 检查容器状态
    $psOutput = docker-compose ps
    if ($psOutput -match "Up") {
        Write-Host "✓ 服务运行正常" -ForegroundColor Green
        Write-Host ""

        # 显示容器信息
        Write-Host "容器状态:" -ForegroundColor Green
        docker-compose ps
        Write-Host ""

        # 显示访问地址
        $composeContent = Get-Content docker-compose.yml
        $portLine = $composeContent | Select-String -Pattern '^\s+-\s+"(\d+):' | Select-Object -First 1
        if ($portLine) {
            $port = $portLine.Matches.Groups[1].Value
            Write-Host "访问地址:" -ForegroundColor Green
            Write-Host "  http://localhost:$port"
            Write-Host "  (或替换为您的服务器IP)"
        }
        Write-Host ""

        # 显示日志
        if ($Logs) {
            Write-Host "显示实时日志 (按 Ctrl+C 退出)..." -ForegroundColor Yellow
            Write-Host ""
            docker-compose logs -f
        } else {
            Write-Host "部署完成！" -ForegroundColor Green
            Write-Host ""
            Write-Host "常用命令:"
            Write-Host "  查看日志:    docker-compose logs -f"
            Write-Host "  查看状态:    docker-compose ps"
            Write-Host "  停止服务:    docker-compose down"
            Write-Host "  重启服务:    docker-compose restart"
        }
    } else {
        Write-Host "✗ 服务启动失败，请查看日志" -ForegroundColor Red
        Write-Host "运行以下命令查看错误:"
        Write-Host "  docker-compose logs"
        exit 1
    }
} catch {
    Write-Host "部署过程中发生错误: $_" -ForegroundColor Red
    Write-Host "请检查错误信息并重试"
    exit 1
}

