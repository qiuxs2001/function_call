# # 导入必要的库
# import os  # 操作系统接口，用于访问环境变量
# from dotenv import load_dotenv, find_dotenv  # 用于加载.env文件中的环境变量
# from openai import OpenAI  # OpenAI API客户端，用于与智谱AI进行交互
# import json  # JSON数据处理库，用于解析和序列化JSON数据
# import requests  # HTTP请求库，用于发送网络请求

# # 加载环境变量文件
# load_dotenv(find_dotenv())

# # 初始化OpenAI兼容的客户端，用于连接智谱AI服务
# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),  # 从环境变量获取智谱AI的API密钥
#     base_url=os.getenv("OPENAI_BASE_URL")  # 从环境变量获取智谱AI的API基础URL
# )

# def get_rmb_exchange():
#     url = "http://web.juhe.cn/finance/exchange/rmbquot" 
#     requestParams = {
#         'key': "e5263620236bf8e2285dba6dad35cc3f",
#         'type': '0',
#         'bank': '1',
#     }
#     response = requests.get(url=url,params=requestParams)
#     return response.text

# def multiply_two_numbers(a, b):
#     result = a * b
#     return result

# def division_two_numbers(a, b):
#     result = a / b
#     return result

# tools = [
#         {
#         "type": "function",
#         "function": {
#             "name": "get_rmb_exchange",
#             "description": "100外币兑换成人民币, 买入和卖出价格实时查询。",
#             "parameters": {
#                 "type": "object",
#                 "properties": {},      # 空对象
#                 "required": []         # 空列表
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "multiply_two_numbers",
#             "description": "两个数相乘",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "a": {
#                         "type": "number",
#                         "description": "第一个数字"
#                     },
#                     "b":{
#                         "type": "number",
#                         "description": "第二个数字"
#                     }
#                 },
#                 "required": [
#                     "a", "b"
#                 ]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "division_two_numbers",
#             "description": "两个数相除",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "a": {
#                         "type": "number",
#                         "description": "被除数"
#                     },
#                     "b":{
#                         "type": "number",
#                         "description": "除数"
#                     }
#                 },
#                 "required": [
#                     "a", "b"
#                 ]
#             }
#         }
#     }]

# messages = []
# messages.append({"role": "system", "content": (
#                  "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息。"
#                  "人民币兑换外币时，需要使用以下步骤："
#                  "1. 先调用get_rmb_exchange()获取汇率数据"
#                  "2. 找到对应外币的卖出价(fSellPri)，该价格表示100单位外币兑换的人民币数量"
#                  "3. 使用multiply_two_numbers函数计算：人民币金额 * 100，得到中间结果"
#                  "4. 使用division_two_numbers函数计算：中间结果 / 卖出价，得到最终外币数量"
#                  "例如：20000人民币兑换美元，美元卖出价719.37，计算步骤为：20000*100=2000000，然后2000000/719.37≈2780美元"
# )})
# # 函数调用
# messages.append({"role": "user", "content": "20000元人民币能兑换多少美元？"})

# response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         tools=tools,
#         tool_choice="auto"
#     )

# while response.choices[0].message.tool_calls != None:
#     # 将AI的响应（包含工具调用请求）添加到对话历史
#     messages.append(response.choices[0].message)
    
#     # 处理所有工具调用
#     for tool_call in response.choices[0].message.tool_calls:
#         args = json.loads(tool_call.function.arguments)
#         print("工具调用信息：", args)

#         # 调用当前模块中的函数
#         function = globals()[tool_call.function.name]
#         function_result = function(**args)
#         print("工具调用结果：", function_result)

#         # 将工具调用结果添加到消息列表中
#         messages.append({
#             "role": "tool",
#             "content": f"{json.dumps(function_result)}",
#             "tool_call_id": tool_call.id
#         })

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",  # 填写需要调用的模型名称
#         messages=messages,
#         tools=tools,
#     )

# result = response.choices[0].message.content
# print("大模型输出信息", result)