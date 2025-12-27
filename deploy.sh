#!/bin/bash

# 图片互动应用部署脚本
# 用法: ./deploy.sh [选项]
# 选项:
#   -f, --force    强制重新构建（不使用缓存）
#   -l, --logs     部署后查看日志
#   -h, --help     显示帮助信息

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 默认参数
FORCE_REBUILD=false
SHOW_LOGS=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE_REBUILD=true
            shift
            ;;
        -l|--logs)
            SHOW_LOGS=true
            shift
            ;;
        -h|--help)
            echo "用法: $0 [选项]"
            echo "选项:"
            echo "  -f, --force    强制重新构建（不使用缓存）"
            echo "  -l, --logs     部署后查看日志"
            echo "  -h, --help     显示帮助信息"
            exit 0
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            echo "使用 -h 或 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  图片互动应用部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: 未找到 docker-compose 命令${NC}"
    echo "请先安装 docker-compose"
    exit 1
fi

# 检查 Dockerfile 是否存在
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}错误: 未找到 Dockerfile${NC}"
    echo "请在项目根目录运行此脚本"
    exit 1
fi

# 步骤 1: 停止当前容器
echo -e "${YELLOW}[1/4] 停止当前容器...${NC}"
docker-compose down
echo -e "${GREEN}✓ 容器已停止${NC}"
echo ""

# 步骤 2: 重新构建镜像
echo -e "${YELLOW}[2/4] 构建 Docker 镜像...${NC}"
if [ "$FORCE_REBUILD" = true ]; then
    echo -e "${YELLOW}  使用 --no-cache 强制重新构建...${NC}"
    docker-compose build --no-cache
else
    docker-compose build
fi
echo -e "${GREEN}✓ 镜像构建完成${NC}"
echo ""

# 步骤 3: 启动服务
echo -e "${YELLOW}[3/4] 启动服务...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ 服务已启动${NC}"
echo ""

# 等待服务启动
echo -e "${YELLOW}[4/4] 等待服务就绪...${NC}"
sleep 3

# 检查容器状态
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ 服务运行正常${NC}"
    echo ""
    
    # 显示容器信息
    echo -e "${GREEN}容器状态:${NC}"
    docker-compose ps
    echo ""
    
    # 显示访问地址
    PORT=$(grep -E "^\s+- \"\d+:" docker-compose.yml | sed 's/.*"\([^"]*\):.*/\1/' | head -1)
    echo -e "${GREEN}访问地址:${NC}"
    echo "  http://localhost:${PORT}"
    echo "  (或替换为您的服务器IP)"
    echo ""
else
    echo -e "${RED}✗ 服务启动失败，请查看日志${NC}"
    echo "运行以下命令查看错误:"
    echo "  docker-compose logs"
    exit 1
fi

# 显示日志
if [ "$SHOW_LOGS" = true ]; then
    echo -e "${YELLOW}显示实时日志 (按 Ctrl+C 退出)...${NC}"
    echo ""
    docker-compose logs -f
else
    echo -e "${GREEN}部署完成！${NC}"
    echo ""
    echo "常用命令:"
    echo "  查看日志:    docker-compose logs -f"
    echo "  查看状态:    docker-compose ps"
    echo "  停止服务:    docker-compose down"
    echo "  重启服务:    docker-compose restart"
fi

