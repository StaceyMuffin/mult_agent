文档包含的关键文件：
1. API服务器 - FastAPI架构、生命周期管理、API端点设计
2. 命令行客户端 - 异步交互流程、智能体调用机制
3. 高德地图MCP服务器 - 四个核心工具的实现细节
4. 时间MCP服务器 - 时间查询服务的技术实现
5. MCP服务器配置 - 标准化配置结构
6. 智能体提示词 - 角色定义和行为规范
7. 依赖配置 - 完整的技术栈说明

一、项目概述
本项目是一个相对完整的AI多智能体系统，通过MCP协议实现了工具的标准化集成，基于LangGraph实现了智能的推理和工具调用，可实现天气查询、地图服务、时间查询和文件操作等功能。
项目采用前后端分离架构，支持API服务、命令行客户端和Web界面三种交互方式，具有良好的扩展性和可维护性，可作为AI应用开发的基础框架。

二、项目架构
2.1 整体架构
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                              │
├──────────────────┬──────────────────┬────────────────────┤
│   Web前端        │   API客户端      │   CLI客户端        │
│   (Vue.js)       │   (HTTP)         │   (Python)         │
└──────────────────┴──────────────────┴────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  API服务层                               │
│              (FastAPI + Uvicorn)                        │
├─────────────────────────────────────────────────────────┤
│  LangGraph智能体  │  会话管理  │  工具调度              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 MCP工具层                                │
├──────────────┬──────────────┬──────────────┬────────────┤
│  天气服务器   │  地图服务器   │  时间服务器   │  写入服务器 │
│  (weather)   │  (amap)      │  (time)      │  (write)    │
└──────────────┴──────────────┴──────────────┴────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                外部服务层                                │
├──────────────┬──────────────┬──────────────┬────────────┤
│  天气API     │  高德地图API │  系统时间    │  本地文件   │
└──────────────┴──────────────┴──────────────┴────────────┘

2.2 文件结构
mcp_agent/
├── api_server.py        # FastAPI 服务器（提供 HTTP API）
├── client.py            # CLI 交互式客户端
├── client_simple.py     # 单次调用示例
├── weather_server.py    # 天气查询服务
├── amap_server.py       # 高德地图服务
├── write_server.py      # 文件写入服务
├── time_server.py       # 时间查询服务
├── servers_config.json  # MCP 服务器配置
├── agent_prompts.txt    # Agent 提示词
├── requirements.txt     # Python 依赖
└── .env                 # 环境变量（API Key）

2.3 数据流程
用户输入 "南京今天天气怎么样？"
           │
           ▼
    ┌──────────────┐
    │  Agent 接收   │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  LLM 思考    │  "用户询问天气，我应该使用 query_weather 工具"
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 调用 MCP 工具 │  query_weather("Nanjing")
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Weather Server│  → 调用 OpenWeather API
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  返回结果    │  🌡 温度: 22°C, 🌤 天气: 晴
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  LLM 组织回复 │  "南京今天天气晴朗，温度22°C..."
    └──────┬───────┘
           │
           ▼
      用户看到回复

三、核心组件
3.1 API服务器 (api_server.py)
功能概述
提供RESTful API接口，封装LangGraph智能体和MCP工具，支持多轮对话和工具调用。
技术架构
- 框架: FastAPI + Uvicorn
- AI模型: 通义千问 (ChatTongyi)
- 智能体框架: LangGraph ReAct Agent
- 工具集成: LangChain MCP Adapters
- 状态管理: InMemorySaver (内存检查点)
  
核心组件
Configuration类
- 负责环境变量加载和MCP服务器配置
- 自动转换相对路径为绝对路径
- 验证API密钥完整性
  
生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：连接MCP服务器、初始化Agent
    # 关闭时：清理MCP连接资源

API端点
- POST /chat: 聊天接口，支持多线程对话
- 请求参数: message (消息内容), thread_id (会话ID)
- 响应格式: ChatResponse (content, status, error)
  
关键特性
- 支持跨域访问 (CORS)
- 非流式响应，避免LangGraph索引错误
- 自动错误处理和日志记录
- 多线程会话隔离

3.2 命令行客户端 (client.py)
功能概述
提供交互式命令行界面，直接调用LangGraph Agent处理用户输入。

技术架构
- 运行环境: Python asyncio
- 智能体: LangGraph ReAct Agent
- 工具集成: MultiServerMCPClient
- 状态管理: InMemorySaver
  
核心流程
初始化阶段
1. 加载环境变量和配置
2. 连接多台MCP服务器
3. 获取可用工具列表
4. 初始化大模型和智能体
  
对话循环
while True:
    user_input = input("\n你: ").strip()
    if user_input.lower() == "quit":
        break
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config
    )
    print(f"\nAI: {result['messages'][-1].content}")

关键特性
- 支持多轮对话记忆
- 自动工具选择和调用
- 优雅的资源清理
- 实时日志输出

3.3 高德地图MCP服务器 (amap_server.py)
功能概述
基于高德地图API提供地点搜索、路线规划、周边查询和地理编码等地图服务。

技术架构
- 框架: FastMCP (MCP服务器框架)
- HTTP客户端: httpx (异步)
- API提供商: 高德地图REST API
  
核心工具
search_place: 地点搜索
- 参数: keywords (关键词), city (城市，可选)
- 功能: 根据关键词搜索POI信息
- 返回: 地点名称、地址、坐标、电话等
  
plan_route: 路线规划
- 参数: origin (起点), destination (终点), city (城市，可选)
- 功能: 规划驾车路线
- 返回: 距离、时间、详细导航步骤
  
search_around: 周边搜索
- 参数: location (坐标), keywords (关键词), radius (半径)
- 功能: 搜索指定范围内的POI
- 返回: 周边地点列表及距离
  
geocode: 地理编码
- 参数: address (地址), city (城市，可选)
- 功能: 将地址转换为经纬度坐标
- 返回: 坐标、完整地址、行政区划
  
技术特点
- 异步HTTP请求，提高并发性能
- 完善的错误处理和超时控制
- 结构化的结果格式化输出
- 支持中英文混合搜索

3.4 时间MCP服务器 (time_server.py)
功能概述
提供当前日期、时间和星期查询等基础时间服务。

技术架构
- 框架: FastMCP
- 时间处理: Python datetime模块
  
核心工具
get_current_time: 获取当前时间
- 返回格式: "YYYY年MM月DD日 HH:MM:SS"
  
get_current_date: 获取当前日期
- 返回格式: "YYYY年MM月DD日"
  
get_day_of_week: 获取星期几
- 返回格式: "星期一" ~ "星期日"
  
技术特点
- 轻量级设计，无外部依赖
- 准确的本地时间获取
- 中文友好的输出格式

3.5 MCP服务器配置 (servers_config.json)
配置结构
{
  "mcpServers": {
    "weather": {
      "command": "python3",
      "args": ["weather_server.py"],
      "transport": "stdio"
    },
    "write": {
      "command": "python3",
      "args": ["write_server.py"],
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
    }
  }
}

配置说明
- command: 启动服务器的命令
- args: 服务器脚本路径列表
- transport: 通信方式 (stdio)
  
技术特点
- 支持多服务器并发连接
- 标准化的MCP协议配置
- 灵活的服务器扩展机制

3.6 智能体提示词 (agent_prompts.txt)
功能概述
定义智能体的角色、能力和行为规范，指导AI如何与用户交互和选择工具。

核心内容
角色定义
- 名称: "智行助手"
- 定位: 智能助手，连接多种外部工具
  
工具能力
1. 天气查询: 查询各地实时天气
2. 文件操作: 将信息写入本地文件
3. 地图与出行: 高德地图服务
4. 时间查询: 获取日期、时间、星期
  
行为规范
- 知识截止日期提醒
- 实时时间查询强制要求
- 工具选择优先级
- 信息缺失处理策略
  
技术特点
- 明确的能力边界
- 强制工具使用规则
- 友好的交互风格
- 完善的错误处理指导

3.7 依赖配置 (requirements.txt)
核心依赖
AI框架
- langgraph: 智能体编排框架
- langchain-community: 社区扩展
- langchain-core: 核心功能
- langchain-mcp-adapters: MCP适配器
  
Web服务
- fastapi: Web框架
- uvicorn: ASGI服务器
  
工具集成
- mcp: MCP协议支持
- httpx: 异步HTTP客户端
- python-dotenv: 环境变量管理
  
AI模型
- dashscope: 通义千问SDK

四、核心代码详解
4.1 MCP 服务器配置 (servers_config.json)
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["weather_server.py"],
      "transport": "stdio"          // 标准输入输出通信
    },
    "write": {
      "command": "python", 
      "args": ["write_server.py"],
      "transport": "stdio"
    },
    "amap-maps": {
      "transport": "sse",           // Server-Sent Events 通信
      "url": "https://mcp.api-inference.modelscope.net/099239f1c74241/sse"
    }
  }
}
关键点解析：
暂时无法在飞书文档外展示此内容

4.2 天气服务器 (weather_server.py)
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("WeatherServer")

@mcp.tool()  # 装饰器将函数注册为 MCP 工具
async def query_weather(city: str) -> str:
    """
    输入指定城市的英文名称，返回今日天气查询结果。
    :param city: 城市名称（需使用英文）
    :return: 格式化后的天气信息
    """
    data = await fetch_weather(city)  # 调用 OpenWeather API
    return format_weather(data)       # 格式化返回

@mcp.tool()
async def get_weather_tips(season: str) -> str:
    """
    获取指定季节的天气贴士。
    :param season: 季节名称 (spring, summer, autumn, winter)
    """
    tips = {
        "spring": "🌸 春季多风，注意防风保暖",
        "summer": "☀️ 夏季炎热，注意防暑",
        # ...
    }
    return tips.get(season.lower(), "❓ 未知季节")

if __name__ == "__main__":
    mcp.run(transport='stdio')  # 以 STDIO 模式启动
关键点解析：
1. @mcp.tool() 装饰器：将普通函数注册为 MCP 工具，LLM 可以自动发现和调用
2. 函数文档字符串：非常重要！LLM 通过文档字符串理解工具的功能
3. transport='stdio'：通过标准输入/输出与客户端通信

4.3 API 服务器 (api_server.py)
from fastapi import FastAPI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

# 全局变量
mcp_client: MultiServerMCPClient = None
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理"""
    global mcp_client, agent
    
    # 1. 读取 MCP 服务器配置
    servers_cfg = Configuration.load_servers()
    
    # 2. 连接 MCP 服务器并获取工具
    mcp_client = MultiServerMCPClient(servers_cfg)
    tools = await mcp_client.get_tools()
    
    # 3. 初始化 ReAct Agent
    model = ChatTongyi(model=cfg.model, streaming=False)
    checkpointer = InMemorySaver()  # 内存中保存对话历史
    
    agent = create_react_agent(
        model=model, 
        tools=tools,
        prompt=prompt,
        checkpointer=checkpointer
    )
    
    yield  # 应用运行中
    
    # 4. 清理资源
    await mcp_client.cleanup()

app = FastAPI(lifespan=lifespan)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """聊天接口"""
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=request.message)]},
        {"configurable": {"thread_id": request.thread_id}}
    )
    return ChatResponse(content=result["messages"][-1].content)
关键点解析：
1. lifespan 上下文管理器：
  - 应用启动时初始化 MCP 连接和 Agent
  - 应用关闭时清理资源
2. MultiServerMCPClient：
  - 同时连接多个 MCP 服务器
  - 自动获取所有可用工具
3. create_react_agent：
  - 创建 ReAct 模式的 Agent
  - ReAct = Reasoning + Acting（推理 + 行动）
4. checkpointer：
  - 保存对话历史
  - 支持多轮对话

4.4 CLI 客户端 (client.py)
async def run_chat_loop() -> None:
    """启动 MCP-Agent 聊天循环"""
    
    # 1. 连接多台 MCP 服务器
    mcp_client = MultiServerMCPClient(servers_cfg)
    tools = await mcp_client.get_tools()
    
    # 2. 初始化大模型
    model = ChatTongyi(model=cfg.model)
    
    # 3. 构造 Agent（带记忆）
    checkpointer = InMemorySaver()
    agent = create_react_agent(
        model=model, 
        tools=tools,
        prompt=prompt,
        checkpointer=checkpointer
    )
    
    # 4. CLI 聊天循环
    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() == "quit":
            break
            
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"configurable": {"thread_id": "1"}}  # 对话ID
        )
        print(f"\nAI: {result['messages'][-1].content}")
    
    # 5. 清理
    await mcp_client.cleanup()
关键点解析：
1. thread_id：用于区分不同的对话会话，保持上下文
2. ainvoke：异步调用 Agent 处理消息
3. 消息格式：LangChain 标准消息格式 {"role": "user", "content": "..."}

五、关键技术与亮点
5.1 核心技术特点
5.1.1 多智能体架构
  - 基于LangGraph的ReAct模式
  - 支持多轮对话和上下文记忆
  - 自动工具选择和调用
5.1.2 MCP协议集成
  - 标准化的工具接口
  - 支持多服务器并发连接
  - 异步通信机制
5.1.3 多模态交互
  - RESTful API接口
  - 命令行交互界面
  - Web前端界面
5.1.4 状态管理
  - 基于thread_id的会话隔离
  - 内存检查点存储
  - 支持多用户并发
5.1.5 错误处理
  - 完善的异常捕获
  - 详细的日志记录
  - 友好的错误提示
5.2 技术亮点
1. 模块化设计: 各组件职责清晰，易于维护和扩展
2. 异步架构: 充分利用异步IO，提高并发性能
3. 标准化接口: 基于MCP协议，工具集成标准化
4. 多模态支持: 支持多种交互方式，适应不同场景
5. 智能体编排: LangGraph提供强大的智能体编排能力
6. 实时工具调用: 动态工具选择，实时响应用户需求

六、扩展指南
6.1 添加新的MCP服务器
1. 创建新的服务器脚本
2. 在servers_config.json中添加配置
3. 实现必要的工具函数
4. 重启API服务器
  
6.2 自定义智能体行为
1. 修改agent_prompts.txt
2. 调整工具选择逻辑
3. 优化响应格式
  
6.3 集成新的AI模型
1. 修改Configuration类
2. 更新模型初始化代码
3. 调整API调用参数

七、项目运行
7.1 环境要求
- Python 3.11+
- Node.js 20.19.0+ (前端)
- 通义千问API密钥
- OpenWeather API 密钥
- 高德地图API密钥
  
7.2 启动流程
7.2.1 流程总览
1. 配置环境变量 (.env)
2. 安装Python依赖 (pip install -r requirements.txt)
3. 启动API服务器 (python api_server.py)
4. (可选) 启动前端 (npm run dev)
5. (可选) 启动CLI客户端 (python client.py)

7.2.2 配置环境变量
1. 查看 .env.example 文件
  - 该文件位于 example/mcp_agent/.env.example
  - 包含了所有需要的环境变量模板

2. 创建 .env 文件
# 在项目根目录执行
cd /mult_agent/example/mcp_agent
cp .env.example .env

3. 填写 API 密钥
   打开 example/mcp_agent/.env 文件，按照以下格式填写实际的 API 密钥：
# 阿里云百炼API密钥（通义千问）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 模型名称
MODEL=qwen-plus-2025-07-28
# OpenWeather API 密钥（天气查询）
OPENWEATHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 高德地图API密钥
AMAP_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

4. API 密钥获取方式
  - DASHSCOPE_API_KEY：登录阿里云百炼平台获取
  -  OPENWEATHER_API_KEY：注册 OpenWeather 账号获取
  - AMAP_API_KEY：注册高德地图开放平台账号获取

5. 配置说明
  - 所有 API 密钥都必须填写，否则相关功能将无法使用
  - 确保 API 密钥格式正确，不要包含多余的空格或引号
  - 不同的模型版本可能需要不同的 MODEL 值，请根据实际使用的模型调整

7.2.3 后端API服务器
# 进入项目目录
cd /Users/stacey/Desktop/Trae_Projects/mult_agent/example/mcp_agent

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 安装依赖（如果未安装）
pip install -r requirements.txt

# 运行API服务器
python api_server.py
服务器将在 http://localhost:8000 上运行。

7.2.4 命令行客户端
# 进入项目目录
cd /Users/stacey/Desktop/Trae_Projects/mult_agent/example/mcp_agent

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 运行客户端
python client.py
启动后可以输入消息与智能体交互，输入 quit 退出。

7.2.5 前端应用
# 进入前端目录
cd /Users/stacey/Desktop/Trae_Projects/mult_agent/example/mcp_agent/front/mcp_agent

# 安装依赖（如果未安装）
npm install

# 启动开发服务器
npm run dev
前端将在 http://localhost:5173 上运行。
