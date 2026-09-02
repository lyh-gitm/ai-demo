from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
from IPython.display import display, HTML
import json

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY is not set in the environment variables.")

#配置客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"   # ← 关键：
)
#定义工具（Tools）
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city and state e.g., San Francisco, CA"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to calculate"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

#3.本地函数实现-真正的"行动"发生
def get_weather(city: str) -> str:
    # 这里可以调用实际的天气API来获取天气信息
   weather_data = {
       "北京": "晴天，25度",
        "上海": "多云，28度",
        "深圳": "小雨，30度"
   }
   return weather_data.get(city, f"抱歉，没有{city}的天气数据")

def calculate(expression: str) -> str:
    """执行计算"""
    try:
        result = eval(expression)  # 生产环境建议用 ast 安全解析
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"
    
# 函数名到实际函数的映射
available_functions = {
    "get_weather": get_weather,
    "calculate": calculate
}

def run_agent(user_query: str, max_iterations: int = 5):
    """
    运行最小 Agent
    max_iterations: 防止无限循环
    """
    
    # 消息历史 —— 这就是模型的“工作记忆”
    messages = [
        {
            "role": "system",
            "content": "你是一个智能助手。请仔细思考用户的问题，"
                       "如果需要查天气或算数，请调用工具。"
                       "拿到工具结果后，给出最终回答。"
        },
        {
            "role": "user",
            "content": user_query
        }
    ]
    
    print(f"🙋 用户: {user_query}\n")
    
    for i in range(max_iterations):
        print(f"{'='*50}")
        print(f"🔄 第 {i+1} 轮循环")
        print(f"{'='*50}")
        
        # ---------- 思考（Thought）----------
        # 调用 API，模型决定下一步
        response = client.chat.completions.create(
            model="deepseek-chat",  # 用 V3，工具调用最稳定
            messages=messages,
            tools=tools,
            tool_choice="auto"  # 让模型自己决定是否调工具
        )
        
        response_message = response.choices[0].message
        
        # 把模型的回复加入历史
        messages.append(response_message)
        
        # 打印模型的思考过程
        if response_message.content:
            print(f"💭 思考: {response_message.content}")
        
        # ---------- 行动（Action）----------
        # 检查模型是否请求调用工具
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                print(f"🔧 行动: 调用 {func_name}({func_args})")
                
                # ---------- 观察（Observation）----------
                # 执行本地函数
                if func_name in available_functions:
                    func_to_call = available_functions[func_name]
                    observation = func_to_call(**func_args)
                    print(f"👁️ 观察: {observation}")
                    
                    # 把观察结果喂回给模型
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(observation)
                    })
                else:
                    print(f"❌ 错误: 未知工具 {func_name}")
        
        else:
            # 模型没有请求工具调用，说明它准备给出最终答案
            print(f"\n✅ 最终答案: {response_message.content}")
            break
    else:
        print("\n⚠️ 达到最大循环次数，强制结束")


# ---------- 运行测试 ----------
if __name__ == "__main__":
    run_agent("北京今天天气怎么样？另外帮我算一下 125 * 8 等于多少？")