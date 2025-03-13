from traceback import print_tb

from openai import OpenAI


if __name__ == '__main__':
    print('deepseek')  #以函数组成插件式的筛选条件
    client = OpenAI(api_key='pBLJ4YH446r2n58m',base_url='https://llmapi.horizon.auto/v1')

    response = client.chat.completions.create(
        model='DeepSeek-R1',
        messages=[
            {"role":"system","content":"你是一个助手"}
        ],
        stream=False
    )
    print(response.choices[0].message.content)
