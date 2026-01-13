"""测试七牛云 API 连接"""
from openai import OpenAI
import json

# 读取配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 获取七牛云配置
qiniu_config = config['qiniu']

print("="*50)
print("七牛云 AI API 测试")
print("="*50)
print(f"API 地址: {qiniu_config['base_url']}")
print(f"模型: {qiniu_config['model']}")
print("="*50)

# 初始化客户端
client = OpenAI(
    base_url=qiniu_config['base_url'],
    api_key=qiniu_config['api_key']
)

# 测试请求
print("\n正在发送测试请求...")

messages = [
    {"role": "user", "content": "你好，请用一句话介绍七牛云"}
]

try:
    response = client.chat.completions.create(
        model=qiniu_config['model'],
        messages=messages,
        stream=False,
        max_tokens=100
    )

    content = response.choices[0].message.content

    print("\n" + "="*50)
    print("[SUCCESS] API 调用成功！")
    print("="*50)
    print(f"\n回复内容:\n{content}")
    print("\n" + "="*50)
    print("测试成功！可以运行 anki_process.py 了")
    print("="*50)

except Exception as e:
    print("\n" + "="*50)
    print("[ERROR] API 调用失败！")
    print("="*50)
    print(f"\n错误信息: {e}")
    print("\n请检查:")
    print("1. API KEY 是否正确")
    print("2. 网络连接是否正常")
    print("3. API 地址是否正确")
