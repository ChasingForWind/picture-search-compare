# 性能优化说明

## 已实施的优化措施

### 1. 图片压缩和尺寸限制

- **最大尺寸限制**：1920x1920 像素（保持宽高比）
- **自动压缩**：上传时自动压缩为 JPEG 格式
- **渐进式 JPEG**：使用渐进式JPEG格式，提升加载体验
- **质量优化**：JPEG 质量设置为 85%，在质量和文件大小之间取得平衡
- **前端压缩**：浏览器端先压缩，减少上传数据量

### 2. 生产服务器（Gunicorn）

- **多进程**：使用 4 个 worker 进程处理请求
- **多线程**：每个进程使用 2 个线程
- **超时设置**：120 秒超时，适合大文件上传
- **日志记录**：访问日志和错误日志输出到标准输出

### 3. 文件大小限制

- **单文件最大**：10MB
- **自动降质**：如果压缩后仍超过限制，自动降低质量

## 性能对比

**优化前：**
- 使用 Flask 开发服务器（单线程）
- 无图片压缩
- 可能上传非常大的原始图片

**优化后：**
- 使用 Gunicorn（4进程 x 2线程 = 8并发）
- 图片自动压缩和尺寸调整
- 上传数据量显著减少（通常减少 70-90%）

## 进一步优化建议

### 1. 使用 CDN（内容分发网络）

如果图片需要频繁访问，可以考虑使用 CDN：
- 阿里云 OSS + CDN
- 腾讯云 COS + CDN
- AWS S3 + CloudFront

### 2. 图片懒加载

在历史记录列表中，使用图片懒加载：
```javascript
// 使用 Intersection Observer API
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            observer.unobserve(img);
        }
    });
});
```

### 3. 添加缓存

在 Nginx 配置中添加缓存头：
```nginx
location /static/ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 4. 数据库优化（如果数据量大）

如果图片对数量很大（>1000），可以考虑：
- 使用 SQLite 或 PostgreSQL 替代 JSON 文件
- 添加分页功能
- 添加索引

### 5. 监控和日志

添加性能监控：
- 监控上传时间
- 监控服务器资源使用
- 设置告警

## Gunicorn 配置调优

如果需要调整 Gunicorn 配置，可以创建 `gunicorn_config.py`：

```python
bind = "0.0.0.0:5000"
workers = 4
threads = 2
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
```

然后在 Dockerfile 中：
```dockerfile
CMD ["gunicorn", "-c", "gunicorn_config.py", "run:app"]
```

## 测试性能

可以使用以下方法测试性能：

```bash
# 测试上传速度
time curl -X POST -F "image1=@test.jpg" -F "image2=@test2.jpg" http://localhost:5005/upload

# 查看服务器资源使用
docker stats picture-search-app

# 查看 Gunicorn 进程
docker-compose exec picture-search ps aux | grep gunicorn
```

