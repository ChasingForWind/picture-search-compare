import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from typing import Tuple, Optional

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file, upload_folder: str) -> Optional[Tuple[str, str]]:
    """
    保存上传的图片文件
    
    Returns:
        Tuple[原始文件名, 保存的文件路径] 或 None
    """
    if file and file.filename and allowed_file(file.filename):
        # 生成唯一的文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(upload_folder, filename)
        
        try:
            # 验证并保存图片
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
            
            # 保存为JPEG格式（统一格式）
            if ext.lower() != 'jpg' and ext.lower() != 'jpeg':
                filename = f"{uuid.uuid4()}.jpg"
                filepath = os.path.join(upload_folder, filename)
            
            img.save(filepath, 'JPEG', quality=85)
            
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

