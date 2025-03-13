import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton
from stock_filter_common_lib import *


class StringInputApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('股票代码输入')
        self.setGeometry(300, 300, 300, 300)

        layout = QVBoxLayout()

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText('请输入股票代码...')
        layout.addWidget(self.input_field)

        self.button = QPushButton('确定', self)
        self.button.clicked.connect(self.on_confirm)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def on_confirm(self):
        input_text = self.input_field.text()
        print(f'输入的字符串: {input_text}')
        stock_code = input_text
        # stock_code = sys.argv[1]
        #
        df = ak.stock_zh_a_hist(symbol=stock_code, period='daily', adjust="qfq", start_date="20241001",
                                end_date="22241110")
        # df = akshare.stock_zh_a_hist_min_em(symbol=stock_code, period='120', adjust="qfq",start_date="20240901", end_date="22241110")
        # df = df[df['时间'].str.contains(r'11:30:00')]

        vr_list, close_list = reply_test(df)

        x = range(len(vr_list))
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        # 创建图形和左侧纵轴
        fig, ax1 = plt.subplots()

        # 绘制溢价率（右侧纵轴）
        ax2 = ax1.twinx()  # 创建右侧纵轴
        line1 = ax2.plot(x, vr_list, label='成交量比率（VR）', marker='o', color='green')  # 绿色表示溢价率
        ax2.set_ylabel('成交量比率（VR）', color='green')  # 设置右侧纵轴标签
        ax2.tick_params(axis='y', labelcolor='green')  # 设置右侧纵轴刻度颜色

        # 绘制A股价格和H股价格（左侧纵轴）
        line2 = ax1.plot(x, close_list, label='收盘价', marker='o', color='blue')  # 蓝色表示A股价格
        ax1.set_xlabel('索引')  # 设置横轴标签
        ax1.set_ylabel('价格', color='black')  # 设置左侧纵轴标签
        ax1.tick_params(axis='y', labelcolor='black')  # 设置左侧纵轴刻度颜色

        # 添加标题
        plt.title(stock_code)  # 使用中文标题

        # 合并图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')  # 显示图例

        # 启用mplcursors，为所有线添加交互式注释
        cursor1 = mplcursors.cursor(line1, hover=True)  # 溢价率注释
        cursor2 = mplcursors.cursor(line2, hover=True)  # A股价格注释

        # 显示图形
        plt.show()
        # time.sleep(1)
        # plt.savefig(save_path+'\\'+stock_code,dpi=300)
        # print(cal_VR(df, -2))  #最近1日的 vr

def reply_test(reply_df):
    reply_df_len = len(reply_df)
    vr_list = []
    close_list = []
    for i in range(1,reply_df_len+1):
        df = reply_df.head(i)
        # print(df)
        if len(df)>5:
            # print(df["日期"].iloc[-1],cal_VR(df, 5))  # 最近1日的 vr
            vr_list.append(cal_VR(df, 5))
            close_list.append(df["收盘"].iloc[-1])
    return vr_list,close_list

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StringInputApp()
    window.show()
    sys.exit(app.exec_())
