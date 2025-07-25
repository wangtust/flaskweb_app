#项目配置文件
from flask_sqlalchemy import SQLAlchemy

import os

#创建flask-sqlalchemy的实例对象
db = SQLAlchemy()

class Config:
    #调试模式
    DEBUG = False
    #指定数据库的链接地址   
    #获取当前文件所在目录
    basedir = os.path.abspath(os.path.dirname(__file__))
    # 使用本地 MySQL 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://xxx:xxxxxxx@127.0.0.1:3306/flask_house'
    # 关闭警告信息
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # Flask-Mail and email confirmation settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'changeme-to-a-secure-key')
    MAIL_SERVER = "smtp.qq.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "xxxxxx" #此处推荐配置qq邮箱，在qq邮箱开启SMTP服务
    MAIL_PASSWORD = "xxxxxxxxxxx"
    MAIL_DEFAULT_SENDER = ("JNU租房系统注册验证", MAIL_USERNAME)  # 邮件显示的发件人名称
