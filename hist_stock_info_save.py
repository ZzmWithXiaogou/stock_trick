
from stock_filter_common_lib import *

def df_hist_list_read(code_list):
    for item in code_list:
        # print(time.time())
        # stock_data_1min_hist = ak.stock_zh_a_hist_min_em(symbol=str(item), period='1', adjust="qfq")
        # stock_data_1min_hist.tail(run_time_args_dic['历史数据缓存长度1min']).to_csv(run_time_args_dic['历史数据存储路径']+"/df_1min_hist_list_"+str(item)+".csv", index=False, encoding="utf-8-sig")

        stock_data_5min_hist = ak.stock_zh_a_hist_min_em(symbol=str(item), period='5', adjust="qfq")
        stock_data_5min_hist.tail(run_time_args_dic['历史数据缓存长度5min']).to_csv(run_time_args_dic['历史数据存储路径']+"/df_5min_hist_list_"+str(item)+".csv", index=False, encoding="utf-8-sig")

        stock_data_15min_hist = ak.stock_zh_a_hist_min_em(symbol=str(item), period='15', adjust="qfq")
        stock_data_15min_hist.tail(run_time_args_dic['历史数据缓存长度15min']).to_csv(run_time_args_dic['历史数据存储路径'] + "/df_15min_hist_list_" + str(item) + ".csv",index=False, encoding="utf-8-sig")

        stock_data_30min_hist = ak.stock_zh_a_hist_min_em(symbol=str(item), period='30', adjust="qfq")
        stock_data_30min_hist.tail(run_time_args_dic['历史数据缓存长度30min']).to_csv(
            run_time_args_dic['历史数据存储路径'] + "/df_30min_hist_list_" + str(item) + ".csv", index=False,
            encoding="utf-8-sig")

        stock_data_60min_hist = ak.stock_zh_a_hist_min_em(symbol=str(item), period='60', adjust="qfq")
        stock_data_60min_hist.tail(run_time_args_dic['历史数据缓存长度60min']).to_csv(
            run_time_args_dic['历史数据存储路径'] + "/df_60min_hist_list_" + str(item) + ".csv", index=False,
            encoding="utf-8-sig")

        stock_data_120min_hist = ak.stock_zh_a_hist_min_em(symbol=str(item), period='120', adjust="qfq")
        stock_data_120min_hist.tail(run_time_args_dic['历史数据缓存长度120min']).to_csv(
            run_time_args_dic['历史数据存储路径'] + "/df_120min_hist_list_" + str(item) + ".csv", index=False,
            encoding="utf-8-sig")

        # print(time.time())

def index_hist_list_read(index_list):
    for item in index_list:
        stock_data_1min_hist = ak.index_zh_a_hist_min_em(symbol=str(item), period='1')
        # print(len(stock_data_1min_hist))
        # print(stock_data_1min_hist['时间'].tolist())
        # fliter_df = stock_data_1min_hist[('09:30:00' in stock_data_1min_hist['时间'])]
        # print(fliter_df)
        # 假设 df 是您的 DataFrame，'时间' 列包含日期时间字符串
        stock_data_1min_hist['时间'] = stock_data_1min_hist['时间'].astype(str)  # 将 '时间' 列转换为字符串类型

        stock_data_15min_hist = stock_data_1min_hist[stock_data_1min_hist['时间'].str.contains(r'09:45:00|10:00:00|10:15:00|10:30:00|10:45:00|11:00:00|11:15:00|11:30:00|13:15:00|13:30:00|13:45:00|14:00:00|14:15:00|14:30:00|14:45:00|15:00:00')]
        stock_data_30min_hist = stock_data_1min_hist[stock_data_1min_hist['时间'].str.contains(r'10:00:00|10:30:00|11:00:00|11:30:00|13:30:00|14:00:00|14:30:00|15:00:00')]
        stock_data_60min_hist = stock_data_1min_hist[stock_data_1min_hist['时间'].str.contains(r'10:30:00|11:30:00|14:00:00|15:00:00')]
        stock_data_120min_hist = stock_data_1min_hist[stock_data_1min_hist['时间'].str.contains(r'11:30:00|15:00:00')]

        filtered_df = stock_data_1min_hist[~stock_data_1min_hist['时间'].str.contains('09:30:00')]
        stock_data_5min_hist = filtered_df[filtered_df['时间'].str.contains(r'5:00|0:00')]

        # 查看筛选后的结果
        # print(stock_data_5min_hist)
        # stock_data_1min_hist.to_csv(
        #     run_time_args_dic['历史数据存储路径'] + "/dfindex_1min_hist_list_" + str(item) + ".csv", index=False,
        #     encoding="utf-8-sig")
        # stock_data_1min_hist.tail(run_time_args_dic['历史数据缓存长度1min']).to_csv(
        #     run_time_args_dic['历史数据存储路径'] + "/dfindex_1min_hist_list_" + str(item) + ".csv", index=False,
        #     encoding="utf-8-sig")


        #
        # stock_data_5min_hist = ak.index_zh_a_hist_min_em(symbol=str(item), period='5')
        stock_data_5min_hist.tail(run_time_args_dic['历史数据缓存长度5min']).to_csv(
            run_time_args_dic['历史数据存储路径'] + "/dfindex_5min_hist_list_" + str(item) + ".csv", index=False,
            encoding="utf-8-sig")
        #
        # stock_data_15min_hist = ak.index_zh_a_hist_min_em(symbol=str(item), period='15')
        stock_data_15min_hist.tail(run_time_args_dic['历史数据缓存长度15min']).to_csv(
            run_time_args_dic['历史数据存储路径'] + "/dfindex_15min_hist_list_" + str(item) + ".csv", index=False,
            encoding="utf-8-sig")
        #
        # stock_data_30min_hist = ak.index_zh_a_hist_min_em(symbol=str(item), period='30')
        stock_data_30min_hist.tail(run_time_args_dic['历史数据缓存长度30min']).to_csv(
            run_time_args_dic['历史数据存储路径'] + "/dfindex_30min_hist_list_" + str(item) + ".csv", index=False,
            encoding="utf-8-sig")
        #
        # stock_data_60min_hist = ak.index_zh_a_hist_min_em(symbol=str(item), period='60')
        stock_data_60min_hist.tail(run_time_args_dic['历史数据缓存长度60min']).to_csv(
            run_time_args_dic['历史数据存储路径'] + "/dfindex_60min_hist_list_" + str(item) + ".csv", index=False,
            encoding="utf-8-sig")
        #
        # stock_data_120min_hist = ak.index_zh_a_hist_min_em(symbol=str(item), period='120')
        stock_data_120min_hist.tail(run_time_args_dic['历史数据缓存长度120min']).to_csv(
            run_time_args_dic['历史数据存储路径'] + "/dfindex_120min_hist_list_" + str(item) + ".csv", index=False,
            encoding="utf-8-sig")







if __name__ == '__main__':
    print('hist_stock_info_save')

    # trad_time_check()

    #step1 读取代码列表
    file_path =run_time_args_dic['代码列表路径']
    print(file_path)
    code_list = code_list_read(file_path)

    clear_dataframe_path(run_time_args_dic['历史数据存储路径'])


    df_hist_list_read(code_list)

    index_list=['000001']
    index_hist_list_read(index_list)


