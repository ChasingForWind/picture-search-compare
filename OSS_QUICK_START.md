# OSS 快速配置指南

## 问题根源

您的服务器带宽只有 **0.01 Mbps**，这是上传慢的根本原因：
- 上传 2MB 图片需要：**26 分钟**！
- 即使压缩后 1.5MB，也需要 **20 分钟**！

## CDN 加速原理（通俗解释）

### 传统方式的问题

想象您要去图书馆借书：
- 图书馆在杭州（您的服务器）
- 您在北京
- 图书馆只有一条小路（0.01 Mbps）
- **结果**：需要走很久很久 😰

### 使用 CDN 后的方式

CDN 就像在各地开了分店：
- 您在北京 → 去北京的分店（CDN节点）
- 分店就在附近 → 很快拿到书 ✅
- 如果分店没有，分店会去总店取（自动缓存）

### OSS + CDN 的工作流程

**上传（绕过您的服务器）**：
```
用户浏览器 → 直接上传到 OSS → 完成
（不经过您的服务器，所以不受 0.01 Mbps 限制）
```

**访问（通过 CDN）**：
```
用户浏览器 → 最近的 CDN 节点 → 快速返回
（CDN 节点带宽很大，通常 10 Gbps+）
```

## 快速配置步骤（10 分钟）

### 1. 创建 OSS Bucket（5 分钟）

1. 登录 [阿里云控制台](https://oss.console.aliyun.com/)
2. 点击"创建 Bucket"
3. 填写信息：
   ```
   Bucket 名称：picture-search-images（或其他唯一名称）
   地域：华东1（杭州）或离您最近的
   读写权限：公共读
   ```
4. 点击"确定"

### 2. 获取 AccessKey（2 分钟）

1. 鼠标悬停右上角头像
2. 点击"AccessKey 管理"
3. 创建或查看 AccessKey
4. **保存这两项**：
   - AccessKey ID
   - AccessKey Secret

### 3. 配置 CDN（可选，3 分钟）

1. 进入 [CDN 控制台](https://cdn.console.aliyun.com/)
2. 添加域名：
   ```
   加速域名：images.yourdomain.com（或使用系统分配的子域名）
   源站类型：OSS 域名
   源站地址：选择您刚创建的 Bucket
   ```
3. 保存后，会得到一个 CNAME 地址

### 4. 在服务器上配置（2 分钟）

SSH 登录服务器，编辑 `.env` 文件：

```bash
cd /path/to/picture-search-compare
nano .env
```

添加以下内容：

```bash
# OSS 配置
OSS_ACCESS_KEY_ID=LTAI5txxxxxxxxxxxxxx
OSS_ACCESS_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=picture-search-images

# CDN 配置（如果配置了 CDN）
OSS_CDN_DOMAIN=images.yourdomain.com
```

保存并退出（Ctrl+X, Y, Enter）

### 5. 重新部署（1 分钟）

```bash
./deploy.sh --force
```

### 6. 验证

查看日志确认 OSS 已启用：
```bash
docker-compose logs picture-search | grep OSS
```

应该看到：
```
OSS initialized: bucket=picture-search-images, endpoint=...
```

## 效果对比

### 配置前
- **上传速度**：26 分钟/2MB
- **服务器负担**：高（需要处理上传）
- **成本**：0 元（但几乎无法使用）

### 配置后
- **上传速度**：1-2 秒/2MB（提升约 **1000 倍**）
- **服务器负担**：低（不处理上传）
- **成本**：约 1-2 元/月

## 注意事项

1. **AccessKey 安全**：
   - 不要提交到代码仓库
   - 只给 OSS 读写权限，不要给其他权限

2. **Bucket 权限**：
   - 设置为"公共读"（否则 CDN 无法访问）
   - 不要设置为"公共读写"（安全风险）

3. **成本控制**：
   - 设置 OSS 生命周期规则
   - 定期清理旧图片

4. **CDN 缓存**：
   - 首次访问可能稍慢（需要回源）
   - 后续访问会很快（从缓存返回）

## 故障排查

### OSS 未启用

查看日志：
```bash
docker-compose logs picture-search | grep -i oss
```

如果看到 "OSS not configured"，检查：
- `.env` 文件是否正确配置
- 环境变量是否传递到容器

### 上传仍然慢

1. 确认 OSS 已启用（查看日志）
2. 检查图片是否真的上传到 OSS：
   - 登录 OSS 控制台
   - 查看 `uploads/images/` 目录
3. 查看浏览器网络请求：
   - 开发者工具 → Network
   - 查看上传请求的 URL

## 下一步

配置完成后，上传速度应该从 26 分钟降到 1-2 秒！

如果有问题，查看详细文档：
- `OSS_INTEGRATION.md` - 完整的集成方案
- `CDN_EXPLANATION.md` - CDN 原理解释

