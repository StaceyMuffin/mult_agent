#!/usr/bin/env python3
"""简单的系统测试"""

import asyncio
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from dotenv import load_dotenv
import os

load_dotenv(SCRIPT_DIR / ".env")

print("=" * 60)
print("系统配置验证")
print("=" * 60)

api_key = os.getenv("DASHSCOPE_API_KEY")
model = os.getenv("MODEL")
weather_key = os.getenv("OPENWEATHER_API_KEY")

print(f"✅ DASHSCOPE_API_KEY: {len(api_key or '')} 字符")
print(f"✅ MODEL: {model}")
print(f"✅ OPENWEATHER_API_KEY: {len(weather_key or '')} 字符")
print()

os.environ["DASHSCOPE_API_KEY"] = api_key

print("=" * 60)
print("正在启动 MCP Agent...")
print("=" * 60)

import json
from langchain_community.chat_models import ChatTongyi
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage

# 读取 prompt
with open(SCRIPT_DIR / "agent_prompts.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

# 读取服务器配置
config_file = SCRIPT_DIR / "servers_config.json"
with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

servers = config.get("mcpServers", {})

# 转换路径
for server_name, server_config in servers.items():
    if "args" in server_config and len(server_config["args"]) > 0:
        script_path = server_config["args"][0]
        if not os.path.isabs(script_path):
            absolute_path = str(SCRIPT_DIR / script_path)
            server_config["args"][0] = absolute_path

# 暂时禁用 amap-maps
if "amap-maps" in servers:
    del servers["amap-maps"]

async def main():
    mcp_client = None
    try:
        print("🔄 连接 MCP 服务器...")
        mcp_client = MultiServerMCPClient(servers)
        tools = await mcp_client.get_tools()
        print(f"✅ 已加载 {len(tools)} 个工具: {[t.name for t in tools]}")
        
        print("\n🔄 初始化 Agent...")
        llm = ChatTongyi(model=model, streaming=False)
        checkpointer = InMemorySaver()
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=prompt,
            checkpointer=checkpointer
        )
        print("✅ Agent 初始化成功")
        
        print("\n" + "=" * 60)
        print("测试对话")
        print("=" * 60)
        
        test_queries = [
            "你好，请介绍一下你自己",
            "给我一个春季的天气小贴士",
            "查询一下北京的天气",
        ]
        
        config = {"configurable": {"thread_id": "test"}}
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'─' * 60}")
            print(f"测试 {i}/{len(test_queries)}")
            print(f"{'─' * 60}")
            print(f"👤 用户: {query}")
            
            try:
                result = await agent.ainvoke(
                    {"messages": [HumanMessage(content=query)]},
                    config
                )
                ai_response = result["messages"][-1].content
                print(f"🤖 AI: {ai_response}")
            except Exception as e:
                print(f"❌ 错误: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("🎉 测试完成！")
        print("=" * 60)
        print("\n现在你可以运行 'python client.py' 开始对话了！")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if mcp_client:
            try:
                await mcp_client.__aexit__(None, None, None)
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())
