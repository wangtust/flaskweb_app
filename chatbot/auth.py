# auth.py
# 在auth.py顶部添加以下导入
import re
import time
import random
import string
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
# auth.py 顶部新增
import datetime  # 用于处理时间戳

# 从 models.py 导入数据库和模型
from models import db, User, ChatHistory

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)



# 新增：发送邮箱验证码的路由（前端AJAX调用）
@auth_bp.route('/send-verify-code', methods=['POST'])
def send_verify_code():
    # 接收前端发送的邮箱
    data = request.get_json()
    email = data.get('email', '').strip()

    # 1. 验证邮箱格式（后端二次校验，防止绕过前端）
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'success': False, 'msg': '邮箱格式不正确'})

    # 2. 检查邮箱是否已被注册（提前提示，避免用户浪费时间）
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'msg': '该邮箱已被注册'})

    # 3. 生成6位数字验证码（易输入）
    verify_code = ''.join(random.choices(string.digits, k=6))  # 如：123456

    # 4. 存储验证码到session（关联邮箱，设置5分钟过期）
    session_key = f'verify_code_{email}'  # 用邮箱作为session key的一部分，避免冲突
    session[session_key] = {
        'code': verify_code,
        'expire_time': time.time() + 300  # 300秒=5分钟后过期
    }
    # 发送邮件时才导入（延迟导入，避免循环）
    from app import mail
    from flask_mail import Message  # 补充导入Message
    # 5. 发送验证码邮件
    try:
        # 构建邮件内容
        msg = Message(
            subject='【Chatbot】注册邮箱验证码',  # 邮件标题
            recipients=[email],  # 收件人邮箱
            body=f'你的注册验证码是：{verify_code}\n5分钟内有效，请尽快完成验证。\n请勿向他人泄露验证码。'
        )
        mail.send(msg)  # 发送邮件（需确保app.py中mail配置正确）
        return jsonify({'success': True, 'msg': '验证码已发送至邮箱'})
    except Exception as e:
        print(f"邮件发送失败：{str(e)}")  # 调试用
        return jsonify({'success': False, 'msg': '发送失败，请检查邮箱是否有效'})

# 修改原注册路由：添加邮箱、验证码校验
@auth_bp.route('/register', methods=['GET', 'POST'], endpoint='register')
def register():
    if request.method == 'POST':
        # 1. 获取前端提交的所有字段
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        verify_code = request.form.get('verify_code', '').strip()

        # 2. 基础字段非空校验
        if not all([username, email, password, confirm_password, verify_code]):
            flash('所有字段均为必填项', 'error')
            return redirect(url_for('auth.register'))

        # 3. 用户名格式校验（纯英文，3-16位）
        if not re.match(r'^[A-Za-z]{3,16}$', username):
            flash('用户名必须为3-16位纯英文（仅大小写字母）', 'error')
            return redirect(url_for('auth.register'))

        # 4. 邮箱格式校验
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('邮箱格式不正确', 'error')
            return redirect(url_for('auth.register'))

        # 5. 密码格式校验（包含大小写、数字，8-20位）
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,20}$', password):
            flash('密码需包含大小写字母、数字，且长度为8-20位', 'error')
            return redirect(url_for('auth.register'))

        # 6. 确认密码校验
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return redirect(url_for('auth.register'))

        # 7. 验证码校验（核心）
        session_key = f'verify_code_{email}'
        stored_code_info = session.get(session_key)  # 从session获取存储的验证码

        if not stored_code_info:
            flash('请先获取验证码', 'error')
            return redirect(url_for('auth.register'))

        if time.time() > stored_code_info['expire_time']:
            flash('验证码已过期，请重新获取', 'error')
            return redirect(url_for('auth.register'))

        if verify_code != stored_code_info['code']:
            flash('验证码不正确', 'error')
            return redirect(url_for('auth.register'))

        # 8. 检查用户名/邮箱是否已注册
        if User.query.filter_by(username=username).first():
            flash('用户名已被注册', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return redirect(url_for('auth.register'))

        # 9. 所有校验通过：创建用户
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)  # 加密存储密码
        )
        db.session.add(new_user)
        db.session.commit()

        # 10. 清理session中的验证码（避免重复使用）
        session.pop(session_key, None)

        # 11. 提示注册成功，跳转登录
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))

    # GET请求：返回注册页面
    return render_template('register.html')


# 登录路由
@auth_bp.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            # 使用flash存储错误消息
            flash('用户名或密码错误', 'error')
            # 重定向回登录页面
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')

# 登出路由
@auth_bp.route('/logout', endpoint='logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))

# 检查用户是否登录的装饰器
def login_required(f):
    @wraps(f)  # 添加这一行，保留被装饰函数的名称
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function