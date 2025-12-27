# MediaPipe库手动下载指南

## 快速下载链接（可直接在浏览器打开）

### 核心文件（必需）

#### 1. hands.js (~1.5 MB)
**方法1：直接下载（推荐）- 使用最新版本**
- 链接1（jsdelivr，最新版本）：https://cdn.jsdelivr.net/npm/@mediapipe/hands@latest/hands.js
- 链接2（jsdelivr，0.4版本）：https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4/hands.js
- 链接3（unpkg，最新版本）：https://unpkg.com/@mediapipe/hands@latest/hands.js
- 链接4（指定版本，可能不存在）：https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands.js
- **操作**：右键链接 → "另存为" → 保存到 `static/lib/mediapipe/hands.js`

**方法2：GitHub Releases**
- MediaPipe 官方仓库：https://github.com/google/mediapipe
- 但 JavaScript 版本主要通过 npm 分发，GitHub 主要包含源代码

**方法3：npm 包页面**
- npm 包：https://www.npmjs.com/package/@mediapipe/hands
- 版本 0.4.1675469404：https://www.npmjs.com/package/@mediapipe/hands/v/0.4.1675469404
- 在页面右侧可以找到 "Downloads" 链接

#### 2. camera_utils.js (~50 KB)
**方法1：直接下载（推荐）- 使用最新版本**
- 链接1（jsdelivr，最新版本）：https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@latest/camera_utils.js
- 链接2（jsdelivr，0.3版本）：https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@0.3/camera_utils.js
- 链接3（unpkg，最新版本）：https://unpkg.com/@mediapipe/camera_utils@latest/camera_utils.js
- **操作**：右键链接 → "另存为" → 保存到 `static/lib/mediapipe/camera_utils.js`

**方法2：npm 包页面**
- npm 包：https://www.npmjs.com/package/@mediapipe/camera_utils
- 版本 0.3.1675466867：https://www.npmjs.com/package/@mediapipe/camera_utils/v/0.3.1675466867

#### 3. drawing_utils.js (~30 KB)
**方法1：直接下载（使用最新版本）**
- 链接1（jsdelivr，最新版本）：https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils@latest/drawing_utils.js
- 链接2（jsdelivr，0.3版本）：https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils@0.3/drawing_utils.js
- 链接3（unpkg，最新版本）：https://unpkg.com/@mediapipe/drawing_utils@latest/drawing_utils.js

### 依赖文件（推荐下载，提升性能）

#### 4. hands_solution_packed_assets.data
- https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_solution_packed_assets.data

#### 5. hands_solution_packed_assets_loader.js
- https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_solution_packed_assets_loader.js

#### 6. hands.binarypb
- https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands.binarypb

#### 7. hands_wasm_internal.js
- https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_wasm_internal.js

#### 8. hands_wasm_internal.wasm
- https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_wasm_internal.wasm

#### 9. hands_landmark_full.tflite
- https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/hands_landmark_full.tflite

## 手动下载步骤

### Windows 浏览器下载

1. **创建目录**
   ```
   在项目根目录创建：static\lib\mediapipe\
   ```

2. **下载文件**
   - 点击上面的链接，如果浏览器直接打开（显示代码），按 `Ctrl+S` 保存
   - 或者右键链接 → "链接另存为" → 选择保存位置为 `static\lib\mediapipe\`
   - 确保文件名完全正确（包括扩展名）

3. **验证文件**
   - `hands.js` 应该约 1.5 MB
   - `camera_utils.js` 应该约 50 KB
   - `drawing_utils.js` 应该约 30 KB

## 如果 CDN 链接无法访问

### 备选方案1：使用 VPN
- 开启 VPN 后，重新尝试上面的链接

### 备选方案2：从其他镜像下载
- 尝试 unpkg 链接（如果 jsdelivr 不行）
- 尝试使用代理工具下载

### 备选方案3：通过 npm 下载（如果已安装 Node.js）

```bash
# 安装 npm 包到临时目录
mkdir temp_mediapipe
cd temp_mediapipe

# 安装指定版本
npm install @mediapipe/hands@0.4.1675469404
npm install @mediapipe/camera_utils@0.3.1675466867
npm install @mediapipe/drawing_utils@0.3.1620248257

# 复制文件到项目目录
# Windows
xcopy /Y node_modules\@mediapipe\hands\hands.js ..\..\static\lib\mediapipe\
xcopy /Y node_modules\@mediapipe\camera_utils\camera_utils.js ..\..\static\lib\mediapipe\
xcopy /Y node_modules\@mediapipe\drawing_utils\drawing_utils.js ..\..\static\lib\mediapipe\

# Linux/Mac
cp node_modules/@mediapipe/hands/hands.js ../../static/lib/mediapipe/
cp node_modules/@mediapipe/camera_utils/camera_utils.js ../../static/lib/mediapipe/
cp node_modules/@mediapipe/drawing_utils/drawing_utils.js ../../static/lib/mediapipe/
```

### 备选方案4：GitHub Packages（如果可用）

MediaPipe 的 JavaScript 版本主要通过 npm 分发，但您可以尝试：
- https://github.com/google/mediapipe/releases
- 查找包含 JavaScript 构建的版本

## 文件结构检查

下载完成后，确保文件结构如下：

```
picture-search/
└── static/
    └── lib/
        └── mediapipe/
            ├── hands.js                    (必需，~1.5 MB)
            ├── camera_utils.js             (必需，~50 KB)
            ├── drawing_utils.js            (必需，~30 KB)
            ├── hands_solution_packed_assets.data          (推荐)
            ├── hands_solution_packed_assets_loader.js     (推荐)
            ├── hands.binarypb                            (推荐)
            ├── hands_wasm_internal.js                    (推荐)
            ├── hands_wasm_internal.wasm                  (推荐)
            └── hands_landmark_full.tflite                (推荐)
```

## 验证下载

下载完成后，在项目根目录运行：

```bash
# Windows PowerShell
dir static\lib\mediapipe\

# 或使用 Git
git status
```

应该能看到下载的文件。

## 提交到 Git

```bash
git add static/lib/mediapipe/
git commit -m "Add MediaPipe libraries"
git push
```

