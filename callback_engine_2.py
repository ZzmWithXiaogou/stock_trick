from stock_filter_common_lib import *

class MACDStrategy(bt.Strategy):
    def __init__(self):
        self.dif = self.data.dif
        self.dea = self.data.dea

    def next(self):
        if self.dif > self.dea and not self.position:
            self.buy()
            print(f"买入：{self.data.datetime.date(0)} 价格：{self.data.close[0]}")  # 输出买入日期和价格
        elif self.dif < self.dea and self.position:
            self.sell()
            print(f"卖出：{self.data.datetime.date(0)} 价格：{self.data.close[0]}")  # 输出卖出日期和价格

    def stop(self):
        # 打印回测结束时的账户资金和持仓信息
        print(f"最终现金余额: {self.broker.get_cash()}")
        print(f"最终总资产: {self.broker.get_value()}")



class MyData(bt.feeds.PandasData):
    lines = ('dif', 'dea', 'macd')  # 这是Backtrader中定义的数据行名称
    params = (
        ('dif', 'DIF'),  # 映射Pandas列名 'DIF' 到Backtrader中的 'dif'
        ('dea', 'DEA'),  # 映射Pandas列名 'DEA' 到Backtrader中的 'dea'
        ('macd', 'MACD'),  # 映射Pandas列名 'MACD' 到Backtrader中的 'macd'
    )

if __name__ == '__main__':
    print('callback_engine')
    # 获取上证指数的历史日线数据
    data = stock_zh_a_hist_alex(symbol="000988")
    data = cal_DIF_DEA_MACD(data)

    # data.to_csv(run_time_args_dic['临时数据'] + "/callback.csv", index=False,encoding="utf-8-sig")

    # 修改列名
    data.rename(columns={'日期': 'date','股票代码': 'symbol', '开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low','成交量': 'volume'}, inplace=True)
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    # 将DataFrame转换为Backtrader支持的格式
    data = MyData(dataname=data)

    # 设置回测
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MACDStrategy)  # 添加策略
    cerebro.adddata(data)  # 添加数据
    cerebro.broker.set_cash(100000)  # 初始资金
    cerebro.broker.setcommission(commission=0.001)  # 交易佣金

    # 运行回测
    cerebro.run()



    # # 输出回测结果
    # cerebro.plot()