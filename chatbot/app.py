from flask import Flask, request, jsonify, render_template, session
from flask_mail import Mail  # 1. 先导入 Mail 类
import config
from chatbot import get_ark_response
# 修改app.py中的导入部分（去重）
from auth import (
    auth_bp, 
    db, 
    login_required, 
    User,  # 仅导入一次User
    ChatHistory  # 仅导入一次ChatHistory
)
import datetime  # 导入时间处理模块
# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(config)  # 加载配置
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # 添加数据库配置
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 新增：初始化邮件服务
mail = Mail(app)  # 初始化mail对象，供auth.py使用

# 初始化数据库
db.init_app(app)

# 注册认证蓝图
app.register_blueprint(auth_bp)

# 创建数据库表（确保包含User.email字段）
with app.app_context():
    # db.drop_all()  # 开发环境：删除旧表（生产环境注释此行）
    db.create_all()  # 创建新表

print("数据库连接地址：", app.config['SQLALCHEMY_DATABASE_URI'])  # 启动时会输出MySQL连接信息
# 首页路由（返回聊天页面）
@app.route('/', endpoint='index')  # 明确指定端点名称
@login_required
def index():
    current_user = User.query.filter_by(username=session['username']).first()
    if not current_user:
        return redirect(url_for('auth.login'))
    
    # 查询该用户的所有聊天记录（按时间排序）
    chat_history = ChatHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(ChatHistory.timestamp).all()
    
    # 将记录转换为前端可处理的列表（例如：[{"sender": "user", "message": "...", ...}, ...]）
    history_list = [
        {
            "sender": item.sender,
            "message": item.message,
            "time": item.timestamp.strftime("%Y-%m-%d %H:%M")  # 格式化时间
        } for item in chat_history
    ]
    
    return render_template(
        'index.html', 
        username=session.get('username'),
        chat_history=history_list  # 传递历史记录到前端
    )

# 配置信息接口
@app.route('/config')
def get_config():
    return jsonify({
        "model": config.MODEL,
        "api_configured": config.API_CONFIGURED
    })

# 聊天接口
@app.route('/chat', methods=['POST'], endpoint='chat')  
@login_required
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "缺少消息内容", "response": ""})
    
    # 获取当前登录用户
    current_user = User.query.filter_by(username=session['username']).first()
    if not current_user:
        return jsonify({"error": "用户不存在", "response": ""})
    
    # 获取用户输入和历史对话
    user_message = data["message"].strip()
    history = data.get("history", [])
    
    # 调用ARK API获取回复
    response, error = get_ark_response(user_message, history)
    bot_response = response or "抱歉，无法生成回复"
    
    # ---------------- 保存聊天记录到数据库 ----------------
    # 1. 保存用户发送的消息
    user_chat = ChatHistory(
        user_id=current_user.id,
        sender="user",
        message=user_message,
        timestamp=datetime.datetime.utcnow()
    )
    db.session.add(user_chat)
    
    # 2. 保存机器人回复的消息
    bot_chat = ChatHistory(
        user_id=current_user.id,
        sender="bot",
        message=bot_response,
        timestamp=datetime.datetime.utcnow()
    )
    db.session.add(bot_chat)
    
    # 提交数据库事务
    db.session.commit()
    # ------------------------------------------------------
    
    return jsonify({
        "response": bot_response,
        "error": error
    })

# 清空聊天记录接口
@app.route('/clear-chat', methods=['POST'])
@login_required
def clear_chat():
    try:
        # 获取当前登录用户
        current_user = User.query.filter_by(username=session['username']).first()
        if not current_user:
            return jsonify({"success": False, "error": "用户不存在"}), 400
        
        # 删除该用户的所有聊天记录
        ChatHistory.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        return jsonify({"success": True, "message": "聊天记录已清空"})
    
    except Exception as e:
        # 发生错误时回滚事务
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5070, debug=config.DEBUG)