# -*- coding: utf-8 -*-
"""
智能天气查询助手 - 工具函数模块

本模块定义了AI助手可以调用的各种工具函数，主要包括：
- 天气查询功能（OpenWeatherMap API）
- 百度搜索功能（百度千帆AI搜索API）
- 汇率查询功能（聚合数据API）
- 基础数学运算功能

每个工具都包含两部分：
1. 工具定义（符合OpenAI Function Calling规范）
2. 具体实现函数

主要依赖：
- requests: HTTP请求库
- json: JSON数据处理
- logging: 日志记录
- datetime: 时间处理

作者：AI Assistant
版本：1.0
"""

from gradio import data_classes  # Gradio数据类（当前未使用）
import requests  # HTTP请求库，用于API调用
import json  # JSON数据处理
import logging  # 日志记录
import os  # 操作系统接口

# 配置日志系统
# 设置日志级别为INFO，记录重要的操作信息
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ==================== 工具定义部分 ====================
# 以下是符合OpenAI Function Calling规范的工具定义
# AI模型会根据这些定义来决定何时调用哪个工具

# 百度搜索工具定义
# 使用百度千帆AI搜索API进行互联网信息检索
BAIDU_SEARCH = {
    "type": "function",
    "function": {
        "name": "baidu_search",
        "description": "根据用户提供信息通过互联网搜索引擎查询对应的信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "description": "需要查询的信息",
                    "type": "string"
                }   
            },
            "required": ["query"]
        }
    }
}
# 汇率查询工具定义
# 使用聚合数据API查询人民币汇率信息
# 注意：这里的函数名应该是huiju_search，但定义中错误地写成了baidu_search
HUIJU_SEARCH = {
    "type": "function",
    "function": {
        "name": "huiju_search",  # 修正：应该是huiju_search而不是baidu_search
        "description": "查询人民币与外币兑换的汇率信息，单位为100外币",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}
# 天气查询工具定义
# 使用OpenWeatherMap API查询城市天气信息
# 这是当前应用的核心功能工具
WEATHER_SEARCH = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "查询指定城市的实时天气情况，包括当前温度、湿度、风力等详细信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "description": "要查询天气的城市名称，如'北京'、'上海'等",
                    "type": "string"
                }
            },
            "required": ["city"]
        }
    }
}

# ==================== 工具实现函数部分 ====================

def get_current_weather(city):
    """
    获取指定城市的详细天气信息
    
    这是应用的核心功能函数，通过OpenWeatherMap API获取全面的天气数据，
    包括基础气象信息、空气质量数据和智能生活建议。
    
    功能特点：
    - 基础天气：温度、体感温度、湿度、气压、能见度、风速风向
    - 空气质量：AQI指数、PM2.5、PM10、CO、NO2、O3等污染物浓度
    - 生活建议：根据温度和空气质量提供穿衣、健康、出行建议
    - 时间信息：记录查询的具体日期和时间
    
    参数:
        city (str): 要查询天气的城市名称，支持中英文城市名
    
    返回:
        dict: 包含完整天气信息的字典，包括：
            - query_date: 查询日期
            - query_time: 查询时间
            - city: 城市名称
            - temperature: 当前温度
            - feels_like: 体感温度
            - humidity: 湿度百分比
            - pressure: 大气压强
            - visibility: 能见度（公里）
            - wind_speed: 风速
            - wind_direction: 风向（中文描述）
            - air_quality_index: 空气质量指数
            - pm2_5, pm10, co, no2, o3: 各种污染物浓度
            - clothing_suggestion: 穿衣建议
            - health_suggestion: 健康建议
            - travel_suggestion: 出行建议
    
    异常:
        如果API调用失败或城市不存在，返回包含error字段的字典
    """
    import datetime
    
    log.info(f"开始查询城市天气信息: city={city}")
    
    # OpenWeatherMap API密钥配置
    # 注意：在生产环境中应该从环境变量获取API密钥以确保安全性
    # api_key = os.getenv("OPENWEATHER_API_KEY")
    api_key = "b79482acf0b4b85e25ffcb74eaf9aaa8"  # 硬编码密钥（仅用于演示）
    if not api_key:
        return {"error": "OpenWeather API密钥未配置，请在.env文件中添加OPENWEATHER_API_KEY"}
    
    # 获取当前查询时间信息
    # 记录查询的具体时间，便于用户了解数据的时效性
    current_time = datetime.datetime.now()
    query_date = current_time.strftime("%Y年%m月%d日")  # 格式：2024年01月15日
    query_time = current_time.strftime("%H:%M")        # 格式：14:30
    
    # 第一步：通过地理编码API获取城市的经纬度坐标
    # OpenWeatherMap需要经纬度坐标来查询天气信息
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={api_key}"
    geocoding_response = requests.get(geocoding_url)
    geocoding_data = geocoding_response.json()

    if geocoding_response.status_code == 200 and len(geocoding_data) > 0:
        # 获取第一个匹配结果的坐标
        lat = geocoding_data[0]["lat"]  # 纬度
        lon = geocoding_data[0]["lon"]  # 经度
        log.info(f"成功获取{city}的坐标 - 纬度：{lat}, 经度：{lon}")
    else:
        log.error(f"无法找到城市 {city} 的坐标信息")
        return {"error": f"无法找到城市 {city} 的坐标信息"}
    
    # 第二步：并行获取天气信息和空气质量信息
    # 使用metric单位系统（摄氏度、米/秒等）和中文语言包
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=zh_cn"
    weather_response = requests.get(weather_url)
    
    # 获取空气质量信息（AQI和各种污染物浓度）
    air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    air_response = requests.get(air_url)
    
    # 第三步：处理天气API响应数据
    if weather_response.status_code == 200:
        weather_data = weather_response.json()
        log.info(f"成功获取{city}的天气数据")
        
        # 提取基础天气信息
        temp = weather_data['main']['temp']                    # 当前温度（摄氏度）
        feels_like = weather_data['main']['feels_like']        # 体感温度（摄氏度）
        humidity = weather_data['main']['humidity']            # 湿度（百分比）
        pressure = weather_data['main']['pressure']            # 大气压强（hPa）
        visibility = weather_data.get('visibility', 0) / 1000  # 能见度（转换为公里）
        wind_speed = weather_data['wind']['speed']             # 风速（米/秒）
        wind_deg = weather_data['wind'].get('deg', 0)          # 风向角度（度）
        
        # 提取天气描述信息
        weather_desc = weather_data['weather'][0]['description']  # 天气描述（中文）
        weather_main = weather_data['weather'][0]['main']         # 主要天气类型（英文）
        
        # 构建基础天气信息字典
        weather_info = {
            "query_date": query_date,                              # 查询日期
            "query_time": query_time,                              # 查询时间
            "city": weather_data.get('name', city),                # 城市名称（API返回的标准名称）
            "country": weather_data['sys']['country'],             # 国家代码
            "temperature": round(temp, 1),                         # 当前温度（保留1位小数）
            "feels_like": round(feels_like, 1),                    # 体感温度（保留1位小数）
            "description": weather_desc,                           # 天气描述
            "humidity": humidity,                                  # 湿度百分比
            "pressure": pressure,                                  # 大气压强
            "visibility": round(visibility, 1),                   # 能见度（公里）
            "wind_speed": wind_speed,                              # 风速
            # 风向计算：根据角度转换为中文风向描述
            # 使用16方位风向，每个方位占22.5度
            "wind_direction": (
                "北风" if wind_deg >= 337.5 or wind_deg < 22.5 else
                "东北风" if wind_deg < 67.5 else
                "东风" if wind_deg < 112.5 else
                "东南风" if wind_deg < 157.5 else
                "南风" if wind_deg < 202.5 else
                "西南风" if wind_deg < 247.5 else
                "西风" if wind_deg < 292.5 else
                "西北风"
            )
        }
        
        # 第四步：处理空气质量数据
        if air_response.status_code == 200:
            air_data = air_response.json()
            aqi = air_data['list'][0]['main']['aqi']              # 空气质量指数（1-5级）
            components = air_data['list'][0]['components']        # 各种污染物浓度
            
            # 将空气质量信息添加到天气信息字典中
            weather_info.update({
                "air_quality_index": aqi,
                # AQI等级转换：1=优，2=良，3=轻度污染，4=中度污染，5=重度污染
                "air_quality_level": (
                    "优" if aqi == 1 else
                    "良" if aqi == 2 else
                    "轻度污染" if aqi == 3 else
                    "中度污染" if aqi == 4 else
                    "重度污染"
                ),
                "pm2_5": components.get('pm2_5', 0),             # PM2.5浓度（μg/m³）
                "pm10": components.get('pm10', 0),               # PM10浓度（μg/m³）
                "co": components.get('co', 0),                   # 一氧化碳浓度（μg/m³）
                "no2": components.get('no2', 0),                 # 二氧化氮浓度（μg/m³）
                "o3": components.get('o3', 0)                    # 臭氧浓度（μg/m³）
            })
        
        # 第五步：生成智能生活建议
        # 根据温度、空气质量、天气状况等因素提供个性化建议
        weather_info.update({
            # 穿衣建议：根据温度范围提供穿衣指导
            "clothing_suggestion": (
                f"根据当前温度{round(temp, 1)}°C，建议" + 
                ("穿着轻薄衣物" if temp > 25 else
                 "穿着适中衣物" if temp > 15 else
                 "穿着保暖衣物")
            ),
            # 健康建议：根据空气质量指数提供健康指导
            "health_suggestion": (
                f"空气质量{weather_info.get('air_quality_level', '未知')}，" +
                ("适宜户外活动" if weather_info.get('air_quality_index', 5) <= 2 else
                 "建议减少户外活动")
            ),
            # 出行建议：综合天气状况和风速提供出行指导
            "travel_suggestion": (
                f"当前天气{weather_desc}，" +
                ("适宜出行" if 'rain' not in weather_desc.lower() and wind_speed < 5 else
                 "出行请注意安全")
            )
        })
        
        return weather_info
        
    else:
        # 天气API调用失败的错误处理
        log.error(f"获取天气数据失败，状态码：{weather_response.status_code}")
        return {"error": f"获取 {city} 天气信息失败，请检查城市名称是否正确"}
def weather_search(query):
    """
    城市天气搜索函数（聚合数据API版本）
    
    注意：此函数当前未被使用，主要天气查询功能由get_current_weather函数实现。
    这是一个备用的天气查询实现，使用聚合数据的城市搜索API。
    
    参数:
        query (str): 查询参数（当前未使用）
    
    返回:
        None: 函数只打印结果，不返回数据
    
    API说明:
        - 使用聚合数据的城市搜索API
        - API密钥需要在聚合数据平台申请
        - 当前实现仅作为示例代码
    """
    import requests

    # 聚合数据 - 城市搜索API配置
    # 注意：这是示例代码，实际使用时需要根据业务需求修改

    # API基本配置
    apiUrl = 'http://apis.juhe.cn/atmos/citys'  # 聚合数据城市搜索API端点
    apiKey = "e5263620236bf8e2285dba6dad35cc3f"  # API密钥（需要在聚合数据平台申请）

    # 请求参数配置
    requestParams = {
        'key': apiKey,      # API密钥
        'q': '',           # 查询关键词（城市名称）
        'language': '',    # 语言设置
        'limit': '',       # 返回结果数量限制
        'offset': '',      # 结果偏移量
    }

    # 发起HTTP GET请求
    response = requests.get(apiUrl, params=requestParams)

    # 处理API响应
    if response.status_code == 200:
        responseResult = response.json()
        # 请求成功，打印结果（实际应用中应该返回处理后的数据）
        print(responseResult)
    else:
        # 请求失败，打印错误信息
        print('请求异常')

def huiju_search(query):
    """
    人民币汇率查询函数
    
    使用聚合数据API查询人民币与外币的兑换汇率信息。
    注意：当前此函数在工具定义中存在命名错误，实际未被AI调用。
    
    参数:
        query (str): 查询参数（当前未使用）
    
    返回:
        None: 函数只打印结果，不返回数据
    
    API说明:
        - 使用聚合数据的人民币牌价API
        - 汇率单位为100外币对应的人民币金额
        - 支持多种银行的汇率数据
    
    使用示例:
        查询美元、欧元等主要货币的实时汇率
    """
    import requests

    # 聚合数据 - 人民币牌价API配置
    # 用于查询人民币与各种外币的实时汇率

    # API基本配置
    apiUrl = 'http://web.juhe.cn/finance/exchange/rmbquot'  # 人民币牌价API端点
    apiKey = "e5263620236bf8e2285dba6dad35cc3f"  # API密钥（需要在聚合数据平台申请）

    # 请求参数配置
    requestParams = {
        'key': apiKey,     # API密钥
        'type': '',        # 汇率类型（如：美元USD、欧元EUR等）
        'bank': '',        # 银行代码（不同银行的汇率可能略有差异）
    }

    # 发起HTTP GET请求
    response = requests.get(apiUrl, params=requestParams)

    # 处理API响应
    if response.status_code == 200:
        responseResult = response.json()
        # 请求成功，打印汇率数据（实际应用中应该返回格式化的汇率信息）
        print(responseResult)
    else:
        # 请求失败，打印错误信息
        print('请求异常')

def baidu_search(query):
    """
    百度千帆AI搜索函数
    
    使用百度千帆AI搜索API进行互联网信息检索，提供智能搜索结果。
    该函数包含完整的错误处理和调试信息，确保搜索功能的稳定性。
    
    功能特点：
    - 使用百度千帆AI搜索API
    - 支持自然语言查询
    - 完整的错误处理机制
    - 详细的日志记录
    - 智能结果解析
    
    参数:
        query (str): 用户的搜索查询内容
    
    返回:
        str: 搜索结果内容，如果出错则返回错误信息
    
    异常处理:
        - 网络连接错误
        - API认证失败
        - JSON解析错误
        - 响应格式异常
    
    注意:
        需要有效的百度千帆API访问令牌
    """
    try:
            log.info(f"开始百度搜索: query={query}")
            
            # 百度千帆AI搜索API配置
            uri = "https://qianfan.baidubce.com/v2/ai_search"  # API端点
            heads = {
                # 百度千帆API访问令牌（Bearer Token认证）
                "Authorization": "Bearer bce-v3/ALTAK-aRMg6MEoJByl4VgjTH7HP/e7e1bda63554815c23176e054139cd66203d0834",
                "Content-Type": "application/json"  # 请求内容类型
            }

            # 构建API请求载荷
            # 遵循百度千帆AI搜索API的消息格式规范
            payload = {
                "messages": [
                    {
                        "role": "user",      # 用户角色
                        "content": query     # 搜索查询内容
                    }
                ],
                "stream": False  # 非流式响应
            }
            
            log.info(f"请求载荷: {json.dumps(payload, ensure_ascii=False)}")
            
            # 发起POST请求到百度千帆AI搜索API
            response = requests.post(
                uri,
                json=payload,      # JSON格式的请求体
                headers=heads,     # 请求头
                timeout=30         # 30秒超时
            )
        
        # 第一步：检查HTTP响应状态
            log.info(f"HTTP状态码: {response.status_code}")
            if response.status_code != 200:
                log.error(f"API请求失败，状态码: {response.status_code}")
                return f"搜索失败：HTTP {response.status_code}"
            
            # 第二步：检查响应内容是否为空
            if not response.text:
                log.warning("API返回空响应")
                return "搜索结果为空"
            
            # 第三步：记录原始响应用于调试
            # 只记录前500字符以避免日志过长
            log.info(f"API原始响应: {response.text[:500]}...")
        
        # 第四步：解析JSON响应
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError as e:
                log.error(f"JSON解析失败: {e}")
                return f"搜索失败：响应格式错误 - {str(e)}"
            
            # 第五步：分析响应数据结构
            log.info(f"解析后的数据结构: {list(result.keys()) if isinstance(result, dict) else type(result)}")
            
            # 第六步：智能提取搜索结果
            if isinstance(result, dict):
                # 定义可能包含搜索结果的字段名列表
                # 按优先级排序，优先检查最可能的字段
                possible_fields = ['references', 'results', 'data', 'content', 'answer', 'response']
                found_field = None
                
                # 遍历可能的字段名，寻找包含搜索结果的字段
                for field in possible_fields:
                    if field in result:
                        found_field = field
                        log.info(f"找到数据字段: {field}")
                        break
                
                if found_field:
                    # 找到预期字段，返回其内容
                    return f"搜索结果: {result[found_field]}"
                else:
                    # 未找到预期字段，返回完整结果并记录警告
                    log.warning(f"未找到预期字段，返回完整结果。可用字段: {list(result.keys())}")
                    return f"搜索结果: {result}"
            else:
                # 响应不是字典类型，直接返回
                log.warning(f"意外的数据类型: {type(result)}")
                return f"搜索结果: {result}"
            
    # 异常处理：捕获各种可能的错误
    except requests.exceptions.RequestException as e:
            # 网络相关错误（连接超时、DNS解析失败等）
            log.error(f"网络请求错误: {e}")
            return f"搜索失败：网络错误 - {str(e)}"
    except Exception as e:
            # 其他未预期的错误
            log.error(f"搜索过程中发生未知错误: {e}")
            return f"搜索失败：{str(e)}"

# ==================== 数学运算工具函数 ====================
# 以下是基础的数学运算函数，可以被AI调用来执行计算任务

def multiply_two_numbers(a, b):
    """
    两数相乘函数
    
    参数:
        a (float/int): 第一个数字
        b (float/int): 第二个数字
    
    返回:
        float/int: 两数的乘积
    """
    result = a * b
    return result

def add_two_numbers(a, b):
    """
    两数相加函数
    
    参数:
        a (float/int): 第一个数字
        b (float/int): 第二个数字
    
    返回:
        float/int: 两数的和
    """
    result = a + b
    return result

def subtract_two_numbers(a, b):
    """
    两数相减函数
    
    参数:
        a (float/int): 被减数
        b (float/int): 减数
    
    返回:
        float/int: 两数的差（a - b）
    """
    result = a - b
    return result

def divide_two_numbers(a, b):
    """
    两数相除函数
    
    参数:
        a (float/int): 被除数
        b (float/int): 除数
    
    返回:
        float: 两数的商（a / b）
    
    注意:
        如果除数b为0，会抛出ZeroDivisionError异常
    """
    result = a / b
    return result

# ==================== 数学运算工具定义 ====================
# 除法运算工具定义（示例）
# 注意：当前应用主要专注于天气查询，数学运算工具未被激活使用

DIVIDE_TWO_NUMBERS = {
    "type": "function",
    "function": {
        "name": "divide_two_numbers",  # 除法函数名
        "description": "两个数相除",  # 除法函数描述
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "被除数（第一个数字）"
                },
                "b": {
                    "type": "number",
                    "description": "除数（第二个数字，不能为0）"
                }
            },
            "required": [
                "a", "b"
            ]
        }
    }
}

# 注意：可以类似地定义其他数学运算工具
# 如：ADD_TWO_NUMBERS, SUBTRACT_TWO_NUMBERS, MULTIPLY_TWO_NUMBERS
# 但当前应用专注于天气查询功能，这些工具暂未启用