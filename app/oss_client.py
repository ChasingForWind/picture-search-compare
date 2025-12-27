"""
OSS 客户端封装
支持阿里云 OSS 或其他兼容 S3 的对象存储服务
"""
import os
from typing import Optional

# 尝试导入 OSS SDK
try:
    import oss2
    OSS_AVAILABLE = True
except ImportError:
    OSS_AVAILABLE = False
    print("Warning: oss2 not installed, OSS features will be disabled")

class OSSClient:
    """OSS 客户端，如果未配置则禁用"""
    
    def __init__(self):
        # 从环境变量读取配置
        self.access_key_id = os.environ.get('OSS_ACCESS_KEY_ID')
        self.access_key_secret = os.environ.get('OSS_ACCESS_KEY_SECRET')
        self.endpoint = os.environ.get('OSS_ENDPOINT', 'https://oss-cn-hangzhou.aliyuncs.com')
        self.bucket_name = os.environ.get('OSS_BUCKET_NAME')
        
        # 检查是否启用 OSS
        self.use_oss = OSS_AVAILABLE and all([
            self.access_key_id,
            self.access_key_secret,
            self.bucket_name
        ])
        
        if self.use_oss:
            try:
                auth = oss2.Auth(self.access_key_id, self.access_key_secret)
                self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
                print(f"OSS initialized: bucket={self.bucket_name}, endpoint={self.endpoint}")
            except Exception as e:
                print(f"OSS initialization failed: {e}")
                self.use_oss = False
                self.bucket = None
        else:
            self.bucket = None
            if not OSS_AVAILABLE:
                print("OSS not available: oss2 package not installed")
            else:
                print("OSS not configured: missing environment variables")
    
    def upload_file(self, file_path: str, object_name: str) -> Optional[str]:
        """
        上传本地文件到 OSS
        
        Args:
            file_path: 本地文件路径
            object_name: OSS 对象名称（包含路径）
            
        Returns:
            OSS URL 或 None（如果上传失败或未启用）
        """
        if not self.use_oss:
            return None
        
        try:
            # 上传文件
            result = self.bucket.put_object_from_file(object_name, file_path)
            
            # 如果设置了 CDN 域名，使用 CDN 域名
            cdn_domain = os.environ.get('OSS_CDN_DOMAIN')
            if cdn_domain:
                # 移除协议前缀
                cdn_domain = cdn_domain.replace('https://', '').replace('http://', '')
                url = f"https://{cdn_domain}/{object_name}"
            else:
                # 使用 OSS 默认域名
                endpoint_domain = self.endpoint.replace('https://', '').replace('http://', '')
                url = f"https://{self.bucket_name}.{endpoint_domain}/{object_name}"
            
            return url
        except Exception as e:
            print(f"OSS upload error: {e}")
            return None
    
    def upload_file_object(self, file_obj, object_name: str) -> Optional[str]:
        """
        直接上传文件对象到 OSS（不需要先保存到本地）
        
        Args:
            file_obj: 文件对象（有 read 方法）
            object_name: OSS 对象名称
            
        Returns:
            OSS URL 或 None
        """
        if not self.use_oss:
            return None
        
        try:
            # 重置文件指针
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            
            # 上传文件对象
            result = self.bucket.put_object(object_name, file_obj)
            
            # 构建 URL
            cdn_domain = os.environ.get('OSS_CDN_DOMAIN')
            if cdn_domain:
                cdn_domain = cdn_domain.replace('https://', '').replace('http://', '')
                url = f"https://{cdn_domain}/{object_name}"
            else:
                endpoint_domain = self.endpoint.replace('https://', '').replace('http://', '')
                url = f"https://{self.bucket_name}.{endpoint_domain}/{object_name}"
            
            return url
        except Exception as e:
            print(f"OSS upload error: {e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        """
        删除 OSS 上的文件
        
        Args:
            object_name: OSS 对象名称
            
        Returns:
            是否删除成功
        """
        if not self.use_oss:
            return False
        
        try:
            self.bucket.delete_object(object_name)
            return True
        except Exception as e:
            print(f"OSS delete error: {e}")
            return False

# 全局实例
oss_client = OSSClient()

