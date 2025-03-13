import akshare as ak
import pandas as pd
import numpy as np
import multiprocessing as mp
from datetime import datetime, timedelta,date
import time
import os
import feisu_robot
import logging
import matplotlib.pyplot as plt
import mplcursors
import talib as ta #https://ta-lib.org/install/ 先安装msi，然后 pip install ta-lib
import backtrader as bt
import requests
import stock_filter
import excel_handle
from openpyxl import Workbook, load_workbook
from functools import lru_cache
import pybroker
import random
import traceback
import sys



run_time_args_dic = {
        '代码列表路径': r'C:\Users\Administrator\Desktop\趋势票模板.xlsx',
        '历史数据缓存长度1min': 100,
        '历史数据缓存长度5min': 100,
        '历史数据缓存长度15min': 100,
        '历史数据缓存长度30min': 100,
        '历史数据缓存长度60min': 100,
        '历史数据缓存长度120min': 100,
        '历史数据存储路径':'dataframe',
        '临时数据': '临时数据',
        '每日数据': '每日数据',
        'debug_mode': 0,
        'A股早盘开盘时': 9,
        'A股早盘开盘分': 30,
        'A股早盘收盘时': 11,
        'A股早盘收盘分': 30,
        'A股午盘开盘时': 13,
        'A股午盘开盘分': 0,
        'A股收盘时': 15,
        'A股收盘分': 0,
        'reply_mode': 0,
        '最大重试次数': 2
    }

eval_arg_dic_small = {
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
        '输出表格': r'C:\Users\Administrator\Desktop\导入模板.xlsx',
        'debug_mode': 0  # 0 常规模式，支持当日日期，快速筛选，以及历史日期全量筛选  1 屏蔽掉当日快速筛选功能
    }



eval_arg_dic_large = {
        'arg_type':1,
        '最小市值': 400,  # symbol_value
        '最大市值': 2000,  # symbol_value
        '最小换手率': 1,  # symbol_tr
        '最大换手率': 10,  # symbol_tr
        '最小动态市盈率': 0,  # symbol_ttm
        '最大动态市盈率': 50,  # symbol_ttm
        '近期判断天数': 7,  # 判断最近若干天的最大最小价格--不要了
        '近期超涨系数': 999999,  # 判断最近若干天的最大最小价格的最大倍速--不要了
        '次新股天数': 60,  # symbol_trade_days
        '过去1年最高价比当前价比值上限': 2,
        '过去1年最低价比当前价比值下限': 0.2,
        '月线死叉': 1,
        '周线死叉': 1,
        '日线死叉': 1,
        '最大5日乖离率': 99999,#百分比，当前收盘价和移动平均价的溢价率
        '最小5日乖离率': -99999,
        '最大10日乖离率': 3,
        '最小10日乖离率': -99999,
        '60日最大涨幅': 100,  # symbol_change_60_day
        '成交量比率，上涨时下限': 1.2,  # 成交量比率（VR）= 当日成交量/20日均量  主力介入信号：价格上涨时VR>1.5，下跌时VR<0.7（主力吸筹特征）
        '成交量比率，下跌时上限': 0.7,
        '输出表格': r'C:\Users\Administrator\Desktop\导入模板_大市值.xlsx',
        'debug_mode': 0  # 0 常规模式，支持当日日期，快速筛选，以及历史日期全量筛选  1 屏蔽掉当日快速筛选功能
    }

#todo
#买卖盘
#筹码分布
def cal_vr_ontime(df,stock_code,stock_name,stock_fenshi,vr_days,large_vr,small_vr): #根据输入的5min分时数据计算过去5天同一个分时的量比
    time_ = df.iloc[-1, df.columns.get_loc('时间')]
    time_str = time_.split(' ')[1]
    # print(time_str)
    # stock_data_935_hist = stock_data_5min_hist[stock_data_5min_hist['时间'].str.contains(r'09:50:00')]
    handle_df = df[df['时间'].str.contains(time_str)]
    if len(handle_df)<vr_days:
        return 0
    vr = cal_VR(handle_df, vr_days)
    symbol_delta = handle_df.iloc[-1, handle_df.columns.get_loc('涨跌幅')]
    close = handle_df.iloc[-1, handle_df.columns.get_loc('收盘')]
    # print(vr, time_, symbol_delta,stock_name,stock_name,stock_fenshi)
    if vr > large_vr:
        # print(vr,time_,symbol_delta)
        vr = round(vr, 3 - len(str(int(vr))))
        info_message = time_ + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name +" "+stock_fenshi+"min分时级别" + " 成交量强势突破，量比：" + str(vr) + " 涨跌幅：" + str(symbol_delta) +" 成交价："+str(close)
        print_and_log(info_message)
        message = {
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": info_message
            }
        }
        feisu_robot.robot_send_with_fenshi(stock_fenshi+'vr', message)
    if vr > small_vr and vr <=large_vr:
        # print(vr,time_,symbol_delta)
        vr = round(vr, 3 - len(str(int(vr))))
        info_message = time_ + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name +" "+stock_fenshi+"min分时级别" + " 成交量温和放大，量比：" + str(vr) + " 涨跌幅：" + str(symbol_delta) +" 成交价："+str(close)
        print_and_log(info_message)
        message = {
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": info_message
            }
        }
        feisu_robot.robot_send_with_fenshi(stock_fenshi+'vr', message)
def cal_VR(df,days):
    df = df.copy()
    df = df.tail(days)
    trade_list = df['成交量'].tolist()
    if len(trade_list) == 0:
        return -99  # 防止除以零错误
    last_trade = trade_list[-1]
    average_trade = sum(trade_list) / len(trade_list)
    vr =last_trade/average_trade
    return vr

def cal_VR_df(df,days):
    df = df.copy()
    df_len = len(df)
    if df_len < days:
        print('输入dataframe长度不足')
        return df
    df['过去'+str(days)+'周期平均成交量'] = df['成交量'].rolling(window=days).mean()
    # 计算当日成交量与过去5日成交量均值的比值
    df['过去'+str(days)+'周期量比'] = df['成交量'] / df['过去'+str(days)+'周期平均成交量']
    return df

def cal_BIAS(days,df):
    df = df.copy()
    df = df.tail(days)

    close_list = df['收盘'].tolist()
    if len(close_list) == 0:
        return -99  # 防止除以零错误
    sma = sum(close_list) / len(close_list)
    close_last = close_list[-1]
    bias =100* (close_last-sma)/sma
    return bias

def cal_BIAS_df(df,days):
    df = df.copy()
    df_len = len(df)
    if df_len < days:
        print('输入dataframe长度不足')
        return df
    # 计算5日均价
    df['ma_'+str(days)] = df['收盘'].rolling(window=days).mean()
    # 计算5日 BIAS
    df['bias_'+str(days)] = (df['收盘'] - df['ma_'+str(days)]) / df['ma_'+str(days)] * 100
    return df

def cal_DIF_DEA_MACD(stock_data):
    stock_data = stock_data.copy()
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


def detect_macd_cross(df):
    """
    计算MACD金叉和死叉，并在DataFrame中标记。

    参数：
    df: pandas.DataFrame，必须包含 "DIF" 和 "DEA" 列

    返回：
    带有 "golden_cross" 和 "death_cross" 两列的 DataFrame
    """
    df = df.copy()  # 避免修改原始DataFrame

    # 创建金叉、死叉的标记列，初始化为0
    df['golden_cross'] = 0
    df['death_cross'] = 0
    # 计算金叉 (DIF 由下向上穿过 DEA)
    df.loc[(df['DIF'].shift(1) < df['DEA'].shift(1)) & (df['DIF'] > df['DEA']), 'golden_cross'] = 1

    # 计算死叉 (DIF 由上向下穿过 DEA)
    df.loc[(df['DIF'].shift(1) > df['DEA'].shift(1)) & (df['DIF'] < df['DEA']), 'death_cross'] = 1

    return df


def list_files_in_directory(directory):
    # 获取目录中的所有文件和文件夹
    all_items = os.listdir(directory)

    # 过滤出文件
    files = [item for item in all_items if os.path.isfile(os.path.join(directory, item))]

    return files


def cal_DIF_up_through_DEA(stock_data):
    DIF_last = stock_data.iloc[-2, stock_data.columns.get_loc('DIF')]
    DIF_now = stock_data.iloc[-1, stock_data.columns.get_loc('DIF')]
    DEA_last = stock_data.iloc[-2, stock_data.columns.get_loc('DEA')]
    DEA_now = stock_data.iloc[-1, stock_data.columns.get_loc('DEA')]

    if DIF_now < DEA_now:
        return 0
    else:
        if DIF_last <= DEA_last:
            return 1 #up through
        else:
            return 0

def cal_DEA_up_through_DIF(stock_data):
    DIF_last = stock_data.iloc[-2, stock_data.columns.get_loc('DIF')]
    DIF_now = stock_data.iloc[-1, stock_data.columns.get_loc('DIF')]
    DEA_last = stock_data.iloc[-2, stock_data.columns.get_loc('DEA')]
    DEA_now = stock_data.iloc[-1, stock_data.columns.get_loc('DEA')]

    if DIF_now > DEA_now:
        return 0
    else:
        if DIF_last >= DEA_last:
            return 1 #up through
        else:
            return 0


def cal_new_hightest(stock_data,df,file):
    stock_code = file.split('_')[4]
    stock_name = file.split('_')[5]
    stock_fenshi = file.split('_')[1].split('min')[0]
    stock_data = stock_data.copy()
    # 找到最后一行索引（最新数据的索引）
    last_index = stock_data.index[-1]

    # 找到最新数据之前最近的死叉索引
    death_cross_indices = stock_data.index[stock_data['death_cross'] == 1].tolist()
    death_cross_idx = max([idx for idx in death_cross_indices if idx < last_index], default=None)

    # 找到最近的死叉索引之前最近的金叉索引
    golden_cross_indices = stock_data.index[stock_data['golden_cross'] == 1].tolist()
    golden_cross_idx = max([idx for idx in golden_cross_indices if idx < death_cross_idx], default=None)
    # print(death_cross_idx)
    last_golden_df = stock_data.loc[golden_cross_idx:death_cross_idx-1]  #从最近的死叉索引之前最近的金叉索引开始，到最近的死叉索引之前一个数据之间的完整df


    max_value = last_golden_df['最高'].max()  # 获取最大值
    max_index = last_golden_df['最高'].idxmax()  # 获取最大值所在的索引(该索引为完整df中的索引）
    max_DEA = last_golden_df["DEA"].iloc[-1]# 获取最大DEA，死叉之前的最近一个点

    last_max =  df["最高"].iloc[-1]#获取最新最高值
    last_DEA = stock_data["DEA"].iloc[-1] #获取最新DEA
    last_MACD = stock_data["MACD"].iloc[-1] #获取最新MACD



    # '价格破前高，黄线没有新高'，只要满足高点条件，就打上高点标签
    if last_max > max_value : ##条件:最新的最高价大于前高
        if last_DEA < max_DEA:##条件:最新的DEA小于前高的的DEA
            info_message = df["时间"].iloc[-1]+" 股票代码:  "+stock_code+" 股票名称:  "+stock_name+" "+stock_fenshi+"min分时级别，价格破前高，黄线没有新高"
            print_and_log(info_message)
            stock_data.iloc[-1, stock_data.columns.get_loc("顶背离")] = '价格破前高，黄线没有新高'
            message = {
                "msg_type": "text",  # 消息类型，这里是文本
                "content": {
                    "text": info_message +' 顶背离参考' # 消息内容
                }
            }
            # if stock_fenshi !='5':
            #     # feisu_robot.robot_send(message)
            #     feisu_robot.robot_send_with_fenshi(stock_fenshi,message)


    # '价格反转!!!!!'
    # 价格在破前高的基础上，因为上面已经计算了最新的最高价有没有破前高，所以只有两种情况
    # 1.当前分时仍然是前高，2.当前分时已经下跌低于前高，但是MACD还没有翻转到前高的MACD之下，此时会被打上Nothing，此时也不满足价格反转!!!!!，所以先不考虑2
    if stock_data["顶背离"].iloc[-1] == '价格破前高，黄线没有新高': # 价格在破前高的基础上
        if last_max <= max_value:#最低价下跌到前高之下
            if last_DEA < max_DEA:#DEA 仍然低于前高的DEA
                info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，顶背离价格反转!!!!!"
                print_and_log(info_message)
                stock_data.iloc[-1, stock_data.columns.get_loc("顶背离")] = '顶背离价格反转!!!!!'
                message = {
                    "msg_type": "text",  # 消息类型，这里是文本
                    "content": {
                        "text": info_message +' 顶背离参考' # 消息内容
                    }
                }
                # feisu_robot.robot_send(message)
                feisu_robot.robot_send_with_fenshi(stock_fenshi, message)

    # '价格反转后死叉!!!!!'
    #情况1，#反转和死叉在同一个分时
    if stock_data["顶背离"].iloc[-1] == '顶背离价格反转!!!!!' and stock_data["MACD"].iloc[-1]<0: #反转和死叉在同一个分时
        info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，顶背离价格反转后死叉!!!!!"
        print_and_log(info_message)
        stock_data.iloc[-1, stock_data.columns.get_loc("顶背离")] = '顶背离价格反转后死叉!!!!!'
        message = {
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": info_message  +' 顶背离参考'# 消息内容
            }
        }
        # feisu_robot.robot_send(message)
        feisu_robot.robot_send_with_fenshi(stock_fenshi, message)

    # 情况2，#反转和死叉不在同一个分时
    # 找到最新数据之前最近的价格反转索引
    redrop_indices = stock_data.index[stock_data['顶背离'] == '顶背离价格反转!!!!!'].tolist()
    redrop_idx = max([idx for idx in redrop_indices if idx < last_index], default=None)

    #只需要考虑最新分时出现死叉的，不出现就一直是金叉等待死叉
    if redrop_idx != None and stock_data["death_cross"].iloc[-1] == 1:  #反转出现了，死叉在最新分时
        info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，顶背离价格反转后死叉!!!!!"
        print_and_log(info_message)
        stock_data.iloc[-1, stock_data.columns.get_loc("顶背离")] = '顶背离价格反转后死叉!!!!!'
        message = {
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": info_message +' 顶背离参考' # 消息内容
            }
        }
        # feisu_robot.robot_send(message)
        feisu_robot.robot_send_with_fenshi(stock_fenshi, message)
    #'价格反转后死叉!!!!!' 之后，新的死叉索引会被更新，新的高点也会被找到，所以整个数据实现循环处理

    return stock_data




def cal_new_lowest(stock_data,df,file):
    stock_code = file.split('_')[4]
    stock_name = file.split('_')[5]
    stock_fenshi = file.split('_')[1].split('min')[0]
    stock_data = stock_data.copy()
    # 找到最后一行索引（最新数据的索引）
    last_index = stock_data.index[-1]
    # 找到最新数据之前最近的金叉索引
    golden_cross_indices = stock_data.index[stock_data['golden_cross'] == 1].tolist()
    golden_cross_idx = max([idx for idx in golden_cross_indices if idx < last_index], default=None)
    # print(golden_cross_idx)

    if golden_cross_idx!=None:
        # 找到最近的金叉索引之前最近的死叉索引
        death_cross_indices = stock_data.index[stock_data['death_cross'] == 1].tolist()
        death_cross_idx = max([idx for idx in death_cross_indices if idx < golden_cross_idx], default=None)
    else:
        info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，未发现前序金叉"
        print_and_log(info_message)
        return stock_data
    # print(death_cross_idx)
    if death_cross_idx!=None:
        last_death_df = stock_data.loc[death_cross_idx:golden_cross_idx-1]  #从最近的金叉索引之前最近的死叉索引开始，到最近的金叉索引之前一个数据之间的完整df
    else:
        info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，未发现前序金叉之前的死叉"
        print_and_log(info_message)
        return stock_data
    # print(last_death_df)
    min_value = last_death_df['最低'].min()  # 获取最小值
    min_index = last_death_df['最低'].idxmin()  # 获取最小值所在的索引(该索引为完整df中的索引）
    min_DEA = last_death_df["DEA"].iloc[-1]# 获取最小DEA,金叉之前的最近一个点

    # last_min = min(stock_data["最低"].iloc[-1], df["最低"].iloc[-1])#获取最新最小值
    last_min =  df["最低"].iloc[-1]#获取最新最小值
    last_DEA = stock_data["DEA"].iloc[-1] #获取最新DEA
    last_MACD = stock_data["MACD"].iloc[-1] #获取最新MACD




    # '价格破前低，黄线没有新低'，只要满足低点条件，就打上低点标签

    if last_min < min_value : ##条件:最新的最低价小于前低
        if last_DEA > min_DEA:##条件:最新的DEA大于前低的的DEA
            info_message = df["时间"].iloc[-1]+" 股票代码:  "+stock_code+" 股票名称:  "+stock_name+" "+stock_fenshi+"min分时级别，价格破前低，黄线没有新低"+"   前低时间:"+stock_data["时间"].iloc[min_index]
            print_and_log(info_message)
            stock_data.iloc[-1, stock_data.columns.get_loc("底背离")] = '价格破前低，黄线没有新低'
            message = {
                "msg_type": "text",  # 消息类型，这里是文本
                "content": {
                    "text": info_message +' 底背离参考' # 消息内容
                }
            }
            if stock_fenshi !='5':
                feisu_robot.robot_send(message)
                feisu_robot.robot_send_with_fenshi(stock_fenshi, message)


    # '价格反转!!!!!'
    # 价格在破前低的基础上，因为上面已经计算了最新的最低价有没有破前低，所以只有两种情况
    # 1.当前分时仍然是前低，2.当前分时已经回升超过前低，但是MACD还没有翻转到前低的MACD之上，此时会被打上Nothing，此时也不满足价格反转!!!!!，所以先不考虑2
    if stock_data["底背离"].iloc[-1] == '价格破前低，黄线没有新低': # 价格在破前低的基础上
        if last_min >= min_value:#最低价回升到前低之上
            if last_DEA > min_DEA:#DEA 仍然高于前低的DEA
                info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，底背离反转价格!!!!!"+"   前低时间:"+stock_data["时间"].iloc[min_index]
                print_and_log(info_message)
                stock_data.iloc[-1, stock_data.columns.get_loc("底背离")] = '底背离反转价格!!!!!'
                message = {
                    "msg_type": "text",  # 消息类型，这里是文本
                    "content": {
                        "text": info_message +' 底背离参考' # 消息内容
                    }
                }
                # feisu_robot.robot_send(message)
                feisu_robot.robot_send_with_fenshi(stock_fenshi, message)





    if stock_data["底背离"].iloc[-1] == '底背离反转价格!!!!!':   #当前周期价格翻转状态下
        if last_min < min_value or last_DEA < min_DEA:   #最低价小于前低 或者dea掉到前面那个比较的dea之下
            stock_data['底背离'] = 'Nothing'
            info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，底背破坏"+"   前低时间:"+stock_data["时间"].iloc[min_index]
            print_and_log(info_message)
            message = {
                "msg_type": "text",  # 消息类型，这里是文本
                "content": {
                    "text": info_message+' 底背离参考'  # 消息内容
                }
            }
            # feisu_robot.robot_send(message)
            feisu_robot.robot_send_with_fenshi(stock_fenshi, message)


    # '价格反转后金叉!!!!!'
    #情况1，#反转和金叉在同一个分时
    if stock_data["底背离"].iloc[-1] == '底背离反转价格!!!!!' and stock_data["MACD"].iloc[-1]>0: #反转和金叉在同一个分时
        info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，底背离价格反转后金叉!!!!!"+"   前低时间:"+stock_data["时间"].iloc[min_index]
        print_and_log(info_message)
        stock_data.iloc[-1, stock_data.columns.get_loc("底背离")] = '底背离价格反转后金叉!!!!!'
        message = {
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": info_message +' 底背离参考' # 消息内容
            }
        }
        # feisu_robot.robot_send(message)
        feisu_robot.robot_send_with_fenshi(stock_fenshi, message)

    # 情况2，#反转和金叉不在同一个分时
    # 找到最新数据之前最近的价格反转索引
    reraise_indices = stock_data.index[stock_data['底背离'] == '底背离反转价格!!!!!'].tolist()
    reraise_idx = max([idx for idx in reraise_indices if idx < last_index], default=None)

    # 找到最近数据之前最近的死叉索引
    death_cross_indices_tolast = stock_data.index[stock_data['death_cross'] == 1].tolist()
    death_cross_idx_tolast = max([idx for idx in death_cross_indices if idx < last_index], default=None)

    if reraise_idx != None and death_cross_idx_tolast!=None:
        if death_cross_idx_tolast>=reraise_idx:#如果价格翻转索引当前或之后出现了死叉，认为上一个底背离破坏
            stock_data['底背离'] = 'Nothing'
            info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，底背破坏，如果价格翻转索引当前或之后出现了死叉，认为上一个底背离破坏"+"   前低时间:"+stock_data["时间"].iloc[min_index]
            print_and_log(info_message)
            message = {
                "msg_type": "text",  # 消息类型，这里是文本
                "content": {
                    "text": info_message+' 底背离参考'  # 消息内容
                }
            }
            # feisu_robot.robot_send(message)
            feisu_robot.robot_send_with_fenshi(stock_fenshi, message)
            reraise_idx = None

    if reraise_idx != None:  #前序周期价格翻转状态下
        if last_min < min_value or last_DEA < min_DEA:   #最低价小于前低 或者dea掉到前面那个比较的dea之下
            stock_data['底背离'] = 'Nothing'
            info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，底背破坏，前序周期价格翻转状态下，最低价小于前低 或者dea掉到前面那个比较的dea之下"+"   前低时间:"+stock_data["时间"].iloc[min_index]
            print_and_log(info_message)
            message = {
                "msg_type": "text",  # 消息类型，这里是文本
                "content": {
                    "text": info_message+' 底背离参考'  # 消息内容
                }
            }
            # feisu_robot.robot_send(message)
            feisu_robot.robot_send_with_fenshi(stock_fenshi, message)
            reraise_idx = None
    #只需要考虑最新分时出现金叉的，不出现就一直是死叉等待金叉
    if reraise_idx != None and stock_data["golden_cross"].iloc[-1] == 1:  #反转出现了，金叉在最新分时
        info_message = df["时间"].iloc[-1] + " 股票代码:  " + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + "min分时级别，底背离价格反转后金叉!!!!!"+"   前低时间:"+stock_data["时间"].iloc[min_index]
        print_and_log(info_message)
        stock_data.iloc[-1, stock_data.columns.get_loc("底背离")] = '底背离价格反转后金叉!!!!!'
        message = {
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": info_message+' 底背离参考'  # 消息内容
            }
        }
        # feisu_robot.robot_send(message)
        feisu_robot.robot_send_with_fenshi(stock_fenshi, message)
    #'价格反转后金叉!!!!!' 之后，新的金叉索引会被更新，新的低点也会被找到，所以整个数据实现循环处理

    # if stock_data["底背离"].iloc[-1] == '底背离反转价格!!!!!':
    #     if stock_fenshi == '30':
    #         file_5min = run_time_args_dic['历史数据存储路径'] + '/' + 'df_5min_hist_list_' + stock_code + '_' + stock_name + '_.csv'
    #         df_5min = pd.read_csv(file_5min)
    #         if df["底背离"].iloc[-1] == '底背离价格反转后金叉!!!!!':  # 5min级别最新分时金叉
    #
    #

    return stock_data


def time_wait(hour,minute):
    while 1:
        time.sleep(1)
        print(f"当前时间: {datetime.now().hour}:{datetime.now().minute}")
        if datetime.now().hour == hour and datetime.now().minute >= minute:
            if hour == 9:
                print("到点啦，开盘啦")
                message = {
                    "msg_type": "text",  # 消息类型，这里是文本
                    "content": {
                        "text": "到点啦，开盘啦"  # 消息内容
                    }
                }
                feisu_robot.robot_send(message)
            break

def print_and_log(str1):
    print(str1)
    logging.info(str1)


def clear_dataframe_path(dir_path):
    # 遍历文件夹内的所有文件
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):  # 仅删除文件，不删除文件夹
            os.remove(file_path)

    print("所有文件已删除")



def code_list_read(file_path):
    code_list = []
    df = pd.read_excel(file_path)
    column_names = df.columns.tolist()
    code_list.append(column_names[0])
    column_data = df.iloc[:, 0].tolist()
    for item in column_data:
        if len(str(item)) == 6:
            # print(item)
            code_list.append(str(item))
        else:
            delta = 6-len(str(item))
            zero_plugin = ''
            for i in range(0,delta):
                zero_plugin = zero_plugin + '0'
            new_item = zero_plugin + str(item)
            code_list.append(new_item)
    print(code_list)
    return code_list

def trad_time_check():
    if run_time_args_dic['debug_mode'] == 1:
        print('debug_mode，跳过校验')
        return 1
    if datetime.now().hour < run_time_args_dic['A股早盘开盘时'] or datetime.now().hour > run_time_args_dic['A股收盘时'] :
        return 0
    if datetime.now().hour == 11 and datetime.now().minute>31:
        return 0
    if datetime.now().hour == 12 :
        return 0
    if datetime.now().hour == run_time_args_dic['A股早盘开盘时'] and datetime.now().minute<=29 :
        return 0
    if datetime.now().hour == 15 and datetime.now().minute>1:
        return 0
    return 1

def dayliy_data_save():
    now_date = str(datetime.now().year)+'_'+str(datetime.now().month)+'_'+str(datetime.now().day)
    print_and_log('执行日期:'+now_date)
    stock_zh_a_spot_em = ak.stock_zh_a_spot_em()
    stock_zh_a_spot_em.to_csv(run_time_args_dic['每日数据']+"/"+now_date+"_每日A股市场股票全貌.csv", index=False, encoding="utf-8-sig")
    stock_zh_index_spot_em = ak.stock_zh_index_spot_em()
    stock_zh_index_spot_em.to_csv(run_time_args_dic['每日数据']+"/"+now_date+"_每日A股市场指数全貌.csv", index=False, encoding="utf-8-sig")

    # fatherpath = run_time_args_dic['每日数据']+"/"+now_date
    # # 创建文件夹（如果不存在的话）
    # if not os.path.exists(fatherpath):
    #     os.makedirs(fatherpath)
    #     print(f"文件夹 {fatherpath} 创建成功")
    # else:
    #     print(f"文件夹 {fatherpath} 已经存在")
    #
    # stock_code_list = stock_zh_a_spot_em['代码'].tolist()
    # stock_path= fatherpath+ "/stock"
    # if not os.path.exists(stock_path):
    #     os.makedirs(stock_path)
    #     print(f"文件夹 {stock_path} 创建成功")
    # else:
    #     print(f"文件夹 {stock_path} 已经存在")
    # index_code_list = stock_zh_index_spot_em['代码'].tolist()
    # index_path= fatherpath+ "/index"
    # if not os.path.exists(index_path):
    #     os.makedirs(index_path)
    #     print(f"文件夹 {index_path} 创建成功")
    # else:
    #     print(f"文件夹 {index_path} 已经存在")
    # # print(index_code_list)
    # for item in stock_code_list:
    #     stock_zh_a_hist_1min_em = ak.stock_zh_a_hist_min_em(symbol=str(item), period='1', adjust="qfq")
    #     # stock_zh_a_hist_5min_em = ak.stock_zh_a_hist_min_em(symbol=str(item), period='5', adjust="qfq")
    #     # stock_zh_a_hist_15min_em = ak.stock_zh_a_hist_min_em(symbol=str(item), period='15', adjust="qfq")
    #     # stock_zh_a_hist_30min_em = ak.stock_zh_a_hist_min_em(symbol=str(item), period='30', adjust="qfq")
    #     # stock_zh_a_hist_60min_em = ak.stock_zh_a_hist_min_em(symbol=str(item), period='60', adjust="qfq")
    #     # stock_zh_a_hist_120min_em = ak.stock_zh_a_hist_min_em(symbol=str(item), period='120', adjust="qfq")
    #     stock_zh_a_hist_1min_em.to_csv(stock_path+"/df_1min_hist_"+str(item)+".csv", index=False, encoding="utf-8-sig")
    #     # stock_zh_a_hist_5min_em.to_csv(stock_path+"/df_5min_hist_"+str(item)+".csv", index=False, encoding="utf-8-sig")
    #     # stock_zh_a_hist_15min_em.to_csv(stock_path+"/df_15min_hist_"+str(item)+".csv", index=False, encoding="utf-8-sig")
    #     # stock_zh_a_hist_30min_em.to_csv(stock_path+"/df_30min_hist_"+str(item)+".csv", index=False, encoding="utf-8-sig")
    #     # stock_zh_a_hist_60min_em.to_csv(stock_path+"/df_60min_hist_"+str(item)+".csv", index=False, encoding="utf-8-sig")
    #     # stock_zh_a_hist_120min_em.to_csv(stock_path+"/df_120min_hist_"+str(item)+".csv", index=False, encoding="utf-8-sig")

def BIAS_test(symbol,raise_date):
    stock_data = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust="qfq",start_date = "19700101",end_date = raise_date)
    print(stock_data)
    print('代码：'+symbol)
    print('6日bias：'+str(cal_BIAS(6, stock_data)))
    print('12日bias：'+str(cal_BIAS(12, stock_data)))
    print('24日bias：'+str(cal_BIAS(24, stock_data)))


#
# import requests
# from datetime import datetime
# import json
#     #alex 离线给与codeid
#     if 9<=datetime.now().hour<=16: #交易时间使用离线json
#         with open("code_id_dict.json", "r", encoding="utf-8") as f:
#             code_id_dict_alex = json.load(f)
#         return code_id_dict_alex
#
#
#     # 将字典保存为 JSON 文件
#     with open("code_id_dict.json", "w", encoding="utf-8") as f:
#         json.dump(code_id_dict, f, ensure_ascii=False, indent=4)
#
#     return code_id_dict


if __name__ == '__main__':
    print('common_lib')
    # dayliy_data_save()

    # detect_bullish_divergence(pd.read_csv(run_time_args_dic['历史数据存储路径'] + '/df_30min_hist_list_002245_蔚蓝锂芯_.csv'))

    # directory = run_time_args_dic['历史数据存储路径']
    # files = list_files_in_directory(directory)
    # print(files)
    # for file in files:
    #     find_Bullish_Divergence(file,pd.read_csv(run_time_args_dic['历史数据存储路径'] + '/' + file))
    #
    # df_his = ak.index_zh_a_hist_min_em(symbol="603015", period='1')
    # print(df_his)
    # stock_zh_a_spot_df = ak.stock_zh_a_spot()
    # print(stock_zh_a_spot_df)
    # stock_zh_a_tick_tx_js_df = ak.stock_zh_a_tick_tx_js(symbol="sz000001")
    # print(stock_zh_a_tick_tx_js_df)

    # while 1:
    #     while 1:
    #         if datetime.now().second == 0:
    #             time.sleep(2)
    #             break
    #         else:
    # #             time.sleep(0.1)
    # stock_data = ak.stock_zh_a_hist(symbol='601919', period='daily', adjust="qfq")
    # print(stock_data)
    # cal_BIAS(5, stock_data)
    # BIAS_test('300126', '20250221')
    # cal_new_lowest(pd.read_csv('df_hist_user.csv'))

    # stock_zh_a_tick_tx_js_df = ak.stock_zh_a_tick_tx_js(symbol="sz000001")
    # print(stock_zh_a_tick_tx_js_df)
    stock_code = '000988'

    # df = ak.stock_zh_a_hist(symbol=stock_code, period='daily', adjust="qfq")
    # print(cal_VR_5day(df,5))  #最近1日的 vr
    stock_bid_ask_em_df = ak.stock_bid_ask_em(symbol='000001')
    print(stock_bid_ask_em_df)
