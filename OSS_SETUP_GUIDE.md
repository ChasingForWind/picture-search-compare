# OSS + CDN 配置指南

## 问题分析

您的服务器配置显示：
- **公网带宽**：0.01 Mbps（非常低）
- **上传 2MB 图片**：理论上需要 26 分钟！

**解决方案**：使用 OSS + CDN，绕过服务器带宽限制

## CDN 加速原理解释

### 传统方式（慢）
```
用户 → 您的服务器（0.01 Mbps）→ 下载图片
问题：受服务器带宽严重限制
```

### 使用 OSS + CDN（快）
```
上传：用户 → OSS（10 Gbps）→ 秒级完成
访问：用户 → CDN节点（10 Gbps）→ 毫秒级返回
优势：完全绕过服务器带宽限制
```

### CDN 工作原理

1. **首次访问**：
   - 用户请求图片
   - CDN 节点检查缓存（没有）
   - 从 OSS 获取并缓存
   - 返回给用户

2. **后续访问**：
   - 用户请求图片
   - CDN 节点直接返回（从缓存）
   - 速度极快，不访问源站

3. **全球加速**：
   - 北京用户 → 北京 CDN 节点
   - 上海用户 → 上海 CDN 节点
   - 每个用户都访问最近的节点

## 配置步骤

### 步骤 1：创建 OSS Bucket

1. 登录阿里云控制台
2. 进入 OSS（对象存储）服务
3. 创建 Bucket：
   - **Bucket 名称**：例如 `picture-search-images`
   - **地域**：选择离您最近的（如：华东1-杭州）
   - **读写权限**：公共读（允许 CDN 访问）
   - **存储类型**：标准存储

### 步骤 2：配置 CDN 加速

1. 进入 CDN（内容分发网络）服务
2. 添加加速域名：
   - **加速域名**：例如 `images.yourdomain.com`
   - **源站类型**：OSS 域名
   - **源站地址**：选择您的 OSS Bucket
   - **加速区域**：仅中国内地（或全球）

3. 配置完成：
   - CDN 会分配一个 CNAME 地址
   - 需要在域名 DNS 中添加 CNAME 记录

### 步骤 3：获取 OSS AccessKey

1. 鼠标悬停右上角头像
2. 选择"AccessKey 管理"
3. 创建 AccessKey（如已有可跳过）
4. 保存：
   - **AccessKey ID**
   - **AccessKey Secret**

### 步骤 4：配置环境变量

在服务器项目目录创建或编辑 `.env` 文件：

```bash
# OSS 配置
OSS_ACCESS_KEY_ID=your-access-key-id
OSS_ACCESS_KEY_SECRET=your-access-key-secret
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=picture-search-images

# CDN 配置（可选，如果配置了 CDN）
OSS_CDN_DOMAIN=images.yourdomain.com
# 或使用 CDN 分配的域名
# OSS_CDN_DOMAIN=your-bucket-name.oss-cn-hangzhou.aliyuncs.com.w.cdngslb.com
```

### 步骤 5：重新部署

```bash
# 使用部署脚本
./deploy.sh --force

# 或手动部署
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 步骤 6：验证

1. 上传一张图片
2. 检查日志：
```bash
docker-compose logs picture-search | grep OSS
```
应该看到：`OSS initialized: bucket=xxx`

3. 查看上传的图片 URL：
   - 如果是 OSS URL：`https://bucket.oss-cn-hangzhou.aliyuncs.com/...`
   - 或 CDN URL：`https://images.yourdomain.com/...`

## OSS Endpoint 列表

根据您的 Bucket 地域选择正确的 endpoint：

```
华东1（杭州）：https://oss-cn-hangzhou.aliyuncs.com
华东2（上海）：https://oss-cn-shanghai.aliyuncs.com
华北2（北京）：https://oss-cn-beijing.aliyuncs.com
华南1（深圳）：https://oss-cn-shenzhen.aliyuncs.com
西南1（成都）：https://oss-cn-chengdu.aliyuncs.com
```

## 成本估算

### OSS 存储费用
- **标准存储**：0.12 元/GB/月
- **示例**：1000 张图片，每张 2MB = 2GB
- **费用**：2GB × 0.12 = 0.24 元/月

### CDN 流量费用
- **中国大陆**：0.24 元/GB
- **示例**：每天 100 次访问，每次 2MB = 200MB/天
- **月流量**：200MB × 30 = 6GB
- **费用**：6GB × 0.24 = 1.44 元/月

### OSS 请求费用
- **PUT 请求**：0.01 元/万次
- **示例**：1000 次上传
- **费用**：0.01 元

### 总成本
**约 1.7 元/月**（相比升级服务器带宽 50-200 元/月，非常便宜）

## 效果对比

### 上传速度
- **使用服务器**：0.01 Mbps，上传 2MB 需要 **26 分钟**
- **使用 OSS**：10 Gbps，上传 2MB 需要 **1-2 秒**
- **提升**：约 **1000 倍**！

### 访问速度
- **使用服务器**：0.01 Mbps，下载 2MB 需要 **26 分钟**
- **使用 CDN**：10-100 Mbps，下载 2MB 需要 **1-2 秒**
- **提升**：约 **1000 倍**！

## 注意事项

1. **首次上传可能稍慢**：需要建立连接
2. **CDN 缓存**：首次访问需要回源，后续访问会很快
3. **安全**：AccessKey 要保密，不要提交到代码仓库
4. **成本控制**：设置 OSS 生命周期规则，自动删除旧文件

## 常见问题

### Q: 不配置 CDN 可以吗？
A: 可以。OSS 本身就很快，但配置 CDN 后访问速度会更快。

### Q: 如何确认 OSS 是否生效？
A: 查看日志，如果看到 "OSS initialized" 说明配置成功。

### Q: 图片 URL 是 OSS 地址还是本地地址？
A: 如果 OSS 配置成功，会返回 OSS URL；失败则使用本地路径。

### Q: 可以混合使用吗？
A: 可以。旧图片使用本地路径，新图片使用 OSS URL。

## 下一步

1. 按照步骤配置 OSS
2. 重新部署应用
3. 测试上传速度
4. （可选）配置 CDN 进一步加速访问

