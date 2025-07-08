import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # MongoDB 配置
    MONGODB_URI = os.environ.get('MONGODB_URI')
    
    # OpenAI 配置
    OPENAI_TOKEN = os.environ.get('OPENAI_TOKEN')
    GPT_API_KEY = os.environ.get('GPT_API_KEY')
    GPT_API_HOST = os.environ.get('GPT_API_HOST')
    
    # 保留 SQLAlchemy 配置用于兼容性
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 阿里云配置
    ALIYUN_REGION = os.environ.get('ALIYUN_REGION', 'cn-hangzhou')
    ALIYUN_ACCESS_KEY_ID = os.environ.get('ALIYUN_ACCESS_KEY_ID')
    ALIYUN_ACCESS_KEY_SECRET = os.environ.get('ALIYUN_ACCESS_KEY_SECRET') 
