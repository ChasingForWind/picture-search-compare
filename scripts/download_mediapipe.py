#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MediaPipe库下载脚本
自动下载MediaPipe Hands、Camera Utils和Drawing Utils库到本地
"""

import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# 版本信息
VERSIONS = {
    'hands': '0.4.1675469404',
    'camera_utils': '0.3.1675466867',
    'drawing_utils': '0.3.1620248257'
}

# CDN地址（多个备选）
CDN_SOURCES = [
    {
        'name': 'jsdelivr',
        'base_url': 'https://cdn.jsdelivr.net/npm/@mediapipe'
    },
    {
        'name': 'unpkg',
        'base_url': 'https://unpkg.com/@mediapipe'
    }
]

def get_project_root():
    """获取项目根目录"""
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    # 返回项目根目录（scripts的父目录）
    return script_dir.parent

def get_target_dir():
    """获取目标目录"""
    root = get_project_root()
    return root / 'static' / 'lib' / 'mediapipe'

def download_file(url, target_path):
    """下载文件"""
    try:
        print(f'正在下载: {url}')
        print(f'保存到: {target_path}')
        
        # 创建目录
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 下载文件
        urllib.request.urlretrieve(url, target_path)
        
        # 检查文件大小
        file_size = target_path.stat().st_size
        if file_size > 0:
            print(f'✅ 下载成功 ({file_size / 1024 / 1024:.2f} MB)')
            return True
        else:
            print(f'❌ 文件大小为0，下载可能失败')
            return False
            
    except urllib.error.URLError as e:
        print(f'❌ 下载失败: {e.reason}')
        return False
    except Exception as e:
        print(f'❌ 发生错误: {str(e)}')
        return False

def download_mediapipe_libraries():
    """下载MediaPipe库"""
    target_dir = get_target_dir()
    
    print('=' * 60)
    print('MediaPipe库下载工具')
    print('=' * 60)
    print(f'目标目录: {target_dir}')
    print()
    
    # 需要下载的文件
    files_to_download = [
        {
            'package': 'hands',
            'file': 'hands.js',
            'version': VERSIONS['hands']
        },
        {
            'package': 'camera_utils',
            'file': 'camera_utils.js',
            'version': VERSIONS['camera_utils']
        },
        {
            'package': 'drawing_utils',
            'file': 'drawing_utils.js',
            'version': VERSIONS['drawing_utils']
        }
    ]
    
    # 尝试从不同的CDN下载
    success_count = 0
    failed_files = []
    
    for file_info in files_to_download:
        package = file_info['package']
        filename = file_info['file']
        version = file_info['version']
        
        print(f'\n📦 下载 {package} ({filename})...')
        
        target_path = target_dir / filename
        downloaded = False
        
        # 尝试每个CDN
        for cdn in CDN_SOURCES:
            url = f"{cdn['base_url']}/{package}@{version}/{filename}"
            print(f'  尝试从 {cdn["name"]} CDN 下载...')
            
            if download_file(url, target_path):
                downloaded = True
                success_count += 1
                break
        
        if not downloaded:
            print(f'❌ {filename} 下载失败（所有CDN都无法访问）')
            failed_files.append(filename)
    
    # 下载MediaPipe Hands的依赖文件（模型文件等）
    print(f'\n📦 下载MediaPipe Hands依赖文件...')
    hands_files = [
        'hands_solution_packed_assets.data',
        'hands_solution_packed_assets_loader.js',
        'hands.binarypb',
        'hands_wasm_internal.js',
        'hands_wasm_internal.wasm',
        'hands_landmark_full.tflite'
    ]
    
    for dep_file in hands_files:
        target_path = target_dir / dep_file
        if target_path.exists():
            print(f'  ✓ {dep_file} 已存在，跳过')
            continue
        
        downloaded = False
        for cdn in CDN_SOURCES:
            url = f"{cdn['base_url']}/hands@{VERSIONS['hands']}/{dep_file}"
            print(f'  下载 {dep_file}...')
            if download_file(url, target_path):
                downloaded = True
                break
        
        if not downloaded:
            print(f'  ⚠️ {dep_file} 下载失败，但不影响基本功能')
    
    # 总结
    print('\n' + '=' * 60)
    print('下载完成！')
    print('=' * 60)
    
    if success_count == len(files_to_download):
        print('✅ 所有核心文件下载成功！')
        print(f'\n文件保存在: {target_dir}')
        print('\n您现在可以刷新浏览器页面，MediaPipe库将从本地加载。')
    else:
        print(f'⚠️ {success_count}/{len(files_to_download)} 个核心文件下载成功')
        if failed_files:
            print(f'失败的文件: {", ".join(failed_files)}')
            print('\n建议：')
            print('1. 检查网络连接')
            print('2. 尝试使用VPN或更换网络环境')
            print('3. 手动下载文件（参见 MEDIAPIPE_DOWNLOAD.md）')
    
    return success_count == len(files_to_download)

if __name__ == '__main__':
    try:
        success = download_mediapipe_libraries()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print('\n\n用户中断下载')
        sys.exit(1)
    except Exception as e:
        print(f'\n\n发生未预期的错误: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

