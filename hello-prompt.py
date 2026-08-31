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
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]
print("🤖 开始对话吧！（输入 'exit' 或 'quit' 退出）\n")


while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chat. Goodbye!")
        break

    # 1.把用户的新问题加入历史
    messages.append({"role": "user", "content": user_input})

    # 2.发送到API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.7,  # Adjust the temperature for creativity
    )

    # 3.提取回复
    reply = response.choices[0].message.content

    # 4.把助手的回复加入历史
    messages.append({"role": "assistant", "content": reply})

    print(f"Assistant: {reply}\n")
   
# def chat(prompt):
#     #1.把用户的新问题加入历史
#     messages.append({"role": "user", "content": prompt})
#     #2.发送到API
#     response = client.chat.completions.create(
#         model="deepseek-chat",
#         messages=messages,
#         temperature=0.7,  # Adjust the temperature for creativity
#     )

#     #3.提取回复
#     reply = response.choices[0].message.content
#     #4.把助手的回复加入历史
#     messages.append({"role": "assistant", "content": reply})
#     return reply

# #模拟多轮对话
# if __name__ == "__main__":
#     print("===第一轮===")
#     r1 = chat("我叫小明，今年18岁")
#     print(f"Assistant: {r1}")
#     print("\n=== 第二轮 ===")
#     r2 = chat("我叫什么名字？多大了？")
#     print(f"AI: {r2}")
    
#     print("\n=== 第三轮 ===")
#     r3 = chat("帮我总结一下我们聊了什么。")
#     print(f"AI: {r3}")
   
# def get_completion(prompt, model="deepseek-chat"):
#      messages=[ {"role": "user", "content": prompt}]
#      response = client.chat.completions.create(
#         model=model,
#         messages=messages,
#         temperature=0.7,  # Adjust the temperature for creativity
       
#     )
#      return response.choices[0].message.content
# if __name__ == "__main__":
#     result = get_completion("你好，请用一句话介绍自己")
#     print(result)