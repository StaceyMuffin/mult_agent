#!/usr/bin/env python3
"""测试 MCP 服务器配置路径是否正确"""

from pathlib import Path
import json
import os

# 获取脚本目录
SCRIPT_DIR = Path(__file__).resolve().parent
print(f"📁 脚本目录: {SCRIPT_DIR}")
print()

# 读取原始配置
config_file = SCRIPT_DIR / "servers_config.json"
with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

servers = config.get("mcpServers", {})
print("=== 原始配置 ===")
for name, cfg in servers.items():
    print(f"  {name}: {cfg}")

print()
print("=== 路径转换测试 ===")
for server_name, server_config in servers.items():
    if "args" in server_config and len(server_config["args"]) > 0:
        script_path = server_config["args"][0]
        if not os.path.isabs(script_path):
            absolute_path = str(SCRIPT_DIR / script_path)
            print(f"  {server_name}:")
            print(f"    原始: {script_path}")
            print(f"    绝对: {absolute_path}")
            print(f"    存在: {Path(absolute_path).exists()}")

print()
print("=== 检查服务器文件 ===")
files_to_check = ["weather_server.py", "write_server.py"]
for filename in files_to_check:
    filepath = SCRIPT_DIR / filename
    exists = filepath.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {filename}")
    if exists:
        print(f"   大小: {filepath.stat().st_size} 字节")
