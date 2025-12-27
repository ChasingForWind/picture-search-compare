# 故障排查指南

## 查看日志

如果遇到 Internal Server Error，首先查看容器日志：

```bash
# 查看实时日志
docker-compose logs -f picture-search

# 查看最近的日志
docker-compose logs --tail=100 picture-search
```

## 常见问题

### 1. Internal Server Error

**可能原因：**
- 模板文件找不到
- 静态文件路径错误
- pairs.json 文件权限问题
- Python 模块导入错误

**解决方法：**

1. **检查容器内的文件结构：**
```bash
docker-compose exec picture-search ls -la /app
docker-compose exec picture-search ls -la /app/templates
docker-compose exec picture-search ls -la /app/static
```

2. **检查 pairs.json 文件：**
```bash
docker-compose exec picture-search ls -la /app/static/uploads/
docker-compose exec picture-search cat /app/static/uploads/pairs.json
```

3. **进入容器调试：**
```bash
docker-compose exec picture-search bash
cd /app
python
>>> from app import create_app
>>> app = create_app()
```

4. **检查 Python 错误：**
```bash
docker-compose exec picture-search python -c "from app import create_app; app = create_app(); print('OK')"
```

### 2. 文件权限问题

如果遇到权限错误，检查并修复：

```bash
# 在宿主机上
chmod -R 755 static/uploads
chown -R $(whoami):$(whoami) static/uploads
```

### 3. 端口占用

检查端口是否被占用：

```bash
netstat -tlnp | grep 5005
# 或
ss -tlnp | grep 5005
```

### 4. 重新构建镜像

如果代码已更新，需要重新构建：

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 5. 清理并重新部署

完全清理并重新部署：

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 获取详细错误信息

在开发环境中，可以临时启用调试模式（仅用于调试，不要在生产环境使用）：

修改 `docker-compose.yml`：

```yaml
environment:
  - FLASK_ENV=development
  - FLASK_DEBUG=1
```

然后查看详细错误信息。

