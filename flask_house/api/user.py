import json
import time
from flask import Blueprint, request, Response, jsonify, session
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import current_app, url_for

from models import User, House  # add House import
from config import db
from flask import session

user_api = Blueprint('user_api', __name__)

@user_api.route('/register', methods=['POST'])
def register():
    #获取用户名、密码、邮箱及验证码
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    code = request.form.get('email_code')
    # 校验邮箱验证码
    now = int(time.time())
    # 验证码错误或不存在
    if not code or code != session.get('reg_code'):
        return jsonify({'valid': 0, 'msg': '邮箱验证码错误'})
    # 验证码过期: 5分钟内有效
    if 'reg_code_time' not in session or now - session.get('reg_code_time') > 300:
        return jsonify({'valid': 0, 'msg': '验证码已过期'})

    #检查数据库当中是否存在该用户
    result = User.query.filter(User.name == username).all()

    #如果查询出来的数据长度为0的话，则该用户名没有被注册过
    if len(result) == 0:
        user = User(name=username, password=password, email=email)
        #将用户对象添加到数据库当中
        db.session.add(user)
        db.session.commit()
        # 清理 session 验证码
        session.pop('reg_code', None)
        session.pop('reg_code_time', None)
        # 注册成功，无需发送邮箱确认链接，仅保留发送的验证码

        # 注册成功，提示登录页面
        return jsonify({'valid':1, 'msg': user.name})
    else:
        return jsonify({'valid':0, 'msg': '该用户已被注册'})
    
# 发送注册邮箱验证码
@user_api.route('/send_reg_code', methods=['POST'])
def send_reg_code():
    email = request.form.get('email')
    if not email:
        return jsonify({'valid': 0, 'msg': '邮箱不能为空'})
    now = int(time.time())
    last_time = session.get('reg_code_time')
    # Prevent resend within 5 minutes
    if last_time and now - last_time < 300:
        remain = 300 - (now - last_time)
        return jsonify({'valid': 0, 'msg': f'请{remain}秒后再发送'})
    import random
    code = f"{random.randint(0, 999999):06d}"
    # 保存到 session
    session['reg_code'] = code
    session['reg_code_time'] = now
    # 使用配置中的默认发件人
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    msg = Message('注册验证码', sender=sender, recipients=[email])
    msg.body = f'您的注册验证码是：{code}，5分钟内有效。'
    current_app.extensions['mail'].send(msg)
    return jsonify({'valid': 1, 'msg': '验证码已发送'})
    
    

#用户登录
@user_api.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    #查询用户是否存在
    user = User.query.filter(User.name == username).first()
    #如果用户存在
    if user:
        # 判断密码是否相等
        if password and user.password == password:
            result = {'valid':1, 'msg': user.name}
            result_json = json.dumps(result)
            res = Response(result_json)
            res.set_cookie('name', user.name, 3600 * 2)
            return res
        else:
            return jsonify({'valid':0, 'msg': '密码错误'})
    else:
        return jsonify({'valid': 0, 'msg': '用户不存在'})
    
#退出登录
@user_api.route('/logout')
def logout():
    #先从cookie中获取用户信息
    name = request.cookies.get('name')
    if name:
        result = {'valid': 1, 'msg': '退出登录成功'}
        json_str = json.dumps(result)
        res = Response(json_str)
        res.delete_cookie('name')
        return res
    else:
        return jsonify({'valid':0, 'msg':'未登录'})

# 修改用户信息
@user_api.route('/modify/userinfo/<option>', methods=['POST'])
def modify_userinfo(option):
    # 获取当前登录用户
    name = request.cookies.get('name')
    if not name:
        return jsonify({'ok': '0', 'msg': '未登录'})
    user = User.query.filter(User.name == name).first()
    if not user:
        return jsonify({'ok': '0', 'msg': '用户不存在'})
    # 修改昵称
    if option == 'name':
        new_name = request.form.get('name')
        user.name = new_name
        db.session.commit()
        res = jsonify({'ok': '1', 'msg': new_name})
        res.set_cookie('name', new_name, 3600 * 2)
        return res
    # 修改地址
    if option == 'addr':
        new_addr = request.form.get('addr')
        user.addr = new_addr
        db.session.commit()
        return jsonify({'ok': '1', 'msg': '地址更新成功'})
    # 修改密码（前端使用pd作为option）
    if option in ('password', 'pd'):
        new_pwd = request.form.get('password') or request.form.get('pd')
        user.password = new_pwd
        db.session.commit()
        return jsonify({'ok': '1', 'msg': '密码更新成功'})
    # 修改邮箱
    if option == 'email':
        new_email = request.form.get('email')
        user.email = new_email
        db.session.commit()
        return jsonify({'ok': '1', 'msg': '邮箱更新成功'})
    # 无效操作
    return jsonify({'ok': '0', 'msg': '无效操作'})

# 收藏房源
@user_api.route('/add/collection/<int:hid>')
def add_collection(hid):
    name = request.cookies.get('name')
    if not name:
        return jsonify({'valid': 0, 'msg': '请先登录'})
    user = User.query.filter(User.name == name).first()
    if not user:
        return jsonify({'valid': 0, 'msg': '用户不存在'})
    collect_str = user.collect_id or ''
    ids = [int(i) for i in collect_str.split(',') if i]
    if hid in ids:
        return jsonify({'valid': 1, 'msg': '已收藏'})
    ids.append(hid)
    user.collect_id = ','.join(str(i) for i in ids)
    db.session.commit()
    return jsonify({'valid': 1, 'msg': '收藏成功'})

# 取消收藏
@user_api.route('/collect_off', methods=['POST'])
def collect_off():
    name = request.cookies.get('name')
    if not name:
        return jsonify({'valid': 0, 'msg': '请先登录'})
    user = User.query.filter(User.name == name).first()
    if not user:
        return jsonify({'valid': 0, 'msg': '用户不存在'})
    hid = request.form.get('house_id')
    ids = [i for i in (user.collect_id or '').split(',') if i]
    if hid and hid in ids:
        ids.remove(hid)
        user.collect_id = ','.join(ids)
        db.session.commit()
        return jsonify({'valid': 1, 'msg': '取消收藏成功'})
    else:
        return jsonify({'valid': 0, 'msg': '收藏无此条目'})

# 删除浏览记录
@user_api.route('/del_record', methods=['POST'])
def delete_record():
    name = request.cookies.get('name')
    if not name:
        return jsonify({'valid': 0, 'msg': '请先登录'})
    user = User.query.filter(User.name == name).first()
    if not user:
        return jsonify({'valid': 0, 'msg': '用户不存在'})
    if user.seen_id:
        user.seen_id = ''
        db.session.commit()
        return jsonify({'valid': 1, 'msg': '删除浏览记录成功'})
    else:
        return jsonify({'valid': 0, 'msg': '暂无浏览记录'})

# 获取收藏列表
@user_api.route('/collections', methods=['GET'])
def get_collections():
    name = request.cookies.get('name')
    if not name:
        return jsonify({'valid': 0, 'msg': '请先登录'})
    user = User.query.filter(User.name == name).first()
    ids = [int(i) for i in (user.collect_id or '').split(',') if i]
    houses = []
    for hid in ids:
        house = House.query.get(hid)
        if house:
            houses.append({
                'id': house.id,
                'title': house.title,
                'address': house.address,
                'block': house.block,
                'price': house.price,
                'rooms': house.rooms
            })
    return jsonify({'valid': 1, 'collections': houses})

# 获取浏览记录
@user_api.route('/history', methods=['GET'])
def get_history():
    name = request.cookies.get('name')
    if not name:
        return jsonify({'valid': 0, 'msg': '请先登录'})
    user = User.query.filter(User.name == name).first()
    ids = [int(i) for i in (user.seen_id or '').split(',') if i]
    houses = []
    for hid in ids:
        house = House.query.get(hid)
        if house:
            houses.append({
                'id': house.id,
                'title': house.title,
                'address': house.address,
                'block': house.block,
                'price': house.price,
                'rooms': house.rooms
            })
    return jsonify({'valid': 1, 'history': houses})

# 邮箱确认路由
@user_api.route('/confirm/<token>')
def confirm_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return jsonify({'valid': 0, 'msg': '验证链接已过期'})
    user = User.query.filter(User.email == email).first()
    if not user:
        return jsonify({'valid': 0, 'msg': '用户不存在'})
    if user.confirmed:
        return jsonify({'valid': 1, 'msg': '邮箱已验证'})
    user.confirmed = True
    db.session.commit()
    return jsonify({'valid': 1, 'msg': '邮箱验证成功'})