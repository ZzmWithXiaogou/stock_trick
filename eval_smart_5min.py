import random
import time

from stock_filter_common_lib import *


logging.basicConfig(filename='log/eval_smart.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',encoding='utf-8')


def timestamp_cal(df_last_time,stock_fenshi):
    year = df_last_time.split('-')[0]
    month = df_last_time.split('-')[1]
    day = df_last_time.split('-')[2].split( )[0]
    hour = df_last_time.split(' ')[1].split(':')[0]
    min = df_last_time.split(' ')[1].split(':')[1]
    sec =  df_last_time.split(' ')[1].split(':')[2]

    if stock_fenshi == '5':
        str_hour = hour
        str_min = min
        str_date = year + '-' + month + '-' + day + ' ' + str_hour + ':' + str_min + ':00'
        return str_date
    if stock_fenshi == '120':
        if int(hour) < 12:
            str_min = '30'
            str_hour = '11'
        if int(hour) >= 12:
            str_min = '00'
            str_hour = '15'
        str_date = year + '-' + month + '-' + day + ' ' + str_hour + ':' + str_min + ':00'
        return str_date
    if stock_fenshi == '60':
        if int(hour) == run_time_args_dic['A股早盘开盘时'] and int(min) >= run_time_args_dic['A股早盘开盘分']:
            str_min = '30'
            str_hour = '10'
        elif int(hour) == 10 or int(hour) == 11:
            str_min = '30'
            str_hour = '11'
        elif int(hour) == run_time_args_dic['A股午盘开盘时']:
            str_min = '00'
            str_hour = '14'
        elif int(hour) == 14:
            str_min = '00'
            str_hour = '15'
        else:
            str_min = '00'
            str_hour = '15'
        str_date = year + '-' + month + '-' + day + ' ' + str_hour + ':' + str_min + ':00'
        return str_date
    if stock_fenshi == '30':
        if int(hour) == 15:
            str_hour = hour
            str_min = '00'
        elif int(hour) == 11:
            str_hour = '11'
            str_min = '30'
        elif int(min) >= int(stock_fenshi):  #30~59
            str_min = '00'
            str_hour = str(int(hour)+1)
        elif int(min) < int(stock_fenshi):
            str_min = '30'
            str_hour = hour
        else:
            str_min = '00'
            str_hour = '15'

        str_date = year + '-' + month + '-' + day + ' ' + str_hour + ':' + str_min + ':00'
        return str_date

    if stock_fenshi == '15':
       if int(hour) == 15:
           str_hour = hour
           str_min = '00'
       elif int(hour) == 11 and int(min) == 30:
            str_hour = '11'
            str_min = '30'
       elif int(min) >= 45: #45~59
           str_min = '00'
           str_hour = str(int(hour)+1)
       elif int(min) >=30 and int(min) <45:
           str_min = '45'
           str_hour = hour
       elif int(min) >= 15 and int(min) < 30:
           str_min = '30'
           str_hour = hour
       else:
           str_min = '15'
           str_hour = hour
       str_date = year + '-' + month + '-' + day + ' ' + str_hour + ':' + str_min + ':00'
       return str_date


def eval_trade_callback(file):
    stock_code = file.split('_')[4]
    stock_name = file.split('_')[5]
    stock_fenshi = file.split('_')[1].split('min')[0]

    re_try_count = 0
    while re_try_count < run_time_args_dic['最大重试次数']:
        try:
            num = random.randint(1, 1000) / 1000
            time.sleep(num)
            df_5min = ak.stock_zh_a_hist_min_em(symbol=stock_code, period='5', adjust='qfq')
            df_15min = ak.stock_zh_a_hist_min_em(symbol=stock_code, period='15', adjust='qfq')
            df_30min = ak.stock_zh_a_hist_min_em(symbol=stock_code, period='30', adjust='qfq')
            df_60min = ak.stock_zh_a_hist_min_em(symbol=stock_code, period='60', adjust='qfq')
            df_120min = ak.stock_zh_a_hist_min_em(symbol=stock_code, period='120', adjust='qfq')
            if len(df_15min) != 0 and not df_15min.empty and len(df_30min) != 0 and not df_30min.empty and len(df_60min) != 0 and not df_60min.empty and len(df_120min) != 0 and not df_120min.empty:
                break
            else:
                time.sleep(10)
                re_try_count = re_try_count + 1
                # print_and_log('开始重试-----' + str(re_try_count) + ' ' + str(e))
        except Exception as e:
            time.sleep(10)
            re_try_count = re_try_count + 1
            # print_and_log('开始重试-----' + str(re_try_count) + ' ' + str(e))
    if re_try_count == run_time_args_dic['最大重试次数']:
        print_and_log('重试超过' + str(re_try_count) + '次-----')
        return 0

    cal_vr_ontime(df_5min, stock_code, stock_name,'5', 5, 2.5, 1.6)
    cal_vr_ontime(df_15min, stock_code, stock_name,'15', 5, 2.5, 1.6)
    cal_vr_ontime(df_30min, stock_code, stock_name,'30', 5, 2.5, 1.6)
    cal_vr_ontime(df_60min, stock_code, stock_name,'60', 5, 2.5, 1.6)
    cal_vr_ontime(df_120min, stock_code, stock_name,'120', 5, 2.5, 1.6)


def eval_smart_callback(df_hist,file,df):

    stock_code = file.split('_')[4]
    stock_name = file.split('_')[5]
    stock_fenshi = file.split('_')[1].split('min')[0]
    hist_last_time = df_hist["时间"].iloc[-1]
    df_last_time = df["时间"].iloc[-1]
    # print(hist_last_time,df_last_time,timestamp_cal(df_last_time, stock_fenshi))
    # print(df.to_string())
    # if stock_fenshi == '120':
    #     cal_vr_ontime(df, stock_code, stock_name,'5', 5, 2.5, 1.6)

    df = df.tail(1)
    if hist_last_time != timestamp_cal(df_last_time, stock_fenshi):  # 第一次获取新的时间戳 需要在原有基础上加1个数据
        df_hist = pd.concat([df_hist, df], axis=0, ignore_index=True)  # 把赋值后的newdf 粘贴在历史df后面
        df_hist.iloc[-1, df_hist.columns.get_loc("时间")] = timestamp_cal(df_last_time, stock_fenshi)
        df_hist.iloc[-1, df_hist.columns.get_loc("开盘")] = df["开盘"].iloc[-1]
        df_hist.iloc[-1, df_hist.columns.get_loc("最低")] = df["最低"].iloc[-1]
        df_hist.iloc[-1, df_hist.columns.get_loc("最高")] = df["最高"].iloc[-1]
        df_hist.iloc[-1, df_hist.columns.get_loc("底背离")] = 'Nothing'
        df_hist.iloc[-1, df_hist.columns.get_loc("顶背离")] = 'Nothing'
    else:
        if df["最低"].iloc[-1] < df_hist["最低"].iloc[-1]:
            df_hist.iloc[-1, df_hist.columns.get_loc("最低")] = df["最低"].iloc[-1]
        if df["最高"].iloc[-1] > df_hist["最高"].iloc[-1]:
            df_hist.iloc[-1, df_hist.columns.get_loc("最高")] = df["最高"].iloc[-1]
    df_hist.iloc[-1, df_hist.columns.get_loc("收盘")] = df["收盘"].iloc[-1]
    df_hist = cal_DIF_DEA_MACD(df_hist)
    df_hist = detect_macd_cross(df_hist)
    #数据处理结束

    #策略
    df_hist = cal_new_lowest(df_hist,df,file)
    # df_hist = cal_new_hightest(df_hist,df,file)
    #     print(df_hist.tail(2).to_string())
    return df_hist

def reply_test(reply_df,file,df_hist):
    reply_df_len = len(reply_df)
    df_hist_user = df_hist
    for i in range(1,reply_df_len+1):
        df = reply_df.head(i)
        df_hist_user = eval_smart_callback(df_hist_user,file,df)  #回调函数本身不实现数据本地录制
        # print(df_hist_user)
        # exit()
    df_hist_user.to_csv("df_hist_user.csv", index=False, encoding="utf-8-sig") #测试过程数据

def eval_smart_main(file):
    stock_code = file.split('_')[4]
    stock_name = file.split('_')[5]
    stock_fenshi = file.split('_')[1].split('min')[0]
    # print(file)
    #通过重试 确保获得数据
    try:
        if stock_fenshi == '120':  # 只在120分时下刷新df
            re_try_count = 0
            while re_try_count < run_time_args_dic['最大重试次数']:
                try:
                    num = random.randint(1,1000)/1000
                    time.sleep(num)
                    df = ak.stock_zh_a_hist_min_em(symbol=stock_code, period='5', adjust='qfq')
                    if len(df) != 0 and not df.empty:
                        break
                    else:
                        time.sleep(10)
                        re_try_count = re_try_count + 1
                        # print_and_log('开始重试-----' + str(re_try_count) + ' ' + str(e))
                except Exception as e:
                    time.sleep(10)
                    re_try_count = re_try_count + 1
                    # print_and_log('开始重试-----' + str(re_try_count) + ' ' + str(e))
            if re_try_count == run_time_args_dic['最大重试次数']:
                print_and_log('重试超过' + str(re_try_count) + '次-----')
                return 0
            df.to_csv(run_time_args_dic['临时数据'] + "/df_5min_hist_list_" + stock_code + '_' + stock_name + '_.csv',index=False, encoding="utf-8-sig")
        else:  # 其他分时直接读取
            df = pd.read_csv(run_time_args_dic['临时数据'] + "/df_5min_hist_list_" + stock_code + '_' + stock_name + '_.csv')
    except Exception as e:
        print_and_log("股票代码：" + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + ' ' + str(e))
        traceback.print_exc()  # 打印完整的错误堆栈信息
        return 0

    df_last_time = df["时间"].iloc[-1]
    df_hist = pd.read_csv(run_time_args_dic['历史数据存储路径'] + '/' + file) #读取本地csv作为历史数据输入
    try:
        df_hist = eval_smart_callback(df_hist,file,df)
    except Exception as e:
        print_and_log(df_last_time+ " " + "股票代码：" + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + ' ' + str(e))
        traceback.print_exc()  # 打印完整的错误堆栈信息

        return 0
    df_hist.to_csv(run_time_args_dic['历史数据存储路径'] + "/" + file, index=False,encoding="utf-8-sig")  # 历史df继续回写表格，如果中断，需要用eval_ontime进行刷新
    # print_and_log(df_last_time+ " " + "股票代码：" + stock_code + " 股票名称:  " + stock_name + " " + stock_fenshi + 'min分时数据已经写入完成')
    return 1




if __name__ == '__main__':
    print_and_log('eval_smart')

    if run_time_args_dic['reply_mode'] == 1:
        hist_file = 'df_120min_hist_list_600377_测试_.csv' #测试用的base历史数据
        reply_file = 'df_5min_hist_list_600377_测试_.csv'
        stock_code = hist_file.split('_')[4]
        stock_fenshi = hist_file.split('_')[1].split('min')[0]

        df = ak.stock_zh_a_hist_min_em(symbol=stock_code,period=stock_fenshi,adjust='qfq',start_date=  "1979-09-01 09:32:00",end_date = "2025-01-15 15:00:00")
        df['底背离'] = 'Nothing'
        df['顶背离'] = 'Nothing'
        df.to_csv(hist_file, index=False, encoding="utf-8-sig")
        df = ak.stock_zh_a_hist_min_em(symbol=stock_code,period='5',adjust='qfq',start_date=  "2025-01-15 16:00:00",end_date = "2225-02-24 15:00:00")
        df.to_csv(reply_file, index=False, encoding="utf-8-sig")

        reply_df = pd.read_csv(reply_file) #用于模拟实时获取数据的1min分时数据
        df_hist = pd.read_csv(hist_file)
        reply_test(reply_df,hist_file,df_hist)
        exit()


    print_and_log('debug_mode:'+str(run_time_args_dic['debug_mode']))
    # 指定目录
    directory = run_time_args_dic['历史数据存储路径']
    # 获取文件列表
    files = list_files_in_directory(directory)
    print(files)
    files_ex5_ex15_ex30_ex60 = list(filter(lambda x: '_5min_' not in x, files)) #过滤掉5minzz
    files_ex5_ex15_ex30_ex60 = list(filter(lambda x: '_15min_' not in x, files_ex5_ex15_ex30_ex60)) #过滤掉5minzz
    files_ex5_ex15_ex30_ex60 = list(filter(lambda x: '_30min_' not in x, files_ex5_ex15_ex30_ex60)) #过滤掉5minzz
    files_ex5_ex15_ex30_ex60 = list(filter(lambda x: '_60min_' not in x, files_ex5_ex15_ex30_ex60)) #过滤掉5minzz
    files_ex120 = list(filter(lambda x: '_120min_' not in x, files))  #
    print(files_ex5_ex15_ex30_ex60)
    print(files_ex120)
    while 1:
        while 1:
            if datetime.now().minute % 5 == 0 and datetime.now().second == 0 and trad_time_check():  #等待整分
                time.sleep(2)
                now_date = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(
                    datetime.now().day) + '-' + str(datetime.now().hour) + '-' + str(datetime.now().minute) + '-' + str(
                    datetime.now().second)
                print_and_log('开始执行时间:' + now_date)
                break
            else:
                time.sleep(0.1)
        with mp.Pool(processes=4) as pool:
            # 使用进程池处理字符串列表中的每个元素
            a = time.time()

            result = pool.map(eval_smart_main, files_ex5_ex15_ex30_ex60) #获取数据，同步处理120分时数据
            pool.map(eval_smart_main, files_ex120)#用离线数据处理120分时数据之外的数据
            pool.map(eval_trade_callback, files_ex5_ex15_ex30_ex60)

            b = time.time()
            pass_count = 0
            fail_count = 0
            for item in result:
                if item != 1:
                    fail_count = fail_count+1
                else:
                    pass_count = pass_count+1
            print_and_log('执行完成:' + now_date+' 耗时:'+str(b-a)+'   pass:'+str(pass_count)+'   fail:'+str(fail_count))
