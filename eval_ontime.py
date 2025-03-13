import time

from stock_filter_common_lib import *

logging.basicConfig(filename='log/eval_ontime.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',encoding='utf-8')

def time_compare(stock_data_1min_hist):

    last_time = stock_data_1min_hist.iloc[-1, stock_data_1min_hist.columns.get_loc('时间')]
    print_and_log('获取到的最近时间：' + last_time)
    last_time_list = last_time.split(' ')[1].split(':')

    if run_time_args_dic['debug_mode'] == 1:
        return 1
    if datetime.now().hour == int(last_time_list[0]) and datetime.now().minute == int(last_time_list[1]):
        print_and_log('时间校验通过')
        return 1
    else:
        print_and_log('时间校验失败')
        return 0


def data_save(folder_path,now_date,code,stock_name,stock_data_hist,fenshi,df_type):
    stock_data_hist = cal_DIF_DEA_MACD(stock_data_hist)
    time_ = stock_data_hist.iloc[-1, stock_data_hist.columns.get_loc('时间')]
    time_list = time_.split(' ')[1].split(':')  # ['14', '25', '00']
    stock_data_hist['顶背离'] = 'Nothing'
    stock_data_hist['底背离'] = 'Nothing'
    if df_type == 0:  # 股票
        stock_data_hist.to_csv(folder_path + "\\df_"+fenshi+"min_hist_list_" + str(code) +"_"+stock_name+"_"+ ".csv", index=False,
                               encoding="utf-8-sig")
        stock_data_hist.to_csv(run_time_args_dic['临时数据'] + "\\df_"+fenshi+"min_hist_list_" + str(code) +"_"+stock_name+"_"+ ".csv", index=False,
                               encoding="utf-8-sig")
    if df_type == 1:  # 指数
        stock_data_hist.to_csv(folder_path + "\\dfindex_"+fenshi+"min_hist_list_" + str(code) +"_"+stock_name+"_"+ ".csv", index=False,
                               encoding="utf-8-sig")




def eval_ontime_metric(fenshi,files,folder_path):
    while 1:
        if run_time_args_dic['debug_mode'] == 0:
            if (datetime.now().hour == run_time_args_dic['A股早盘开盘时'] and datetime.now().minute <=       #过滤9.30
                run_time_args_dic['A股早盘开盘分']) or datetime.now().hour < run_time_args_dic['A股早盘开盘时']:
                print_and_log('早盘未开盘')
                time.sleep(0.5)
                continue
            if (datetime.now().hour == run_time_args_dic['A股早盘收盘时'] and datetime.now().minute >
                run_time_args_dic['A股早盘收盘分']) or datetime.now().hour == 12 or (datetime.now().hour == run_time_args_dic['A股午盘开盘时'] and datetime.now().minute <=
                run_time_args_dic['A股午盘开盘分']):
                print_and_log('午盘收盘')
                time.sleep(0.5)
                continue
            if datetime.now().hour > run_time_args_dic['A股收盘时'] or (
                    datetime.now().hour == run_time_args_dic['A股收盘时'] and datetime.now().minute >
                    run_time_args_dic['A股收盘分']):
                print_and_log('已经收盘')
                return
        #分时过滤
        if fenshi == '5':
            if datetime.now().minute % 5 !=0:
                time.sleep(0.5)
                continue
            if datetime.now().second  !=0:
                time.sleep(0.5)
                continue
        #分时过滤
        if fenshi == '15':
            if datetime.now().minute % 15 !=0:
                time.sleep(0.5)
                continue
            if datetime.now().second  !=0:
                time.sleep(0.5)
                continue
        #分时过滤
        if fenshi == '30':
            if datetime.now().minute % 30 !=0:
                time.sleep(0.5)
                continue
            if datetime.now().second  !=0:
                time.sleep(0.5)
                continue

        if fenshi == '60':
            while 1:
                if (datetime.now().hour == 10 and datetime.now().minute == 30 and datetime.now().second == 0 ) or (datetime.now().hour == 11 and datetime.now().minute == 30 and datetime.now().second == 0 ) or (datetime.now().hour == 14 and datetime.now().minute == 0 and datetime.now().second == 0 ) or (datetime.now().hour == 15 and datetime.now().minute == 0 and datetime.now().second == 0 ) :
                    break
                else:
                    time.sleep(0.5)
                    continue
        if fenshi == '120':
            while 1:
                if (datetime.now().hour == 11 and datetime.now().minute == 30 and datetime.now().second == 0 )  or (datetime.now().hour == 15 and datetime.now().minute == 0 and datetime.now().second == 0 ) :
                    break
                else:
                    time.sleep(0.5)
                    continue
        time.sleep(1)
        for file in files:
            if '_'+fenshi +'min' in file:
                path  = folder_path+'\\'+file
                # print(path)
                df = pd.read_csv(path)
                code = path.split('\\')[2].split('_')[4]
                stock_name = path.split('\\')[2].split('_')[5]
                time_ = df.iloc[-1, df.columns.get_loc('时间')]
                # print(time_,code,stock_name)
                if cal_DIF_up_through_DEA(df):
                   message = {
                        "msg_type": "text",  # 消息类型，这里是文本
                        "content": {
                            "text": time_ + " 股票代码:  " + str(code) + " 股票名称:  " + stock_name + " "+fenshi+"min分时级别发生金叉"
                            # 消息内容
                        }
                   }
                   print_and_log(message)
                   feisu_robot.robot_send(message)

def ontime_monitor_1min(folder_path,index_list,code_list,df_all,df_index_all):   #每分钟都会执行，获取分时数据，任意的1个code如果获取失败，则直接跳过，这个分钟不在获取该code的分时，不影响其他code
    while 1:
        time.sleep(0.1)
        # if datetime.now().second != 0:
        #     continue
        now_date = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day)+ '-' + str(datetime.now().hour)+ '-' + str(datetime.now().minute)+ '-' + str(datetime.now().second)
        print_and_log('开始执行时间:' + now_date)
        time.sleep(5)
        #需要等待指数5min线接口修复，目前拿到的是平安银行
        # for code in index_list:
        #     time.sleep(0.1)
        #     this_stock = df_index_all[df_index_all['代码']==str(code)]
        #     stock_name = this_stock.iloc[0, this_stock.columns.get_loc('名称')]
        #
        #     re_try_count = 0
        #     while re_try_count<5:
        #         try:
        #             stock_data_1min_hist = ak.index_zh_a_hist_min_em(symbol=str(code), period='1')
        #             stock_data_1min_hist['时间'] = stock_data_1min_hist['时间'].astype(str)  # 将 '时间' 列转换为字符串类型
        #             break
        #         except Exception as e:
        #             time.sleep(0.1)
        #             re_try_count= re_try_count+1
        #             print_and_log(str(code)+'开始重试-----'+str(re_try_count))
        #             print_and_log(str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(
        #                 datetime.now().day) + '-' + str(datetime.now().hour) + '-' + str(
        #                 datetime.now().minute) + '-' + str(datetime.now().second) + ':' + " 股票代码:  " + str(
        #                 code) + " 股票名称:  " + stock_name + ' ' + str(e))
        #     if re_try_count == 5:
        #         print_and_log(str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(
        #             datetime.now().day) + '-' + str(datetime.now().hour) + '-' + str(
        #             datetime.now().minute) + '-' + str(datetime.now().second) + ':' + " 股票代码:  " + str(
        #             code) + " 股票名称:  " + stock_name + ' 超过最大重试次数' )
        #         send_message = {
        #             "msg_type": "text",  # 消息类型，这里是文本
        #             "content": {
        #                 "text": "超过最大重试次数，需要重新执行"  # 消息内容
        #             }
        #         }
        #         feisu_robot.robot_send(send_message)
        #         exit()
        #
        #     # if not time_compare(stock_data_1min_hist):
        #     #     continue
        #
        #     filtered_df = stock_data_1min_hist[~stock_data_1min_hist['时间'].str.contains('09:30:00')]
        #     stock_data_5min_hist = filtered_df[filtered_df['时间'].str.contains(r'5:00|0:00')]
        #     stock_data_15min_hist = stock_data_5min_hist[stock_data_5min_hist['时间'].str.contains(r'09:45:00|10:00:00|10:15:00|10:30:00|10:45:00|11:00:00|11:15:00|11:30:00|13:15:00|13:30:00|13:45:00|14:00:00|14:15:00|14:30:00|14:45:00|15:00:00')]
        #     stock_data_30min_hist = stock_data_5min_hist[stock_data_5min_hist['时间'].str.contains(r'10:00:00|10:30:00|11:00:00|11:30:00|13:30:00|14:00:00|14:30:00|15:00:00')]
        #     stock_data_60min_hist = stock_data_5min_hist[stock_data_5min_hist['时间'].str.contains(r'10:30:00|11:30:00|14:00:00|15:00:00')]
        #     stock_data_120min_hist = stock_data_5min_hist[stock_data_5min_hist['时间'].str.contains(r'11:30:00|15:00:00')]
        #
        #
        #     data_save(folder_path,now_date, code, stock_name, stock_data_5min_hist, '5',1)
        #     data_save(folder_path,now_date, code, stock_name, stock_data_15min_hist, '15',1)
        #     data_save(folder_path,now_date, code, stock_name,  stock_data_30min_hist, '30',1)
        #     data_save(folder_path,now_date, code, stock_name,  stock_data_60min_hist, '60',1)
        #     data_save(folder_path,now_date, code, stock_name,  stock_data_120min_hist, '120',1)

        for code in code_list:
            time.sleep(0.1)
            try:
                # print(df_all)
                this_stock = df_all[df_all['代码'] == str(code)]
                stock_name = this_stock.iloc[0, this_stock.columns.get_loc('名称')]
            except:
                print_and_log(str(code)+'获取error')
                traceback.print_exc()  # 打印完整的错误堆栈信息

                continue
            re_try_count = 0
            while re_try_count<5:
                try:

                    stock_data_5min_hist = ak.stock_zh_a_hist_min_em(symbol=str(code), period='5',adjust='qfq')
                    stock_data_15min_hist = ak.stock_zh_a_hist_min_em(symbol=str(code), period='15',adjust='qfq')
                    stock_data_30min_hist = ak.stock_zh_a_hist_min_em(symbol=str(code), period='30',adjust='qfq')
                    stock_data_60min_hist = ak.stock_zh_a_hist_min_em(symbol=str(code), period='60',adjust='qfq')
                    stock_data_120min_hist = ak.stock_zh_a_hist_min_em(symbol=str(code), period='120',adjust='qfq')
                    stock_data_5min_hist['时间'] = stock_data_5min_hist['时间'].astype(str)  # 将 '时间' 列转换为字符串类型
                    stock_data_15min_hist['时间'] = stock_data_15min_hist['时间'].astype(str)  # 将 '时间' 列转换为字符串类型
                    stock_data_30min_hist['时间'] = stock_data_30min_hist['时间'].astype(str)  # 将 '时间' 列转换为字符串类型
                    stock_data_60min_hist['时间'] = stock_data_60min_hist['时间'].astype(str)  # 将 '时间' 列转换为字符串类型
                    stock_data_120min_hist['时间'] = stock_data_120min_hist['时间'].astype(str)  # 将 '时间' 列转换为字符串类型
                    if len(stock_data_5min_hist) != 0 and len(stock_data_15min_hist) != 0 and len(stock_data_30min_hist) != 0 and len(stock_data_60min_hist) != 0 and len(stock_data_120min_hist) != 0:
                        break

                except Exception as e:
                    time.sleep(0.1)
                    re_try_count = re_try_count+1
                    print_and_log(str(code)+'开始重试-----'+str(re_try_count))
                    print_and_log(str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(
                        datetime.now().day) + '-' + str(datetime.now().hour) + '-' + str(
                        datetime.now().minute) + '-' + str(datetime.now().second) + ':' + " 股票代码:  " + str(
                        code) + " 股票名称:  " + stock_name + ' ' + str(e))

            if re_try_count == 5:
                print_and_log(str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(
                    datetime.now().day) + '-' + str(datetime.now().hour) + '-' + str(
                    datetime.now().minute) + '-' + str(datetime.now().second) + ':' + " 股票代码:  " + str(
                    code) + " 股票名称:  " + stock_name + ' 超过最大重试次数' )
                send_message = {
                    "msg_type": "text",  # 消息类型，这里是文本
                    "content": {
                        "text": "超过最大重试次数，需要重新执行"  # 消息内容
                    }
                }
                feisu_robot.robot_send(send_message)
                exit()

            # if not time_compare(stock_data_5min_hist):
            #     continue


            # stock_data_15min_hist = stock_data_5min_hist[stock_data_5min_hist['时间'].str.contains(r'09:45:00|10:00:00|10:15:00|10:30:00|10:45:00|11:00:00|11:15:00|11:30:00|13:15:00|13:30:00|13:45:00|14:00:00|14:15:00|14:30:00|14:45:00|15:00:00')]
            # stock_data_30min_hist = stock_data_5min_hist[stock_data_5min_hist['时间'].str.contains(r'10:00:00|10:30:00|11:00:00|11:30:00|13:30:00|14:00:00|14:30:00|15:00:00')]
            # stock_data_60min_hist = stock_data_5min_hist[stock_data_5min_hist['时间'].str.contains(r'10:30:00|11:30:00|14:00:00|15:00:00')]
            # stock_data_120min_hist = stock_data_5min_hist[stock_data_5min_hist['时间'].str.contains(r'11:30:00|15:00:00')]


            data_save(folder_path,now_date, code, stock_name, stock_data_5min_hist, '5',0)
            data_save(folder_path,now_date, code, stock_name,  stock_data_15min_hist, '15',0)
            data_save(folder_path,now_date, code, stock_name, stock_data_30min_hist, '30',0)
            data_save(folder_path,now_date, code, stock_name,  stock_data_60min_hist, '60',0)
            data_save(folder_path,now_date, code, stock_name, stock_data_120min_hist, '120',0)



        end_date = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day)+ '-' + str(datetime.now().hour)+ '-' + str(datetime.now().minute)+ '-' + str(datetime.now().second)
        print_and_log('结束执行时间:' + end_date)

        message = {
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": now_date + " 最新数据维护完成"
                # 消息内容
            }
        }
        print_and_log(message)
        feisu_robot.robot_send(message)

        return 0



if __name__ == '__main__':

    #ontime_monitor_1min  函数会1min执行一次，维护最新的分时数据，但是执行1次时间10s左右 不适合实时分析，可以用来在run_time_ana中断后断点续传

    print_and_log('eval_ontime start!')
    print_and_log('debug_mode:'+str(run_time_args_dic['debug_mode']))

    index_list = ['000001']
    file_path =run_time_args_dic['代码列表路径']
    print(file_path)
    code_list = code_list_read(file_path)

    re_try_count = 0
    while re_try_count<15:
        try:
            df_all = ak.stock_zh_a_spot_em()
            time.sleep(1)
            df_index_all = ak.stock_zh_index_spot_em()
            # print(df_all)
            if len(df_all) != 0 and not df_all.empty and len(df_index_all) != 0 and not df_index_all.empty:
                break
            else:
                time.sleep(1)
                re_try_count = re_try_count + 1
                print_and_log('开始重试-----' + str(re_try_count) + ' ' + str(e))

        except:
            time.sleep(1)
            re_try_count= re_try_count+1
    if re_try_count == 15:
        print_and_log(' 超过最大重试次数')
        send_message = {
            "msg_type": "text",  # 消息类型，这里是文本
            "content": {
                "text": "超过最大重试次数，需要重新执行"  # 消息内容
            }
        }
        feisu_robot.robot_send(send_message)
        exit()

    # now_date_day = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day)
    # folder_path =  run_time_args_dic['每日数据']+'\\'+now_date_day
    # os.makedirs(folder_path, exist_ok=True)  # exist_ok=True 避免文件夹已存在时报错
    # print(f"文件夹创建成功: {folder_path}")
    # clear_dataframe_path(folder_path)

    folder_path =run_time_args_dic['历史数据存储路径']
    print(folder_path)
    clear_dataframe_path(run_time_args_dic['历史数据存储路径'])


    ontime_monitor_1min(folder_path,index_list, code_list, df_all, df_index_all)


    # data_save_mp  = mp.Process(target=ontime_monitor_1min,args=(folder_path,index_list,code_list,df_all,df_index_all,))
    # data_save_mp.start()

    # while 1:
    #     # 获取文件列表
    #     files = list_files_in_directory(folder_path)
    #     # print(files)
    #     if len(files) !=0:
    #         print_and_log(' 开始监控')
    #         break
    #     time.sleep(1)
    #
    # eval_ontime_metric_5m_mp = mp.Process(target=eval_ontime_metric,args=('5',files,folder_path,))
    # eval_ontime_metric_15m_mp = mp.Process(target=eval_ontime_metric,args=('15',files,folder_path,))
    # eval_ontime_metric_30m_mp = mp.Process(target=eval_ontime_metric,args=('30',files,folder_path,))
    # eval_ontime_metric_60m_mp = mp.Process(target=eval_ontime_metric,args=('60',files,folder_path,))
    # eval_ontime_metric_120m_mp = mp.Process(target=eval_ontime_metric,args=('120',files,folder_path,))
    #
    # eval_ontime_metric_5m_mp.start()
    # eval_ontime_metric_15m_mp.start()
    # eval_ontime_metric_30m_mp.start()
    # eval_ontime_metric_60m_mp.start()
    # eval_ontime_metric_120m_mp.start()
    #
    # eval_ontime_metric_5m_mp.join()
    # eval_ontime_metric_15m_mp.join()
    # eval_ontime_metric_30m_mp.join()
    # eval_ontime_metric_60m_mp.join()
    # eval_ontime_metric_120m_mp.join()
    #
    # print_and_log('监控结束')

