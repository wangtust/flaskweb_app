from flask import Blueprint, render_template, redirect

from models import User, House

user_page = Blueprint('user_page', __name__)

#用户中心页面
@user_page.route('/user/<username>')
def user(username):
    #查询用户
    user = User.query.filter(User.name == username).first()
    #如果用户存在
    if user:
        # 获取收藏房源列表
        collect_house_list = []
        if user.collect_id:
            for hid in user.collect_id.split(','):
                try:
                    h = House.query.get(int(hid))
                    if h:
                        collect_house_list.append(h)
                except ValueError:
                    continue
        # 获取浏览记录列表
        seen_house_list = []
        if user.seen_id:
            for hid in user.seen_id.split(','):
                try:
                    h = House.query.get(int(hid))
                    if h:
                        seen_house_list.append(h)
                except ValueError:
                    continue
        # 渲染页面 with lists
        return render_template('user_page.html', user=user,
                               collect_house_list=collect_house_list,
                               seen_house_list=seen_house_list)
    else:
        #不存在则跳转回首页
        return redirect('/')