import datetime
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("TimeServer")


@mcp.tool()
async def get_current_time() -> str:
    """
    获取当前日期和时间
    :return: 当前日期时间字符串
    """
    now = datetime.datetime.now()
    return now.strftime("%Y年%m月%d日 %H:%M:%S")


@mcp.tool()
async def get_current_date() -> str:
    """
    获取当前日期
    :return: 当前日期字符串
    """
    now = datetime.datetime.now()
    return now.strftime("%Y年%m月%d日")


@mcp.tool()
async def get_day_of_week() -> str:
    """
    获取今天是星期几
    :return: 星期几
    """
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    now = datetime.datetime.now()
    return weekdays[now.weekday()]


if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')
