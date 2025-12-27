# 部署指南

## 使用 docker-compose 部署

### 前置要求

- Linux 服务器（推荐 Ubuntu 20.04+ 或 CentOS 7+）
- Docker 20.10+
- docker-compose 1.29+

### 快速开始

1. **上传项目文件到服务器**

```bash
# 使用 scp 或其他方式将项目上传到服务器
scp -r picture-search user@your-server:/opt/
```

2. **登录服务器并进入项目目录**

```bash
ssh user@your-server
cd /opt/picture-search
```

3. **配置环境变量（可选）**

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置 SECRET_KEY
nano .env
```

在 `.env` 文件中设置：
```
SECRET_KEY=your-random-secret-key-here
```

4. **启动服务**

```bash
# 构建并启动容器（后台运行）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看服务状态
docker-compose ps
```

5. **访问应用**

打开浏览器访问：`http://your-server-ip:5005`

> 注意：如果 5005 端口也被占用，可以在 `docker-compose.yml` 中将端口映射改为其他端口，例如 `8888:5000`

### 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 重新构建镜像
docker-compose build

# 重新构建并启动
docker-compose up -d --build
```

### 配置 Nginx 反向代理

如果需要使用域名访问，可以配置 Nginx：

1. **安装 Nginx**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

2. **创建 Nginx 配置文件**

```bash
sudo nano /etc/nginx/sites-available/picture-search
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件缓存
    location /static/ {
        proxy_pass http://localhost:5005;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

3. **启用配置**

```bash
# Ubuntu/Debian
sudo ln -s /etc/nginx/sites-available/picture-search /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# CentOS/RHEL
sudo cp /etc/nginx/sites-available/picture-search /etc/nginx/conf.d/
sudo nginx -t
sudo systemctl reload nginx
```

### 配置 HTTPS（推荐）

使用 Let's Encrypt 获取免费 SSL 证书：

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx  # Ubuntu/Debian
sudo yum install certbot python3-certbot-nginx      # CentOS/RHEL

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

### 数据备份

上传的图片数据存储在 `./static/uploads` 目录，建议定期备份：

```bash
# 备份脚本示例
tar -czf picture-search-backup-$(date +%Y%m%d).tar.gz static/uploads/
```

### 故障排查

1. **查看容器日志**
```bash
docker-compose logs -f picture-search
```

2. **检查容器状态**
```bash
docker-compose ps
docker ps -a
```

3. **进入容器调试**
```bash
docker-compose exec picture-search bash
```

4. **检查端口占用**
```bash
sudo netstat -tlnp | grep 5005
# 或
sudo ss -tlnp | grep 5005
```

5. **重启服务**
```bash
docker-compose restart
```

### 性能优化

1. **使用 Gunicorn 替代 Flask 开发服务器**（可选）

修改 Dockerfile 的 CMD：

```dockerfile
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

并在 requirements.txt 中添加：
```
gunicorn==21.2.0
```

2. **配置资源限制**

在 docker-compose.yml 中添加：

```yaml
services:
  picture-search:
    # ... 其他配置
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 安全建议

1. 修改默认的 SECRET_KEY
2. 配置防火墙规则
3. 使用 HTTPS
4. 定期更新系统和 Docker 镜像
5. 限制上传文件大小（已在代码中限制为 10MB）

