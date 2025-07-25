import math

from flask import Blueprint, render_template

from models import House

list_page = Blueprint('list_page', __name__)


#最新房源
@list_page.route('/list/pattern/<int:page>')
def new_list(page):
    #获取房源总数
    house_num = House.query.count()
    #计算页码数，向上取整
    total_num = math.ceil(house_num / 10)
    result = House.query.order_by(House.publish_time.desc()).paginate(page=page, per_page=10)
    return render_template('list.html', house_list=result.items, page_num=result.page, total_num=total_num)

#热门房源
@list_page.route('/list/hot_house/<int:page>')
def hot_list(page):
    house_num = House.query.count()
    total_num = math.ceil(house_num / 10)
    result = House.query.order_by(House.page_views.desc()).paginate(page=page, per_page=10)
    return render_template('list.html', house_list=result.items, page_num=result.page, total_num=total_num)