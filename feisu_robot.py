import requests
import json
import stock_filter_common_lib



def robot_send_with_fenshi(fenshi,message):
    webhook_url_5min = "https://open.feishu.cn/open-apis/bot/v2/hook/4bc29877-dcf3-4046-a073-563457f882df"
    webhook_url_15min = "https://open.feishu.cn/open-apis/bot/v2/hook/fc2ad073-8380-4f06-a1ab-f9fb78dc533e"
    webhook_url_30min = "https://open.feishu.cn/open-apis/bot/v2/hook/20a32333-138c-4705-9549-95b2f683f5af"
    webhook_url_60min = "https://open.feishu.cn/open-apis/bot/v2/hook/e6beb930-386c-4603-92ec-d430e57e71ec"
    webhook_url_120min = "https://open.feishu.cn/open-apis/bot/v2/hook/20c72440-22f1-4f23-9514-7fdfd25be89e"
    webhook_url_vr_5min = "https://open.feishu.cn/open-apis/bot/v2/hook/b73aa772-9334-48fd-80bd-8dbbf05622d5"
    webhook_url_vr_15min = "https://open.feishu.cn/open-apis/bot/v2/hook/43f1bd4e-ea72-4e46-bf66-b343a8295dc7"
    webhook_url_vr_30min = "https://open.feishu.cn/open-apis/bot/v2/hook/e807b2a9-0516-4929-b4bd-d57215c02fe3"
    webhook_url_vr_60min = "https://open.feishu.cn/open-apis/bot/v2/hook/83c33b62-6239-4cbc-a28e-b47b71d54125"
    webhook_url_vr_120min = "https://open.feishu.cn/open-apis/bot/v2/hook/50506c1e-7a1b-45ac-942c-1184febbf74c"

    if fenshi == '5':
        webhook_url = webhook_url_5min
    elif fenshi == '15':
        webhook_url = webhook_url_15min
    elif fenshi == '30':
        webhook_url = webhook_url_30min
    elif fenshi == '60':
        webhook_url = webhook_url_60min
    elif fenshi == '120':
        webhook_url = webhook_url_120min
    elif fenshi == '5vr':
        webhook_url = webhook_url_vr_5min
    elif fenshi == '15vr':
        webhook_url = webhook_url_vr_15min
    elif fenshi == '30vr':
        webhook_url = webhook_url_vr_30min
    elif fenshi == '60vr':
        webhook_url = webhook_url_vr_60min
    elif fenshi == '120vr':
        webhook_url = webhook_url_vr_120min
    else:
        webhook_url = webhook_url_5min


    if stock_filter_common_lib.run_time_args_dic['reply_mode'] == 1:
        # stock_filter_common_lib.print_and_log('reply 模式，不发送飞书通知')
        return
    # 发送请求
    response = requests.post(webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})

    # 检查响应
    if response.status_code == 200:
        print("消息发送成功!")
    else:
        print(f"发送失败，状态码: {response.status_code}")



def robot_send(message):
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/4bc29877-dcf3-4046-a073-563457f882df"

    if stock_filter_common_lib.run_time_args_dic['reply_mode'] == 1:
        # stock_filter_common_lib.print_and_log('reply 模式，不发送飞书通知')
        return

    # 发送请求
    response = requests.post(webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})

    # 检查响应
    if response.status_code == 200:
        print("消息发送成功!")
    else:
        print(f"发送失败，状态码: {response.status_code}")

if __name__ == '__main__':
    print("feishu_robot")
    # 消息内容
    message = {
        "msg_type": "text",  # 消息类型，这里是文本
        "content": {
            "text": "Hello, this is a message sent by a Python script!"  # 消息内容
        }
    }


    robot_send(message)