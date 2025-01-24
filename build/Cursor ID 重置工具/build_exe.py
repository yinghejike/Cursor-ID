import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'cursor_id_refresher.py',  # 主程序文件
    '--name=Cursor ID 重置工具',  # 程序名称
    '--windowed',  # 使用 GUI 模式
    '--onefile',   # 打包成单个文件
    '--icon=iconlogo.ico',  # 程序图标
    '--version-file=version_info.txt',  # 版本信息文件
    '--add-data=README.md;.',  # 添加额外文件
    '--add-data=iconlogo.ico;.',  # 添加图标文件到打包数据中
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不确认覆盖
    f'--distpath={os.path.join(current_dir, "dist")}',  # 输出目录
    f'--workpath={os.path.join(current_dir, "build")}',  # 工作目录
    '--noupx',  # 不使用 UPX 压缩
    # 添加所需的隐式导入
    '--hidden-import=PyQt6',
    '--hidden-import=psutil',
    # 添加运行时临时文件处理
    '--runtime-tmpdir=.',  # 设置运行时临时目录为当前目录
    '--noconsole',  # 禁用控制台输出
]) 