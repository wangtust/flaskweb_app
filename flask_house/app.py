#项目入口文件
from flask import Flask, render_template
from flask_mail import Mail
from config import Config, db

#首页
from page.index import index_page
#搜索页
from page.query import query_page
#列表页
from page.list import list_page
#详情页
from page.detail import detail_page
#详情页API
from api.detail import detail_api
#用户中心页面
from page.user import user_page


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
# Initialize Flask-Mail
mail = Mail(app)

# 导入需要 mail 的蓝图需在 mail 初始化后
from api.user import user_api

#注册首页
app.register_blueprint(index_page, url_prefix='/')
#注册搜索页
app.register_blueprint(query_page, url_prefix='/')
#注册列表页
app.register_blueprint(list_page, url_prefix='/')
#注册详情页
app.register_blueprint(detail_page, url_prefix='/')
#注册用户中心页面
app.register_blueprint(user_page, url_prefix='/')
#注册详情页API
app.register_blueprint(detail_api, url_prefix='/get/')
#注册用户登录与注册接口
app.register_blueprint(user_api, url_prefix='/')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5080,debug=Config.DEBUG)