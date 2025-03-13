from typing import final

from stock_filter_common_lib import *


logging.basicConfig(filename='log/eval_hk_jiejing.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',encoding='utf-8')


def wait_for_jiejing_stock(code):
    df = ak.stock_hk_hist(symbol=code, period='daily', adjust="qfq")
    if 109 < len(df) < 115:
        print_and_log('筛选到：'+str(code))
    else:
        print_and_log('不满足条件：'+str(code))

if __name__ == '__main__':
    print_and_log('eval_hk_jiejing')
    df_h = ak.stock_hk_spot_em()
    # print(df_h)
    code_list = df_h['代码'].tolist()
    # for item in code_list:
    #     print(item)
    with mp.Pool(processes=8) as pool:
        # 使用进程池处理字符串列表中的每个元素
        result = pool.map(wait_for_jiejing_stock, code_list)
