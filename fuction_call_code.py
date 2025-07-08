import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import json
import function_tools as ft


if __name__ == "__main__":
    load_dotenv(find_dotenv())

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "multiply_two_numbers",
                "description": "两个数相乘",
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

    

    # print(response.choices[0].message.tool_calls)
    if response.choices[0].message.tool_calls is not None:
        args = response.choices[0].message.tool_calls[0].function.arguments
        args = json.loads(args)
        function_name = response.choices[0].message.tool_calls[0].function.name
        invoke_fun = getattr(ft, function_name)
        result = invoke_fun(**args)
        # print(f"函数调用结果：{result}")

        messages.append(response.choices[0].message)
        messages.append({
            "role": "tool",
            "content":f"{json.dumps(result)}",
            "tool_call_id": response.choices[0].message.tool_calls[0].id
        })

        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "123.123乘以456.456等于多少？"}],
        tools=tools
    )
    print(response.choices[0].message.content)

        

