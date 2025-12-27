from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from werkzeug.exceptions import RequestEntityTooLarge
import os
import uuid
from datetime import datetime
from app.models import PairManager
from app.utils import save_uploaded_image

bp = Blueprint('main', __name__)

def get_pair_manager():
    """获取PairManager实例"""
    return PairManager(current_app.config['PAIRS_FILE'])

@bp.route('/')
def index():
    """上传页面"""
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload():
    """处理图片上传"""
    try:
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({'error': '请选择两张图片'}), 400
        
        image1_file = request.files['image1']
        image2_file = request.files['image2']
        description = request.form.get('description', '').strip()
        
        if image1_file.filename == '' or image2_file.filename == '':
            return jsonify({'error': '请选择两张图片'}), 400
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # 保存两张图片
        result1 = save_uploaded_image(image1_file, upload_folder)
        result2 = save_uploaded_image(image2_file, upload_folder)
        
        if not result1 or not result2:
            return jsonify({'error': '图片格式不支持或保存失败。支持格式：PNG, JPG, JPEG, WEBP, GIF'}), 400
        
        _, image1_path = result1
        _, image2_path = result2
        
        # 创建图片对记录
        pair_id = str(uuid.uuid4())
        pair_data = {
            'pair_id': pair_id,
            'created_at': datetime.now().isoformat(),
            'image1': image1_path,
            'image2': image2_path,
            'description': description
        }
        
        # 保存到JSON文件
        pair_manager = get_pair_manager()
        pair_manager.save_pair(pair_data)
        
        return jsonify({
            'success': True,
            'pair_id': pair_id,
            'redirect_url': url_for('main.display', pair_id=pair_id)
        })
        
    except RequestEntityTooLarge:
        return jsonify({'error': '文件太大，单张图片最大10MB'}), 400
    except Exception as e:
        return jsonify({'error': f'上传失败：{str(e)}'}), 500

@bp.route('/display/<pair_id>')
def display(pair_id):
    """展示页面"""
    pair_manager = get_pair_manager()
    pair = pair_manager.get_pair(pair_id)
    
    if not pair:
        return redirect(url_for('main.index'))
    
    return render_template('display.html', pair=pair)

@bp.route('/api/history')
def api_history():
    """获取历史记录列表"""
    try:
        pair_manager = get_pair_manager()
        pairs = pair_manager.load_pairs()
        
        # 按创建时间倒序排列
        pairs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # 添加完整的图片URL
        for pair in pairs:
            pair['image1_url'] = url_for('static', filename=f"uploads/{pair['image1']}")
            pair['image2_url'] = url_for('static', filename=f"uploads/{pair['image2']}")
            pair['display_url'] = url_for('main.display', pair_id=pair['pair_id'])
        
        return jsonify({'pairs': pairs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/pair/<pair_id>')
def api_get_pair(pair_id):
    """获取指定图片对详情"""
    try:
        pair_manager = get_pair_manager()
        pair = pair_manager.get_pair(pair_id)
        
        if not pair:
            return jsonify({'error': '图片对不存在'}), 404
        
        # 添加完整的图片URL
        pair['image1_url'] = url_for('static', filename=f"uploads/{pair['image1']}")
        pair['image2_url'] = url_for('static', filename=f"uploads/{pair['image2']}")
        
        return jsonify(pair)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/pair/<pair_id>', methods=['DELETE'])
def api_delete_pair(pair_id):
    """删除指定图片对"""
    try:
        pair_manager = get_pair_manager()
        pair = pair_manager.get_pair(pair_id)
        
        if not pair:
            return jsonify({'error': '图片对不存在'}), 404
        
        # 删除图片文件
        upload_folder = current_app.config['UPLOAD_FOLDER']
        image1_path = os.path.join(upload_folder, os.path.basename(pair['image1']))
        image2_path = os.path.join(upload_folder, os.path.basename(pair['image2']))
        
        try:
            if os.path.exists(image1_path):
                os.remove(image1_path)
            if os.path.exists(image2_path):
                os.remove(image2_path)
        except Exception as e:
            print(f"Error deleting image files: {e}")
        
        # 从JSON中删除记录
        success = pair_manager.delete_pair(pair_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': '删除失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


