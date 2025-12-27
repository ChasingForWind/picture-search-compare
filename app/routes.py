from flask import Blueprint, render_template, redirect, url_for

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """上传页面"""
    return render_template('index.html')

@bp.route('/display')
def display():
    """展示页面"""
    return render_template('display.html')


