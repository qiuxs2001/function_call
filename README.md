# 🌤️ 智能天气查询助手

一个基于 AI 的智能天气查询系统，支持多种 AI 模型（OpenAI GPT、智谱 AI GLM）和工具调用功能，提供全面的天气信息查询服务。

## ✨ 功能特性

### 🌡️ 天气信息查询
- **基础天气数据**：温度、体感温度、天气描述、湿度、气压、能见度、风速风向
- **空气质量监测**：AQI 指数、PM2.5、PM10、CO、NO2、O3 等污染物浓度
- **智能生活建议**：根据天气和空气质量提供穿衣、健康、出行建议
- **实时数据**：基于 OpenWeatherMap API 获取最新天气信息

### 🤖 AI 模型支持
- **OpenAI GPT**：支持 GPT-4o-mini 等模型
- **智谱 AI GLM**：支持 GLM-4-Flash 等模型
- **Function Calling**：AI 自动调用工具获取实时数据
- **温度控制**：可调节 AI 响应的随机性和创造性

### 🔧 扩展工具
- **百度搜索**：基于百度千帆 AI 搜索 API
- **汇率查询**：人民币与外币汇率信息
- **数学运算**：基础数学计算功能

### 🖥️ 用户界面
- **Web 界面**：基于 Gradio 的现代化 Web UI
- **命令行界面**：支持脚本直接调用
- **预设示例**：快速开始使用的示例问题

## 📁 项目结构

```
function_call/
├── weather_search_code_邱子轩.py    # Gradio Web 界面主程序
├── function_call_code5.py           # 命令行版本示例
├── function_tools.py                # 工具函数模块
├── .env                            # 环境变量配置文件
├── .gitignore                      # Git 忽略文件
└── README.md                       # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 网络连接（用于 API 调用）

### 安装依赖

```bash
pip install gradio openai python-dotenv requests
```

### 配置环境变量

创建 `.env` 文件并配置以下环境变量：

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# 智谱 AI API 配置
ZHIPU_API_KEY=your_zhipu_api_key
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# OpenWeatherMap API 配置（可选，代码中已包含演示密钥）
OPENWEATHER_API_KEY=your_openweather_api_key
```

### 运行应用

#### Web 界面版本

```bash
python weather_search_code_邱子轩.py
```

访问 `http://localhost:7860` 使用 Web 界面。

#### 命令行版本

```bash
python function_call_code5.py
```

## 📖 使用指南

### Web 界面使用

1. **输入问题**：在文本框中输入天气查询问题
2. **选择模型**：选择 OpenAI 或智谱 AI 模型
3. **调节温度**：设置 AI 响应的随机性（0.0-1.0）
4. **提交查询**：点击提交按钮获取结果
5. **查看结果**：在回答区域查看详细的天气信息

### 示例查询

- "北京今天的天气怎么样？"
- "上海的空气质量如何？"
- "广州今天的湿度是多少？"
- "深圳今天适合穿什么衣服？"
- "杭州今天适合户外运动吗？"

### API 调用示例

```python
from function_tools import get_current_weather

# 查询北京天气
result = get_current_weather("北京")
print(result)
```

## 🔧 配置说明

### AI 模型配置

- **OpenAI 模型**：需要有效的 OpenAI API 密钥
- **智谱 AI 模型**：需要智谱 AI 平台的 API 密钥
- **温度参数**：控制 AI 回答的随机性
  - 0.0：完全确定性回答
  - 1.0：最大随机性回答
  - 推荐值：0.7（平衡确定性和创造性）

### 天气 API 配置

- 使用 OpenWeatherMap API 获取天气数据
- 支持全球主要城市查询
- 包含基础天气和空气质量数据

## 🛠️ 开发说明

### 核心模块

#### `function_tools.py`
- 定义所有工具函数和 API 调用
- 包含天气查询、搜索、汇率等功能
- 符合 OpenAI Function Calling 规范

#### `weather_search_code_邱子轩.py`
- Gradio Web 界面实现
- AI 模型调用和工具集成
- 用户交互逻辑

### 扩展开发

1. **添加新工具**：在 `function_tools.py` 中定义新的工具函数
2. **修改界面**：在主程序中调整 Gradio 组件
3. **集成新模型**：添加新的 AI 模型支持

## 📝 注意事项

### API 密钥安全
- 不要将 API 密钥提交到版本控制系统
- 使用环境变量存储敏感信息
- 定期更换 API 密钥

### 使用限制
- OpenWeatherMap API 有调用频率限制
- AI 模型 API 可能产生费用
- 网络连接质量影响响应速度

### 错误处理
- 检查网络连接状态
- 验证 API 密钥有效性
- 处理城市名称不存在的情况

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 📄 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [OpenWeatherMap](https://openweathermap.org/) - 天气数据 API
- [Gradio](https://gradio.app/) - Web 界面框架
- [OpenAI](https://openai.com/) - AI 模型 API
- [智谱 AI](https://open.bigmodel.cn/) - AI 模型 API

---

**作者**：邱子轩  
**版本**：1.0  
**更新时间**：2024年