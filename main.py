from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

import base64
import requests
import argparse



# —— 配置 —— #
REST_HOST = "http://139.155.69.131:8212"
USERNAME = "admin"
PASSWORD = "17191719"

# Basic Auth 头
auth_bytes = f"{USERNAME}:{PASSWORD}".encode("utf-8")
auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
HEADERS = {
    "Authorization": f"Basic {auth_b64}",
    "Content-Type": "application/json"
}

# —— REST API 查询 —— #
def get_server_info():
    url = f"{REST_HOST}/v1/api/info"
    resp = requests.get(url, headers=HEADERS, timeout=5)
    return resp.json()

def get_server_metrics():
    url = f"{REST_HOST}/v1/api/metrics"
    resp = requests.get(url, headers=HEADERS, timeout=5)
    return resp.json()

def get_player_list():
    url = f"{REST_HOST}/v1/api/players"
    resp = requests.get(url, headers=HEADERS, timeout=5)
    return resp.json().get("players", [])

# —— 文本生成 —— #
def format_output(show_health=False, ping_threshold=100):
    try:
        info = get_server_info()
    except Exception as e:
        return f"❌ 获取服务器信息失败：{e}"

    try:
        metrics = get_server_metrics()
    except Exception as e:
        metrics = {}

    try:
        players = get_player_list()
    except Exception as e:
        players = []

    text = ["🦖 Palworld REST API 服务器状态\n"]

    # 基本信息
    text.append("🎮 服务器信息")
    text.append(f"名称：{info.get('servername')}")
    text.append(f"描述：{info.get('description')}")
    text.append(f"版本：{info.get('version')}")
    text.append(f"最大玩家数：{info.get('maxPlayers', '未知')}")
    text.append(f"在线玩家数：{len(players)}")
    uptime_sec = metrics.get("uptime", 0)
    text.append(f"运行时长：{uptime_sec // 3600}h {(uptime_sec % 3600) // 60}m")

    # 玩家信息
    text.append("👥 在线玩家详情")
    if not players:
        text.append("暂无玩家在线")
    else:
        for p in players:
            name = p.get("name")
            lvl = p.get("level", 0)
            ping = p.get("ping", 0)
            x = p.get("location_x", 0)
            y = p.get("location_y", 0)
            health = p.get("health", "未知") if show_health else None

            high_ping = "⚠️" if ping > ping_threshold else ""
            line = f"- {name} 等级:{lvl} Ping:{ping}{high_ping} 坐标:({x},{y})"
            if show_health:
                line += f" 血量:{health}"
            text.append(line)

    text.append("\nℹ 数据来源：REST API，可能存在数秒延迟")
    return "\n".join(text)

parser = argparse.ArgumentParser(description="Palworld REST API 服务器状态查询")
parser.add_argument("--show-health", action="store_true", help="显示玩家血量")
parser.add_argument("--ping-threshold", type=int, default=100, help="Ping 超过阈值标记 ⚠️")
args = parser.parse_args()

@register("pal", "YourName", "一个简单的 palWorld 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    @filter.command("pal")
    # —— 命令行参数 —— #

    async def pal(self, event: AstrMessageEvent):
        """这是一个 pal world 指令"""
        user_name = event.get_sender_name()
        message_chain = event.get_messages() 
        message_str = format_output(show_health=args.show_health, ping_threshold=args.ping_threshold)
        logger.info(message_chain)
        yield event.plain_result(f"你好，{user_name},你请求的服务器信息：\n{message_str}!") 

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
