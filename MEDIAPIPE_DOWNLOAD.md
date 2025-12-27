# MediaPipe库下载说明

## 概述

由于CDN访问可能受限（特别是在中国大陆），本应用支持使用**服务器本地**的MediaPipe库。

**说明**：
- **"本地"指服务器本地**：MediaPipe库文件存储在服务器的 `static/lib/mediapipe/` 目录中
- **工作方式**：浏览器通过HTTP从您的服务器加载这些文件（类似从CDN加载，但源是您的服务器）
- **优势**：不依赖外部CDN，即使CDN无法访问也能正常工作
- **下载后**：应用将优先使用服务器本地文件，如果本地文件不存在才尝试从CDN加载

## 自动下载（推荐）

### 方法1：Windows环境下载（开发环境推荐）

如果您想在Windows开发环境下载，然后提交到Git，服务器拉取部署：

**使用PowerShell脚本**：
```powershell
# 在项目根目录执行
.\scripts\download_mediapipe_windows.ps1
```

**或使用批处理脚本**：
```cmd
# 双击运行，或在命令行执行
.\scripts\download_mediapipe_windows.bat
```

**下载完成后提交到Git**：
```bash
# 1. 检查文件
git status

# 2. 添加文件（注意：.gitignore已经允许提交MediaPipe库）
git add static/lib/mediapipe/

# 3. 提交
git commit -m "Add MediaPipe libraries for local serving"

# 4. 推送到GitHub
git push
```

**在服务器上拉取并部署**：
```bash
# 在服务器上
git pull
# 然后重新部署（使用docker-compose或您的部署脚本）
```

### 方法2：使用Python脚本（跨平台）

```bash
# 进入项目目录
cd picture-search

# 运行下载脚本
python scripts/download_mediapipe.py
```

脚本会自动：
- 创建 `static/lib/mediapipe/` 目录
- 从多个CDN下载必要的文件
- 如果某个CDN失败，自动尝试下一个

### 方法3：在Docker容器中下载

如果您在服务器上使用Docker：

```bash
# 进入容器
docker exec -it picture-search-app bash

# 运行下载脚本
python scripts/download_mediapipe.py

# 退出容器
exit
```

## 手动下载

如果自动脚本无法访问CDN，您可以手动下载文件。

**快速下载链接（可直接在浏览器打开）**：
- 📄 [完整手动下载指南](MEDIAPIPE_MANUAL_DOWNLOAD.md) - 包含所有文件的直接下载链接

**核心文件快速链接**：
1. **hands.js** (~1.5 MB)
   - https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands.js
   - https://unpkg.com/@mediapipe/hands@0.4.1675469404/hands.js
   
2. **camera_utils.js** (~50 KB)
   - https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@0.3.1675466867/camera_utils.js
   - https://unpkg.com/@mediapipe/camera_utils@0.3.1675466867/camera_utils.js

3. **drawing_utils.js** (~30 KB)
   - https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils@0.3.1620248257/drawing_utils.js
   - https://unpkg.com/@mediapipe/drawing_utils@0.3.1620248257/drawing_utils.js

**下载方法**：
- 点击链接，如果浏览器显示代码，按 `Ctrl+S` 保存
- 或右键链接 → "链接另存为"
- 保存到 `static/lib/mediapipe/` 目录

### 手动下载详细步骤

### 需要下载的文件

将以下文件下载到 `static/lib/mediapipe/` 目录：

#### 核心JavaScript文件（必需）

1. **hands.js**
   - URL: https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands.js
   - 或: https://unpkg.com/@mediapipe/hands@0.4.1675469404/hands.js

2. **camera_utils.js**
   - URL: https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@0.3.1675466867/camera_utils.js
   - 或: https://unpkg.com/@mediapipe/camera_utils@0.3.1675466867/camera_utils.js

3. **drawing_utils.js**
   - URL: https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils@0.3.1620248257/drawing_utils.js
   - 或: https://unpkg.com/@mediapipe/drawing_utils@0.3.1620248257/drawing_utils.js

#### 依赖文件（可选，但推荐下载）

以下文件会在运行时动态加载，建议一并下载：

4. **hands_solution_packed_assets.data**
   - URL: https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_solution_packed_assets.data

5. **hands_solution_packed_assets_loader.js**
   - URL: https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_solution_packed_assets_loader.js

6. **hands.binarypb**
   - URL: https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands.binarypb

7. **hands_wasm_internal.js**
   - URL: https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_wasm_internal.js

8. **hands_wasm_internal.wasm**
   - URL: https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_wasm_internal.wasm

9. **hands_landmark_full.tflite**
   - URL: https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_landmark_full.tflite

### 下载步骤

1. **创建目录**
   ```bash
   mkdir -p static/lib/mediapipe
   ```

2. **下载文件**

   使用浏览器：
   - 右键点击上述URL → "另存为"
   - 保存到 `static/lib/mediapipe/` 目录

   或使用命令行（Linux/Mac）：
   ```bash
   cd static/lib/mediapipe
   
   # 下载核心文件
   wget https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands.js
   wget https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@0.3.1675466867/camera_utils.js
   wget https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils@0.3.1620248257/drawing_utils.js
   
   # 下载依赖文件
   wget https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_solution_packed_assets.data
   wget https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_solution_packed_assets_loader.js
   wget https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands.binarypb
   wget https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_wasm_internal.js
   wget https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_wasm_internal.wasm
   wget https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_landmark_full.tflite
   ```

   使用curl（如果wget不可用）：
   ```bash
   curl -L -o hands.js https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands.js
   # ... 其他文件类似
   ```

## 验证安装

下载完成后，目录结构应该是：

```
static/
└── lib/
    └── mediapipe/
        ├── hands.js
        ├── camera_utils.js
        ├── drawing_utils.js
        ├── hands_solution_packed_assets.data
        ├── hands_solution_packed_assets_loader.js
        ├── hands.binarypb
        ├── hands_wasm_internal.js
        ├── hands_wasm_internal.wasm
        └── hands_landmark_full.tflite
```

然后：
1. 重启应用（如果正在运行）
2. 刷新浏览器页面
3. 打开浏览器控制台（F12），应该看到：
   ```
   尝试从本地加载 MediaPipe 库...
   ✅ 成功从本地加载 MediaPipe
   ```

## 故障排查

### 问题1：脚本下载失败

**原因**：无法访问CDN

**解决方案**：
- 检查网络连接
- 尝试使用VPN
- 使用手动下载方法

### 问题2：文件已下载但页面仍提示加载失败

**可能原因**：
1. 文件路径不正确
2. 文件不完整或损坏
3. 应用未重启

**解决方案**：
1. 检查文件是否在 `static/lib/mediapipe/` 目录
2. 检查文件大小（hands.js应该约1-2MB）
3. 重新下载文件
4. 重启Docker容器或应用服务器

### 问题3：Docker容器中找不到文件

**原因**：文件下载在容器外部，未挂载到容器内

**解决方案**：
- 在容器内运行下载脚本
- 或确保 `static/` 目录已挂载到容器（docker-compose.yml中已配置）

## 文件大小参考

- hands.js: ~1.5 MB
- camera_utils.js: ~50 KB
- drawing_utils.js: ~30 KB
- 依赖文件总计: ~5-10 MB

总大小约 7-12 MB

## 常见问题

### Q: "本地"是指浏览器本地还是服务器本地？

**A: 服务器本地**

- **文件存储位置**：`服务器磁盘/static/lib/mediapipe/` 目录
- **加载方式**：浏览器通过HTTP请求从您的服务器加载，URL类似：`http://您的域名/static/lib/mediapipe/hands.js`
- **对比说明**：
  - **CDN方式**：浏览器从外部CDN（jsdelivr/unpkg）加载 → `https://cdn.jsdelivr.net/...`
  - **本地方式**：浏览器从您的服务器加载 → `http://您的服务器/static/lib/mediapipe/...`

### Q: 为什么不是存储在浏览器本地？

浏览器本地存储（如IndexedDB/LocalStorage）有限制：
- 存储容量有限（通常几MB到几十MB）
- MediaPipe库文件较大（约7-12MB）
- 需要用户手动下载到浏览器不现实

存储在服务器本地的优势：
- ✅ 所有用户共享，只需下载一次
- ✅ 通过服务器HTTP服务，加载速度快
- ✅ 不依赖外部CDN，稳定可靠

## 注意事项

1. **Git忽略**：这些文件已添加到 `.gitignore`，不会被提交到Git仓库
2. **备份**：建议备份下载的库文件，避免重复下载
3. **更新**：如果MediaPipe版本更新，需要重新下载相应版本的文件
4. **存储位置**：文件存储在**服务器**上，不是在用户浏览器中

## 技术支持

如果遇到问题：
1. 检查浏览器控制台的错误信息
2. 查看服务器日志
3. 确认文件路径和权限正确

