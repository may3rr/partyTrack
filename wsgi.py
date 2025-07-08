import sys
import logging
from app import create_app

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    app = create_app()
    application = app  # Vercel需要这个变量名
except Exception as e:
    logger.error(f"Failed to create app: {str(e)}")
    logger.error(f"Exception type: {type(e)}")
    logger.error(f"Stack trace: {sys.exc_info()}")
    raise

@app.errorhandler(500)
def handle_500_error(error):
    logger.error(f"Internal Server Error: {error}")
    return {"error": "Internal Server Error", "message": str(error)}, 500

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled Exception: {error}")
    return {"error": "Internal Server Error", "message": str(error)}, 500

if __name__ == '__main__':
    app.run() 