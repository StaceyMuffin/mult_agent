#!/usr/bin/env python3
"""
高德地图 MCP 服务器
提供地点搜索、路线规划、周边查询等功能
"""

import os
import httpx
from mcp.server.fastmcp import FastMCP
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).resolve().parent

# 加载环境变量
load_dotenv(SCRIPT_DIR / ".env")

mcp = FastMCP("AmapServer")

AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")
AMAP_BASE_URL = "https://restapi.amap.com"


@mcp.tool()
def search_place(keyword: str, city: str = "北京", citylimit: bool = False) -> str:
    """
    搜索地点
    
    Args:
        keyword: 搜索关键词（如"咖啡店"、"天安门"）
        city: 搜索城市，默认为"北京"
        citylimit: 是否限制在指定城市内搜索，默认为 False
    
    Returns:
        搜索结果列表，包含地点名称、地址、经纬度等信息
    """
    if not AMAP_API_KEY:
        return "❌ 错误：未配置 AMAP_API_KEY 环境变量"
    
    url = f"{AMAP_BASE_URL}/v3/place/text"
    params = {
        "key": AMAP_API_KEY,
        "keywords": keyword,
        "city": city,
        "citylimit": "true" if citylimit else "false",
        "output": "json"
    }
    
    try:
        response = httpx.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "1" and data.get("pois"):
            pois = data["pois"]
            result = f"📍 在 {city} 找到 {len(pois)} 个结果：\n\n"
            
            for i, poi in enumerate(pois[:10], 1):
                name = poi.get("name", "未知")
                address = poi.get("address", "无地址")
                location = poi.get("location", "")
                distance = poi.get("distance", "")
                
                result += f"{i}. **{name}**\n"
                result += f"   📍 地址: {address}\n"
                if location:
                    result += f"   🌐 坐标: {location}\n"
                if distance:
                    result += f"   📏 距离: {distance}米\n"
                result += "\n"
            
            return result
        else:
            return f"❌ 未找到相关地点。错误信息：{data.get('info', '未知错误')}"
    
    except Exception as e:
        return f"❌ 搜索失败：{str(e)}"


@mcp.tool()
def plan_route(
    origin: str, 
    destination: str, 
    city: str = "北京",
    strategy: int = 0
) -> str:
    """
    规划驾车路线
    
    Args:
        origin: 出发地（地点名称或经纬度，如"天安门"或"116.397128,39.916527"）
        destination: 目的地（地点名称或经纬度）
        city: 城市，默认为"北京"
        strategy: 路线规划策略
                 0-速度优先
                 1-费用优先
                 2-距离优先
                 3-不走高速
    
    Returns:
        路线规划结果，包含距离、时间、路线详情等
    """
    if not AMAP_API_KEY:
        return "❌ 错误：未配置 AMAP_API_KEY 环境变量"
    
    url = f"{AMAP_BASE_URL}/v3/direction/driving"
    params = {
        "key": AMAP_API_KEY,
        "origin": origin,
        "destination": destination,
        "city": city,
        "strategy": strategy,
        "output": "json"
    }
    
    try:
        response = httpx.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "1" and data.get("route"):
            route = data["route"]["paths"][0]
            distance = route.get("distance", "0")
            duration = route.get("duration", "0")
            steps = route.get("steps", [])
            
            distance_km = int(distance) / 1000
            duration_min = int(duration) / 60
            
            result = f"🚗 路线规划结果\n\n"
            result += f"📏 总距离: {distance_km:.2f} 公里\n"
            result += f"⏱ 预计时间: {duration_min:.0f} 分钟\n\n"
            result += f"📍 出发地: {origin}\n"
            result += f"📍 目的地: {destination}\n\n"
            result += f"🛣️ 路线详情（前5步）：\n"
            
            for i, step in enumerate(steps[:5], 1):
                instruction = step.get("instruction", "继续行驶")
                step_distance = step.get("distance", "0")
                step_distance_km = int(step_distance) / 1000
                
                result += f"{i}. {instruction} ({step_distance_km:.2f}km)\n"
            
            if len(steps) > 5:
                result += f"... 还有 {len(steps) - 5} 步\n"
            
            return result
        else:
            return f"❌ 路线规划失败。错误信息：{data.get('info', '未知错误')}"
    
    except Exception as e:
        return f"❌ 规划失败：{str(e)}"


@mcp.tool()
def search_around(
    location: str, 
    keywords: str, 
    radius: int = 1000
) -> str:
    """
    搜索周边地点
    
    Args:
        location: 中心点坐标（经纬度，如"116.397128,39.916527"）
        keywords: 搜索关键词（如"餐厅"、"加油站"、"酒店"）
        radius: 搜索半径（米），默认为 1000 米
    
    Returns:
        周边地点列表
    """
    if not AMAP_API_KEY:
        return "❌ 错误：未配置 AMAP_API_KEY 环境变量"
    
    url = f"{AMAP_BASE_URL}/v3/place/around"
    params = {
        "key": AMAP_API_KEY,
        "location": location,
        "keywords": keywords,
        "radius": radius,
        "output": "json"
    }
    
    try:
        response = httpx.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "1" and data.get("pois"):
            pois = data["pois"]
            result = f"🔍 在中心点 {location} 周围 {radius} 米内找到 {len(pois)} 个{keywords}：\n\n"
            
            for i, poi in enumerate(pois[:10], 1):
                name = poi.get("name", "未知")
                address = poi.get("address", "无地址")
                distance = poi.get("distance", "")
                
                result += f"{i}. **{name}**\n"
                result += f"   📍 地址: {address}\n"
                if distance:
                    result += f"   📏 距离: {distance}米\n"
                result += "\n"
            
            return result
        else:
            return f"❌ 未找到周边{keywords}。错误信息：{data.get('info', '未知错误')}"
    
    except Exception as e:
        return f"❌ 搜索失败：{str(e)}"


@mcp.tool()
def get_weather_by_city(city: str = "北京") -> str:
    """
    获取指定城市的天气信息（高德地图天气查询）
    
    Args:
        city: 城市名称，默认为"北京"
    
    Returns:
        天气信息，包括温度、湿度、风向等
    """
    if not AMAP_API_KEY:
        return "❌ 错误：未配置 AMAP_API_KEY 环境变量"
    
    url = f"{AMAP_BASE_URL}/v3/weather/weatherInfo"
    params = {
        "key": AMAP_API_KEY,
        "city": city,
        "extensions": "base",
        "output": "json"
    }
    
    try:
        response = httpx.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "1" and data.get("lives"):
            lives = data["lives"][0]
            province = lives.get("province", "")
            city_name = lives.get("city", "")
            weather = lives.get("weather", "")
            temperature = lives.get("temperature", "")
            winddirection = lives.get("winddirection", "")
            windpower = lives.get("windpower", "")
            humidity = lives.get("humidity", "")
            reporttime = lives.get("reporttime", "")
            
            result = f"🌤️ {province}{city_name} 天气预报\n\n"
            result += f"🌡 温度: {temperature}°C\n"
            result += f"☁️ 天气: {weather}\n"
            result += f"💧 湿度: {humidity}%\n"
            result += f"🌬 风向: {winddirection}\n"
            result += f"💨 风力: {windpower}级\n"
            result += f"🕐 更新时间: {reporttime}\n"
            
            return result
        else:
            return f"❌ 获取天气失败。错误信息：{data.get('info', '未知错误')}"
    
    except Exception as e:
        return f"❌ 查询失败：{str(e)}"


if __name__ == "__main__":
    print("🚀 启动高德地图 MCP 服务器...")
    print(f"📝 AMAP_API_KEY: {'已配置' if AMAP_API_KEY else '未配置'}")
    mcp.run()
