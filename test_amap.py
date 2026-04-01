#!/usr/bin/env python3
"""
测试高德地图 MCP 服务器
"""

import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from pathlib import Path
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent

# 加载环境变量
load_dotenv(SCRIPT_DIR / ".env")
async def test_amap_tools():
    print("=" * 60)
    print("测试高德地图 MCP 服务器")
    print("=" * 60)
    print()
    
    # 检查 API Key
    amap_key = os.getenv("AMAP_API_KEY")
    if not amap_key:
        print("⚠️  警告：未配置 AMAP_API_KEY")
        print("   请在 .env 文件中添加：AMAP_API_KEY=your_key")
        print()
        print("   你可以在这里申请：https://console.amap.com/")
        print()
        return
    
    print(f"✅ AMAP_API_KEY 已配置（长度：{len(amap_key)}）")
    print()
    
    # 加载服务器配置
    servers_cfg = {
        "amap-maps": {
            "command": "python",
            "args": [str(SCRIPT_DIR / "amap_server.py")],
            "transport": "stdio"
        }
    }
    
    print("📦 正在连接高德地图 MCP 服务器...")
    
    try:
        mcp_client = MultiServerMCPClient(servers_cfg)
        tools = await mcp_client.get_tools()
        print(f"✅ 成功连接！加载了 {len(tools)} 个工具：")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        print()
        
        print("✅ 高德地图服务已成功集成！")
        print("✅ 所有工具都已加载完成！")
        print()
        print("🎯 现在你可以在聊天中使用以下功能：")
        print("   - 搜索地点：'帮我搜索北京的咖啡店'")
        print("   - 路线规划：'规划从天安门到故宫的路线'")
        print("   - 周边搜索：'查找天安门附近的餐厅'")
        print("   - 天气查询：'查询上海的天气'")
        print()
        
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_amap_tools())
