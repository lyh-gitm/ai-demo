from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
from IPython.display import display, HTML

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY is not set in the environment variables.")
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
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
prod_review_zh = f"""
这个熊猫公仔是我给女儿的生日礼物，她很喜欢，去哪都带着。
公仔很软，超级可爱，面部表情也很和善。但是相比于价钱来说，
它有点小，我感觉在别的地方用同样的价钱能买到更大的。
快递比预期提前了一天到货，所以在送给女儿之前，我自己玩了会。，从而导致更详细和相关的输出。
"""

# 6. 指令内容，使用 ``` 来分隔指令和待总结的内容
prompt = f"""
你的任务是从电子商务网站上生成一个产品评论的简短摘要。

你的任务是从电子商务网站上的产品评论中提取相关信息。

请从以下三个反引号之间的评论文本中提取产品运输相关的信息，最多30个词汇。


评论: ```{prod_review_zh}```
"""

# 7. 输出
response = get_completion(prompt)
print(response)