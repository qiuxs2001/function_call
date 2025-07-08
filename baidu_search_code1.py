# 导入requests库，用于发送HTTP请求
import requests
# 导入json库，用于处理JSON数据
import json

# 主程序入口，确保脚本被直接运行时才执行以下代码
if __name__ == '__main__':
    # 设置百度千帆平台AI搜索服务的API端点URL
    uri = "https://qianfan.baidubce.com/v2/ai_search"
    # 定义HTTP请求头
    heads = {
        # 设置授权令牌，用于API身份验证
        "Authorization": "Bearer bce-v3/ALTAK-aRMg6MEoJByl4VgjTH7HP/e7e1bda63554815c23176e054139cd66203d0834",
        # 设置请求内容类型为JSON格式
        "Content-Type": "application/json"
    }

    # 发送POST请求到百度千帆AI搜索API
    response = requests.post(
        # API端点URL
        uri,
        # 请求体数据，以JSON格式发送
        json={
            # 定义对话消息列表
            "messages":[{
                # 设置消息角色为用户
                "role": "user",
                # 设置用户询问的问题内容
                "content": "北京的旅游景区有哪些？"
            }]
        },
        # 设置请求头
        headers=heads
    )
    
    # 将API响应的JSON文本解析为Python字典对象
    result = json.loads(response.text)
    # 遍历搜索结果中的每个引用项
    for item in result['references']:
        # 打印搜索结果的标题
        print(item['title'])
        # 打印分隔线
        print("=" * 20)
        # 打印搜索结果的内容
        print(item['content'])
        # 打印空行，用于分隔不同的搜索结果
        print()
    


    
