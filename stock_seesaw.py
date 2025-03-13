from stock_filter_common_lib import *

logging.basicConfig(filename='log/stock_seesaw.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',encoding='utf-8')


def plt_graph(data_len,list1,list2):
    if len(list1)< data_len or len(list2) <data_len:
        print('数据长度错误')
        return
    x = range(data_len)
    list1 = list1[-data_len-1:-1]
    list2 = list2[-data_len-1:-1]
    list3 = []
    for i in range(0,data_len):
        list3.append((list2[i]-list1[i])/list1[i])
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    # 绘制折线图
    line1=plt.plot(x, list1, label='中证红利', marker='o')
    line2=plt.plot(x, list2, label='机器人', marker='o')
    # line3=plt.plot(x, list3, label='机器人&中证红利溢价率', marker='o')


    # 添加标题和标签
    plt.title('跷跷板比较')  # 使用中文标题
    plt.xlabel('索引')  # 使用中文x轴标签
    plt.ylabel('值')  # 使用中文y轴标签
    # 显示图例
    plt.legend()
    # 启用mplcursors，为两条线添加交互式注释
    cursor1 = mplcursors.cursor(line1, hover=True)  # 为第一条线添加注释
    cursor2 = mplcursors.cursor(line2, hover=True)  # 为第二条线添加注释
    # cursor3 = mplcursors.cursor(line3, hover=True)  # 为第二条线添加注释


    # 显示图形
    plt.show()


def avg_delta_cal(data_len,list1,list2):
    if len(list1) < data_len or len(list2) < data_len:
        print('数据长度错误')
        return
    list1 = list1[-data_len-1:-1]
    list2 = list2[-data_len-1:-1]
    list3 = []
    for i in range(0,data_len):
        list3.append((list2[i]-list1[i])/list1[i])
    max_list3 = max(list3)
    min_list3 = min(list3)

    avg_list3 = 0
    for i in range(0,data_len):
        avg_list3 = avg_list3+list3[i]
    avg_list3 = avg_list3/data_len
    return avg_list3,max_list3,min_list3

if __name__ == '__main__':
    print_and_log('stock_seesaw')

    zzhletf = "515080"
    jqretf = "562500"

    # fund_etf_spot_df = ak.fund_etf_spot_em()
    # fund_etf_spot_df.to_csv("fund_etf_spot_df.csv", index=False, encoding="utf-8-sig")
    zzhletf_hist_df = ak.fund_etf_hist_em(symbol=zzhletf, period="daily", adjust="qfq")
    # fund_etf_hist_df.to_csv("fund_etf_hist_df.csv", index=False, encoding="utf-8-sig")
    jqretf_hist_df = ak.fund_etf_hist_em(symbol=jqretf, period="daily", adjust="qfq")

    # plt_graph(60,zzhletf_hist_df['收盘'].tolist(), jqretf_hist_df['收盘'].tolist())

    jqretf_zzhletf = (jqretf_hist_df['收盘'].tolist()[-1]-zzhletf_hist_df['收盘'].tolist()[-1])/zzhletf_hist_df['收盘'].tolist()[-1]
    # print(jqretf_zzhletf)
    avg_list3, max_list3, min_list3 = avg_delta_cal(60,zzhletf_hist_df['收盘'].tolist(),jqretf_hist_df['收盘'].tolist())
    jqretf_zzhletf = round(jqretf_zzhletf, 2)
    avg_list3 = round(avg_list3, 2)
    max_list3 = round(max_list3, 2)
    min_list3 = round(min_list3, 2)

    message = {
        "msg_type": "text",  # 消息类型，这里是文本
        "content": {
            "text":"机器人ETF相比中证红利ETF\n最新溢价率 "+str(jqretf_zzhletf)+ "\n最近60日最大溢价率 "+str(max_list3)+ "\n最近60日最小溢价率 "+str(min_list3)+ "\n最近60日平均溢价率 "+str(avg_list3)   # 消息内容
        }
    }
    feisu_robot.robot_send(message)