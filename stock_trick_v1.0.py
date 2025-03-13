
from stock_filter_common_lib import *

if __name__ == '__main__':
    print('stock_trick_v1.0')
    path = r'C:\Users\Administrator\Desktop\导入模板.xlsx'

    args_dic = {
        '最小市值': 50,
        '最小换手率': 5,
        '最大换手率': 15,
        '最小动态市盈率': 0,
        '近期判断天数': 7,  # 判断最近若干天的最大最小价格
        '近期超涨系数': 1.25,  # 判断最近若干天的最大最小价格的最大倍速
        '次新股天数': 60,
        '过去1年最高价比当前价比值上限': 5,
        '过去1年最低价比当前价比值下限': 0.2,
        '60日最大涨幅' : 100
    }

    now_date = str(datetime.now().year)+'_'+str(datetime.now().month)+'_'+str(datetime.now().day)
    print_and_log('执行日期:'+now_date)
    dayliy_data_save()
    # 创建新工作簿
    wb = Workbook()
    # a = time.time()
    spot_df = ak.stock_zh_a_spot_em()
    # spot_df = stock_zh_a_spot_em_alex()
    # spot_df.to_csv(run_time_args_dic['每日数据']+"/"+now_date+"_每日市场全貌.csv", index=False, encoding="utf-8-sig")

    # print(spot_df)
    # b = time.time()
    # print('耗时：',b-a)
    print('所有股票数量:', len(spot_df))
    pass_stock_data_list = stock_filter.stock_fliter_1(spot_df,args_dic)

    count = 0
    message = '筛选条件:'+'\n'
    for item in args_dic.keys():
        message = message+item+':'+str(args_dic[item])+'\n'
    message = message + '筛选出的股票总数:'+str(len(pass_stock_data_list))+'\n'
    for item in pass_stock_data_list:
        count = count+1
        # message = message + item +'\n'
        excel_handle.write_excel(path, "Sheet1", "A"+str(count), item,wb)
    print(message)
    # 消息内容
    send_message = {
        "msg_type": "text",  # 消息类型，这里是文本
        "content": {
            "text": message  # 消息内容
        }
    }
    feisu_robot.robot_send(send_message)