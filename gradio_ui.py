# -*- coding: utf-8 -*-
"""
智能天气查询助手 - Gradio Web界面

本模块提供基于Gradio的Web界面，用户可以通过友好的界面查询天气信息。
支持多种AI模型（OpenAI GPT、智谱AI GLM）和工具调用功能。

主要功能：
- 天气信息查询（温度、湿度、空气质量等）
- 生活建议（穿衣、健康、出行建议）
- 多模型支持（OpenAI、智谱AI）
- 可调节的AI响应温度参数

"""

import gradio as gr  # Gradio Web界面框架
import os  # 操作系统接口，用于环境变量访问
from dotenv import load_dotenv, find_dotenv  # 环境变量加载工具
from openai import OpenAI  # OpenAI API客户端（兼容智谱AI）
import json  # JSON数据处理
import function_tools as ft  # 自定义工具函数模块

# 加载环境变量配置文件（.env）
# find_dotenv()会自动查找.env文件，load_dotenv()加载其中的环境变量
load_dotenv(find_dotenv())

def chatbot_interface(query, model_input, temperature):
    """
    聊天机器人核心接口函数
    
    处理用户查询请求，根据选择的AI模型调用相应的API，
    支持工具调用（Function Calling）来获取实时天气数据。
    
    参数:
        query (str): 用户输入的查询问题
        model_input (str): 选择的AI模型 ("openai" 或 "zhipuai")
        temperature (float): AI响应的随机性控制参数 (0.0-1.0)
                           0.0表示确定性回答，1.0表示最大随机性
    
    返回:
        str: AI生成的回答内容
    
    异常:
        如果API调用失败或工具调用出错，会直接抛出异常
    """
    # 根据用户选择的模型类型配置不同的API客户端
    if model_input == "zhipuai":
        # 配置智谱AI客户端
        # 使用OpenAI兼容的接口格式，通过base_url指向智谱AI的API端点
        client = OpenAI(
            api_key=os.getenv("ZHIPU_API_KEY"),  # 从环境变量获取智谱AI的API密钥
            base_url=os.getenv("ZHIPU_BASE_URL")  # 智谱AI的API基础URL
        )
        model_name = "glm-4-flash"  # 智谱AI的GLM-4-Flash模型
    else:  # openai
        # 配置OpenAI客户端
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),  # 从环境变量获取OpenAI的API密钥
            base_url=os.getenv("OPENAI_BASE_URL")  # OpenAI的API基础URL（可能是代理地址）
        )
        model_name = "gpt-4o-mini"  # OpenAI的GPT-4o-mini模型
    
    # 定义AI可以调用的工具列表
    # WEATHER_SEARCH是在function_tools模块中定义的天气查询工具
    tools = [ft.WEATHER_SEARCH]
    
    # 构建对话消息列表，遵循OpenAI Chat Completions API格式
    messages = [
        {
            "role": "system", 
            "content": "你是一个专业的天气查询助手，可以帮助用户查询详细的天气信息，包括温度、湿度、空气质量、穿衣建议、健康建议和出行建议等。回答时必须明确说明用户所要查询的具体日期，例如：\"明天的日期是7月9日，天气是，今天的日期是7月8日\"，并将天气信息以清晰、结构化的方式呈现给用户。不需要要求用户补充问题，直接按问题调用工具获取最新天气数据。"
        },
        {"role": "user", "content": query}  # 用户的查询内容
    ]
    
    # 首次调用AI API，获取初始响应
    # 如果AI判断需要调用工具，会在响应中包含tool_calls
    response = client.chat.completions.create(
        model=model_name,  # 使用前面配置的模型名称
        messages=messages,  # 对话消息历史
        tools=tools,  # 可用工具列表
        tool_choice="auto",  # 让AI自动决定是否调用工具
        temperature=temperature  # 控制回答的随机性
    )
    
    # 处理工具调用循环
    # 如果AI在响应中包含工具调用请求，则进入循环处理
    while response.choices[0].message.tool_calls is not None:
        # 将AI的工具调用请求添加到消息历史中
        # 这样AI就能知道它之前请求了哪些工具调用
        messages.append(response.choices[0].message)
        
        # 遍历处理每个工具调用请求
        for tool_call in response.choices[0].message.tool_calls:
            # 解析工具调用的参数（JSON格式字符串转为Python字典）
            args = json.loads(tool_call.function.arguments)
            
            # 动态获取并调用对应的工具函数
            function_name = tool_call.function.name  # 获取要调用的函数名
            invoke_fun = getattr(ft, function_name)  # 从function_tools模块获取函数对象
            result = invoke_fun(**args)  # 使用解析的参数调用函数
            
            # 将工具调用的结果添加到消息历史中
            # AI会根据这个结果生成最终的用户回答
            messages.append({
                "role": "tool",  # 标识这是工具调用的结果
                "content": json.dumps(result, ensure_ascii=False),  # 工具返回的结果（保持中文字符）
                "tool_call_id": tool_call.id  # 关联到对应的工具调用请求
            })
        
        # 再次调用AI API，让AI根据工具调用结果生成最终回答
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,  # 包含完整对话历史和工具调用结果
            tools=tools,
            temperature=temperature
        )
    
    # 返回AI生成的最终回答内容
    # 此时AI已经基于工具调用结果生成了完整的回答
    return response.choices[0].message.content

# 创建Gradio Web应用界面
# 使用Blocks布局模式，提供更灵活的界面设计
with gr.Blocks(title="智能助手", theme=gr.themes.Soft()) as demo:
    # 创建标题和介绍区域
    with gr.Row():
        # 使用Markdown组件显示应用介绍和功能说明
        gr.Markdown(
            """# 🌤️ 智能天气查询助手
            
            欢迎使用智能天气查询助手！我可以为您提供全面的天气信息，包括：
            
            🌡️ **基础天气**：温度、体感温度、天气描述、湿度、气压、能见度、风速风向
            
            🌬️ **空气质量**：AQI指数、PM2.5、PM10、CO、NO2、O3等污染物浓度
            
            👔 **生活建议**：穿衣建议、健康建议、出行建议
            
            只需输入城市名称，即可获取详细的天气信息和贴心的生活建议！
            """
        )
    
    # 创建输入控制区域
    with gr.Row():
        # 左侧输入区域（占2/3宽度）
        with gr.Column(scale=2):
            # 用户问题输入框，支持多行文本输入
            query = gr.Textbox(label="请输入您的问题", lines=6)

            # 右侧控制区域（占1/3宽度）
            with gr.Column(scale=1):
                # AI模型选择单选框
                # 支持OpenAI GPT和智谱AI GLM两种模型
                model_input = gr.Radio(
                    choices=["openai", "zhipuai"], 
                    label="选择模型", 
                    value="openai"  # 默认选择OpenAI模型
                )
                # AI响应温度控制滑块
                # 温度值影响AI回答的随机性和创造性
                temperature = gr.Slider(
                    minimum=0,      # 最小值：完全确定性回答
                    maximum=1,      # 最大值：最大随机性回答
                    step=0.1,       # 步长
                    label="温度", 
                    value=0.7       # 默认值：平衡确定性和创造性
                )
                # 提交按钮，触发查询处理
                submit_button = gr.Button("提交")

    # 创建输出显示区域
    with gr.Row():
        # AI回答显示文本框，支持多行显示
        text_output = gr.Textbox(label="回答", lines=6)

    # 绑定提交按钮的点击事件
    # 当用户点击提交按钮时，调用chatbot_interface函数处理请求
    submit_button.click(
        fn=chatbot_interface,  # 处理函数
        inputs=[query, model_input, temperature],  # 输入参数：用户问题、模型选择、温度设置
        outputs=[text_output]  # 输出目标：回答显示框
    )


    # 预设示例问题，帮助用户快速开始使用
    # 每个示例包含：[问题文本, 推荐模型, 推荐温度值]
    examples = [
        ["北京今天的天气怎么样？", "openai", 0.7],      # 基础天气查询
        ["上海的空气质量如何？", "zhipuai", 0.5],        # 空气质量专项查询
        ["广州今天的湿度是多少？", "openai", 0.6],        # 特定气象指标查询
        ["深圳今天适合穿什么衣服？", "zhipuai", 0.7],     # 生活建议查询
        ["杭州今天适合户外运动吗？", "openai", 0.8]       # 活动建议查询
    ]
    # 创建示例组件，用户点击示例会自动填充对应的输入值
    gr.Examples(examples, [query, model_input, temperature])

    # 启动Gradio Web应用
    # 默认在本地7860端口启动，可通过浏览器访问
    demo.launch()

    