"""
简单的图标生成脚本，用于创建视频转码工具的应用图标
"""

import os
from PIL import Image, ImageDraw, ImageFont
import sys

def create_icon(output_path="icon.ico", size=256):
    """创建一个简单的应用图标"""
    # 创建一个正方形画布
    img = Image.new('RGBA', (size, size), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    center = size // 2
    radius = size // 2 - 10
    draw.ellipse(
        [(center - radius, center - radius), (center + radius, center + radius)],
        fill=(58, 126, 191, 255)  # 蓝色背景
    )
    
    # 绘制视频播放标志
    inner_radius = radius * 0.8
    triangle_size = inner_radius * 0.8
    
    # 绘制转换图标 (两个箭头)
    arrow_width = radius * 0.2
    arrow_length = radius * 1.0
    
    # 第一个箭头 (顶部)
    arrow1_start = (center - arrow_length // 2, center - triangle_size // 2)
    arrow1_end = (center + arrow_length // 2, center - triangle_size // 2)
    
    # 第二个箭头 (底部)
    arrow2_start = (center + arrow_length // 2, center + triangle_size // 2)
    arrow2_end = (center - arrow_length // 2, center + triangle_size // 2)
    
    # 绘制箭头线
    for i in range(int(arrow_width)):
        offset = i - arrow_width // 2
        draw.line(
            [
                (arrow1_start[0], arrow1_start[1] + offset),
                (arrow1_end[0], arrow1_end[1] + offset)
            ],
            fill=(255, 255, 255, 255),
            width=1
        )
        draw.line(
            [
                (arrow2_start[0], arrow2_start[1] + offset),
                (arrow2_end[0], arrow2_end[1] + offset)
            ],
            fill=(255, 255, 255, 255),
            width=1
        )
    
    # 绘制箭头头部
    arrowhead_size = arrow_width
    
    # 第一个箭头头部 (右侧)
    draw.polygon(
        [
            (arrow1_end[0], arrow1_end[1]),
            (arrow1_end[0] - arrowhead_size, arrow1_end[1] - arrowhead_size),
            (arrow1_end[0] - arrowhead_size, arrow1_end[1] + arrowhead_size)
        ],
        fill=(255, 255, 255, 255)
    )
    
    # 第二个箭头头部 (左侧)
    draw.polygon(
        [
            (arrow2_end[0], arrow2_end[1]),
            (arrow2_end[0] + arrowhead_size, arrow2_end[1] - arrowhead_size),
            (arrow2_end[0] + arrowhead_size, arrow2_end[1] + arrowhead_size)
        ],
        fill=(255, 255, 255, 255)
    )
    
    # 保存图标
    img.save(output_path)
    print(f"图标已保存为 {output_path}")
    
    # 返回图标路径
    return output_path

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw
        output = "icon.ico"
        if len(sys.argv) > 1:
            output = sys.argv[1]
        create_icon(output)
    except ImportError:
        print("错误: 需要安装PIL库才能创建图标")
        print("请运行: pip install pillow") 