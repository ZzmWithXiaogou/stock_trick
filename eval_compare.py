from stock_filter_common_lib import *

##通过对个股AH过去60日股价对比，得出溢价率区间，进而探求套利机会

def compare_ah(df_a,df_h,df_hkd):
    df_a = df_a.copy()
    df_h = df_h.copy()
    df_hkd = df_hkd.copy()

    # print(len(df_a),len(df_h),len(df_hkd))
    # 将列表转换为集合
    set1 = set(df_a['日期'].tolist())
    set2 = set(df_h['日期'].tolist())
    set3 = set(df_hkd['日期'].tolist())
    # 找到三个集合的交集
    common_elements = set1 & set2 & set3
    # 将结果转换回列表
    time_merage = list(common_elements)
    # 使用 isin() 方法筛选出匹配的行
    new_df_a = df_a[df_a['日期'].isin(time_merage)]
    new_df_h = df_h[df_h['日期'].isin(time_merage)]
    new_df_hkd = df_hkd[df_hkd['日期'].isin(time_merage)]

    df_a_close_list = new_df_a['收盘'].tolist()
    df_h_close_hkd_list = new_df_h['收盘'].tolist()
    df_hkd_buy_list = df_hkd['中行汇买价'].tolist()

    df_h_close_list = []
    for index in range(0,len(df_h_close_hkd_list)):
        df_h_close_list.append(df_h_close_hkd_list[index]*df_hkd_buy_list[index]/100)

    exceed_rate_list = []
    for index in range(0, len(df_a_close_list)):
        exceed_rate = (df_a_close_list[index]-df_h_close_list[index])/df_h_close_list[index]
        # exceed_rate = (df_h_close_list[index] - df_a_close_list[index]) / df_a_close_list[index]
        exceed_rate_list.append(exceed_rate*100)
    # print(exceed_rate_list)
    #
    #
    # x = range(len(exceed_rate_list))
    # # 设置中文字体
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    # plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    #
    # # 绘制折线图
    # line1 = plt.plot(x, exceed_rate_list, label='溢价率', marker='o')
    # line2 = plt.plot(x, df_a_close_list, label='a股价格', marker='o')
    # line3 = plt.plot(x, df_h_close_list, label='h股价格', marker='o')
    #
    # # 添加标题和标签
    # plt.title('溢价率')  # 使用中文标题
    # plt.xlabel('索引')  # 使用中文x轴标签
    # plt.ylabel('值')  # 使用中文y轴标签
    # # 显示图例
    # plt.legend()
    # # 启用mplcursors，为两条线添加交互式注释
    # cursor1 = mplcursors.cursor(line1, hover=True)  # 为第一条线添加注释
    # cursor2 = mplcursors.cursor(line2, hover=True)  # 为第一条线添加注释
    # cursor3 = mplcursors.cursor(line3, hover=True)  # 为第一条线添加注释
    #
    # # 显示图形
    # plt.show()
    # 示例数据
    x = range(len(exceed_rate_list))  # 横轴数据

    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    # 创建图形和左侧纵轴
    fig, ax1 = plt.subplots()

    # 绘制溢价率（右侧纵轴）
    ax2 = ax1.twinx()  # 创建右侧纵轴
    line1 = ax2.plot(x, exceed_rate_list, label='溢价率', marker='o', color='green')  # 绿色表示溢价率
    ax2.set_ylabel('溢价率', color='green')  # 设置右侧纵轴标签
    ax2.tick_params(axis='y', labelcolor='green')  # 设置右侧纵轴刻度颜色

    # 绘制A股价格和H股价格（左侧纵轴）
    line2 = ax1.plot(x, df_a_close_list, label='A股价格', marker='o', color='blue')  # 蓝色表示A股价格
    line3 = ax1.plot(x, df_h_close_list, label='H股价格', marker='o', color='red')  # 红色表示H股价格
    ax1.set_xlabel('索引')  # 设置横轴标签
    ax1.set_ylabel('价格', color='black')  # 设置左侧纵轴标签
    ax1.tick_params(axis='y', labelcolor='black')  # 设置左侧纵轴刻度颜色

    # 添加标题
    plt.title('溢价率与A股/H股价格对比')  # 使用中文标题

    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')  # 显示图例

    # 启用mplcursors，为所有线添加交互式注释
    cursor1 = mplcursors.cursor(line1, hover=True)  # 溢价率注释
    cursor2 = mplcursors.cursor(line2, hover=True)  # A股价格注释
    cursor3 = mplcursors.cursor(line3, hover=True)  # H股价格注释

    # 显示图形
    plt.show()

if __name__ == '__main__':
    print_and_log('eval_compare')
    stock_code_a = ['601919','600377','600036']
    stock_code_h = ['01919','00177','03968']
    df_a = ak.stock_zh_a_hist(symbol=stock_code_a[2], period='daily', adjust="qfq")
    # print(df_a)
    df_h = ak.stock_hk_hist(symbol=stock_code_h[2], period='daily', adjust="qfq")
    # print(df_h)
    df_hkd = ak.currency_boc_sina(symbol="港币", start_date="20241004", end_date="22241110")
    # print(df_hkd)
    compare_ah(df_a, df_h,df_hkd)