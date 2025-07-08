import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    
    # MongoDB配置
    MONGO_URI = os.environ.get('MONGODB_URI') or \
        'mongodb://localhost:27017/partyTrack'
    
    # Vercel 环境配置
    VERCEL_ENV = os.environ.get('VERCEL_ENV')
    IS_VERCEL = os.environ.get('VERCEL') == '1' 