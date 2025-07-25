from flask import Blueprint, request, render_template, redirect, url_for, abort

from models import House

query_page = Blueprint('query_page', __name__)

#统一处理查询逻辑的工具函数
def query_house(filter_condition, empty_message="暂无匹配房源"):
    """
    通用查询函数
    :param filter_condition: SQLAlchemy查询条件
    :param empty_message: 查询结果为空时的提示信息
    :return: 渲染后的模版
    """
    result = House.query.filter(filter_condition)\
                        .order_by(House.publish_time.desc())\
                        .all()
    return render_template('search_list.html',
                           house_list=result,
                           empty_message=empty_message)

@query_page.route('/query')
def search_txt_info():
    #获取所有可能得查询参数
    addr = request.args.get('addr')
    rooms = request.args.get('rooms')

    #检查是否有有效的查询参数
    if not (addr or rooms):
        return redirect(url_for('index_page.index'))
    
    #根据参数执行查询
    if addr:
        return query_house(House.address == addr, f"暂无 {addr} 地区的房源")
    
    if rooms:
        return query_house(House.rooms == rooms, f"暂无 {rooms} 户型的房源")
    
    #默认重定向（理论上不会执行到这）
    return redirect(url_for('index_page.index'))

#模版过滤器 - 处理标题过长
@query_page.app_template_filter('dealover')
def deal_title_over(title):
    if not title:
        return "无标题"
    return title[:15] + '...' if len(title) > 15 else title

#模版过滤器 - 处理空方向/交通信息
@query_page.app_template_filter('dealdirection')
def deal_direction(word):
    return '暂无信息' if not word or word.strip() == '' else word

#模版过滤器 - 处理交通信息
@query_page.app_template_filter('dealTraffic')
def deal_direction(word):
    return '交通便利' if not word or word.strip() == '' else word













# """
# 实现搜索列表页功能
# 1、先定义了一个/query的视图函数
# 2、通过request获取到请求当中的字段的内容
# 3、使用orm模型查询house表里边的字段
# 4、使用render_template进行渲染
# """

# @query_page.route('/query')
# def search_txt_info():
#     #获取地区字段的查询
#     if request.args.get('addr'):
#         addr = request.args.get('addr')
#         result = House.query.filter(House.address == addr).order_by(House.publish_time.desc()).all()
#         return render_template('search_list.html',house_list=result)
#     #获取户型字段的查询
#     if request.args.get('rooms'):
#         rooms = request.args.get('rooms')
#         result = House.query.filter(House.rooms == rooms).order_by(House.publish_time.desc()).all()
#         return render_template('search_list.html',house_list=result)
#     return redirect(url_for('index_page.index'))

# #当房源标题长度大于15的时候，用省略号替代
# def deal_title_over(title):
#     if len(title) > 15:
#         return title[:15] + '...'
#     else:
#         return title
    
# #当房源朝向，交通条件为空的时候，显示暂无信息
# def deal_direction(word):
#     if len(word) == 0 or word is None:
#         return '暂无信息'
#     else:
#         return word

# #添加过滤器
# query_page.add_app_template_filter(deal_title_over, 'dealover')
# query_page.add_app_template_filter(deal_direction, 'dealdirection')