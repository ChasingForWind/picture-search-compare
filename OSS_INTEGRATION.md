# OSS 集成方案

使用阿里云 OSS 或其他对象存储服务可以显著提升上传速度和用户体验。

## 为什么使用 OSS？

### 优势

1. **上传速度更快**
   - OSS 专为文件上传优化
   - 支持分片上传，大文件上传更快
   - 带宽更大，不受服务器带宽限制

2. **减轻服务器负担**
   - 图片存储在 OSS，不占用服务器磁盘
   - 减少服务器磁盘 I/O
   - 降低服务器存储成本

3. **CDN 加速**
   - OSS 自动集成 CDN
   - 全球加速，用户访问更快
   - 减少服务器带宽消耗

4. **可扩展性**
   - 存储容量无限扩展
   - 按使用量付费

## 实施步骤

### 方案一：后端上传到 OSS（推荐）

#### 1. 安装 OSS SDK

```bash
pip install oss2
```

在 `requirements.txt` 添加：
```
oss2==2.18.4
```

#### 2. 修改后端代码

创建 `app/oss_client.py`：

```python
import oss2
import os
from typing import Optional

class OSSClient:
    def __init__(self):
        # 从环境变量读取配置
        self.access_key_id = os.environ.get('OSS_ACCESS_KEY_ID')
        self.access_key_secret = os.environ.get('OSS_ACCESS_KEY_SECRET')
        self.endpoint = os.environ.get('OSS_ENDPOINT', 'https://oss-cn-hangzhou.aliyuncs.com')
        self.bucket_name = os.environ.get('OSS_BUCKET_NAME')
        self.use_oss = all([self.access_key_id, self.access_key_secret, self.bucket_name])
        
        if self.use_oss:
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
        else:
            self.bucket = None
    
    def upload_file(self, file_path: str, object_name: str) -> Optional[str]:
        """上传文件到 OSS"""
        if not self.use_oss:
            return None
        
        try:
            self.bucket.put_object_from_file(object_name, file_path)
            # 返回公共访问 URL
            url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/{object_name}"
            return url
        except Exception as e:
            print(f"OSS upload error: {e}")
            return None
    
    def upload_file_object(self, file_obj, object_name: str) -> Optional[str]:
        """直接上传文件对象到 OSS"""
        if not self.use_oss:
            return None
        
        try:
            result = self.bucket.put_object(object_name, file_obj)
            url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/{object_name}"
            return url
        except Exception as e:
            print(f"OSS upload error: {e}")
            return None

# 全局实例
oss_client = OSSClient()
```

#### 3. 修改上传逻辑

修改 `app/utils.py`，添加 OSS 上传支持：

```python
from app.oss_client import oss_client

def save_uploaded_image(file, upload_folder: str) -> Optional[Tuple[str, str]]:
    """保存图片，优先上传到 OSS"""
    if file and file.filename and allowed_file(file.filename):
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(upload_folder, filename)
        
        try:
            # 处理图片...
            img = Image.open(file.stream)
            # ... (处理逻辑保持不变)
            
            # 保存到本地（作为备份）
            img.save(filepath, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
            
            # 尝试上传到 OSS
            object_name = f"uploads/images/{filename}"
            oss_url = oss_client.upload_file(filepath, object_name)
            
            if oss_url:
                # 使用 OSS URL
                return file.filename, oss_url
            else:
                # 使用本地路径
                relative_path = os.path.join('images', filename).replace('\\', '/')
                return file.filename, relative_path
                
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    return None
```

#### 4. 配置环境变量

在 `docker-compose.yml` 中添加：

```yaml
environment:
  - OSS_ACCESS_KEY_ID=${OSS_ACCESS_KEY_ID}
  - OSS_ACCESS_KEY_SECRET=${OSS_ACCESS_KEY_SECRET}
  - OSS_ENDPOINT=${OSS_ENDPOINT:-https://oss-cn-hangzhou.aliyuncs.com}
  - OSS_BUCKET_NAME=${OSS_BUCKET_NAME}
```

在 `.env` 文件中配置：

```bash
OSS_ACCESS_KEY_ID=your-access-key-id
OSS_ACCESS_KEY_SECRET=your-access-key-secret
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your-bucket-name
```

### 方案二：前端直传到 OSS（最快）

前端直接上传到 OSS，完全绕过服务器。

#### 1. 后端生成签名 URL

添加 API 端点生成临时上传凭证：

```python
@bp.route('/api/oss/upload_token', methods=['POST'])
def get_upload_token():
    """获取 OSS 上传凭证"""
    # 使用 STS 临时凭证或签名 URL
    # 返回上传 URL 和参数
    pass
```

#### 2. 前端直接上传

```javascript
// 获取上传凭证
const tokenResponse = await fetch('/api/oss/upload_token');
const { uploadUrl, formData: formFields } = await tokenResponse.json();

// 直接上传到 OSS
const formData = new FormData();
for (let key in formFields) {
    formData.append(key, formFields[key]);
}
formData.append('file', file);

await fetch(uploadUrl, {
    method: 'POST',
    body: formData
});
```

## 成本估算

### 阿里云 OSS 价格（示例）

- **存储费用**：0.12 元/GB/月
- **流量费用**：
  - 0.5 元/GB（中国大陆）
  - 0.8 元/GB（海外）
- **请求费用**：0.01 元/万次 PUT 请求

**示例计算**（1000 张图片，每张 2MB）：
- 存储：2GB × 0.12 元 = 0.24 元/月
- 上传流量：2GB × 0.5 元 = 1 元（一次性）
- 请求费用：1000 次 × 0.01/10000 = 0.001 元

**总计**：约 1.24 元（首次）+ 0.24 元/月

## 其他优化建议

### 1. 升级服务器配置

- **增加带宽**：从 1Mbps 升级到 5Mbps 或 10Mbps
- **增加内存**：4GB → 8GB（支持更多并发）
- **使用 SSD**：提升磁盘 I/O 性能

### 2. 使用 CDN

即使不用 OSS，也可以使用 CDN 加速图片访问：
- 阿里云 CDN
- 腾讯云 CDN
- Cloudflare（免费）

### 3. 优化网络

- 使用专线连接
- 优化服务器到 OSS 的网络路径
- 使用多地域部署

### 4. 图片预处理

- 提前压缩图片
- 使用 WebP 格式（文件更小）
- 实现图片懒加载

## 推荐方案

**最佳性价比**：
1. 使用 OSS（方案一：后端上传）
2. 配合 CDN 加速
3. 前端优化（减少压缩时间）

**最快速度**：
1. 前端直传 OSS（方案二）
2. 使用 OSS 分片上传
3. 多线程上传

