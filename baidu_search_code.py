# 导入OpenAI库，用于与OpenAI兼容的API进行交互
from openai import OpenAI

# 主程序入口，确保脚本被直接运行时才执行以下代码
if __name__ == '__main__':
    # 初始化OpenAI客户端
    client = OpenAI(
        # 设置API基础URL，指向百度千帆平台的AI搜索服务端点
        base_url="https://qianfan.baidubce.com/v2/ai_search/",
        # 设置API密钥，用于身份验证和授权访问
        api_key="bce-v3/ALTAK-aRMg6MEoJByl4VgjTH7HP/e7e1bda63554815c23176e054139cd66203d0834"
    )

    # 发起聊天完成请求
    response = client.chat.completions.create(
        # 指定使用的AI模型
        model="deepseek-r1",
        # 定义对话消息列表
        messages=[{
            # 设置消息角色为用户
            "role": "user",
            # 设置用户询问的问题内容
            "content": "北京的旅游景区有哪些？"

        }]
    )

    # 打印AI模型返回的第一个回答选择的消息内容
    print(response.choices[0].message.content)
