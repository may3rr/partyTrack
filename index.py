#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys

def handler(event, context):
    # 安装依赖
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-fc.txt'])
    
    # 启动Flask应用
    from wsgi import app
    return app 