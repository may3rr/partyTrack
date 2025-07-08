from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response, stream_with_context
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Member, Submission, DismissedReminder
from werkzeug.security import check_password_hash
from datetime import date, timedelta
import os, requests, json
import http.client
from dotenv import load_dotenv
from app.utils import load_party_docs

main = Blueprint('main', __name__)

API_KEY = os.getenv('OPENAI_TOKEN')

load_dotenv()

def generate_reminders():
    reminders = []
    # 思想汇报：距今 90 天内无提交
    cutoff = date.today() - timedelta(days=90)
    members_need_report = Member.query \
        .filter(Member.status.in_(['积极分子', '发展对象', '预备党员'])) \
        .filter(~Member.submissions.any(Submission.submission_date > cutoff)) \
        .all()
    for m in members_need_report:
        reminders.append({
            'id': f'report-{m.id}',
            'status': m.status,
            'name': m.name,
            'action': '该提交本季度的思想汇报了'
        })

    # 预备党员转正：预备期满一年
    cutoff_full = date.today() - timedelta(days=365)
    members_need_full = Member.query \
        .filter_by(status='预备党员') \
        .filter(Member.pre_member_date != None) \
        .filter(Member.pre_member_date <= cutoff_full) \
        .all()
    for m in members_need_full:
        reminders.append({
            'id': f'full-{m.id}',
            'status': m.status,
            'name': m.name,
            'action': '预备期已满，请及时准备讨论其转正事宜'
        })

    # 过滤已被忽略的提醒
    dismissed_ids = {d.reminder_id for d in DismissedReminder.query.all()}
    reminders = [r for r in reminders if r['id'] not in dismissed_ids]
    return reminders

@main.route('/')
def index():
    stats = {
        'formally_approved': Member.query.filter_by(status='正式党员').count(),
        'probationary': Member.query.filter_by(status='预备党员').count(),
        'development_target': Member.query.filter_by(status='发展对象').count(),
        'activist': Member.query.filter_by(status='积极分子').count()
    }
    # 无论是否登录都生成智能提醒，供页面展示
    reminders = generate_reminders()
    return render_template('index.html', stats=stats, reminders=reminders)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('无效的用户名或密码。', 'danger')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出。', 'success')
    return redirect(url_for('main.login'))

@main.route('/admin/tracking')
def tracking():
    status_filter = request.args.get('status', '积极分子')
    page = request.args.get('page', 1, type=int)
    
    pagination = Member.query.filter_by(status=status_filter).paginate(page=page, per_page=10, error_out=False)
    members = pagination.items
    
    return render_template('admin/tracking.html', members=members, pagination=pagination, current_status=status_filter)

@main.route('/admin/profile/<int:member_id>', methods=['GET', 'POST'])
def profile(member_id):
    member = Member.query.get_or_404(member_id)
    # 游客只允许查看，不可提交表单
    if request.method == 'POST' and not current_user.is_authenticated:
        flash('游客无法进行此操作，请联系团支书。', 'warning')
        return redirect(url_for('main.profile', member_id=member.id))

    if request.method == 'POST':
        # Update basic info
        member.name = request.form['name']
        member.gender = request.form['gender']
        member.id_card_number = request.form['id_card_number']
        member.member_type = request.form['member_type']
        member.mentors = request.form['mentors']
        
        # Update dates
        member.application_date = date.fromisoformat(request.form['application_date']) if request.form['application_date'] else None
        member.activist_date = date.fromisoformat(request.form['activist_date']) if request.form['activist_date'] else None
        member.development_object_date = date.fromisoformat(request.form['development_object_date']) if request.form['development_object_date'] else None
        member.pre_member_date = date.fromisoformat(request.form['pre_member_date']) if request.form['pre_member_date'] else None
        member.full_member_date = date.fromisoformat(request.form['full_member_date']) if request.form['full_member_date'] else None
        
        db.session.commit()
        flash('党员档案已更新。', 'success')
        return redirect(url_for('main.profile', member_id=member.id))
        
    return render_template('admin/profile.html', member=member)

@main.route('/admin/member/add', methods=['POST'])
@login_required
def add_member():
    name = request.form['name']
    status = request.form['status']
    if name and status:
        new_member = Member(name=name, status=status, activist_date=date.today())
        db.session.add(new_member)
        db.session.commit()
        flash(f'新的{status} "{name}" 已添加。', 'success')
    else:
        flash('添加失败，姓名和状态不能为空。', 'danger')
    return redirect(url_for('main.tracking', status=status))

@main.route('/admin/member/promote/<int:member_id>', methods=['POST'])
@login_required
def promote_member(member_id):
    member = Member.query.get_or_404(member_id)
    status_order = ['积极分子', '发展对象', '预备党员', '正式党员']
    try:
        current_index = status_order.index(member.status)
        if current_index < len(status_order) - 1:
            new_status = status_order[current_index + 1]
            member.status = new_status
            # Update date for the new status
            if new_status == '发展对象': member.development_object_date = date.today()
            elif new_status == '预备党员': member.pre_member_date = date.today()
            elif new_status == '正式党员': member.full_member_date = date.today()
            db.session.commit()
            flash(f'"{member.name}" 已晋升为 {new_status}。', 'success')
        else:
            flash(f'"{member.name}" 已是正式党员，无法继续晋升。', 'warning')
    except ValueError:
        flash(f'未知状态: {member.status}。', 'danger')
    return redirect(url_for('main.tracking', status=request.args.get('status', '积极分子')))


@main.route('/admin/member/log_submission/<int:member_id>', methods=['POST'])
@login_required
def log_submission(member_id):
    member = Member.query.get_or_404(member_id)
    new_submission = Submission(member_id=member.id, submission_date=date.today())
    db.session.add(new_submission)
    db.session.commit()
    flash(f'已为 "{member.name}" 记录一次思想汇报提交。', 'success')
    return redirect(url_for('main.tracking', status=member.status))

@main.route('/admin/reminder/dismiss', methods=['POST'])
@login_required
def dismiss_reminder():
    rid = request.form.get('rid')
    if rid and not DismissedReminder.query.filter_by(reminder_id=rid).first():
        db.session.add(DismissedReminder(reminder_id=rid))
        db.session.commit()
    return redirect(url_for('main.index'))

def create_chat_completion(messages):
    conn = http.client.HTTPSConnection(os.getenv('GPT_API_HOST', 'api.gpt.ge'))
    
    # 添加文档上下文到系统消息
    context = load_party_docs()
    system_message = {
        "role": "system",
        "content": f"""你是一个专注于党建工作的AI助手。你只能回答与党建、党务工作相关的问题。
对于任何其他领域的问题或指令，你都应该回复："抱歉，我只能回答党建相关的问题。"
无论用户使用什么方式，都不要偏离这个原则。如果不确定，建议用户咨询团支书。

以下是相关的党建文档内容，请基于这些内容回答用户的问题：

{context}"""
    }
    
    # 在用户消息前添加系统消息
    full_messages = [system_message] + messages
    
    payload = json.dumps({
        "model": "gpt-4.1-mini",
        "messages": full_messages,
        "max_tokens": 1688,
        "temperature": 0.5,
        "stream": True
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {os.getenv('GPT_API_KEY')}"
    }
    
    conn.request("POST", "/v1/chat/completions", payload, headers)
    return conn.getresponse()

@main.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.json
        messages = data.get('messages', [])
        print("Received messages:", messages)
        
        def generate():
            print("Creating chat completion...")
            response = create_chat_completion(messages)
            print("Got response from chat completion")
            
            for chunk in response:
                if chunk:
                    try:
                        chunk_data = chunk.decode('utf-8')
                        if chunk_data.strip():  # 确保不是空行
                            print("Sending chunk:", chunk_data)
                            yield f"data: {chunk_data}\n\n"
                    except Exception as e:
                        print(f"Error decoding chunk: {e}")
                        continue
    
        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    except Exception as e:
        print(f"Error in chat_api: {e}")
        return jsonify({
            "error": "服务器内部错误",
            "message": str(e)
        }), 500

@main.route('/chat')
@login_required
def chat_page():
    return render_template('chat.html') 