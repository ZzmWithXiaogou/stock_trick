import logging
import time

from stock_filter_common_lib import *

logging.basicConfig(filename='log/runtime_macd_ana.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',encoding='utf-8')


def cyc_get_runtime_stock_data(cyctime,files):
    if cyctime !=5 and cyctime !=15 and cyctime !=1 and cyctime !=30 and cyctime !=60 and cyctime !=120:
        print_and_log('输入的数据获取周期错误')
        exit()
    wait_seconds = cyctime*60

    while 1:
        if run_time_args_dic['debug_mode'] == 0:
            if (datetime.now().hour == run_time_args_dic['A股早盘开盘时'] and datetime.now().minute <= run_time_args_dic['A股早盘开盘分']) or datetime.now().hour < run_time_args_dic['A股早盘开盘时'] :
                print_and_log('早盘未开盘')
                time.sleep(1)
                continue
            if (datetime.now().hour == run_time_args_dic['A股早盘收盘时'] and datetime.now().minute >= run_time_args_dic['A股早盘收盘分']) or datetime.now().hour == 12 or (datetime.now().hour == run_time_args_dic['A股午盘开盘时'] and datetime.now().minute <=
                run_time_args_dic['A股午盘开盘分']):
                print_and_log('午盘收盘')
                time.sleep(1)
                continue
            if datetime.now().hour > run_time_args_dic['A股收盘时'] or ( datetime.now().hour == run_time_args_dic['A股收盘时'] and datetime.now().minute >= run_time_args_dic['A股收盘分'] ) :
                print_and_log('已经收盘')
                return

        while 1:
            if cyctime == 120:
                if (datetime.now().hour == 11 and datetime.now().minute == 30 and datetime.now().second <= 2 )  or (datetime.now().hour == 15 and datetime.now().minute == 0 and datetime.now().second <= 2 ) :
                    print_and_log(str(cyctime)+'触发成功')
                    break
                else:
                    time.sleep(0.1)
            if cyctime == 60:
                if (datetime.now().hour == 10 and datetime.now().minute == 30 and datetime.now().second <= 2 ) or (datetime.now().hour == 11 and datetime.now().minute == 30 and datetime.now().second <= 2 ) or (datetime.now().hour == 14 and datetime.now().minute == 0 and datetime.now().second <= 2 ) or (datetime.now().hour == 15 and datetime.now().minute == 0 and datetime.now().second <= 2 ) :
                    print_and_log(str(cyctime)+' min触发成功')
                    break
                else:
                    time.sleep(0.1)
            if cyctime == 30:
                if datetime.now().minute % 30 == 0 and datetime.now().second  <= 2 :
                    print_and_log(str(cyctime)+' min触发成功')
                    break
                else:
                    time.sleep(0.1)
            if cyctime == 15:
                if datetime.now().minute % 15 == 0 and datetime.now().second <= 2 :
                    print_and_log(str(cyctime)+' min触发成功')
                    break
                else:
                    time.sleep(0.1)
            if cyctime == 5:
                if datetime.now().minute % 5 == 0 and datetime.now().second  <= 2 :
                    print_and_log(str(cyctime)+' min触发成功')
                    break
                else:
                    time.sleep(0.1)

        # time.sleep(wait_seconds)
        # time.sleep(1)


        a = time.time()

        re_try_count = 0
        while re_try_count < run_time_args_dic['最大重试次数']:
            try:
                df_all = ak.stock_zh_a_spot_em()
                time.sleep(0.1)
                df_index_all = ak.stock_zh_index_spot_em()
                if len(df_all) != 0 and len(df_index_all)!=0:
                    break
                else:
                    time.sleep(0.1)
                    re_try_count = re_try_count + 1
                    print_and_log('开始重试-----' + str(re_try_count) + ' ' + str(e))
            except Exception as e:
                time.sleep(0.1)
                re_try_count = re_try_count + 1
                print_and_log('开始重试-----' + str(re_try_count)+ ' ' + str(e))
        if re_try_count == run_time_args_dic['最大重试次数']:
            print_and_log('重试超过'+ str(re_try_count)+'次-----')
            continue

        # df_all = ak.stock_zh_a_spot_em()
        # df_index_all = ak.stock_zh_index_spot_em()
        b = time.time()
        print_and_log('耗时：'+str(b - a))
        for file in files:
            code = file.split('_')[4].split('.')[0]
            if '_'+str(cyctime)+'min_' in file:
                # print(str(cyctime)+'min_'+code)
                df = pd.read_csv(run_time_args_dic['历史数据存储路径']+'/'+file) #读取历史dataframe
                if 'dfindex_' in file:
                    filtered_df = df_index_all[df_index_all['代码'] == code]  # 当前dataframe按照代码筛选
                elif 'df_' in file:
                    filtered_df = df_all[df_all['代码']== code] #当前dataframe按照代码筛选
                else:
                    print('文件名不合法')
                    continue
                df_new = pd.DataFrame({col: pd.Series(dtype=df[col].dtype) for col in df.columns}) #创建一个和历史dataframe格式一样的空df
                try:
                    df_new.at[0, '收盘'] = filtered_df.iloc[0, filtered_df.columns.get_loc('最新价')] #空df的收盘价格 用当前df的最新价赋值
                    stock_name =  filtered_df.iloc[0, filtered_df.columns.get_loc('名称')]
                    # 添加一个获取时间字段，记录数据抓取的时刻
                    fetch_time = pd.Timestamp.now()
                    df_new.at[0, '时间'] = fetch_time
                    df = pd.concat([df, df_new], axis=0, ignore_index=True)#把赋值后的newdf 粘贴在历史df后面

                    macd_df = cal_DIF_DEA_MACD(df) #计算macd得到最终的df
                    if cal_DIF_up_through_DEA(macd_df):
                        message = {
                            "msg_type": "text",  # 消息类型，这里是文本
                            "content": {
                                "text": fetch_time.strftime('%Y-%m-%d %H:%M:%S')+" 股票代码:  "+code+" 股票名称:  "+stock_name+" "+str(cyctime)+"min分时级别发生金叉"  # 消息内容
                            }
                        }
                        feisu_robot.robot_send(message)
                    if cal_DEA_up_through_DIF(macd_df):
                        message = {
                            "msg_type": "text",  # 消息类型，这里是文本
                            "content": {
                                "text": fetch_time.strftime('%Y-%m-%d %H:%M:%S')+" 股票代码:  "+code+" 股票名称:  "+stock_name+" "+str(cyctime)+"min分时级别发生死叉"  # 消息内容
                            }
                        }
                        feisu_robot.robot_send(message)
                    macd_df.to_csv(run_time_args_dic['历史数据存储路径'] + "/"+file, index=False,encoding="utf-8-sig") #历史df继续回写表格，如果中断，需要用eval_ontime进行刷新
                    print_and_log(fetch_time.strftime('%Y-%m-%d %H:%M:%S')+" "+"股票代码："+code+" 股票名称:  "+stock_name+" "+str(cyctime)+'min分时数据已经写入完成')

                except Exception as e:
                    print(df_all)
                    print(filtered_df)
                    print_and_log(str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(
                        datetime.now().day) + '-' + str(datetime.now().hour) + '-' + str(
                        datetime.now().minute) + '-' + str(datetime.now().second) + ':' + " 股票代码:  " + str(
                        code)  + str(e))


if __name__ == '__main__':

    print_and_log('runtime_macd_ana start!')
    print_and_log('debug_mode:'+str(run_time_args_dic['debug_mode']))
    # 指定目录
    directory = run_time_args_dic['历史数据存储路径']
    # 获取文件列表
    files = list_files_in_directory(directory)
    print(files)
    # cyc_get_runtime_stock_data(5, files)
    # mp_1min = mp.Process(target=cyc_get_runtime_stock_data,args=(1, files,))
    # mp_5min = mp.Process(target=cyc_get_runtime_stock_data,args=(5, files,))
    mp_15min = mp.Process(target=cyc_get_runtime_stock_data,args=(15, files,))
    mp_30min = mp.Process(target=cyc_get_runtime_stock_data,args=(30, files,))
    mp_60min = mp.Process(target=cyc_get_runtime_stock_data,args=(60, files,))
    mp_120min = mp.Process(target=cyc_get_runtime_stock_data,args=(120, files,))
    # mp_1min.start()
    # mp_5min.start()
    mp_15min.start()
    mp_30min.start()
    mp_60min.start()
    mp_120min.start()

    send_message = {
        "msg_type": "text",  # 消息类型，这里是文本
        "content": {
            "text": "实时监控启动！"  # 消息内容
        }
    }
    feisu_robot.robot_send(send_message)


    # mp_1min.join()
    # mp_5min.join()
    mp_15min.join()
    mp_30min.join()
    mp_60min.join()
    mp_120min.join()

    print_and_log('监控结束')
    # while 1:
    #     print('股票监控程序正在运行')
    #     time.sleep(60)

