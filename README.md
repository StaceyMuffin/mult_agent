# 智行助手 (Zhixing Assistant)

> 基于 MCP 协议与 LangGraph 构建的 AI 多智能体系统，支持天气查询、地图服务、时间查询、文件操作等功能。

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-ReAct-orange.svg)](https://github.com/langchain-ai/langgraph)
[![MCP](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io/)

---

## ✨ 项目简介

本项目是一个相对完整的 **AI 多智能体系统**，通过 **MCP 协议** 实现工具的标准化集成，基于 **LangGraph** 实现智能推理与工具调用。采用前后端分离架构，支持 API 服务、命令行客户端和 Web 界面三种交互方式，具有良好的扩展性和可维护性，可作为 AI 应用开发的基础框架。

## 🎯 核心功能

- 🌤️ **天气查询** — 查询全球城市实时天气（基于 OpenWeather API）
- 🗺️ **地图服务** — 地点搜索、路线规划、周边查询、地理编码（基于高德地图 API）
- 🕐 **时间查询** — 获取当前日期、时间和星期
- 📝 **文件操作** — 将信息写入本地文件
- 💬 **多轮对话** — 基于 `thread_id` 的会话隔离与上下文记忆
- 🔌 **多种交互方式** — REST API / CLI / Web 前端

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户交互层                          │
├──────────────────┬──────────────────┬───────────────────┤
│    Web 前端      │    API 客户端    │    CLI 客户端     │
│    (Vue.js)      │     (HTTP)       │    (Python)       │
└──────────────────┴──────────────────┴───────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                      API 服务层                          │
│                  (FastAPI + Uvicorn)                    │
├─────────────────────────────────────────────────────────┤
│   LangGraph 智能体  │   会话管理   │   工具调度          │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                     MCP 工具层                           │
├──────────────┬──────────────┬──────────────┬───────────┤
│  天气服务器  │  地图服务器  │  时间服务器  │ 写入服务器│
│  (weather)   │    (amap)    │    (time)    │  (write)  │
└──────────────┴──────────────┴──────────────┴───────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                     外部服务层                           │
├──────────────┬──────────────┬──────────────┬───────────┤
│  OpenWeather │  高德地图API │   系统时间   │ 本地文件  │
└──────────────┴──────────────┴──────────────┴───────────┘
```

### 数据流示例

以"南京今天天气怎么样？"为例：

```
用户输入 → Agent 接收 → LLM 推理（选择工具）
       → 调用 MCP 工具 query_weather("Nanjing")
       → Weather Server 请求 OpenWeather API
       → 返回天气数据 → LLM 组织自然语言回复 → 展示给用户
```

## 📁 项目结构

```
mcp_agent/
├── api_server.py          # FastAPI 服务器（提供 HTTP API）
├── client.py              # CLI 交互式客户端
├── client_simple.py       # 单次调用示例
├── weather_server.py      # 天气查询服务
├── amap_server.py         # 高德地图服务
├── write_server.py        # 文件写入服务
├── time_server.py         # 时间查询服务
├── servers_config.json    # MCP 服务器配置
├── agent_prompts.txt      # Agent 提示词
├── requirements.txt       # Python 依赖
└── .env                   # 环境变量（API Key）
```

## 🛠️ 技术栈

| 类别            | 技术                                                        |
| --------------- | ----------------------------------------------------------- |
| **AI 框架**     | LangGraph（ReAct Agent）、LangChain、langchain-mcp-adapters |
| **大语言模型**  | 通义千问（ChatTongyi / qwen-plus）                          |
| **Web 框架**    | FastAPI + Uvicorn                                           |
| **协议层**      | MCP (Model Context Protocol)                                |
| **HTTP 客户端** | httpx（异步）                                               |
| **状态管理**    | InMemorySaver（内存检查点）                                 |
| **前端**        | Vue.js                                                      |

## 🔧 MCP 工具详解

### 🗺️ 高德地图服务器（amap_server.py）

| 工具            | 功能          | 参数                             |
| --------------- | ------------- | -------------------------------- |
| `search_place`  | 地点搜索      | `keywords`, `city`               |
| `plan_route`    | 驾车路线规划  | `origin`, `destination`, `city`  |
| `search_around` | 周边 POI 搜索 | `location`, `keywords`, `radius` |
| `geocode`       | 地址转经纬度  | `address`, `city`                |

### 🌤️ 天气服务器（weather_server.py）

| 工具               | 功能                           |
| ------------------ | ------------------------------ |
| `query_weather`    | 查询指定城市天气（英文城市名） |
| `get_weather_tips` | 获取季节性天气贴士             |

### 🕐 时间服务器（time_server.py）

| 工具               | 返回格式                  |
| ------------------ | ------------------------- |
| `get_current_time` | `YYYY年MM月DD日 HH:MM:SS` |
| `get_current_date` | `YYYY年MM月DD日`          |
| `get_day_of_week`  | `星期一` ~ `星期日`       |

### 📝 MCP 服务器配置示例

```json
{
  "mcpServers": {
    "weather": {
      "command": "python3",
      "args": ["weather_server.py"],
      "transport": "stdio"
    },
    "amap": {
      "command": "python3",
      "args": ["amap_server.py"],
      "transport": "stdio"
    },
    "time": {
      "command": "python3",
      "args": ["time_server.py"],
      "transport": "stdio"
    },
    "write": {
      "command": "python3",
      "args": ["write_server.py"],
      "transport": "stdio"
    }
  }
}
```

> `transport` 支持 `stdio`（本地进程）或 `sse`（远程 HTTP）

## 🚀 快速开始

### 环境要求

- Python **3.11+**
- Node.js **20.19.0+**（仅前端需要）
- 通义千问 API 密钥（[阿里云百炼平台](https://bailian.console.aliyun.com/)）
- OpenWeather API 密钥（[OpenWeather](https://openweathermap.org/api)）
- 高德地图 API 密钥（[高德开放平台](https://lbs.amap.com/)）

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd mult_agent/example/mcp_agent
```

### 2. 配置环境变量

复制 `.env.example` 并填写 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 阿里云百炼 API 密钥（通义千问）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 模型名称
MODEL=qwen-plus-2025-07-28

# OpenWeather API 密钥（天气查询）
OPENWEATHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 高德地图 API 密钥
AMAP_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ 所有 API 密钥都必须填写，否则相关功能将无法使用。确保密钥格式正确，不要包含多余的空格或引号。

### 3. 安装依赖

```bash
# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows

# 安装 Python 依赖
pip install -r requirements.txt
```

### 4. 启动服务

#### 🔹 方式一：API 服务器

```bash
python api_server.py
```

服务启动后访问：<http://localhost:8000>

**API 端点**：

| 方法   | 路径    | 说明                     |
| ------ | ------- | ------------------------ |
| `POST` | `/chat` | 聊天接口，支持多线程对话 |

**请求示例**：

```json
{
  "message": "南京今天天气怎么样？",
  "thread_id": "user_001"
}
```

#### 🔹 方式二：CLI 客户端

```bash
python client.py
```

启动后可直接输入消息与智能体交互，输入 `quit` 退出。

```
你: 帮我查一下北京到上海的路线
AI: （智能体调用 plan_route 工具并返回结果）
```

#### 🔹 方式三：Web 前端

```bash
cd front/mcp_agent
npm install
npm run dev
```

前端服务启动于：<http://localhost:5173>

## 🔌 扩展指南

### 添加新的 MCP 服务器

1. 创建新的服务器脚本，使用 `FastMCP` 框架
2. 使用 `@mcp.tool()` 装饰器注册工具函数
3. 在 `servers_config.json` 中添加配置
4. 重启 API 服务器即可自动加载

示例：

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
async def my_tool(param: str) -> str:
    """工具说明（LLM 通过文档字符串理解工具功能）"""
    return f"处理结果: {param}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

### 自定义智能体行为

- 修改 `agent_prompts.txt`，调整角色定义与行为规范
- 调整工具选择优先级
- 优化响应格式

### 集成新的 AI 模型

- 修改 `Configuration` 类中的模型配置
- 更新模型初始化代码
- 根据需要调整 API 调用参数

## 💡 技术亮点

- **模块化设计** — 各组件职责清晰，易于维护和扩展
- **异步架构** — 充分利用 `asyncio`，提升并发性能
- **标准化接口** — 基于 MCP 协议，工具集成标准化
- **多模态支持** — API / CLI / Web 三种交互方式
- **智能体编排** — LangGraph 提供强大的 ReAct 模式推理能力
- **实时工具调用** — 动态工具选择，实时响应用户需求
