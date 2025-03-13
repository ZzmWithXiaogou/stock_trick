import logging
import time

from stock_filter_common_lib import *
logging.basicConfig(filename='log/eval_master.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',encoding='utf-8')



def eval_DIF_DEA_MACD_period_len(code,period_len):
    # 获取指定股票的日线数据
    stock_code = code  # 这里替换成你想要查询的股票代码

    re_try_count = 0
    while re_try_count < run_time_args_dic['最大重试次数']:
        try:
            stock_data = ak.stock_zh_a_hist(symbol=stock_code, period=period_len, adjust="qfq")
            # stock_data = stock_filter_common_lib.stock_zh_a_hist_alex(symbol=stock_code, period=period_len, adjust="qfq")
            if len(stock_data) != 0:
                break
            else:
                time.sleep(0.1)
                re_try_count = re_try_count + 1
                print_and_log('开始重试-----' + str(re_try_count) + ' ' + str(e))
        except Exception as e:
            time.sleep(0.1)
            re_try_count = re_try_count + 1
            print_and_log('开始重试-----' + str(re_try_count) + ' ' + str(e))
    if re_try_count == run_time_args_dic['最大重试次数']:
        print_and_log('重试超过' + str(re_try_count) + '次-----')
        # 消息内容
        send_message = {
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": "筛选失败，需要重新筛选"  # 消息内容
            }
        }
        feisu_robot.robot_send(send_message)
        exit()
    # 计算12日EMA和26日EMA
    stock_data['EMA12'] = stock_data['收盘'].ewm(span=12, adjust=False).mean()
    stock_data['EMA26'] = stock_data['收盘'].ewm(span=26, adjust=False).mean()

    # 计算MACD
    stock_data['DIF'] = stock_data['EMA12'] - stock_data['EMA26']

    # 计算信号线（9日EMA）
    stock_data['DEA'] = stock_data['DIF'].ewm(span=9, adjust=False).mean()

    # 计算柱状图
    stock_data['MACD'] = 2 * (stock_data['DIF'] - stock_data['DEA'])

    # 输出结果
    # stock_data = stock_data.iloc[::-1]
    # stock_data.to_csv("cal_DIF_DEA_MACD_period_len.csv", index=False, encoding="utf-8-sig")
    return stock_data

def eval_DIF_DEA_MACD_time_len(code,time_len):
    # 获取指定股票的日线数据

    # stock_data = ak.stock_zh_a_hist_min_em(symbol=code, period=time_len, adjust="qfq")
    # stock_data = stock_filter_common_lib.stock_zh_a_hist_min_em_alex(symbol=code, period=time_len_used, adjust="qfq")
    re_try_count = 0
    while re_try_count < run_time_args_dic['最大重试次数']:
        try:
            stock_data = ak.stock_zh_a_hist_min_em(symbol=code, period=time_len, adjust="qfq")
            # stock_data = stock_filter_common_lib.stock_zh_a_hist_alex(symbol=stock_code, period=period_len, adjust="qfq")
            if len(stock_data) != 0:
                break
            else:
                time.sleep(0.1)
                re_try_count = re_try_count + 1
                print_and_log('开始重试-----' + str(re_try_count) + ' ' + str(e))
        except Exception as e:
            time.sleep(0.1)
            re_try_count = re_try_count + 1
            print_and_log('开始重试-----' + str(re_try_count) + ' ' + str(e))
    if re_try_count == run_time_args_dic['最大重试次数']:
        print_and_log('重试超过' + str(re_try_count) + '次-----')
        # 消息内容
        send_message = {
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": "筛选失败，需要重新筛选"  # 消息内容
            }
        }
        feisu_robot.robot_send(send_message)
        exit()
    # 计算12小时和26小时的 EMA
    stock_data['EMA12'] = stock_data['收盘'].ewm(span=12, adjust=False).mean()
    stock_data['EMA26'] = stock_data['收盘'].ewm(span=26, adjust=False).mean()

    # 计算MACD
    stock_data['DIF'] = stock_data['EMA12'] - stock_data['EMA26']

    # 计算信号线（9日EMA）
    stock_data['DEA'] = stock_data['DIF'].ewm(span=9, adjust=False).mean()

    # 计算柱状图
    stock_data['MACD'] = 2 * (stock_data['DIF'] - stock_data['DEA'])

    return stock_data

def symbol_fliter(eval_arg_dic,symbol,start_date):

    if eval_arg_dic['debug_mode'] != 1 and int(start_date.split('-')[0]) == datetime.now().year and int(start_date.split('-')[1]) == datetime.now().month and int(start_date.split('-')[2]) == datetime.now().day:
        # print_and_log('输入的是当日日期') #当日日期 不需要借助每日市值筛选
        pass
    else:
        value_data = ak.stock_value_em(symbol=symbol)
        value_data['数据日期'] = value_data['数据日期'].astype(str)
        value_to_start_date = value_data[value_data['数据日期'] <= start_date]
        value_after_start_date = value_data[value_data['数据日期'] > start_date]
        if value_to_start_date.empty:
            print_and_log('输入日期不存在')
            return 0
        symbol_value = value_to_start_date.iloc[-1, value_to_start_date.columns.get_loc('总市值')]
        symbol_ttm = value_to_start_date.iloc[-1, value_to_start_date.columns.get_loc('PE(TTM)')]

        if symbol_value <= eval_arg_dic['最小市值']*100000000:
            print_and_log(symbol+'：fail,市值小于'+str(eval_arg_dic['最小市值'])+'亿')
            return 0
        if symbol_ttm <= eval_arg_dic['最小动态市盈率']:
            print_and_log(symbol+'：fail,动态市盈率小于'+str(eval_arg_dic['最小动态市盈率']))
            return 0
    #todo 看下这里得到的市值和全貌得到的市值关系是啥样的  需要得到预估全年利润  总市值/预估全年利润 =动态市盈率


    stock_data = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust="qfq")
    stock_data['日期'] = stock_data['日期'].astype(str)
    stock_to_start_date = stock_data[stock_data['日期'] <= start_date]
    stock_after_start_date = stock_data[stock_data['日期'] > start_date]
    if stock_to_start_date.empty:
        print_and_log('输入日期不存在')
        return 0

    symbol_tr = stock_to_start_date.iloc[-1, stock_to_start_date.columns.get_loc('换手率')]
    close_price = stock_to_start_date.iloc[-1, stock_to_start_date.columns.get_loc('收盘')]


    symbol_trade_days = len(stock_to_start_date)
    if symbol_trade_days <= eval_arg_dic['次新股天数']:
        print_and_log(symbol + '：fail,上市天数小于' + str(eval_arg_dic['次新股天数']))
        return 0

    symbol_delta = stock_to_start_date.iloc[-1, stock_to_start_date.columns.get_loc('涨跌幅')]

    if eval_arg_dic['arg_type'] == 0:
        if symbol_delta > 0:
            if cal_VR(stock_to_start_date,5) < eval_arg_dic['成交量比率，上涨时下限']:
                print_and_log(symbol + '：fail,成交量比率，上涨时,小于' + str(eval_arg_dic['成交量比率，上涨时下限']))
                return 0
        else:
            if cal_VR(stock_to_start_date,5) > eval_arg_dic['成交量比率，下跌时上限']:
                print_and_log(symbol + '：fail,成交量比率，下跌时,大于' + str(eval_arg_dic['成交量比率，下跌时上限']))
                return 0

    if eval_arg_dic['arg_type'] == 1:
        if symbol_delta > 0:
            if cal_VR(stock_to_start_date,5) < eval_arg_dic['成交量比率，上涨时下限']:
                print_and_log(symbol + '：fail,成交量比率，上涨时,小于' + str(eval_arg_dic['成交量比率，上涨时下限']))
                return 0
        else:
            if cal_VR(stock_to_start_date,5) > eval_arg_dic['成交量比率，下跌时上限']:
                print_and_log(symbol + '：fail,成交量比率，下跌时,大于' + str(eval_arg_dic['成交量比率，下跌时上限']))
                return 0



    symbol_5day_bias = cal_BIAS(5,stock_data)
    if symbol_5day_bias >= eval_arg_dic['最大5日乖离率']:
        print_and_log(symbol + '：fail,5日乖离率大于' + str(eval_arg_dic['最大5日乖离率'])+'%')
        return 0

    symbol_10day_bias = cal_BIAS(10,stock_data)
    if symbol_10day_bias >= eval_arg_dic['最大10日乖离率']:
        print_and_log(symbol + '：fail,10日乖离率大于' + str(eval_arg_dic['最大10日乖离率'])+'%')
        return 0
    if symbol_10day_bias <= eval_arg_dic['最小10日乖离率']:
        print_and_log(symbol + '：fail,10日乖离率小于' + str(eval_arg_dic['最小10日乖离率'])+'%')
        return 0




    if symbol_tr <= eval_arg_dic['最小换手率'] or symbol_tr >= eval_arg_dic['最大换手率']:
        print_and_log(symbol+'：fail,换手率不满足'+str(eval_arg_dic['最小换手率'])+'~'+str(eval_arg_dic['最大换手率']))
        return 0

    close_price_before_60_day = stock_to_start_date.iloc[-61, stock_to_start_date.columns.get_loc('收盘')]
    symbol_change_60_day = 100 * ((close_price - close_price_before_60_day) / close_price_before_60_day)
    if symbol_change_60_day >= eval_arg_dic['60日最大涨幅']:
        print_and_log(symbol+'：fail,60日涨幅大于'+str(eval_arg_dic['60日最大涨幅']))
        return 0

    max_price_dayily = stock_to_start_date['最高'].tolist()
    min_price_dayily = stock_to_start_date['最低'].tolist()

    if symbol_trade_days > 365:
        one_year_max_price_dayily = max_price_dayily[-365:]
        one_year_min_price_dayily = min_price_dayily[-365:]
    else:
        one_year_max_price_dayily = max_price_dayily
        one_year_min_price_dayily = min_price_dayily
    max_price = max(one_year_max_price_dayily)
    min_price = min(one_year_min_price_dayily)

    if max_price / close_price >= eval_arg_dic['过去1年最高价比当前价比值上限'] or min_price / close_price <= eval_arg_dic['过去1年最低价比当前价比值下限']:
        print_and_log(symbol+'：fail,最近一年最高价相对于当前价格比不满足'+str(eval_arg_dic['过去1年最低价比当前价比值下限'])+'~'+str(eval_arg_dic['过去1年最高价比当前价比值上限']))
        return 0

    last_seven_day_max_price = max(stock_to_start_date['最高'].tolist()[0-eval_arg_dic['近期判断天数']:])
    last_seven_day_min_price = min(stock_to_start_date['最低'].tolist()[0-eval_arg_dic['近期判断天数']:])
    if last_seven_day_max_price / last_seven_day_min_price >= eval_arg_dic['近期超涨系数']:
        print_and_log(symbol+'：fail,最近'+str(eval_arg_dic['近期判断天数'])+'个交易日内最高价格相对于当前价格比超过'+str(eval_arg_dic['近期超涨系数']))
        return 0

    if eval_arg_dic['月线死叉'] == 1:
        monthly_macd_stock_df = eval_DIF_DEA_MACD_period_len(symbol, 'monthly')
        if monthly_macd_stock_df['DIF'].tolist()[-1] <= monthly_macd_stock_df['DEA'].tolist()[-1]:
            print_and_log(symbol+'：fail,月线死叉')
            return 0
    if eval_arg_dic['周线死叉'] == 1:
        weekly_macd_stock_df = eval_DIF_DEA_MACD_period_len(symbol, 'weekly')
        if weekly_macd_stock_df['DIF'].tolist()[-1] <= weekly_macd_stock_df['DEA'].tolist()[-1]:
            print_and_log(symbol+'：fail,周线死叉')
            return 0
    if eval_arg_dic['日线死叉'] == 1:
        dayily_macd_stock_df = eval_DIF_DEA_MACD_period_len(symbol, 'daily')
        if dayily_macd_stock_df['DIF'].tolist()[-1] <= dayily_macd_stock_df['DEA'].tolist()[-1]:
            print_and_log(symbol + '：fail,日线死叉')
            return 0
    # twohour_macd_stock_df = eval_DIF_DEA_MACD_time_len(symbol, "120")
    # if twohour_macd_stock_df['DIF'].tolist()[-1] <= twohour_macd_stock_df['DEA'].tolist()[-1]:
    #     print_and_log(symbol + '：fail,120分线死叉')
    #     return 0
    # hour_macd_stock_df = eval_DIF_DEA_MACD_time_len(symbol, "60")
    # if hour_macd_stock_df['DIF'].tolist()[-1] <= hour_macd_stock_df['DEA'].tolist()[-1]:
    #     print_and_log(symbol + '：fail,60分线死叉')
    #     return 0
    return 1

def eval_master_main(eval_arg_dic,start_date):

    pass_stock_list=[]

    stock_zh_a_spot_em = ak.stock_zh_a_spot_em()


    if eval_arg_dic['debug_mode'] != 1 and (int(start_date.split('-')[0]) == datetime.now().year and int(start_date.split('-')[1]) == datetime.now().month and int(start_date.split('-')[2]) == datetime.now().day):
        print_and_log('输入的是当日日期') #当日日期
        stock_zh_a_spot_em = stock_zh_a_spot_em[
            (stock_zh_a_spot_em["市盈率-动态"] > eval_arg_dic['最小动态市盈率']) & (stock_zh_a_spot_em["市盈率-动态"] < eval_arg_dic['最大动态市盈率']) & (stock_zh_a_spot_em["换手率"] > eval_arg_dic['最小换手率']) & (
                        stock_zh_a_spot_em["换手率"] < eval_arg_dic['最大换手率']) & (
                        stock_zh_a_spot_em["流通市值"] > eval_arg_dic['最小市值'] * 100000000) & (
                        stock_zh_a_spot_em["60日涨跌幅"] < eval_arg_dic['60日最大涨幅'])& (
                        stock_zh_a_spot_em["流通市值"] < eval_arg_dic['最大市值'] * 100000000)]

    stock_code_list = stock_zh_a_spot_em['代码'].tolist()
    count = 1
    print_and_log('所有股票数量:'+str(len(stock_code_list)))

    for symbol in stock_code_list:
        print_and_log('筛选进度:'+str(100*count/len(stock_code_list)))
        count = count+1
        time.sleep(0.1)
        try:
            ret = symbol_fliter(eval_arg_dic, symbol, start_date)
        except:
            print_and_log(symbol+' error')
            ret = 0
            traceback.print_exc()  # 打印完整的错误堆栈信息

        if ret == 0:
            continue
        else:
            print_and_log('筛选到：'+symbol)
            pass_stock_list.append(symbol)

    return pass_stock_list

if __name__ == '__main__':
    print_and_log('eval_master')


    dayliy_data_save()

    now_date = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day)
    print_and_log('执行日期:' + now_date)

    # symbol = '601919'
    # start_date = now_date # '2025-02-16'
    # start_date = '2025-02-16' # '2025-02-16'
    # ret = symbol_fliter(eval_arg_dic, symbol, start_date)
    # print(ret)
    # exit()

    a = time.time()
    pass_stock_list = eval_master_main(eval_arg_dic_small,now_date)
    b = time.time()
    print_and_log('筛选耗时：'+str(b-a)+'秒')
    print(pass_stock_list)
    # 创建新工作簿
    wb = Workbook()

    count = 0
    message = '筛选条件:' + '\n'
    for item in eval_arg_dic_small.keys():
        message = message + item + ':' + str(eval_arg_dic_small[item]) + '\n'
    message = message + '筛选出的股票总数:' + str(len(pass_stock_list)) + '\n'
    for item in pass_stock_list:
        count = count + 1
        # message = message + item +'\n'
        excel_handle.write_excel(eval_arg_dic_small['输出表格'], "Sheet1", "A" + str(count), item, wb)
    print_and_log(message)



    # 消息内容
    send_message = {
        "msg_type": "text",  # 消息类型，这里是文本
        "content": {
            "text": message  # 消息内容
        }
    }
    feisu_robot.robot_send(send_message)




    a = time.time()
    pass_stock_list = eval_master_main(eval_arg_dic_large, now_date)
    b = time.time()
    print_and_log('筛选耗时：' + str(b - a) + '秒')
    print(pass_stock_list)
    # 创建新工作簿
    wb = Workbook()

    count = 0
    message = '筛选条件:' + '\n'
    for item in eval_arg_dic_large.keys():
        message = message + item + ':' + str(eval_arg_dic_large[item]) + '\n'
    message = message + '筛选出的股票总数:' + str(len(pass_stock_list)) + '\n'
    for item in pass_stock_list:
        count = count + 1
        # message = message + item +'\n'
        excel_handle.write_excel(eval_arg_dic_large['输出表格'], "Sheet1", "A" + str(count), item, wb)
    print_and_log(message)

    # 消息内容
    send_message = {
        "msg_type": "text",  # 消息类型，这里是文本
        "content": {
            "text": message  # 消息内容
        }
    }
    feisu_robot.robot_send(send_message)
