// 手部识别和图片叠加逻辑

let hands = null;
let camera = null;
let canvas = null;
let ctx = null;
let video = null;
let backgroundImage = null;
let overlayImage = null;
let isImagesLoaded = false;
let lastHandPosition = null;

// 初始化函数
async function initHandTracking() {
    canvas = document.getElementById('displayCanvas');
    ctx = canvas.getContext('2d');
    video = document.getElementById('videoElement');
    
    const statusMessage = document.getElementById('statusMessage');
    
    // 显示状态消息
    function showStatus(message, type = 'info') {
        statusMessage.textContent = message;
        statusMessage.className = `status-message ${type}`;
        statusMessage.style.display = 'block';
    }
    
    try {
        // 从浏览器存储加载图片
        showStatus('正在加载图片...', 'info');
        await loadImagesFromStorage();
        
        // 初始化MediaPipe Hands
        showStatus('正在初始化手部识别...', 'info');
        hands = new Hands({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469404/${file}`;
            }
        });
        
        hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });
        
        hands.onResults(onHandResults);
        
        // 请求摄像头权限
        showStatus('正在请求摄像头权限...', 'info');
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'user',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        
        video.srcObject = stream;
        
        video.addEventListener('loadedmetadata', () => {
            // 设置canvas尺寸匹配视频
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // 启动摄像头处理
            camera = new Camera(video, {
                onFrame: async () => {
                    await hands.send({ image: video });
                },
                width: video.videoWidth,
                height: video.videoHeight
            });
            
            camera.start();
            
            // 隐藏状态消息
            statusMessage.style.display = 'none';
            
            // 开始绘制循环
            drawLoop();
        });
        
    } catch (error) {
        console.error('初始化失败:', error);
        showStatus('初始化失败: ' + error.message + '。请确保允许摄像头权限。', 'error');
    }
}

// 从浏览器存储加载图片
async function loadImagesFromStorage() {
    // 从URL参数获取图片对ID
    const urlParams = new URLSearchParams(window.location.search);
    const pairId = urlParams.get('id');
    
    if (!pairId) {
        throw new Error('缺少图片ID参数');
    }

    // 从 IndexedDB 加载图片对
    await imageStorage.init();
    const imagePair = await imageStorage.getImagePair(pairId);
    
    // 加载图片
    return new Promise((resolve, reject) => {
        let loadedCount = 0;
        
        backgroundImage = new Image();
        overlayImage = new Image();
        
        function onImageLoad() {
            loadedCount++;
            if (loadedCount === 2) {
                isImagesLoaded = true;
                resolve();
            }
        }
        
        backgroundImage.onload = onImageLoad;
        backgroundImage.onerror = () => reject(new Error('背景图片加载失败'));
        backgroundImage.src = imagePair.image1;
        
        overlayImage.onload = onImageLoad;
        overlayImage.onerror = () => reject(new Error('叠加图片加载失败'));
        overlayImage.src = imagePair.image2;
    });
}

// 手部检测结果处理
function onHandResults(results) {
    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        const handLandmarks = results.multiHandLandmarks[0];
        
        // 计算手掌中心点和半径
        const palmCenter = calculatePalmCenter(handLandmarks);
        const palmRadius = calculatePalmRadius(handLandmarks, palmCenter);
        
        lastHandPosition = {
            x: palmCenter.x * canvas.width,
            y: palmCenter.y * canvas.height,
            radius: palmRadius * canvas.width
        };
    } else {
        lastHandPosition = null;
    }
}

// 计算手掌中心点
function calculatePalmCenter(landmarks) {
    // 使用手腕和手指根部的关键点
    // 0: 手腕, 5: 食指根部, 9: 中指根部, 13: 无名指根部, 17: 小指根部
    const keyPoints = [landmarks[0], landmarks[5], landmarks[9], landmarks[13], landmarks[17]];
    
    let sumX = 0;
    let sumY = 0;
    
    keyPoints.forEach(point => {
        sumX += point.x;
        sumY += point.y;
    });
    
    return {
        x: sumX / keyPoints.length,
        y: sumY / keyPoints.length
    };
}

// 计算手掌半径
function calculatePalmRadius(landmarks, center) {
    const keyPoints = [landmarks[0], landmarks[5], landmarks[9], landmarks[13], landmarks[17]];
    
    let maxDistance = 0;
    
    keyPoints.forEach(point => {
        const dx = point.x - center.x;
        const dy = point.y - center.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        maxDistance = Math.max(maxDistance, distance);
    });
    
    // 添加缓冲区，使区域更大（转换为像素时需要乘以canvas宽度）
    // 这里返回的是归一化的值（0-1之间）
    return maxDistance * 2.5;
}

// 绘制循环
function drawLoop() {
    if (!isImagesLoaded || !backgroundImage || !overlayImage) {
        requestAnimationFrame(drawLoop);
        return;
    }
    
    // 绘制背景图片（第一张图片）
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 计算图片适应canvas的尺寸，保持宽高比
    const bgAspect = backgroundImage.width / backgroundImage.height;
    const canvasAspect = canvas.width / canvas.height;
    
    let bgWidth, bgHeight, bgX, bgY;
    
    if (bgAspect > canvasAspect) {
        // 背景图片更宽，以高度为准
        bgHeight = canvas.height;
        bgWidth = bgHeight * bgAspect;
        bgX = (canvas.width - bgWidth) / 2;
        bgY = 0;
    } else {
        // 背景图片更高，以宽度为准
        bgWidth = canvas.width;
        bgHeight = bgWidth / bgAspect;
        bgX = 0;
        bgY = (canvas.height - bgHeight) / 2;
    }
    
    ctx.drawImage(backgroundImage, bgX, bgY, bgWidth, bgHeight);
    
    // 如果检测到手，绘制第二张图片在手掌区域
    if (lastHandPosition) {
        const { x, y, radius } = lastHandPosition;
        
        // 保存canvas状态
        ctx.save();
        
        // 创建圆形裁剪区域，添加边缘羽化效果
        // 先创建裁剪路径
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.clip();
        
        // 绘制第二张图片，调整位置使其与背景对齐
        const overlayAspect = overlayImage.width / overlayImage.height;
        let overlayWidth, overlayHeight, overlayX, overlayY;
        
        if (overlayAspect > canvasAspect) {
            overlayHeight = canvas.height;
            overlayWidth = overlayHeight * overlayAspect;
            overlayX = (canvas.width - overlayWidth) / 2;
            overlayY = 0;
        } else {
            overlayWidth = canvas.width;
            overlayHeight = overlayWidth / overlayAspect;
            overlayX = 0;
            overlayY = (canvas.height - overlayHeight) / 2;
        }
        
        ctx.drawImage(overlayImage, overlayX, overlayY, overlayWidth, overlayHeight);
        
        // 创建渐变遮罩实现边缘羽化
        const gradient = ctx.createRadialGradient(x, y, radius * 0.7, x, y, radius);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(0.8, 'rgba(255, 255, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        // 应用渐变遮罩
        ctx.globalCompositeOperation = 'destination-in';
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        
        // 恢复canvas状态
        ctx.restore();
    }
    
    requestAnimationFrame(drawLoop);
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHandTracking);
} else {
    initHandTracking();
}

