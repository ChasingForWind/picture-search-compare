from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'images')
    app.config['PAIRS_FILE'] = os.path.join('static', 'uploads', 'pairs.json')
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    pairs_file_dir = os.path.dirname(app.config['PAIRS_FILE'])
    if pairs_file_dir:
        os.makedirs(pairs_file_dir, exist_ok=True)
    
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app

