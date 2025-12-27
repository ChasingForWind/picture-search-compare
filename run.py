#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app

app = create_app()

if __name__ == '__main__':
    # 开发模式使用Flask开发服务器
    app.run(host='0.0.0.0', port=5000, debug=False)

