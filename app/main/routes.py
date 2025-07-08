from flask import render_template, jsonify
from app.main import bp
from app import mongo

@bp.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/health')
def api_health():
    return jsonify({"status": "ok"}) 