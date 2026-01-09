from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from palworld_coord import sav_to_map, map_to_sav


try:
    from .paintPlayers import piantPlayersOnMap
except ImportError:
    from paintPlayers import piantPlayersOnMap
import base64
import requests
import argparse
import os



# —— 配置 —— #
REST_HOST = "http://139.155.69.131:8212"
USERNAME = "admin"
PASSWORD = "17191719"

TOOL_VER = "1.0.3" # 这个脚本的版本号

# Basic Auth 头
auth_bytes = f"{USERNAME}:{PASSWORD}".encode("utf-8")
auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
HEADERS = {
    "Authorization": f"Basic {auth_b64}",
    "Accept": "application/json"
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
    data = resp.json()

    players = data.get("players", [])

    if isinstance(players, dict):
        players = list(players.values())

    return players


# —— 文本生成 —— #
def format_output(ping_threshold=100, output_dir="."):
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
    
    players.sort(key=lambda p: p.get("level",0),reverse=True)

    text = ["🦖 Palworld服务器状态\n"]

    # 基本信息
    text.append("🎮 服务器信息")
    text.append(f"名称：{info.get('servername')}")
    text.append(f"描述：{info.get('description')}")
    text.append(f"版本：{info.get('version')}")
    text.append(f"在线玩家数：{len(players)}")
    days = metrics.get("days")
    if days is None:
        text.append("这是帕鲁世界的第：未知天")
    else:
        text.append(f"这是帕鲁世界的第：{days}天")
    uptime_sec = metrics.get("uptime")
    if uptime_sec is None:
        text.append("运行时长：未知")
    else:
        text.append(f"运行时长：{uptime_sec // 3600}h {(uptime_sec % 3600) // 60}m")

    # 玩家信息
    text.append("👥 在线玩家详情：")
    if not players:
        text.append("暂无玩家在线喵~")
    else:
        names = []
        xs = []
        ys = []
        for p in players:
            text.append("\n----------")
            name = p.get("name","未知玩家")
            lvl = p.get("level", 0)
            ping = p.get("ping", 0)
            ping_str = f"{ping:.1f}"   #用于ping值显示保留一位小数
            apiX = p.get("location_x", 0)
            apiY = p.get("location_y", 0)
            map_point = sav_to_map(apiX, apiY)
            x = map_point.x
            y = map_point.y
            
            names.append(name)
            xs.append(x)
            ys.append(y)
            
            x_str = f"{x:.2f}"
            y_str = f"{y:.2f}"

            high_ping = "⚠️" if ping > ping_threshold else "✅"
            
            line = f"- {name} 等级:{lvl} Ping:{ping_str}{high_ping}\n 坐标:({x_str},{y_str})"
            text.append(line)
        #使用指定的输出目录
        output_path = os.path.join(output_dir, "output.jpeg")
        piantPlayersOnMap(names, xs, ys, output_path=output_path)


    text.append("----------")
    
    text.append(f"工具版本：{TOOL_VER}")
    text.append("\nℹ 以上信息由Caramel为您播报~")
    return "\n".join(text)


parser = argparse.ArgumentParser(description="Palworld REST API 服务器状态查询")
parser.add_argument("--ping-threshold", type=int, default=100, help="Ping 超过阈值标记 ⚠️")
args = parser.parse_args()

@register("pal", "YourName", "一个简单的 palWorld 插件", TOOL_VER)
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    #@filter.command("pal")
    #async def pal_Info(self, event: AstrMessageEvent):
    #    """这是一个 pal world 指令"""
    #    message_chain = event.get_messages() 
    #    message_str = format_output(ping_threshold=args.ping_threshold)
    #    logger.info(message_chain)
    #    yield event.plain_result(f"{message_str}!") 

    @filter.command("pal")
    async def pal(self, event: AstrMessageEvent):
        """这是一个 pal world 指令"""
        # 获取插件目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 设置输出图片路径
        output_file = os.path.join(current_dir, "output.jpeg")
    
        # 将输出路径传递给 format_output 函数
        message_str = format_output(ping_threshold=args.ping_threshold, output_dir=current_dir)
    
        # 检查图片是否存在，如果不存在则输出错误信息
        if os.path.exists(output_file):
            yield event.plain_result(message_str)
            yield event.image_result(output_file) # 发送图片
        else:
            yield event.plain_result(f"{message_str}\n\n⚠️ 实时定位图生成失败。")
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""