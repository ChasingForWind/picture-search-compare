# 图片互动Web应用

一个基于Flask和MediaPipe的图片互动Web应用，支持上传两张图片，通过摄像头识别手掌位置实现交互式对比展示。

## 功能特性

- 📸 上传两张图片并保存为图片对
- 🎯 摄像头实时手部识别
- 🖼️ 手掌区域动态显示第二张图片，实现交互式对比
- 📚 历史记录管理，支持查看和删除
- 🐳 Docker容器化部署

## 技术栈

- **后端**: Flask (Python 3.9+)
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **手部识别**: MediaPipe Hands
- **图片处理**: Pillow (后端), Canvas API (前端)
- **容器化**: Docker

## 快速开始

### 本地开发

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

3. 访问应用：
打开浏览器访问 `http://localhost:5000`

### Docker部署

#### 方式一：使用 docker-compose（推荐）

1. 确保已安装 docker-compose

2. 配置环境变量（可选，创建 `.env` 文件）：
```bash
SECRET_KEY=your-secret-key-here
```

3. 启动服务：
```bash
docker-compose up -d
```

4. 查看日志：
```bash
docker-compose logs -f
```

5. 停止服务：
```bash
docker-compose down
```

6. 访问应用：
打开浏览器访问 `http://localhost:5000`

#### 方式二：使用 Docker 命令

1. 构建镜像：
```bash
docker build -t picture-search .
```

2. 运行容器：
```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/static/uploads:/app/static/uploads \
  --name picture-search-app \
  --restart unless-stopped \
  picture-search
```

3. 访问应用：
打开浏览器访问 `http://localhost:5000`

### 阿里云部署

1. **使用 docker-compose 部署（推荐）**：
   ```bash
   # 在服务器上克隆项目或上传文件
   cd /path/to/picture-search
   
   # 创建 .env 文件并配置环境变量
   cp .env.example .env
   # 编辑 .env 文件，设置 SECRET_KEY
   
   # 启动服务
   docker-compose up -d
   
   # 查看状态
   docker-compose ps
   docker-compose logs -f
   ```

2. **配置 Nginx 反向代理**（可选）：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **配置 HTTPS**（推荐，因为需要访问摄像头）：
   - 使用 Let's Encrypt 获取免费 SSL 证书
   - 配置 Nginx SSL 证书

4. **数据持久化**：
   - 上传的图片数据保存在 `./static/uploads` 目录
   - 建议定期备份该目录

## 使用说明

1. **上传图片**：在上传页面选择两张图片（建议用于建筑新旧对比）
2. **查看展示**：点击"查看"按钮或上传后自动跳转到展示页面
3. **交互操作**：允许浏览器访问摄像头，将手掌移动到摄像头前，手掌区域会显示第二张图片
4. **历史记录**：在主页面可以查看、加载和删除历史图片对

## 项目结构

```
picture-search/
├── app/                  # Flask应用
│   ├── __init__.py      # 应用初始化
│   ├── routes.py        # 路由处理
│   ├── models.py        # 数据模型
│   └── utils.py         # 工具函数
├── templates/           # HTML模板
├── static/              # 静态资源
│   ├── css/            # 样式文件
│   ├── js/             # JavaScript文件
│   └── uploads/        # 上传文件存储
├── requirements.txt     # Python依赖
└── Dockerfile          # Docker配置
```

## 安全注意事项

- 上传文件类型限制：仅支持图片格式（jpg, jpeg, png, webp）
- 文件大小限制：单张图片最大10MB
- 建议在生产环境配置HTTPS以访问摄像头功能

## 许可证

MIT License

