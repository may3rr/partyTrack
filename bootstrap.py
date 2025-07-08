#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

def install_dependencies():
    try:
        subprocess.check_call([
            sys.executable, 
            '-m', 
            'pip', 
            'install', 
            '-r', 
            'requirements-fc.txt',
            '--target',
            '/code/site-packages'
        ])
        sys.path.insert(0, '/code/site-packages')
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def main():
    # 安装依赖
    install_dependencies()
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'production'
    
    # 启动应用
    from wsgi import app
    app.run(host='0.0.0.0', port=9000)

if __name__ == '__main__':
    main() 