#!/usr/bin/env python3
"""测试完整系统：API keys + MCP 连接 + Agent 基本功能"""

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

# 检查 API keys
api_key = os.getenv("DASHSCOPE_API_KEY")
model = os.getenv("MODEL")
weather_key = os.getenv("OPENWEATHER_API_KEY")

print(f"📋 通义千问 API Key: {'✅' if api_key else '❌'} (长度: {len(api_key or '')})")
print(f"📋 模型名称: {model or '❌'}")
print(f"📋 天气 API Key: {'✅' if weather_key else '❌'} (长度: {len(weather_key or '')})")
print()

if not api_key:
    print("❌ 错误: 未找到 DASHSCOPE_API_KEY")
    sys.exit(1)

os.environ["DASHSCOPE_API_KEY"] = api_key

# 测试 ChatTongyi 初始化
print("=" * 60)
print("测试 ChatTongyi 初始化")
print("=" * 60)
try:
    from langchain_community.chat_models import ChatTongyi
    llm = ChatTongyi(model=model, streaming=False)
    print("✅ ChatTongyi 初始化成功")
except Exception as e:
    print(f"❌ ChatTongyi 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试 MCP 连接
print("=" * 60)
print("测试 MCP 连接")
print("=" * 60)
import json
from langchain_mcp_adapters.client import MultiServerMCPClient

config_file = SCRIPT_DIR / "servers_config.json"
with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

servers = config.get("mcpServers", {})

# 转换路径并过滤 amap-maps
for server_name, server_config in servers.items():
    if "args" in server_config and len(server_config["args"]) > 0:
        script_path = server_config["args"][0]
        if not os.path.isabs(script_path):
            absolute_path = str(SCRIPT_DIR / script_path)
            server_config["args"][0] = absolute_path

if "amap-maps" in servers:
    print("⚠️  暂时跳过 amap-maps（需要配置 URL）")
    del servers["amap-maps"]

mcp_client = None
tools = []
try:
    print("🔄 正在连接 MCP 服务器...")
    mcp_client = MultiServerMCPClient(servers)
    tools = await mcp_client.get_tools()
    print(f"✅ 成功连接！加载了 {len(tools)} 个工具")
    for tool in tools:
        print(f"  - {tool.name}")
except Exception as e:
    print(f"❌ MCP 连接失败: {e}")
    import traceback
    traceback.print_exc()
    if mcp_client:
        try:
            await mcp_client.__aexit__(None, None, None)
        except:
            pass
    sys.exit(1)

print()

# 测试 Agent 初始化
print("=" * 60)
print("测试 Agent 初始化")
print("=" * 60)
try:
    from langgraph.prebuilt import create_react_agent
    from langgraph.checkpoint.memory import InMemorySaver
    
    checkpointer = InMemorySaver()
    
    with open(SCRIPT_DIR / "agent_prompts.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt,
        checkpointer=checkpointer
    )
    print("✅ Agent 初始化成功")
except Exception as e:
    print(f"❌ Agent 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    if mcp_client:
        try:
            await mcp_client.__aexit__(None, None, None)
        except:
            pass
    sys.exit(1)

print()

# 测试一个简单的工具调用
print("=" * 60)
print("测试天气工具调用")
print("=" * 60)
try:
    from langchain_core.messages import HumanMessage
    
    config = {"configurable": {"thread_id": "test"}}
    
    test_message = "给我一个春季的天气小贴士"
    print(f"🤔 用户: {test_message}")
    
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=test_message)]},
        config
    )
    
    ai_message = result["messages"][-1].content
    print(f"🤖 AI: {ai_message}")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("清理资源")
print("=" * 60)

if mcp_client:
    try:
        await mcp_client.__aexit__(None, None, None)
        print("✅ MCP 连接已关闭")
    except Exception as e:
        print(f"⚠️  清理时出错: {e}")

print()
print("🎉 系统测试完成！")
print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
