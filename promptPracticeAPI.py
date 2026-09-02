import os
from openai import OpenAI
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from datetime import datetime
import json

import requests

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY is not set in the environment variables.")

#配置客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"   # ← 关键：
)

#2.定义工具（Tools）
def web_search(query: str) -> str:
    """
    通过 Hacker News 官方 API 获取科技热点
    这是一个真实可用的联网工具，无需 API Key
    """
    try:
        # 1. 获取热门文章 ID 列表
        top_ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        ).json()
        
        # 2. 取前 5 条，获取详细信息
        results = []
        for story_id in top_ids[:5]:
            story = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                timeout=10
            ).json()
            if story and story.get('title'):
                results.append(
                    f"• {story['title']}\n"
                    f"  链接: {story.get('url', '无')}\n"
                    f"  热度: {story.get('score', 0)} 分 | "
                    f"  评论: {story.get('descendants', 0)} 条"
                )
        
        if not results:
            return "未获取到新闻"
        
        # 把 query 相关信息也标注上
        header = f"关于「{query}」的 Hacker News 科技热点 TOP 5：\n\n"
        return header + "\n\n".join(results)
        
    except Exception as e:
        return f"搜索失败: {str(e)}"
    """
    使用DuckDuckGo搜索引擎进行网页搜索，并返回前3条结果的标题和链接。
    """
    try:
        #先创建对象，在调用方法
        ddgs = DDGS()
        results = ddgs.text(query,max_results=3)
        if not results:
            return "没有找到相关结果。"

        # results = DDGS().text(query, max_results=3)

        #格式化文本
        formatted = []
        for result in results:
            title = result.get("title", "No Title")
            body = result.get("body", "No Body")
            href = result.get("href", "No Link")
            formatted.append(f"标题: {title}\n内容: {body}\n链接: {href}\n")    
            return "\n".join(formatted)
    except Exception as e:
        return f"搜索时发生错误: {str(e)}"

def get_current_time() -> str:
    """
    获取当前的日期和时间。
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression: str) -> str:
    """
    计算数学表达式的结果。
    """
    try:
       # 只允许安全的数学运算
        allowed = {"__builtins__": {}}
        result = eval(expression, allowed, {})
        return str(result)
    except Exception as e:
        return f"计算时发生错误: {str(e)}"
    
# 工具名称 → 实际函数的映射表（用于执行）
tool_mapping = {
    "web_search": web_search,
    "get_current_time": get_current_time,
    "calculate": calculate
}

#定义工具的JSON Schema
tools = [
    {
        "type":"function",
        "function": {
            "name": "web_search",
            "description": "使用DuckDuckGo搜索引擎进行网页搜索，并返回前3条结果的标题和链接。",
            "parameters": {
                "type": "object",
                "properties": {#属性
                    "query": {
                        "type": "string",
                        "description": "要搜索的查询字符串"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type":"function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间。",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type":"function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式的结果。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

#4.ReAct 循环
def run_agent(user_query: str,max_turns: int = 6):
    '''
    运行ReAct循环，处理用户查询。
    流程：
    Turn 1: 模型思考 → 决定调工具 → 代码执行 → 得到观察
    Turn 2: 模型看到观察 → 再思考 → 可能再调工具 / 或直接给答案
    ...
    直到模型不再调工具，输出最终答案

    '''

    # 消息历史 —— 这就是模型的“工作记忆”
    messages = [
        {
            "role": "system",
            "content": "你是一个智能助手。请仔细思考用户的问题，"
        },
        {
            "role": "user",
            "content": user_query
        }
    ]   

    
    print(f"\n{'='*60}")
    print(f"🙋 用户问题: {user_query}")
    print(f"{'='*60}\n")


    #ReAct循环
    for turn in range(1, max_turns + 1):
        print(f"--- 🔄 Turn {turn} ---\n")
        
        # ========== THOUGHT：让模型思考 ==========
        print("💭 正在思考...")
        response = client.chat.completions.create(
            model="deepseek-chat",   # V3，工具调用最稳定
            messages=messages,
            tools=tools,
            tool_choice="auto"       # 让模型自己决定是否调工具
        )
        
        assistant_msg = response.choices[0].message
        
        # 把模型的回复加入历史（⚠️ 关键：必须先加，否则 tool_call_id 对不上）
        messages.append(assistant_msg)
        
        # 打印模型的思考内容
        if assistant_msg.content:
            print(f"💬 模型说: {assistant_msg.content}\n")

        
        # ========== ACTION：检查模型是否要调工具 ==========
        if assistant_msg.tool_calls:
            print(f"🔧 模型请求调用 {len(assistant_msg.tool_calls)} 个工具:\n")
            
            # 遍历所有工具调用（模型可能一次调多个）
            for tool_call in assistant_msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                print(f"  📞 函数: {func_name}")
                print(f"  📝 参数: {func_args}")
                
                #tool_mapping ========== 执行：真正调用本地函数 ==========
                if func_name in tool_mapping:
                    try:
                        result = tool_mapping[func_name](**func_args)
                        print(f"  ✅ 执行结果: {result}\n")
                    except Exception as e:
                        result = f"执行出错: {str(e)}"
                        print(f"  ❌ 执行出错: {e}\n")
                else:
                    result = f"未知工具: {func_name}"
                    print(f"  ❌ 未知工具\n")
                
                # ========== OBSERVATION：把结果喂回模型 ==========
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,  # ⚠️ 必须和 assistant_msg 里的 id 对应
                    "content": str(result)
                })
            
            # 本轮工具调用处理完毕，进入下一轮循环让模型继续思考
            print("  👁️ 观察结果已喂回模型，继续下一轮...\n")
            continue
        
        else:
            # ========== FINAL ANSWER：模型不再调工具，给出最终答案 ==========
            print(f"{'='*60}")
            print(f"✅ 最终答案:\n{assistant_msg.content}")
            print(f"{'='*60}\n")
            return assistant_msg.content
    
    # 如果循环结束还没给出答案
    print(f"⚠️ 达到最大轮次 ({max_turns})，强制结束")
    return None
if __name__ == "__main__":
    # 测试1：需要搜索的问题
    run_agent("帮我查一下今天有什么科技新闻，然后算一下 365 * 24 是多少小时")

  # 测试2：需要多步推理的问题
    # run_agent("现在几点了？另外查一下 Python 3.13 有哪些新特性")