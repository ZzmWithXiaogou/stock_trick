import stock_filter_common_lib
from stock_filter_common_lib import *



def stock_fliter_1(spot_df,args_dic): #按照基础信息进行初步筛选
    #筛选市值范围在min_turnover_rate~max_turnover_rate 且 总市值大于min_valuation 且 动态市盈率大于min_TTM
    spot_df_ret = spot_df[(spot_df["市盈率-动态"]>args_dic['最小动态市盈率']) & (spot_df["换手率"]>args_dic['最小换手率']) & (spot_df["换手率"]<args_dic['最大换手率']) & (spot_df["流通市值"]>args_dic['最小市值']*100000000) & (spot_df["60日涨跌幅"]<args_dic['60日最大涨幅'] ) ]
    # print('筛选后股票数量:', len(spot_df_ret))
    # spot_df_ret.to_csv("stock_fliter_1.csv", index=False, encoding="utf-8-sig")
    code_list_1 = spot_df_ret['代码'].tolist()
    pass_stock_data_list=[]
    for item in code_list_1:
        pass_stock_data = cal_max_min(item,args_dic,spot_df)
        # print(pass_stock_data)
        # pass_stock_data.to_csv("stock_fliter_1.csv", index=False, encoding="utf-8-sig")
        # exit()
        try:
            # print('aaaa')
            # print(pass_stock_data)
            # print('bbbb')
            # print(pass_stock_data['收盘'].tolist()[7])
            # print(max(pass_stock_data['最高'].tolist()[0:7]))
            # exit()
            last_seven_day_max_price = max(pass_stock_data['最高'].tolist()[0:args_dic['近期判断天数']])
            last_seven_day_min_price = min(pass_stock_data['最低'].tolist()[0:args_dic['近期判断天数']])
            # print(pass_stock_data['股票代码'].tolist()[0],last_seven_day_max_price,last_seven_day_min_price)
            # exit()
            if len(pass_stock_data['收盘'].tolist()) > args_dic['次新股天数']: #过滤次新股
                if last_seven_day_max_price/last_seven_day_min_price < args_dic['近期超涨系数']:
                    # print(type(pass_stock_data['股票代码'].tolist()[0]))
                    weekly_macd_stock_df = cal_DIF_DEA_MACD_period_len(pass_stock_data['股票代码'].tolist()[0],'weekly')
                    if weekly_macd_stock_df['DIF'].tolist()[-1] > weekly_macd_stock_df['DEA'].tolist()[-1]:
                        dayily_macd_stock_df = cal_DIF_DEA_MACD_period_len(pass_stock_data['股票代码'].tolist()[0],'daily')
                        if dayily_macd_stock_df['DIF'].tolist()[-1] > dayily_macd_stock_df['DEA'].tolist()[-1]:
                            twohour_macd_stock_df = cal_DIF_DEA_MACD_time_len(pass_stock_data['股票代码'].tolist()[0],"120")
                            if twohour_macd_stock_df['DIF'].tolist()[-1] > twohour_macd_stock_df['DEA'].tolist()[-1]:
                                hour_macd_stock_df = cal_DIF_DEA_MACD_time_len(pass_stock_data['股票代码'].tolist()[0],"60")
                                if hour_macd_stock_df['DIF'].tolist()[-1] > hour_macd_stock_df['DEA'].tolist()[-1]:
                                    print(pass_stock_data['股票代码'].tolist()[0])
                                    pass_stock_data_list.append(pass_stock_data['股票代码'].tolist()[0])
                    # print(len(DIF_temp))
                    # print(len(DEA_temp))
                    # print(pass_stock_data['股票代码'].tolist()[0])
                    # print(cal_DIF_down_through_DEA(DIF_temp, DEA_temp))

                    # pass_stock_data_list.append(pass_stock_data['股票代码'].tolist()[0])
        except:
            pass
    print('筛选后股票数量:', len(pass_stock_data_list))
    print(pass_stock_data_list)
    return pass_stock_data_list

    # df_combined = pass_stock_data_list[0]
    # for i in range(1,len(pass_stock_data_list)):
    #     # 使用 concat 合并它们
    #     df_combined = pd.concat([df_combined,pass_stock_data_list[i]], ignore_index=True)
    # print(df_combined)
    # df_combined.to_csv("stock_fliter_1.csv", index=False, encoding="utf-8-sig")
    # return code_list

def stock_fliter_2(spot_df,code):
    # 筛选特定股票代码 eg: spot_df_ret = stock_fliter_2(spot_df,'300418')
    spot_df_ret = spot_df[spot_df["代码"] == code]
    print('筛选后股票数量:', len(spot_df_ret))
    spot_df_ret.to_csv("stock_fliter_2.csv", index=False, encoding="utf-8-sig")
    return spot_df_ret

def cal_max_min(code,args_dic,spot_df):
    # 过去1年，最高价 /当前价 <max_high_now  且 最低价/当前价 >min_low_now  eg:# cal_max_min('000001',5,0.2)
    symbol = code
    stock_data = stock_filter_common_lib.stock_zh_a_hist_alex(symbol=symbol, period="daily", adjust='qfq').iloc[::-1]  # 数据按日期升序排列
    # print(stock_data.columns.tolist())
    close_price = stock_data['收盘'].tolist()
    max_price_dayily = stock_data['最高'].tolist()
    min_price_dayily = stock_data['最低'].tolist()

    # print(close_price[0:365])
    # print(len(close_price))
    # print(len(close_price[0:365]))
    # print(stock_data[stock_data["最低"] == 8.0])
    if len(close_price)>365:
        one_year_close_price = close_price[0:365]
        one_year_max_price_dayily = max_price_dayily[0:365]
        one_year_min_price_dayily = min_price_dayily[0:365]
    else:
        one_year_close_price = close_price
        one_year_max_price_dayily = max_price_dayily
        one_year_min_price_dayily = min_price_dayily
    #now_price = one_year_close_price[0] #历史数据分析
    now_price =  spot_df[spot_df["代码"] == code ]['最新价'].tolist()[0]#当前数据分析
    # print('code ',code,'now_price',now_price)
    max_price = max(one_year_max_price_dayily)
    min_price = min(one_year_min_price_dayily)
    # print(now_price,max_price,min_price)

    if max_price/now_price < args_dic['过去1年最高价比当前价比值上限'] and min_price/now_price >args_dic['过去1年最低价比当前价比值下限'] :
        # print(code)
        return stock_data
    else:
        return 0

def cal_DIF_down_through_DEA(DIF,DEA):
    down_through_index_list = []
    if len(DIF) != len(DEA):
        print('cal_DIF_down_through_DEA input error')
        down_through_index_list.append(99999)
        return down_through_index_list
    for i in range(1,len(DIF)-1): # kick off head and last
        if DIF[i-1]>DEA[i-1] and DIF[i+1]<DEA[i+1]:
            # print('down_through_index:',i)
            down_through_index_list.append(i)
    if len(down_through_index_list) == 0:
        print('no down_through_index')
    return down_through_index_list


def cal_DIF_DEA_MACD_period_len(code,period_len):
    # 获取指定股票的日线数据
    stock_code = code  # 这里替换成你想要查询的股票代码
    stock_data = ak.stock_zh_a_hist(symbol=stock_code, period=period_len, adjust="qfq")
    # stock_data = stock_filter_common_lib.stock_zh_a_hist_alex(symbol=stock_code, period=period_len, adjust="qfq")

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

def cal_DIF_DEA_MACD_time_len(code,time_len):
    # 获取指定股票的日线数据

    if time_len== "120":
        time_len_used = "60"
    else:
        time_len_used = time_len
    stock_data = ak.stock_zh_a_hist_min_em(symbol=code, period=time_len_used, adjust="qfq")
    # stock_data = stock_filter_common_lib.stock_zh_a_hist_min_em_alex(symbol=code, period=time_len_used, adjust="qfq")

    # print(stock_data)
    if time_len == "120":
        stock_data = stock_data.iloc[1::2]
        # print(stock_data)
    # 计算12小时和26小时的 EMA
    stock_data['EMA12'] = stock_data['收盘'].ewm(span=12, adjust=False).mean()
    stock_data['EMA26'] = stock_data['收盘'].ewm(span=26, adjust=False).mean()

    # 计算MACD
    stock_data['DIF'] = stock_data['EMA12'] - stock_data['EMA26']

    # 计算信号线（9日EMA）
    stock_data['DEA'] = stock_data['DIF'].ewm(span=9, adjust=False).mean()

    # 计算柱状图
    stock_data['MACD'] = 2 * (stock_data['DIF'] - stock_data['DEA'])

    # 输出结果
    # stock_data.to_csv("cal_DIF_DEA_MACD_time_len.csv", index=False, encoding="utf-8-sig")
    # DIF_list= stock_data['DIF'].tolist()
    # DEA_list= stock_data['DEA'].tolist()
    #
    # for index in range (-16,0):
    #     print(DIF_list[index])

    return stock_data
#
# def cal_DIF_DEA_MACD_time_len(code,time_len):
#     # 获取指定股票的日线数据
#     if code[0] == '3' and code[1] == '0':
#         stock_code = 'sz'+code  # 这里替换成你想要查询的股票代码
#     elif code[0] == '6' and code[1] == '0':
#         stock_code = 'sh'+code  # 这里替换成你想要查询的股票代码
#     elif code[0] == '6' and code[1] == '8':
#         stock_code = 'sh'+code  # 这里替换成你想要查询的股票代码
#     elif code[0] == '0' and code[1] == '0':
#         stock_code = 'sz'+code  # 这里替换成你想要查询的股票代码
#     else:
#         stock_code = 'bj' + code  # 这里替换成你想要查询的股票代码
#     if time_len== "120":
#         time_len_used = "60"
#     else:
#         time_len_used = time_len
#     stock_data = ak.stock_zh_a_minute(symbol=stock_code, period=time_len_used, adjust="qfq")
#     # print(stock_data)
#     if time_len == "120":
#         stock_data = stock_data.iloc[1::2]
#         # print(stock_data)
#     # 计算12小时和26小时的 EMA
#     stock_data['EMA12'] = stock_data['close'].ewm(span=12, adjust=False).mean()
#     stock_data['EMA26'] = stock_data['close'].ewm(span=26, adjust=False).mean()
#
#     # 计算MACD
#     stock_data['DIF'] = stock_data['EMA12'] - stock_data['EMA26']
#
#     # 计算信号线（9日EMA）
#     stock_data['DEA'] = stock_data['DIF'].ewm(span=9, adjust=False).mean()
#
#     # 计算柱状图
#     stock_data['MACD'] = 2 * (stock_data['DIF'] - stock_data['DEA'])
#
#     # 输出结果
#     # stock_data.to_csv("cal_DIF_DEA_MACD_time_len.csv", index=False, encoding="utf-8-sig")
#     # DIF_list= stock_data['DIF'].tolist()
#     # DEA_list= stock_data['DEA'].tolist()
#     #
#     # for index in range (-16,0):
#     #     print(DIF_list[index])
#
#     return stock_data

if __name__ == '__main__':
    print('stock_filter')

    args_dic={
        '最小市值': 100,
        '最小换手率': 5,
        '最大换手率': 20,
        '最小动态市盈率': 0,
        '近期判断天数': 7,#判断最近若干天的最大最小价格
        '近期超涨系数':1.25,#判断最近若干天的最大最小价格的最大倍速
        '次新股天数':60,
        '过去1年最高价比当前价比值上限': 5,
        '过去1年最低价比当前价比值下限': 0.2
    }
    # 获取所有指数的实时数据




    # dayliy_data_save()

    # stock_data_1min_hist = ak.stock_zh_a_hist_min_em(symbol='601919', period='120', start_date = "1979-09-01 09:32:00",adjust="qfq")
    # print(stock_data_1min_hist)
    # index_df = ak.stock_zh_index_spot_em()
    # print(len(index_df))
    # index_df.to_csv("stock_zh_index_spot_em.csv", index=False, encoding="utf-8-sig")
    # df_his = ak.index_zh_a_hist_min_em(symbol="000001", period='5')
    # print(df_his)
    # df_his.to_csv("index_zh_a_hist_min_em.csv", index=False, encoding="utf-8-sig")
    # df_his = ak.stock_zh_a_hist_min_em(symbol="002245", period="60",adjust='qfq')
    # df_his = stock_filter_common_lib.cal_DIF_DEA_MACD(df_his)
    # df_his.to_csv("002245.csv", index=False, encoding="utf-8-sig")
    # df=ak.fund_etf_spot_em()
    # df.to_csv("fund_etf_spot_em.csv", index=False, encoding="utf-8-sig")
    # fund_etf_hist_em_df = ak.fund_etf_hist_em(symbol="513500", period="daily", adjust="qfq")
    # print(fund_etf_hist_em_df)
    # spot_df = ak.stock_zh_a_spot_em()
    # print(spot_df['代码'].tolist())
    # print('所有股票数量:', len(spot_df))
    # pass_stock_data_list = stock_fliter_1(spot_df,args_dic)
    # stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(symbol="000001", period="60", adjust="qfq")
    # print(stock_zh_a_hist_min_em_df)
    # stock_data = cal_DIF_DEA_MACD_time_len("300133","120")
    # stock_data = cal_DIF_DEA_MACD_period_len('002335', 'weekly')
#todo 找到最近的两个，小时级 MACD 死叉点（DIF下穿DEA）在每个死叉点前后，包括本身找到5个交易小时的价格，并取最高值，如果第二个死叉点的最高价格 高于第前一个死叉点的最高价格，且，第二个死叉点DIF低于第一个死叉点，就叫顶背离，这种股票就需要剔除
