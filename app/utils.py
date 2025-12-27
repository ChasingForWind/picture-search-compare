import os
import uuid
import io
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
    优先上传到 OSS，如果失败则保存到本地
    
    Returns:
        Tuple[原始文件名, 保存的文件路径或OSS URL] 或 None
    """
    if file and file.filename and allowed_file(file.filename):
        # 生成唯一的文件名
        filename = f"{uuid.uuid4()}.jpg"
        
        try:
            # 验证并处理图片
            # 重置文件流指针
            file.stream.seek(0)
            img = Image.open(file.stream)
            
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
            
            # 将图片保存到内存中的 BytesIO
            img_buffer = io.BytesIO()
            
            # 先以标准质量保存
            img.save(img_buffer, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
            
            # 检查文件大小，如果太大则进一步压缩
            file_size_mb = len(img_buffer.getvalue()) / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                quality = 75
                while file_size_mb > MAX_FILE_SIZE_MB and quality > 50:
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, 'JPEG', quality=quality, optimize=True, progressive=True)
                    file_size_mb = len(img_buffer.getvalue()) / (1024 * 1024)
                    quality -= 5
            
            # 尝试上传到 OSS
            try:
                from app.oss_client import oss_client
                img_buffer.seek(0)
                object_name = f"uploads/images/{filename}"
                oss_url = oss_client.upload_file_object(img_buffer, object_name)
                
                if oss_url:
                    print(f"Image uploaded to OSS: {oss_url}")
                    return file.filename, oss_url
            except Exception as oss_error:
                print(f"OSS upload failed, falling back to local storage: {oss_error}")
            
            # 如果 OSS 上传失败，保存到本地
            filepath = os.path.join(upload_folder, filename)
            os.makedirs(upload_folder, exist_ok=True)
            
            img_buffer.seek(0)
            with open(filepath, 'wb') as f:
                f.write(img_buffer.getvalue())
            
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

