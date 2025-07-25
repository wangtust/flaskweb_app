from sklearn.linear_model import LinearRegression
import numpy

#基于线性回归模型预测功能
def linear_model_main(x_parameter, y_parameter, predict_value):
    #创建线性回归模型
    linear_reg = LinearRegression()
    #训练线性回归模型
    linear_reg.fit(x_parameter, y_parameter)
    #预测新的样本
    predict_value = numpy.array([predict_value]).reshape(-1, 1)
    predict_outcome = linear_reg.predict(predict_value)

    #返回新的预测值
    return predict_outcome


#判断是否在当前文件下运行的程序
#可以用于某个功能的测试代码的编写
if __name__ == '__main__':
    #广告费
    x_data = [[4], [8], [9], [8], [7], [12]]
    #销售额
    y_data = [9, 19, 23, 22, 15, 25]
    #新样本值
    predict_value = 6
    predict_outcome = linear_model_main(x_data, y_data, predict_value)
    print('预测结果：', predict_outcome)
