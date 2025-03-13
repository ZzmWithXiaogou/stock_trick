import akshare as ak  # 用于获取股票数据
import pandas as pd
from sklearn.model_selection import train_test_split  # 用于数据划分为训练集和测试集
from sklearn.metrics import mean_squared_error  # 用于评估模型的表现（均方误差）
import xgboost as xgb  # 导入XGBoost回归模型

# 获取股票数据（这里以上证指数为例）
stock_data = ak.stock_zh_index_daily(symbol="sh000001")  # 可以替换为其他股票代码
stock_data['date'] = pd.to_datetime(stock_data['date'])  # 转换日期格式为pandas的datetime类型

# 特征工程：计算常用的技术指标
stock_data['MA5'] = stock_data['close'].rolling(window=5).mean()  # 5日简单移动平均
stock_data['MA20'] = stock_data['close'].rolling(window=20).mean()  # 20日简单移动平均
# RSI指标：相对强弱指数，用于衡量市场是否超买或超卖
stock_data['RSI'] = 100 - (100 / (1 + (stock_data['close'].diff().clip(lower=0).rolling(window=14).mean() /
                                          stock_data['close'].diff().clip(upper=0).rolling(window=14).mean())))
# MACD指标：指数平滑异同移动平均线，用于捕捉价格趋势的变化
stock_data['MACD'] = stock_data['close'].diff().ewm(span=12).mean() - stock_data['close'].diff().ewm(span=26).mean()

# 删除包含NaN值的行，因为某些技术指标需要移动窗口，导致前几行会有NaN
stock_data = stock_data.dropna()

# 目标变量：下一个交易日的股价，目标是预测下一个交易日的收盘价
stock_data['target'] = stock_data['close'].shift(-1)  # shift(-1)将目标值平移1天，表示下一个交易日的股价

# 特征选择：选择合适的特征作为模型输入
features = ['close', 'MA5', 'MA20', 'RSI', 'MACD']

# 准备训练数据：特征X和目标y
X = stock_data[features]  # 特征矩阵
y = stock_data['target']  # 目标变量

# 拆分数据集：80%的数据用于训练，20%用于测试
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)  # shuffle=False保持时间顺序

# XGBoost回归模型训练
model = xgb.XGBRegressor(objective='reg:squarederror')  # 使用均方误差作为目标函数
model.fit(X_train, y_train)  # 用训练数据拟合模型

# 预测：使用测试数据集进行预测
y_pred = model.predict(X_test)

y_test = y_test.dropna()
print(y_test)

y_pred = y_pred[:len(y_test)]
print('------')
print(y_pred)
# 评估模型：计算均方误差（MSE）
mse = mean_squared_error(y_test, y_pred)
print(f"均方误差 (MSE): {mse}")  # 输出均方误差，值越小表示模型越准确

# 可选：将模型用于未来的预测（预测未来股价）
# y_future_pred = model.predict(X_future)  # X_future为未来的特征数据
