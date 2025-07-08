# 导入必要的库
import os  # 操作系统接口，用于访问环境变量
from dotenv import load_dotenv, find_dotenv  # 用于加载.env文件中的环境变量
from openai import OpenAI  # OpenAI API客户端，用于与智谱AI进行交互
import json  # JSON数据处理库，用于解析和序列化JSON数据
import function_tools as ft  # 导入自定义的工具函数模块，包含百度搜索等功能
import gradio as gr  # Gradio库，用于创建Web界面


def weather_query(user_message, chat_history, platform, model):
    """
    处理天气查询的函数
    Args:
        user_message: 用户输入的天气查询消息
        chat_history: 聊天历史记录
        platform: 选择的平台（zhipu或openai）
        model: 选择的模型
    Returns:
        tuple: (空字符串, 更新后的聊天历史)
    """
    # 根据平台选择客户端
    if platform == "zhipu":
        current_client = zhipu_client
        # 确保使用智谱AI支持的模型
        if model not in ["glm-4-flash", "glm-4"]:
            model = "glm-4-flash"
    else:
        current_client = openai_client
        # 确保使用OpenAI支持的模型
        if model not in ["gpt-4o-mini", "gpt-3.5-turbo"]:
            model = "gpt-4o-mini"
    
    # 构建消息列表
    messages = [
        {"role": "system", "content": "你是一个专业的天气查询助手，可以帮助用户查询详细的天气信息，包括温度、湿度、空气质量、穿衣建议、健康建议和出行建议等。回答时必须明确说明用户所要查询的具体日期，例如：”明天的日期是7月9日，天气是，今天的日期是7月8日”，并将天气信息以清晰、结构化的方式呈现给用户。不需要要求用户补充问题，直接按问题调用工具获取最新天气数据。"},
    ]
    
    # 添加对话历史（保留最近3轮对话）
    for user_msg, ai_msg in chat_history[-3:]:
        messages.extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": ai_msg}
        ])
    
    # 添加当前用户消息
    messages.append({"role": "user", "content": user_message})
    
    # 调用AI
    response = current_client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    # 处理工具调用
    while response.choices[0].message.tool_calls is not None:
        # 直接添加assistant消息
        messages.append(response.choices[0].message)
        
        for tool_call in response.choices[0].message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            function_name = tool_call.function.name
            invoke_fun = getattr(ft, function_name)
            result = invoke_fun(**args)
            
            messages.append({
                "role": "tool",
                "content": json.dumps(result, ensure_ascii=False),
                "tool_call_id": tool_call.id
            })
        
        response = current_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools
        )
    
    # 获取AI回复并更新聊天历史
    ai_reply = response.choices[0].message.content
    chat_history.append((user_message, ai_reply))
    return "", chat_history

def clear_chat():
    """清空聊天历史"""
    return [], []

def update_model_choices(platform):
    """根据选择的平台更新模型选项"""
    if platform == "zhipu":
        return gr.Dropdown(choices=["glm-4-flash", "glm-4"], value="glm-4-flash")
    else:
        return gr.Dropdown(choices=["gpt-4o-mini", "gpt-3.5-turbo"], value="gpt-4o-mini")

if __name__ == "__main__":
    # 加载环境变量
    load_dotenv(find_dotenv())
    
    # 初始化OpenAI客户端
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    
    # 初始化智谱AI客户端
    zhipu_client = OpenAI(
        api_key=os.getenv("ZHIPU_API_KEY"),
        base_url=os.getenv("ZHIPU_BASE_URL")
    )
    
    # 定义可用工具
    tools = [ft.BAIDU_SEARCH, ft.WEATHER_SEARCH]
    
    # 创建Gradio界面
    with gr.Blocks(title="天气查询助手") as demo:
        gr.Markdown("# 智能天气查询助手")
        gr.Markdown("输入城市名称或天气相关问题，我会帮您查询最新的天气信息！")
        
        # 创建左右布局
        with gr.Row():
            # 左侧聊天区域
            with gr.Column(scale=3):
                # 创建聊天记录显示区域
                chatbot = gr.Chatbot(
                    [],
                    height=500,
                    label="对话历史",
                    placeholder="欢迎使用天气查询助手！请输入您想查询的城市天气信息。"
                )
                
                # 创建输入框和按钮
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="请输入天气查询，如：北京今天天气怎么样？",
                        lines=2,
                        label="天气查询",
                        scale=4
                    )
                    send = gr.Button("查询")
                
                # 添加清空按钮
                clear = gr.Button("清空对话")
                
                # 添加示例问题
                gr.Examples(
                    examples=[
                        "北京今天天气怎么样？",
                        "上海明天会下雨吗？",
                        "广州这周的天气预报",
                        "深圳现在的温度是多少？",
                        "杭州适合穿什么衣服？"
                    ],
                    inputs=msg,
                    label="示例查询"
                )
            
            # 右侧模型选择区域
            with gr.Column(scale=1):
                gr.Markdown("### 模型设置")
                
                # 平台选择
                platform_dropdown = gr.Dropdown(
                    choices=["openai", "zhipu"],
                    value="openai",
                    label="选择平台",
                    info="选择AI服务平台"
                )
                
                # 模型选择
                model_dropdown = gr.Dropdown(
                    choices=["gpt-4o-mini", "glm-4-flash"],
                    value="gpt-4o-mini",
                    label="选择模型",
                    info="选择对话模型"
                )
                
                # # 模型信息显示
                # gr.Markdown("""
                # ### 📋 使用说明
                # **OpenAI平台：**
                # - gpt-4o-mini：快速响应
                # - gpt-3.5-turbo：经典模型
                
                # **智谱AI平台：**
                # - glm-4-flash：高速处理
                # - glm-4：标准模型
                
                # ### 🌟 功能特点
                # - 实时天气查询
                # - 多城市支持
                # - 详细天气信息
                # - 穿衣建议
                # """)
        
        # 绑定事件处理函数
        msg.submit(weather_query, [msg, chatbot, platform_dropdown, model_dropdown], [msg, chatbot])
        send.click(weather_query, [msg, chatbot, platform_dropdown, model_dropdown], [msg, chatbot])
        clear.click(clear_chat, outputs=[chatbot, msg])
        
        # 平台选择变化时更新模型选项
        platform_dropdown.change(update_model_choices, inputs=[platform_dropdown], outputs=[model_dropdown])
    
    # 启动界面
    demo.launch()

        

