from flask import Flask
import os

def create_app():
    # 获取应用根目录
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    app = Flask(__name__, 
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
    
    # 使用绝对路径
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads', 'images')
    app.config['PAIRS_FILE'] = os.path.join(basedir, 'static', 'uploads', 'pairs.json')
    
    # 确保上传目录存在
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        pairs_file_dir = os.path.dirname(app.config['PAIRS_FILE'])
        if pairs_file_dir:
            os.makedirs(pairs_file_dir, exist_ok=True)
    except Exception as e:
        print(f"Warning: Failed to create directories: {e}")
    
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app

