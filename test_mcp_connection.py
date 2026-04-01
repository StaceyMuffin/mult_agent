#!/usr/bin/env python3
"""测试 MCP 连接是否正常"""

import asyncio
import sys
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from dotenv import load_dotenv
import os

load_dotenv(SCRIPT_DIR / ".env")
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY", "")

import json
from langchain_mcp_adapters.client import MultiServerMCPClient

print("=== 测试 MCP 连接 ===\n")

# 加载并修改服务器配置
config_file = SCRIPT_DIR / "servers_config.json"
with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

servers = config.get("mcpServers", {})

# 转换路径并过滤掉 amap-maps（因为需要配置 URL）
for server_name, server_config in servers.items():
    if "args" in server_config and len(server_config["args"]) > 0:
        script_path = server_config["args"][0]
        if not os.path.isabs(script_path):
            absolute_path = str(SCRIPT_DIR / script_path)
            server_config["args"][0] = absolute_path
            print(f"✅ {server_name}: {script_path} → {absolute_path}")

# 暂时禁用 amap-maps，因为需要配置 URL
if "amap-maps" in servers:
    print("⚠️  暂时跳过 amap-maps（需要配置 URL）")
    del servers["amap-maps"]

print()

async def test_mcp():
    try:
        print("🔄 正在连接 MCP 服务器...")
        mcp_client = MultiServerMCPClient(servers)
        tools = await mcp_client.get_tools()
        print(f"✅ 成功连接！加载了 {len(tools)} 个工具")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:50]}...")
        
        await mcp_client.cleanup()
        print("\n🧹 连接已清理")
        return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

asyncio.run(test_mcp())
