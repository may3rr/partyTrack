#!/bin/bash

# 创建临时目录
rm -rf code
mkdir -p code

# 复制应用代码
cp -r app code/
cp wsgi.py code/
cp config.py code/
cp requirements-fc.txt code/

# 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-fc.txt -t code/

# 部署到阿里云
s deploy

# 清理
deactivate
rm -rf venv 