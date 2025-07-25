from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from sqlalchemy import func

from models import House
from utils.linear_model import linear_model_main

detail_api = Blueprint('detail_api', __name__)

#户型占比接口api
@detail_api.route('/piedata/<block>')
def pie_data(block):
    result = House.query.with_entities(House.rooms, func.count()).filter(House.block == block).group_by(
        House.rooms
    ).order_by(func.count().desc()).all()
    data = []
    for one_house in result:
        #将房源户型数据追加到data列表中
        data.append({'name': one_house[0], 'value': one_house[1]})
    return jsonify({'data':data})

#小区房源数量TOP20 API
@detail_api.route('/columndata/<block>')
def column_data(block):
    result = House.query.with_entities(House.address, func.count()).filter(House.block == block).group_by(
        House.address
    ).order_by(func.count().desc()).all()

    name_list = []
    num_list = []

    #将地区和数量分别存入对应的列表中
    for addr, num in result:
        #提取地区名，去掉-
        addr_name = addr.rsplit('-',1)[1]
        name_list.append(addr_name)
        num_list.append(num)

    #如果地址数量超过20则只显示20条
    if len(name_list) > 20:
        data = {'name_list_x': name_list[:20], 'num_list_y': num_list[:20]}
    else:
        data = {'name_list_x': name_list, 'num_list_y': num_list}

    return jsonify({'data': data})


#房价预测
@detail_api.route('/scatterdata/<block>')
def scatter_data(block):
    #根据时间序列获取房源数据
    #House.price / House.area = 房子价格/房子面积
    #代码实际执行的sql语句
    # SELECT AVG(price/area) FROM house_info WHERE block = '朝阳-工体' GROUP BY publish_time ORDER BY publish_time;
    result = House.query.with_entities(func.avg(House.price / House.area)).filter(
        House.block == block
    ).group_by(House.publish_time).order_by(House.publish_time).all()
    #SELECT publish_time FROM house_info WHERE block = '朝阳-工体';
    time_stamp = House.query.with_entities(House.publish_time).filter(House.block == block).all()
    time_stamp.sort(reverse=True)

    #生成最近30天的日期列表
    date_list = []
    for i in range(1, 30):
        #将时间戳(timestamp)转换成具体的日期
        latest_release = datetime.fromtimestamp(int(time_stamp[0][0]))
        #获取最新房源发布时间的1天
        day = latest_release + timedelta(days=-i)
        #将1天的日期格式化为字符串的形式并添加到date_list列表中
        #y = 年 m = 月 d = 日
        date_list.append(day.strftime("%m-%d"))
    #将日期列表反转
    date_list.reverse()

    #获取平均价格
    data = []
    x = []
    y = []

    #将result结果转换为列表格式
    for index, i in enumerate(result):
        #将平均价格的索引添加到x列表中
        x.append([index])
        #将平均价格四舍五入保留两位小数添加到y列表中
        y.append(round(i[0],2))
        #将索引和平均价格添加到data列表中
        data.append([index, round(i[0], 2)])

    #对未来一天的价格作预测
    #预测的索引值
    predict_value = len(data)
    #调用线性回归模型进行预测
    predict_outcome = linear_model_main(x, y, predict_value)
    #将预测出来的房价四舍五入
    p_outcome = round(predict_outcome[0],2)
    #将预测的数据加入到data列表中
    data.append([predict_value, p_outcome])
    return jsonify({'data': {'data-predict': data, 'date_li': date_list}})

#户型价格走势
@detail_api.route('/brokenlinedata/<block>')
def broke_line_data(block):
    #获取房源时间序列
    time_stamp = House.query.with_entities(House.publish_time).filter(House.block == block).all()
    time_stamp.sort(reverse=True)

    #生成最近14天的日期列表
    date_list = []
    for i in range(1, 14):
        #将时间戳(timestamp)转换成具体的日期
        latest_release = datetime.fromtimestamp(int(time_stamp[0][0]))
        #获取最新房源发布时间的i天
        day = latest_release + timedelta(days=-i)
        #将1天的日期格式化为字符串的形式并添加到date_list列表中
        #y = 年 m = 月 d = 日
        date_list.append(day.strftime("%m-%d"))
    #将日期列表反转
    date_list.reverse()

    #1室1厅的户型
    result = House.query.with_entities(func.avg(House.price / House.area)).filter(
        House.block == block,
        House.rooms == '1室1厅'
    ).group_by(House.publish_time).order_by(House.publish_time).all()

    print(result)

    data = []
    for i in result[-14:]:
        data.append(round(i[0], 2))

    #2室1厅的户型
    result = House.query.with_entities(func.avg(House.price / House.area)).filter(
        House.block == block,
        House.rooms == '2室1厅'
    ).group_by(House.publish_time).order_by(House.publish_time).all()
    data1 = []
    for i in result[-14:]:
        data1.append(round(i[0], 2))

    #2室2厅的户型
    result = House.query.with_entities(func.avg(House.price / House.area)).filter(
        House.block == block,
        House.rooms == '2室2厅'
    ).group_by(House.publish_time).order_by(House.publish_time).all()
    data2 = []
    for i in result[-14:]:
        data2.append(round(i[0], 2))

    #3室2厅的户型
    result = House.query.with_entities(func.avg(House.price / House.area)).filter(
        House.block == block,
        House.rooms == '3室2厅'
    ).group_by(House.publish_time).order_by(House.publish_time).all()
    data3 = []
    for i in result[-14:]:
        data3.append(round(i[0], 2))

    return jsonify({'data':
        {
            '1室1厅':data,
            '2室1厅':data1,
            '2室2厅':data2,
            '3室2厅':data3,
            'date_li': date_list
        }
    })
