# API配置
ARK_API_KEY = "axxxxxxx" #隐藏本人秘钥
ARK_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL = "doubao-1-5-pro-32k-250115"

# 前端展示用
API_CONFIGURED = bool(ARK_API_KEY)  # 检查API密钥是否配置

# Flask配置
DEBUG = True
SECRET_KEY = "your-flask-secret-key"  # 生产环境建议更换为随机字符串（如："a-random-32-char-string-here"）
PERMANENT_SESSION_LIFETIME = 3600  # 会话有效期（秒）

# 新增：邮件服务配置（根据你的邮箱类型填写）
# 示例：QQ邮箱配置（其他邮箱需修改SMTP服务器）
MAIL_SERVER = "smtp.qq.com"  # QQ邮箱SMTP服务器地址
MAIL_PORT = 465  # SSL加密端口（QQ邮箱固定为465）
MAIL_USE_SSL = True  # 启用SSL加密（必须开启）
MAIL_USERNAME = "xxxxxxx"  # 你的邮箱地址（发件人）
MAIL_PASSWORD = "xxxxxxxx"  # 邮箱SMTP授权码（不是登录密码！）提交版隐藏本人信息
MAIL_DEFAULT_SENDER = ("Chatbot注册验证", MAIL_USERNAME)  # 邮件显示的发件人名称

# config.py 新增 MySQL 配置（替换原有的 SQLite 配置）
# MySQL 数据库连接信息（根据你的实际环境修改）
MYSQL_USER = "xxxxxx"  # 数据库用户名
MYSQL_PASSWORD = "xxxxx"  # 数据库密码（你的 MySQL 登录密码）
MYSQL_HOST = "localhost"  # 数据库主机（本地为 localhost，远程为服务器 IP）
MYSQL_PORT = 3306  # 数据库端口（默认 3306）
MYSQL_DB = "chatbot_db"  # 数据库名称（需提前在 MySQL 中创建）

# 数据库连接 URI（SQLAlchemy 格式）
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"

# 关闭 SQLAlchemy 跟踪修改（提升性能）
SQLALCHEMY_TRACK_MODIFICATIONS = False