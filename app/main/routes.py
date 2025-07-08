from flask import render_template, jsonify, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.main import bp
from app import mongo
from app.models import User

@bp.route('/')
def index():
    try:
        return render_template('index.html', current_user=current_user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = mongo.db.users.find_one({'username': username})
        
        if user_data and user_data.get('password') == password:  # 实际应用中应该使用密码哈希
            user = User(user_data)
            login_user(user)
            return redirect(url_for('main.index'))
        flash('用户名或密码错误')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/api/health')
def api_health():
    return jsonify({"status": "ok"}) 