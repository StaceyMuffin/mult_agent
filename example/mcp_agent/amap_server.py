import os
import httpx
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 获取脚本所在目录的绝对路径
SCRIPT_DIR = Path(__file__).resolve().parent

# 加载环境变量
load_dotenv(SCRIPT_DIR / ".env")

# 初始化 MCP 服务器
mcp = FastMCP("AmapServer")

# 高德地图 API 配置
AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")
AMAP_BASE_URL = "https://restapi.amap.com/v3"


@mcp.tool()
async def search_place(keywords: str, city: str = "") -> str:
    """
    搜索地点信息
    :param keywords: 搜索关键词（如"南京南站"）
    :param city: 城市名称（可选，如"南京"）
    :return: 地点搜索结果
    """
    if not AMAP_API_KEY:
        return "错误：未配置高德地图 API Key"
    
    url = f"{AMAP_BASE_URL}/place/text"
    params = {
        "key": AMAP_API_KEY,
        "keywords": keywords,
        "extensions": "all"
    }
    if city:
        params["city"] = city
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "1":
            return f"搜索失败：{data.get('info', '未知错误')}"
        
        pois = data.get("pois", [])
        if not pois:
            return f"未找到与'{keywords}'相关的地点"
        
        result = f"找到 {len(pois)} 个相关地点：\n\n"
        for i, poi in enumerate(pois[:5], 1):  # 只显示前5个
            name = poi.get("name", "未知")
            address = poi.get("address", "未知")
            location = poi.get("location", "未知")
            tel = poi.get("tel", "无")
            result += f"{i}. {name}\n"
            result += f"   地址：{address}\n"
            result += f"   坐标：{location}\n"
            if tel and tel != "[]":
                result += f"   电话：{tel}\n"
            result += "\n"
        
        return result
    
    except Exception as e:
        return f"搜索出错：{str(e)}"


@mcp.tool()
async def plan_route(origin: str, destination: str, city: str = "") -> str:
    """
    规划驾车路线
    :param origin: 起点（可以是地名或经纬度坐标，如"116.481028,39.989576"）
    :param destination: 终点（可以是地名或经纬度坐标）
    :param city: 城市名称（当使用地名时需要）
    :return: 路线规划结果
    """
    if not AMAP_API_KEY:
        return "错误：未配置高德地图 API Key"
    
    url = f"{AMAP_BASE_URL}/direction/driving"
    params = {
        "key": AMAP_API_KEY,
        "origin": origin,
        "destination": destination,
        "extensions": "all"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "1":
            return f"路线规划失败：{data.get('info', '未知错误')}"
        
        route = data.get("route", {})
        paths = route.get("paths", [])
        
        if not paths:
            return "未找到可行路线"
        
        path = paths[0]
        distance = path.get("distance", "0")
        duration = path.get("duration", "0")
        
        # 转换单位
        distance_km = int(distance) / 1000
        duration_min = int(duration) / 60
        
        result = f"🚗 路线规划结果\n"
        result += f"距离：{distance_km:.1f} 公里\n"
        result += f"预计时间：{duration_min:.0f} 分钟\n\n"
        result += "详细路线：\n"
        
        steps = path.get("steps", [])
        for i, step in enumerate(steps, 1):
            instruction = step.get("instruction", "")
            step_distance = step.get("distance", "0")
            result += f"{i}. {instruction} ({step_distance}米)\n"
        
        return result
    
    except Exception as e:
        return f"路线规划出错：{str(e)}"


@mcp.tool()
async def search_around(location: str, keywords: str = "", radius: int = 1000) -> str:
    """
    周边搜索
    :param location: 中心点坐标（格式：经度,纬度）
    :param keywords: 搜索关键词（如"餐厅"、"酒店"）
    :param radius: 搜索半径（米，默认1000米）
    :return: 周边搜索结果
    """
    if not AMAP_API_KEY:
        return "错误：未配置高德地图 API Key"
    
    url = f"{AMAP_BASE_URL}/place/around"
    params = {
        "key": AMAP_API_KEY,
        "location": location,
        "radius": radius,
        "extensions": "all"
    }
    if keywords:
        params["keywords"] = keywords
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "1":
            return f"搜索失败：{data.get('info', '未知错误')}"
        
        pois = data.get("pois", [])
        if not pois:
            return f"在 {radius} 米范围内未找到相关地点"
        
        result = f"在 {radius} 米范围内找到 {len(pois)} 个地点：\n\n"
        for i, poi in enumerate(pois[:5], 1):
            name = poi.get("name", "未知")
            address = poi.get("address", "未知")
            distance = poi.get("distance", "未知")
            result += f"{i}. {name}\n"
            result += f"   地址：{address}\n"
            result += f"   距离：{distance}米\n\n"
        
        return result
    
    except Exception as e:
        return f"搜索出错：{str(e)}"


@mcp.tool()
async def geocode(address: str, city: str = "") -> str:
    """
    地理编码：将地址转换为坐标
    :param address: 地址（如"北京市朝阳区望京"）
    :param city: 城市名称（可选）
    :return: 坐标信息
    """
    if not AMAP_API_KEY:
        return "错误：未配置高德地图 API Key"
    
    url = f"{AMAP_BASE_URL}/geocode/geo"
    params = {
        "key": AMAP_API_KEY,
        "address": address
    }
    if city:
        params["city"] = city
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "1":
            return f"地理编码失败：{data.get('info', '未知错误')}"
        
        geocodes = data.get("geocodes", [])
        if not geocodes:
            return f"未找到'{address}'的坐标"
        
        result = f"📍 '{address}' 的坐标信息：\n\n"
        for i, geo in enumerate(geocodes[:3], 1):
            location = geo.get("location", "未知")
            formatted_address = geo.get("formatted_address", "未知")
            province = geo.get("province", "")
            city = geo.get("city", "")
            district = geo.get("district", "")
            
            result += f"{i}. 坐标：{location}\n"
            result += f"   完整地址：{formatted_address}\n"
            result += f"   行政区划：{province} {city} {district}\n\n"
        
        return result
    
    except Exception as e:
        return f"地理编码出错：{str(e)}"


if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')
