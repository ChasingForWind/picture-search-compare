import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from typing import Tuple, Optional

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# 图片处理配置
MAX_IMAGE_SIZE = (1920, 1920)  # 最大尺寸（宽度，高度）
MAX_FILE_SIZE_MB = 10  # 最大文件大小（MB）
JPEG_QUALITY = 85  # JPEG压缩质量

def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(img: Image.Image, max_size: Tuple[int, int]) -> Image.Image:
    """
    智能调整图片大小，保持宽高比
    """
    if img.size[0] <= max_size[0] and img.size[1] <= max_size[1]:
        return img
    
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    return img

def save_uploaded_image(file, upload_folder: str) -> Optional[Tuple[str, str]]:
    """
    保存上传的图片文件，自动压缩和调整尺寸
    
    Returns:
        Tuple[原始文件名, 保存的文件路径] 或 None
    """
    if file and file.filename and allowed_file(file.filename):
        # 生成唯一的文件名
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(upload_folder, filename)
        
        try:
            # 验证并处理图片
            img = Image.open(file.stream)
            
            # 获取原始尺寸信息（用于日志）
            original_size = img.size
            original_format = img.format
            
            # 转换为RGB模式（处理RGBA等格式）
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整图片尺寸（如果太大）
            img = resize_image(img, MAX_IMAGE_SIZE)
            
            # 优化保存：使用渐进式JPEG和优化选项
            img.save(
                filepath, 
                'JPEG', 
                quality=JPEG_QUALITY,
                optimize=True,  # 优化文件大小
                progressive=True  # 渐进式JPEG
            )
            
            # 检查文件大小，如果还是太大，进一步压缩
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                # 进一步降低质量
                quality = 75
                while file_size_mb > MAX_FILE_SIZE_MB and quality > 50:
                    img.save(filepath, 'JPEG', quality=quality, optimize=True, progressive=True)
                    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    quality -= 5
            
            # 返回相对路径（用于存储）
            relative_path = os.path.join('images', filename).replace('\\', '/')
            return file.filename, relative_path
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    return None

def get_file_size_mb(filepath: str) -> float:
    """获取文件大小（MB）"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath) / (1024 * 1024)
    return 0

