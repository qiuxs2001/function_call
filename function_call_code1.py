# 导入必要的库
import os  # 操作系统接口，用于访问环境变量
from dotenv import load_dotenv, find_dotenv  # 用于加载.env文件中的环境变量
from openai import OpenAI  # OpenAI API客户端
import json  # JSON数据处理
import function_tools as ft  # 导入自定义的数学运算函数模块


if __name__ == "__main__":
    # 加载环境变量文件
    load_dotenv(find_dotenv())

    # 初始化OpenAI客户端
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  # 从环境变量获取API密钥
        base_url=os.getenv("OPENAI_BASE_URL")  # 从环境变量获取API基础URL
    )

    # 定义AI可以调用的工具列表
    tools = [
        # 乘法工具
        {
            "type": "function",  # 工具类型为函数
            "function": {
                "name": "multiply_two_numbers",  # 函数名称
                "description": "两个数相乘",  # 函数描述，帮助AI理解用途
                "parameters": {  # 函数参数配置
                    "type": "object",  # 参数类型为对象
                    "properties": {  # 参数属性定义
                        "a": {
                            "type": "number",  # 参数类型为数字
                            "description": "第一个数字"  # 参数描述
                        },
                        "b":{
                            "type": "number",  # 参数类型为数字
                            "description": "第二个数字"  # 参数描述
                        }
                    },
                    "required": [  # 必需参数列表
                        "a", "b"  # a和b都是必需参数
                    ]
                }
            }
        },
        # 加法工具
        {
            "type": "function",
            "function": {
                "name": "add_two_numbers",  # 加法函数名
                "description": "两个数相加",  # 加法函数描述
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "第一个数字"
                        },
                        "b":{
                            "type": "number",
                            "description": "第二个数字"
                        }
                    },
                    "required": [
                        "a", "b"
                    ]
                }
            }
        },
        # 减法工具
        {
            "type": "function",
            "function": {
                "name": "subtract_two_numbers",  # 减法函数名
                "description": "两个数相减",  # 减法函数描述
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "第一个数字"
                        },
                        "b":{
                            "type": "number",
                            "description": "第二个数字"
                        }
                    },
                    "required": [
                        "a", "b"
                    ]
                }
            }
        },
        # 除法工具
        {
            "type": "function",
            "function": {
                "name": "divide_two_numbers",  # 除法函数名
                "description": "两个数相除",  # 除法函数描述
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "第一个数字"
                        },
                        "b":{
                            "type": "number",
                            "description": "第二个数字"
                        }
                    },
                    "required": [
                        "a", "b"
                    ]
                }
            }
        }
    ]

    # 初始化对话消息列表
    messages = [
        {"role": "user", "content": "计算一下123.45*345.67/5+789.01-8的结果"}  # 用户的复杂数学表达式
    ]
    
    # 首次调用OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 使用GPT-4o-mini模型
        messages=messages,  # 传入对话消息
        tools=tools  # 传入可用工具列表
    )

    # 处理函数调用的主循环
    # 当AI需要调用函数时，循环执行直到得到最终答案
    while response.choices[0].message.tool_calls is not None:
        # 将AI的响应（包含函数调用请求）添加到对话历史
        messages.append(response.choices[0].message)

        # 遍历AI请求的每个函数调用
        for tool_call in response.choices[0].message.tool_calls:
            # 解析函数参数
            args = tool_call.function.arguments  # 获取函数参数（JSON字符串格式）
            args = json.loads(args)  # 将JSON字符串解析为Python字典
            
            # 获取函数名并动态调用对应函数
            function_name = tool_call.function.name  # 获取AI要调用的函数名
            invoke_fun = getattr(ft, function_name)  # 从function_tools模块获取对应函数
            result = invoke_fun(**args)  # 执行函数并获取计算结果
            # print(f"函数调用结果：{result}")  # 调试用，可以打印中间结果

            # 将函数执行结果添加到对话历史
            messages.append({
                "role": "tool",  # 消息角色为工具
                "content": f"{json.dumps(result)}",  # 函数执行结果
                "tool_call_id": tool_call.id  # 对应的函数调用ID
            })

        # 再次调用OpenAI API，传入包含函数执行结果的完整对话历史
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,  # 包含所有历史消息和工具响应
            tools=tools
        )
    
    # 输出AI的最终回答
    print(response.choices[0].message.content)

        

