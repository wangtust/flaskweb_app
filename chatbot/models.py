# models.py
from flask_sqlalchemy import SQLAlchemy
import datetime

# 初始化数据库（全局唯一，供其他文件导入）
db = SQLAlchemy()

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # 用户名（唯一）
    email = db.Column(db.String(120), unique=True, nullable=False)    # 邮箱（唯一）
    password_hash = db.Column(db.String(256), nullable=False)         # 密码哈希

# 聊天记录模型
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))  # 关联用户
    sender = db.Column(db.String(20))  # 发送者："user" 或 "bot"
    message = db.Column(db.Text)       # 消息内容
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # 时间戳

    # 关联用户，方便查询
    user = db.relationship('User', backref=db.backref('chat_history', lazy=True, cascade='all, delete-orphan'))