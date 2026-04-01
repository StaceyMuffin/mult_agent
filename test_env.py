#!/usr/bin/env python3
"""测试环境变量和 API key 是否正确加载"""

from pathlib import Path
import os

# 获取脚本目录
SCRIPT_DIR = Path(__file__).resolve().parent
print(f"📁 脚本目录: {SCRIPT_DIR}")
print()

# 检查 .env 文件
env_file = SCRIPT_DIR / ".env"
if env_file.exists():
    print(f"✅ .env 文件存在: {env_file}")
    print("\n=== .env 文件内容 ===")
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                print(f"  {key}: {'*' * len(value)}")
else:
    print("❌ .env 文件不存在")

print()

# 测试 load_dotenv
from dotenv import load_dotenv
load_dotenv(env_file)
print("=== 环境变量检查 ===")

api_key = os.getenv("DASHSCOPE_API_KEY")
if api_key:
    print(f"✅ DASHSCOPE_API_KEY 已加载 (长度: {len(api_key)})")
else:
    print("❌ DASHSCOPE_API_KEY 未找到")

model = os.getenv("MODEL")
if model:
    print(f"✅ MODEL: {model}")
else:
    print("❌ MODEL 未找到")

openweather_key = os.getenv("OPENWEATHER_API_KEY")
if openweather_key:
    print(f"✅ OPENWEATHER_API_KEY 已加载 (长度: {len(openweather_key)})")

print()

# 测试 ChatTongyi 初始化
print("=== 测试 ChatTongyi 初始化 ===")
try:
    from langchain_community.chat_models import ChatTongyi
    model = ChatTongyi(model="qwen-plus", streaming=False)
    print("✅ ChatTongyi 初始化成功！")
except Exception as e:
    print(f"❌ ChatTongyi 初始化失败: {e}")
    import traceback
    traceback.print_exc()
