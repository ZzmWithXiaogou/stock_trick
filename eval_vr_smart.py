from stock_filter_common_lib import *




def reply_test(reply_df):
    reply_df_len = len(reply_df)
    vr_list = []
    close_list = []
    for i in range(1,reply_df_len+1):
        df = reply_df.head(i)

        # cal_vr_ontime(df,'600377','test',5,2.5,1.6)

        # print(df)
        if len(df)>5:
            # print(df["日期"].iloc[-1],cal_VR(df, 5))  # 最近1日的 vr
            vr_list.append(cal_VR(df, 5))
            close_list.append(df["收盘"].iloc[-1])
    return vr_list,close_list

if __name__ == '__main__':
    print_and_log('eval_vr_smart')

    stock_zh_a_spot_em = ak.stock_zh_a_spot_em()
    stock_zh_a_spot_em = stock_zh_a_spot_em[(stock_zh_a_spot_em["市盈率-动态"] > 0) & (stock_zh_a_spot_em["涨跌幅"] > 0) & (
                        stock_zh_a_spot_em["60日涨跌幅"] < 100)]
    stock_code_list = stock_zh_a_spot_em['代码'].tolist()
    for symbol in stock_code_list:
        stock_data = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust="qfq")
        stock_data = cal_VR_df(stock_data,5)
        print(stock_data)
        stock_data.to_csv("df_hist_user.csv", index=False, encoding="utf-8-sig")  # 测试过程数据

        exit()
        # symbol_trade_days = len(stock_data)
        # if symbol_trade_days <= 60:
        #     continue
        #
        # if cal_VR(stock_data, 5) > 2.5:
        #     print(symbol)

    exit()

    stock_data_5min_hist = ak.stock_zh_a_hist_min_em(symbol='001301', period='5', adjust='qfq',start_date="20240901", end_date="22241110")

    stock_data_935_hist = stock_data_5min_hist[stock_data_5min_hist['时间'].str.contains(r'13:05:00')]

    # stock_data_935_hist.to_csv("stock_data_935_hist.csv", index=False,encoding="utf-8-sig")
    vr_list, close_list = reply_test(stock_data_935_hist)

    # exit()
    x = range(len(vr_list))
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    # 创建图形和左侧纵轴
    fig, ax1 = plt.subplots()

    # 绘制溢价率（右侧纵轴）
    ax2 = ax1.twinx()  # 创建右侧纵轴
    line1 = ax2.plot(x, vr_list, label='vr_list', marker='o', color='green')  # 绿色表示溢价率
    ax2.set_ylabel('成交量比率（VR）', color='green')  # 设置右侧纵轴标签
    ax2.tick_params(axis='y', labelcolor='green')  # 设置右侧纵轴刻度颜色

    # 绘制A股价格和H股价格（左侧纵轴）
    line2 = ax1.plot(x, close_list, label='收盘价', marker='o', color='blue')  # 蓝色表示A股价格
    ax1.set_xlabel('索引')  # 设置横轴标签
    ax1.set_ylabel('价格', color='black')  # 设置左侧纵轴标签
    ax1.tick_params(axis='y', labelcolor='black')  # 设置左侧纵轴刻度颜色

    # 添加标题
    plt.title('分时价格/量比')  # 使用中文标题

    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')  # 显示图例

    # 启用mplcursors，为所有线添加交互式注释
    cursor1 = mplcursors.cursor(line1, hover=True)  # 溢价率注释
    cursor2 = mplcursors.cursor(line2, hover=True)  # A股价格注释

    # 显示图形
    plt.show()