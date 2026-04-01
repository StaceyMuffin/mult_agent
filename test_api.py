#!/usr/bin/env python3
"""测试后端 API 是否正常工作"""

import requests
import json

API_URL = "http://localhost:8000/chat"

print("=" * 60)
print("测试后端 API")
print("=" * 60)
print()

test_queries = [
    "你好，请介绍一下你自己",
    "给我一个春季的天气小贴士",
    "查询一下北京的天气",
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'─' * 60}")
    print(f"测试 {i}/{len(test_queries)}")
    print(f"{'─' * 60}")
    print(f"👤 用户: {query}")
    
    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json={"message": query, "thread_id": "test"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"🤖 AI: {data.get('content', '')}")
            else:
                print(f"❌ 错误: {data.get('error', '未知错误')}")
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
