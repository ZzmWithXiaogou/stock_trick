# 导入相关模块和类
from pybroker import Strategy, StrategyConfig, ExecContext
from pybroker.ext.data import AKShare
from stock_filter_common_lib import *


symbol = '601919'
start_date='20241213'
end_date='20250216'
# 定义规则
def buy_low(ctx: ExecContext):
    print('aaaa')
    # 止盈止损条件检查
    if ctx.long_pos():  # 如果已有仓位
        # 止盈条件：当前价格大于等于止盈价格，则卖出
        if ctx.close[-1] >= ctx.take_profit_price:
            ctx.sell_all()
            return

        # 止损条件：当前价格小于等于止损价格，则卖出
        if ctx.close[-1] <= ctx.stop_loss_price:
            ctx.sell_all()
            return

    # 如果当前没有持仓，则进行买入
    if not ctx.long_pos():
        if ctx.bars >= 2 and ctx.close[-1] < ctx.low[-2]:  # 买入条件：收盘价小于前一天最低价
            # 计算买入数量
            ctx.buy_shares = ctx.calc_target_shares(0.25)
            # 设置买入限价
            ctx.buy_limit_price = ctx.close[-1] - 0.01
            # 设置持有时长
            ctx.hold_bars = 3
            # 设置止盈止损价格
            ctx.take_profit_price = ctx.close[-1] * 1.05  # 止盈：当前价格上涨 5%
            ctx.stop_loss_price = ctx.close[-1] * 0.97  # 止损：当前价格下跌 3%
            # 记录买入价格
            ctx.entry_price = ctx.close[-1]


def dif_up_through_dea(ctx: ExecContext):
    # 获取不同时间周期的分钟数据
    five_min_data = ak.stock_zh_a_hist_min_em(symbol=symbol, period='5', start_date=start_date, end_date=end_date)
    fifteen_min_data = ak.stock_zh_a_hist_min_em(symbol=symbol, period='15', start_date=start_date, end_date=end_date)
    thirty_min_data = ak.stock_zh_a_hist_min_em(symbol=symbol, period='30', start_date=start_date, end_date=end_date)

    # 在策略中使用这些分钟级数据
    print(five_min_data.head())

def buy_condition(data: pd.DataFrame):
    """
    判断是否满足金叉条件，返回 True 表示满足买入条件
    """
    # 判断 DIF > DEA（即金叉）条件
    if data['DIF'].iloc[-1] > data['DEA'].iloc[-1] and data['DIF'].iloc[-2] < data['DEA'].iloc[-2]:
        return True
    return False


def sell_condition(entry_price: float, current_price: float):
    """
    判断是否满足止盈或止损条件
    """
    # 止盈 5%
    if current_price >= entry_price * 1.05:
        return True

    # 止损 5%
    elif current_price <= entry_price * 0.95:
        return True

    return False

if __name__ == '__main__':
    print('callback_engine')
    #股票选择

    # args_dic = {
    #     '最小市值': 50,
    #     '最小换手率': 5,
    #     '最大换手率': 15,
    #     '最小动态市盈率': 0,
    #     '近期判断天数': 7,  # 判断最近若干天的最大最小价格
    #     '近期超涨系数': 1.25,  # 判断最近若干天的最大最小价格的最大倍速
    #     '次新股天数': 60,
    #     '过去1年最高价比当前价比值上限': 5,
    #     '过去1年最低价比当前价比值下限': 0.2,
    #     '60日最大涨幅' : 100
    # }
    #
    # # spot_df = ak.stock_zh_a_spot_em()
    # # spot_df.to_csv("stock_zh_a_spot_em.csv", index=False, encoding="utf-8-sig")
    #
    # spot_df = pd.read_csv("stock_zh_a_spot_em.csv")
    # print('所有股票数量:', len(spot_df))
    # code_list = spot_df['代码'].to_list()
    # print(code_list)
    # ak.pe()
    # # stock_data = ak.stock_zh_a_hist(symbol='601919', adjust="qfq")
    # # stock_data.to_csv("stock_zh_a_hist.csv", index=False, encoding="utf-8-sig")


    # 策略配置
    # 启用 AKShare 数据源的缓存功能
    pb.enable_data_source_cache('AKShare')


    config = StrategyConfig(initial_cash=10_000)
    strategy = Strategy(
        data_source=AKShare(),
        start_date=start_date,
        end_date=end_date,
        config=config
    )

    print('执行回测')
    # 执行回测
    strategy.add_execution(fn=buy_low, symbols=[symbol])
    # strategy.add_execution(fn=dif_up_through_dea, symbols=[symbol])

    result = strategy.backtest()
    # 查看结果
    print(result.metrics_df)  # 查看绩效
    # print(result.orders)  # 查看订单
    # print(result.positions)  # 查看持仓
    print(result.portfolio)  # 查看投资组合
    # print(result.trades)  # 查看交易

    # 提取日期和equity列
    portfolio_data = result.portfolio[['equity']]

    # 绘制 equity 的变化趋势
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_data.index, portfolio_data['equity'], label='Equity', color='b', lw=2)
    plt.title('Equity Over Time', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Equity', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()