from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
from IPython.display import display, HTML

load_dotenv()
AMAP_API_KEY = os.getenv("AMAP_API_KEY")
if not AMAP_API_KEY:
    raise ValueError("AMAP_API_KEY is not set in the environment variables.")
client = OpenAI(
    api_key=os.getenv("AMAP_API_KEY"),
    base_url="https://api.deepseek.com/v1"   # ← 关键：指向 DeepSeek
)
def get_completion(prompt, model="deepseek-chat"): 
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,  # Adjust the temperature for creativity
        )
    
    return response.choices[0].message.content
def get_completion_from_messages(messages, model="deepseek-chat", temperature=0):
     response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, # 控制模型输出的随机程度
    )
     return response.choices[0].message.content

messages = [
    {'role':'system', 'content':'你是个友好的聊天机器人。'},    
    {'role':'user', 'content':'Hi, 我是Isa。'}  
    # {'role': 'system', 'content': '你是一个像莎士比亚一样说话的助手.'},
    # {'role': 'user', 'content': '给我讲个笑话。'},
    # {'role': 'assistant', 'content': '为什么程序员喜欢在圣诞节编程？'},
    # {'role': 'user', 'content': '我不知道'}
]
response = get_completion_from_messages(messages, temperature=0.7)
print(response)