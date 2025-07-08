# 导入必要的库
import os  # 操作系统接口，用于访问环境变量
from dotenv import load_dotenv, find_dotenv  # 用于加载.env文件中的环境变量
from openai import OpenAI  # OpenAI API客户端，用于与智谱AI进行交互
import json  # JSON数据处理库，用于解析和序列化JSON数据
import function_tools as ft  # 导入自定义的工具函数模块，包含百度搜索等功能


if __name__ == "__main__":
    # 程序主入口，确保脚本被直接运行时才执行以下代码
    
    # 加载环境变量文件
    # find_dotenv()会自动查找.env文件，load_dotenv()将其中的变量加载到环境中
    load_dotenv(find_dotenv())

    # 初始化OpenAI兼容的客户端，用于连接智谱AI服务
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  # 从环境变量获取智谱AI的API密钥
        base_url=os.getenv("OPENAI_BASE_URL")  # 从环境变量获取智谱AI的API基础URL
    )

    # 定义AI可以调用的工具列表
    # 这里包含了百度搜索工具，AI可以根据需要自动调用
    tools = [ft.BAIDU_SEARCH,
             ft.HUIJU_SEARCH,
             ft.DIVIDE_TWO_NUMBERS]


    exchange_exanple = """
    使用查询到汇率信息动态计算结果。

    例如100人民币兑换美元：
    1.首先使用"mSellPri" 获得100美元兑换人民币的价格
    2.然后除以100，得到1美元兑换人民币的价格
    3.最后再乘以需要兑换的人民币数量，得到最终的美元金额
    """

    # 初始化对话消息列表
    # 包含系统提示和用户查询，用于指导AI的行为
    messages = [
        {"role": "system", "content": "不需要要求用户补充问题，直接按问题调用tool"},  # 系统角色：指导AI直接使用工具而不询问
        {"role": "user", "content": "帮我算一下100人民币兑换日元是多少"}  # 用户角色：具体的查询请求
    ]
    
    # 首次调用智谱AI API
    # 发送初始请求，AI会根据用户问题决定是否需要调用工具
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 使用智谱AI的glm-4-flash模型
        messages=messages,  # 传入对话消息列表
        tools=tools,  # 传入可用工具列表，让AI知道可以调用哪些功能
        tool_choice="auto"  # 自动选择是否使用工具，由AI根据上下文决定
    )

    # 处理函数调用的主循环
    # 当AI决定需要调用工具时，进入循环处理，直到AI给出最终答案
    while response.choices[0].message.tool_calls is not None:
        # 将AI的响应（包含工具调用请求）添加到对话历史
        # 这样可以保持完整的对话上下文
        messages.append(response.choices[0].message)

        # 遍历AI请求的每个工具调用
        # AI可能同时请求调用多个工具，需要逐一处理
        for tool_call in response.choices[0].message.tool_calls:
            # 解析工具调用的参数
            args = tool_call.function.arguments  # 获取工具参数（JSON字符串格式）
            args = json.loads(args)  # 将JSON字符串解析为Python字典，便于传递给函数
            
            # 获取工具名并动态调用对应的工具函数
            function_name = tool_call.function.name  # 获取AI要调用的工具函数名
            invoke_fun = getattr(ft, function_name)  # 从function_tools模块动态获取对应的函数对象
            result = invoke_fun(**args)  # 使用解包的参数执行工具函数并获取结果
            # print(f"工具调用结果：{result}")  # 调试用，可以打印中间结果

            # 将工具执行结果添加到对话历史
            # 这样AI就能看到工具调用的结果，并基于此生成最终回答
            messages.append({
                "role": "tool",  # 消息角色标识为工具响应
                "content": f"{json.dumps(result)}",  # 工具执行结果，转换为JSON格式
                "tool_call_id": tool_call.id  # 对应的工具调用ID，用于关联请求和响应
            })

        # 再次调用智谱AI API，传入包含工具执行结果的完整对话历史
        # AI会基于工具返回的结果生成最终回答
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 继续使用相同的模型
            messages=messages,  # 包含所有历史消息、工具调用请求和工具响应
            tools=tools  # 继续提供工具列表，以防AI需要进一步调用工具
        )
    
    # 输出AI的最终回答
    # 当AI不再需要调用工具时，循环结束，输出最终的回答内容
    print(response.choices[0].message.content)

        

