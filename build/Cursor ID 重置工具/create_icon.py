from PIL import Image, ImageDraw
import os

def create_icon():
    # 创建图标尺寸列表
    sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    
    # 创建一个空的图标列表
    images = []
    
    for size in sizes:
        # 创建新图像
        image = Image.new('RGBA', size, (0,0,0,0))
        draw = ImageDraw.Draw(image)
        
        # 计算边距
        padding = size[0] // 8
        
        # 绘制圆形背景
        draw.ellipse([padding, padding, size[0]-padding, size[1]-padding], 
                    fill='#007AFF')
        
        # 绘制刷新符号
        arrow_points = [
            (size[0]//3, size[1]//2),
            (size[0]//2, size[1]//3),
            (2*size[0]//3, size[1]//2)
        ]
        draw.line(arrow_points, fill='white', width=max(1, size[0]//16))
        
        # 添加到图标列表
        images.append(image)
    
    # 保存为ICO文件
    icon_path = 'icon.ico'
    images[0].save(icon_path, format='ICO', sizes=sizes)
    print(f"图标已创建: {os.path.abspath(icon_path)}")

if __name__ == "__main__":
    create_icon()