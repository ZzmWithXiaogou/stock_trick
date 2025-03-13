import time

from stock_filter_common_lib import *


logging.basicConfig(filename='log/stock_choose.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',encoding='utf-8')


eval_arg_dic_base = {
        'arg_type': 0,
        '最小市值': 30,  # symbol_value
        '最大市值': 999999,  # symbol_value
        '最小换手率': 5,  # symbol_tr
        '最大换手率': 15,  # symbol_tr
        '最小动态市盈率': 0,  # symbol_ttm
        '最大动态市盈率': 200,  # symbol_ttm
        '近期判断天数': 7,  # 判断最近若干天的最大最小价格--不要了
        '近期超涨系数': 999999,  # 判断最近若干天的最大最小价格的最大倍速--不要了
        '次新股天数': 60,  # symbol_trade_days
        '过去1年最高价比当前价比值上限': 2.5,
        '过去1年最低价比当前价比值下限': 0.2,
        '月线死叉': 1,
        '周线死叉': 1,
        '日线死叉': 1,
        '最大5日乖离率': 99999,#百分比，当前收盘价和移动平均价的溢价率
        '最小5日乖离率': -99999,
        '最大10日乖离率': 3,
        '最小10日乖离率': -99999,
        '60日最大涨幅': 100,  # symbol_change_60_day
        '成交量比率，上涨时下限': 1.5,#成交量比率（VR）= 当日成交量/5日均量  主力介入信号：价格上涨时VR>1.5，下跌时VR<0.7（主力吸筹特征）
        '成交量比率，下跌时上限': 0.7,
        '输出表格': r'C:\Users\Administrator\Desktop\导入模板_base.xlsx',
        'debug_mode': 0  # 0 常规模式，支持当日日期，快速筛选，以及历史日期全量筛选  1 屏蔽掉当日快速筛选功能
    }


def choose_dayily(df,eval_arg_dic):
    df = df.copy()
    pass_stock_list = []
    #预筛选
    df = df[
        (df["市盈率-动态"] > eval_arg_dic['最小动态市盈率']) & (
         df["市盈率-动态"] < eval_arg_dic['最大动态市盈率']) & (
         df["换手率"] > eval_arg_dic['最小换手率']) & (
         df["换手率"] < eval_arg_dic['最大换手率']) & (
         df["流通市值"] > eval_arg_dic['最小市值'] * 100000000) & (
         df["60日涨跌幅"] < eval_arg_dic['60日最大涨幅']) & (
         df["流通市值"] < eval_arg_dic['最大市值'] * 100000000)
    ]
    stock_code_list = df['代码'].tolist()
    count = 1
    print_and_log('所有股票数量:'+str(len(df)))

    for symbol in stock_code_list:
        print_and_log('筛选进度:'+str(100*count/len(stock_code_list)))
        count = count+1
        time.sleep(0.1)
        stock_data_daily = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust="qfq")
        stock_data_weekly = ak.stock_zh_a_hist(symbol=symbol, period='weekly', adjust="qfq")
        stock_data_monthly = ak.stock_zh_a_hist(symbol=symbol, period='monthly', adjust="qfq")
        # stock_data_5min = ak.stock_zh_a_hist_min_em(symbol=symbol, period='5', adjust='qfq')
        # stock_data_15min = ak.stock_zh_a_hist_min_em(symbol=symbol, period='15', adjust='qfq')
        # stock_data_30min = ak.stock_zh_a_hist_min_em(symbol=symbol, period='30', adjust='qfq')
        # stock_data_60min = ak.stock_zh_a_hist_min_em(symbol=symbol, period='60', adjust='qfq')
        # stock_data_120min = ak.stock_zh_a_hist_min_em(symbol=symbol, period='120', adjust='qfq')

        if not fliter_new_stock(symbol,stock_data_daily,eval_arg_dic):
            continue
        # if not fliter_vr_condition(symbol,stock_data_daily,eval_arg_dic):
        #     continue
        if not fliter_bias_condition(symbol,stock_data_daily,eval_arg_dic,5):
            continue
        if not fliter_bias_condition(symbol,stock_data_daily,eval_arg_dic,10):
            continue
        if not fliter_pric_delta(symbol,stock_data_daily,eval_arg_dic):
            continue
        if not fliter_last_days_price_delta(symbol,stock_data_daily,eval_arg_dic):
            continue
        if not fliter_macd_dead_period(symbol,stock_data_monthly,eval_arg_dic,'monthly'):
            continue
        if not fliter_macd_dead_period(symbol,stock_data_weekly,eval_arg_dic,'weekly'):
            continue
        if not fliter_macd_dead_period(symbol,stock_data_daily,eval_arg_dic,'daily'):
            continue

        print_and_log('筛选到：' + symbol)
        pass_stock_list.append(symbol)

    save_and_send(pass_stock_list, eval_arg_dic)

    return pass_stock_list


def save_and_send(pass_stock_list,eval_arg_dic):
    # 创建新工作簿
    wb = Workbook()

    count = 0
    message = '筛选条件:' + '\n'
    for item in eval_arg_dic.keys():
        message = message + item + ':' + str(eval_arg_dic[item]) + '\n'
    message = message + '筛选出的股票总数:' + str(len(pass_stock_list)) + '\n'
    for item in pass_stock_list:
        count = count + 1
        # message = message + item +'\n'
        excel_handle.write_excel(eval_arg_dic['输出表格'], "Sheet1", "A" + str(count), item, wb)
    print_and_log(message)

    # 消息内容
    send_message = {
        "msg_type": "text",  # 消息类型，这里是文本
        "content": {
            "text": message  # 消息内容
        }
    }
    feisu_robot.robot_send(send_message)




def choose_sample(df,eval_arg_dic):
    df = df.copy()
    pass_stock_list = []
    # 创建新工作簿
    wb = Workbook()
    #预筛选
    df = df[
        (df["市盈率-动态"] > eval_arg_dic['最小动态市盈率']) & (
         df["市盈率-动态"] < eval_arg_dic['最大动态市盈率']) & (
         df["换手率"] > eval_arg_dic['最小换手率']) & (
         df["换手率"] < eval_arg_dic['最大换手率']) & (
         df["流通市值"] > eval_arg_dic['最小市值'] * 100000000) & (
         df["60日涨跌幅"] < eval_arg_dic['60日最大涨幅']) & (
         df["流通市值"] < eval_arg_dic['最大市值'] * 100000000)
    ]
    stock_code_list = df['代码'].tolist()
    count = 1
    print_and_log('所有股票数量:'+str(len(df)))

    for symbol in stock_code_list:
        print_and_log('筛选进度:'+str(100*count/len(stock_code_list)))
        count = count+1
        time.sleep(0.1)
        stock_data_daily = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust="qfq")
        # stock_data_weekly = ak.stock_zh_a_hist(symbol=symbol, period='weekly', adjust="qfq")
        # stock_data_monthly = ak.stock_zh_a_hist(symbol=symbol, period='monthly', adjust="qfq")
        # stock_data_5min = ak.stock_zh_a_hist_min_em(symbol=symbol, period='5', adjust='qfq')
        # stock_data_15min = ak.stock_zh_a_hist_min_em(symbol=symbol, period='15', adjust='qfq')
        # stock_data_30min = ak.stock_zh_a_hist_min_em(symbol=symbol, period='30', adjust='qfq')
        # stock_data_60min = ak.stock_zh_a_hist_min_em(symbol=symbol, period='60', adjust='qfq')
        # stock_data_120min = ak.stock_zh_a_hist_min_em(symbol=symbol, period='120', adjust='qfq')

        if not fliter_new_stock(symbol,stock_data_daily,eval_arg_dic):
            continue
        if not fliter_vr(symbol,stock_data_daily,eval_arg_dic):
            continue
        if not fliter_bias(symbol,stock_data_daily,eval_arg_dic):
            continue

        print_and_log('筛选到：' + symbol)
        pass_stock_list.append(symbol)

    save_and_send(pass_stock_list, eval_arg_dic)
    return pass_stock_list



def eval_DIF_DEA_MACD_period_len(stock_data,period_len):
    # 获取指定股票的日线数据
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



def fliter_macd_dead_period(symbol,stock_data,eval_arg_dic,period):
    stock_data = stock_data.copy()
    stock_data = eval_DIF_DEA_MACD_period_len(stock_data, period)
    if stock_data['DIF'].tolist()[-1] <= stock_data['DEA'].tolist()[-1]:
        print_and_log(symbol + '：fail,'+period+'线死叉')
        return 0
    return 1

def fliter_vr_condition(symbol,stock_data,eval_arg_dic):
    stock_data = stock_data.copy()
    stock_data = cal_VR_df(stock_data, 5)
    symbol_delta = stock_data.iloc[-1, stock_data.columns.get_loc('涨跌幅')]
    symbol_vr = stock_data.iloc[-1, stock_data.columns.get_loc('过去5周期量比')]
    if symbol_delta > 0:
        if symbol_vr < eval_arg_dic['成交量比率，上涨时下限']:
            print_and_log(symbol + '：fail,成交量比率，上涨时,小于' + str(eval_arg_dic['成交量比率，上涨时下限']))
            return 0
    else:
        if symbol_vr > eval_arg_dic['成交量比率，下跌时上限']:
            print_and_log(symbol + '：fail,成交量比率，下跌时,大于' + str(eval_arg_dic['成交量比率，下跌时上限']))
            return 0
    return 1

def fliter_bias_condition(symbol,stock_data,eval_arg_dic,days):
    stock_data = stock_data.copy()
    stock_data = cal_BIAS_df(stock_data,days)
    symbol_day_bias = stock_data.iloc[-1, stock_data.columns.get_loc('bias_'+str(days))]

    if symbol_day_bias >= eval_arg_dic['最大'+str(days)+'日乖离率']:
        print_and_log(symbol + '：fail,'+str(days)+'日乖离率大于' + str(eval_arg_dic['最大'+str(days)+'日乖离率'])+'%')
        return 0
    if symbol_day_bias <= eval_arg_dic['最小'+str(days)+'日乖离率']:
        print_and_log(symbol + '：fail,'+str(days)+'日乖离率小于' + str(eval_arg_dic['最小'+str(days)+'日乖离率'])+'%')
        return 0
    return 1

def fliter_pric_delta(symbol,stock_data,eval_arg_dic):
    stock_data = stock_data.copy()
    max_price_dayily = stock_data['最高'].tolist()
    min_price_dayily = stock_data['最低'].tolist()
    symbol_trade_days = len(stock_data)
    close_price = stock_data.iloc[-1, stock_data.columns.get_loc('收盘')]

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
    return 1
def fliter_last_days_price_delta(symbol,stock_data,eval_arg_dic):
    stock_data = stock_data.copy()
    last_seven_day_max_price = max(stock_data['最高'].tolist()[0-eval_arg_dic['近期判断天数']:])
    last_seven_day_min_price = min(stock_data['最低'].tolist()[0-eval_arg_dic['近期判断天数']:])
    if last_seven_day_max_price / last_seven_day_min_price >= eval_arg_dic['近期超涨系数']:
        print_and_log(symbol+'：fail,最近'+str(eval_arg_dic['近期判断天数'])+'个交易日内最高价格相对于当前价格比超过'+str(eval_arg_dic['近期超涨系数']))
        return 0
    return 1


def fliter_new_stock(symbol,stock_data,eval_arg_dic):
    stock_data = stock_data.copy()
    if len(stock_data)<=eval_arg_dic['次新股天数']:
        print_and_log(symbol + '：fail,上市天数小于' + str(eval_arg_dic['次新股天数']))
        return 0
    else:
        return 1

def fliter_bias(symbol,stock_data,eval_arg_dic):
    stock_data = stock_data.copy()
    stock_data = cal_BIAS_df(stock_data,10)
    last_days_df = stock_data.tail(7)
    bias_list =  last_days_df['bias_10'].tolist()

    if max(bias_list) > 5:
        print_and_log(symbol + '：fail,近7日的最大10日乖离率大于' + str(5))
        return 0
    return 1

def fliter_vr(symbol,stock_data,eval_arg_dic): #评估过去5日VR发生了突增且，成交价格7日内没有大幅上涨
    stock_data = stock_data.copy()
    stock_data = cal_VR_df(stock_data,5)
    last_days_df = stock_data.tail(7)
    # print(last_5days_df)

    close_price_list = last_days_df['收盘'].tolist()
    vr_list = last_days_df['过去5周期量比'].tolist()
    delta_list = last_days_df['涨跌幅'].tolist()
    high_list = last_days_df['最高'].tolist()
    low_list = last_days_df['最低'].tolist()

    # print(vr_list)
    # print(delta_list)
    # print(high_list)
    # print(low_list)

    if max(vr_list) < 2 : #最近7日成交量比率最大值下限
        print_and_log(symbol + '：fail,近7日成交量比率最大值小于' + str(2))
        return 0
    if max(delta_list) > 5 : #最近7日单日涨幅上限，超过一定单日涨幅的剔除
        print_and_log(symbol + '：fail,最近7日单日涨幅大于' + str(5))
        return 0
    if max(high_list)/min(low_list) > 1.20 : #最近7日最高价比最低价上限，超过一定比值的剔除
        print_and_log(symbol + '：fail,最近7日最高价比最低价大于' + str(1.20))
        return 0
    return 1



if __name__ == '__main__':
    print('stock_choose')  #以函数组成插件式的筛选条件
    #
    # while 1:
    #     if datetime.now().hour == 14 and datetime.now().minute == 45:
    #         break
    #     else:
    #         time.sleep(1)
    df = ak.stock_zh_a_spot_em()
    # pass_stock_list = choose_sample(df,eval_arg_dic_base)
    pass_stock_list = choose_dayily(df,eval_arg_dic_small)
    pass_stock_list = choose_dayily(df,eval_arg_dic_large)

    print(pass_stock_list)



    # stock_data_daily = ak.stock_zh_a_hist(symbol='300733', period='daily', adjust="qfq")
    # fliter_5days_vr_eval('601919', stock_data_daily,eval_arg_dic_base)

    # fliter_vr('300733', stock_data_daily, eval_arg_dic_base)