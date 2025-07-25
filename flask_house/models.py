#数据模型文件
from config import db

#house_info表的模型类
class House(db.Model):
    #指定表名
    __tablename__ = 'house_info'
    #主键
    id = db.Column(db.Integer, primary_key=True)
    #房源标题
    title = db.Column(db.String(100))
    #房源户型
    rooms = db.Column(db.String(100))

    area = db.Column(db.String(100))

    price = db.Column(db.String(100))

    direction = db.Column(db.String(100))

    rent_type = db.Column(db.String(100))

    region = db.Column(db.String(100))

    block = db.Column(db.String(100))

    address = db.Column(db.String(100))

    traffic = db.Column(db.String(100))

    publish_time = db.Column(db.Integer)

    facilities = db.Column(db.TEXT)

    highlights = db.Column(db.TEXT)

    matching = db.Column(db.TEXT)

    travel = db.Column(db.TEXT)

    page_views = db.Column(db.Integer)

    landlord = db.Column(db.String(30))

    phone_num = db.Column(db.String(100))

    house_num = db.Column(db.String(100))

    #重写repr方法， 方便查看对象输出的内容
    def __repr__(self):
        return 'House title: %s, ID: %s' % (self.title, self.id)
    
#house_recommend表的模型类
#存储用户浏览记录
class Recommend(db.Model):
    #指定表名
    __tablename__ = 'house_recommend'
    #主键
    id = db.Column(db.Integer, primary_key=True)
    #用户ID
    user_id = db.Column(db.Integer)
    #房源ID
    house_id = db.Column(db.Integer)
    #房源标题
    title = db.Column(db.String(100))
    #房源所在小区
    address = db.Column(db.String(100))
    #房源所在街道
    block = db.Column(db.String(100))
    #浏览次数
    score = db.Column(db.Integer)


#user-info表的模型类
#存储用户信息
class User(db.Model):
    #指定表名
    __tablename__ = 'user_info'
    #用户ID
    id =  db.Column(db.Integer, primary_key=True)
    #用户昵称
    name = db.Column(db.String(100))
    #用户密码
    password = db.Column(db.String(100))
    # 邮箱地址
    email = db.Column(db.String(100))
    # 用户住址
    addr = db.Column(db.String(100))
    # 邮箱是否已验证
    confirmed = db.Column(db.Boolean, default=False)
    # 收藏房源ID
    collect_id = db.Column(db.String(250))
    #用户浏览记录
    seen_id = db.Column(db.String(250))

     #重写repr方法，
    def __repr__(self):
        return 'User: %s, %s' % (self.name, self.id)

