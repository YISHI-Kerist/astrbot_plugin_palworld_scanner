import os
from PIL import Image, ImageDraw, ImageFont

COLORS = [
    (255, 182, 193),  # 浅粉色
    (173, 216, 230),  # 浅蓝色
    (152, 251, 152),  # 浅绿色
    (255, 250, 205),  # 浅黄色
    (221, 160, 221),  # 浅紫色
    (255, 160, 122),  # 浅橙色
    (176, 224, 230),  # 淡青色
    (230, 230, 250),  # 淡紫色
]

#像素位置及其范围
posXMax = 865
posYMax = 800
posX0   = 573.4     
posY0   = 261    
scalX   = 0.29792     #横轴坐标到像素的倍率
scalY   = -scalX      #纵轴坐标到像素的倍率, 像素方向是→和↓，但坐标是→和↑，所以要处理一下


def draw_circle_on_image(img, name, x, y, fill_color, radius=10):
    draw = ImageDraw.Draw(img)
    bbox = (x - radius, y - radius, x + radius, y + radius)
    draw.ellipse(bbox, fill=fill_color, outline=(80, 80, 80), width=2)
    try:
        font = ImageFont.truetype("msyhbd.ttc", 24) 
    except:
        font = ImageFont.load_default()
    
    try:
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    except:
        text_width, text_height = draw.textsize(name, font=font)
    
    text_x = x - text_width // 2
    text_y = y + radius + 2 
    
    draw.text((text_x, text_y), name, fill_color, font=font)
    
    return img

def piantPlayersOnMap(names, xs, ys, output_path="./output.jpeg"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    map_path = os.path.join(current_dir, "originMap.jpeg")
    
    # 如果 map_path 不存在，尝试其他可能的路径
    if not os.path.exists(map_path):
        # 尝试在当前工作目录下查找
        map_path = "originMap.jpeg"
    
    # 如果还是找不到，使用一个默认图像或输出错误
    if not os.path.exists(map_path):
        print(f"警告: 地图文件未找到: {map_path}")
        # 这里可以创建一个简单的默认图像
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((100, 100), "地图文件未找到", fill='black')
    else:
        img = Image.open(map_path).convert('RGB')

    if isinstance(names, str):
        names = [names]
    if not isinstance(xs, (list, tuple)):
        xs = [xs]
    if not isinstance(ys, (list, tuple)):
        ys = [ys]

    for i, (name, x, y) in enumerate(zip(names, xs, ys)):
        posX = x*scalX + posX0
        posY = y*scalY + posY0
        if posX > posXMax:
            posX = posXMax
        if posY > posYMax:
            posY = posYMax
        if posX < 0:
            posX = 0
        if posY < 0:
            posY = 0
        print(f"P1, {name}:({posX:.1f},{posY:.1f})")#debug

        img = draw_circle_on_image(img, name, posX, posY, COLORS[i%8])
    



    img.save(output_path)

