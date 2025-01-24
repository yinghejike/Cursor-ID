import json
import uuid
import os
import sys
import subprocess
import psutil  # 需要先安装：pip install psutil
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QTextEdit, QMessageBox, QHBoxLayout,
                            QLineEdit, QGridLayout, QFrame, QStyle)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QIcon

class ModernUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cursor ID 重置工具")
        self.setFixedSize(800, 600)  # 固定窗口大小
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)  # 禁用最大化按钮

        # 设置窗口图标 - 使用自定义图标
        if getattr(sys, 'frozen', False):
            # 如果是打包后的 exe 运行
            icon_path = os.path.join(sys._MEIPASS, 'iconlogo.ico')
        else:
            # 如果是源码运行
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iconlogo.ico')
            
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # 如果找不到自定义图标，使用系统默认图标
            refresh_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
            self.setWindowIcon(refresh_icon)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton#show_button {
                background-color: #5856D6;
            }
            QPushButton#show_button:hover {
                background-color: #4a49b3;
            }
            QPushButton#open_dir_button {
                background-color: #34C759;
            }
            QPushButton#open_dir_button:hover {
                background-color: #2da84c;
            }
            QPushButton#restart_button {
                background-color: #FF9500;
            }
            QPushButton#restart_button:hover {
                background-color: #e68600;
            }
            QPushButton#smart_button {
                background-color: #5856D6;
                font-weight: bold;
            }
            QPushButton#smart_button:hover {
                background-color: #4a49b3;
            }
            QLabel {
                color: #333333;
            }
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 10px;
                background-color: #ffffff;
                selection-background-color: #007AFF;
                selection-color: white;
            }
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px 12px;
                background-color: #ffffff;
                color: #202124;
                font-family: Consolas;
                font-size: 9pt;
                selection-background-color: #007AFF;
                selection-color: white;
            }
            QLineEdit:disabled {
                background-color: #f8f9fa;
                color: #202124;
            }
            QLabel#id_label {
                color: #202124;
                font-weight: bold;
                font-size: 10pt;
                padding: 5px 10px;
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                min-width: 150px;
                max-width: 150px;
            }
            QFrame#id_frame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        self.setup_ui()
        # 软件启动时自动显示当前ID信息
        self.show_current_ids()
        
    def setup_ui(self):
        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = QLabel("Cursor ID 重置工具")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 说明文本
        description = QLabel("此工具主要解决频繁更换Cursor账号后导致的ID锁定，无法使用Cursor IDE的问题。推荐用户使用智能模式，软件将自动完成Cursor的 ID重置、备份和重启，之后即可登录新账号继续使用Cursor IDE。")
        description.setFont(QFont("Microsoft YaHei", 10))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #666666;")
        description.setWordWrap(True)  # 允许文本自动换行
        layout.addWidget(description)
        
        # 开发者信息
        dev_info = QLabel("开发者：极客硬核   |   QQ：850222952   |   微信公众号：极客硬核")
        dev_info.setFont(QFont("Microsoft YaHei", 9))
        dev_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_info.setStyleSheet("color: #666666; margin-top: 5px;")
        dev_info.setWordWrap(True)
        layout.addWidget(dev_info)
        
        # ID显示区域
        id_frame = QFrame()
        id_frame.setObjectName("id_frame")
        id_layout = QVBoxLayout(id_frame)
        id_layout.setSpacing(15)
        
        # 创建ID输入框字典
        self.id_inputs = {}
        
        # 定义ID类型的显示名称
        id_names = {
            'macMachineId': 'Mac Machine ID',
            'machineId': 'Machine ID',
            'devDeviceId': 'Device ID',
            'sqmId': 'SQM ID'
        }
        
        # 设置固定的标签宽度
        label_width = 150  # 固定宽度为150像素
        
        # 为每个ID创建显示组件
        for key, name in id_names.items():
            # 创建水平布局
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)  # 设置组件之间的间距
            
            # 添加标签
            label = QLabel(name)
            label.setObjectName("id_label")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 文字居中对齐
            label.setFixedWidth(label_width)  # 设置固定宽度
            row_layout.addWidget(label)
            
            # 添加输入框
            input_field = QLineEdit()
            input_field.setReadOnly(True)
            input_field.setMinimumWidth(400)  # 设置最小宽度
            # 移除固定宽度设置，允许自动调整
            self.id_inputs[key] = input_field
            row_layout.addWidget(input_field, 1)  # 设置拉伸因子为1，允许自动填充剩余空间
            
            # 移除弹性空间，因为输入框会自动填充
            # row_layout.addStretch()
            
            # 添加到主布局
            id_layout.addLayout(row_layout)
        
        layout.addWidget(id_frame)
        
        # 按钮布局改为水平布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 左侧按钮布局（智能模式和重置按钮）
        left_button_layout = QVBoxLayout()
        left_button_layout.setSpacing(10)
        
        # 智能模式按钮
        self.smart_button = QPushButton("智能模式 (推荐)")
        self.smart_button.setObjectName("smart_button")
        self.smart_button.setFont(QFont("Microsoft YaHei", 10))
        self.smart_button.clicked.connect(self.smart_mode)
        left_button_layout.addWidget(self.smart_button)
        
        # 重置按钮
        self.refresh_button = QPushButton("重置 ID")
        self.refresh_button.setFont(QFont("Microsoft YaHei", 10))
        self.refresh_button.clicked.connect(self.refresh_ids)
        left_button_layout.addWidget(self.refresh_button)
        
        # 添加左侧按钮布局到主按钮布局
        button_layout.addLayout(left_button_layout)
        
        # 右侧按钮布局
        right_button_layout = QVBoxLayout()
        right_button_layout.setSpacing(10)
        
        # 添加打开配置目录按钮
        self.open_dir_button = QPushButton("打开配置目录")
        self.open_dir_button.setObjectName("open_dir_button")
        self.open_dir_button.setFont(QFont("Microsoft YaHei", 10))
        self.open_dir_button.clicked.connect(self.open_config_dir)
        right_button_layout.addWidget(self.open_dir_button)
        
        # 添加重启Cursor按钮
        self.restart_button = QPushButton("重启 Cursor")
        self.restart_button.setObjectName("restart_button")
        self.restart_button.setFont(QFont("Microsoft YaHei", 10))
        self.restart_button.clicked.connect(self.restart_cursor)
        right_button_layout.addWidget(self.restart_button)
        
        # 添加右侧按钮布局到主按钮布局
        button_layout.addLayout(right_button_layout)
        
        # 添加按钮布局
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        layout.addWidget(button_widget)
        
        # 状态栏
        self.statusBar().setFont(QFont("Microsoft YaHei", 9))
        self.statusBar().setStyleSheet("color: #666666;")
        self.statusBar().showMessage("就绪")
        
    def format_text(self, text, color="#202124", bold=False, size=9):
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        format.setFont(QFont("Microsoft YaHei" if bold else "Consolas", size, 
                           QFont.Weight.Bold if bold else QFont.Weight.Normal))
        cursor = self.id_text.textCursor()
        cursor.insertText(text, format)
        cursor.insertBlock()
        
    def format_id_display(self, title, id_dict, show_comparison=False):
        """格式化ID显示内容"""
        if show_comparison:
            # 只显示更新后的值
            for key, value in id_dict.items():
                self.id_inputs[key].setText(value['new'])
        else:
            # 显示当前值
            for key, value in id_dict.items():
                self.id_inputs[key].setText(value)
            self.statusBar().showMessage("已加载当前 ID 信息")
    
    def show_current_ids(self):
        current_ids = self.read_current_ids()
        if current_ids:
            self.format_id_display("📋 当前 ID 信息", current_ids)
        else:
            # 清空所有输入框
            for input_field in self.id_inputs.values():
                input_field.setText("")
            self.statusBar().showMessage("无法读取 ID 信息")
    
    def refresh_ids(self):
        """重置所有ID"""
        try:
            file_path = self.get_storage_file_path()
            if not os.path.exists(file_path):
                self.statusBar().showMessage("找不到配置文件")
                return
                
            old_ids = self.read_current_ids()
            if not old_ids:
                return
                
            id_formats = {
                key: self.analyze_id_format(value.strip('{}'))
                for key, value in old_ids.items()
            }
            
            new_ids = {}
            for key in old_ids.keys():
                new_id = self.generate_id_by_format(id_formats[key])
                if key == 'sqmId':
                    new_id = '{' + new_id + '}'
                new_ids[key] = new_id
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            data['telemetry.macMachineId'] = new_ids['macMachineId']
            data['telemetry.machineId'] = new_ids['machineId']
            data['telemetry.devDeviceId'] = new_ids['devDeviceId']
            data['telemetry.sqmId'] = new_ids['sqmId']
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            comparison_ids = {}
            for key in old_ids.keys():
                comparison_ids[key] = {
                    'old': old_ids[key],
                    'new': new_ids[key]
                }
            
            self.format_id_display("✨ ID 更新成功", comparison_ids, show_comparison=True)
            self.statusBar().showMessage("ID 已更新，已创建备份文件")
            
        except Exception as e:
            self.statusBar().showMessage(f"重置失败：{str(e)}")
    
    def get_storage_file_path(self):
        return os.path.join(os.getenv('APPDATA'), 'Cursor', 'User', 'globalStorage', 'storage.json')
    
    def read_current_ids(self):
        try:
            with open(self.get_storage_file_path(), 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {
                'macMachineId': data.get('telemetry.macMachineId', 'N/A'),
                'machineId': data.get('telemetry.machineId', 'N/A'),
                'devDeviceId': data.get('telemetry.devDeviceId', 'N/A'),
                'sqmId': data.get('telemetry.sqmId', 'N/A')
            }
        except Exception as e:
            self.statusBar().showMessage(f"读取配置文件失败：{str(e)}")
            return None
    
    def analyze_id_format(self, id_str):
        """分析ID的格式，返回格式信息"""
        if not id_str or id_str == 'N/A':
            return None
        
        # 检查是否是UUID格式 (8-4-4-4-12)
        if '-' in id_str:
            parts = id_str.split('-')
            if len(parts) == 5:
                return {
                    'type': 'uuid',
                    'lengths': [len(p) for p in parts],
                    'case': 'lower' if id_str.islower() else 'upper'
                }
        
        # 检查是否是纯十六进制字符串
        if all(c in '0123456789abcdefABCDEF' for c in id_str):
            return {
                'type': 'hex',
                'length': len(id_str),
                'case': 'lower' if id_str.islower() else 'upper'
            }
        
        return None

    def generate_id_by_format(self, format_info):
        """根据格式信息生成新ID"""
        if not format_info:
            return str(uuid.uuid4())
        
        if format_info['type'] == 'uuid':
            new_id = str(uuid.uuid4())
            if format_info['case'] == 'upper':
                new_id = new_id.upper()
            return new_id
        
        elif format_info['type'] == 'hex':
            # 生成指定长度的十六进制字符串
            hex_str = uuid.uuid4().hex
            while len(hex_str) < format_info['length']:
                hex_str += uuid.uuid4().hex
            hex_str = hex_str[:format_info['length']]
            
            if format_info['case'] == 'upper':
                hex_str = hex_str.upper()
            return hex_str

    def open_config_dir(self):
        """打开配置文件所在目录"""
        try:
            config_dir = os.path.dirname(self.get_storage_file_path())
            if os.path.exists(config_dir):
                subprocess.run(['explorer', config_dir])
                self.statusBar().showMessage("已打开配置目录")
            else:
                self.statusBar().showMessage("配置目录不存在")
        except Exception as e:
            self.statusBar().showMessage(f"无法打开配置目录：{str(e)}")

    def restart_cursor(self):
        """重启Cursor程序"""
        try:
            cursor_killed = False
            cursor_path = None
            
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    if proc.info['name'].lower() == 'cursor.exe':
                        cursor_path = proc.info['exe']
                        proc.kill()
                        cursor_killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if cursor_killed:
                self.statusBar().showMessage("正在关闭 Cursor...")
                QApplication.processEvents()
                psutil.wait_procs(psutil.Process().children(), timeout=3)
                
                if cursor_path and os.path.exists(cursor_path):
                    subprocess.Popen([cursor_path])
                    self.statusBar().showMessage("Cursor 已重启")
                else:
                    self.statusBar().showMessage("Cursor 已关闭，请手动重启")
            else:
                self.statusBar().showMessage("未找到正在运行的 Cursor")
                
        except Exception as e:
            self.statusBar().showMessage(f"重启失败：{str(e)}")

    def smart_mode(self):
        """智能模式：自动完成所有操作"""
        try:
            cursor_path = None
            cursor_running = False
            cursor_process = None
            
            # 1. 检查并关闭 Cursor
            self.statusBar().showMessage("正在检查 Cursor 状态...")
            for proc in psutil.process_iter(['name', 'exe', 'pid']):
                try:
                    if proc.info['name'].lower() == 'cursor.exe':
                        cursor_path = proc.info['exe']
                        cursor_running = True
                        cursor_process = psutil.Process(proc.info['pid'])
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if not cursor_running:
                # 如果 Cursor 未运行，尝试找到安装路径
                possible_paths = [
                    os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', 'Cursor', 'Cursor.exe'),
                    os.path.join(os.getenv('PROGRAMFILES'), 'Cursor', 'Cursor.exe'),
                    os.path.join(os.getenv('PROGRAMFILES(X86)'), 'Cursor', 'Cursor.exe')
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        cursor_path = path
                        break
            
            if cursor_running and cursor_process:
                # 关闭 Cursor
                self.statusBar().showMessage("正在关闭 Cursor...")
                try:
                    # 结束主进程及其所有子进程
                    parent = cursor_process
                    children = parent.children(recursive=True)
                    for child in children:
                        try:
                            child.kill()
                        except psutil.NoSuchProcess:
                            pass
                    parent.kill()
                    
                    # 等待所有进程完全结束
                    gone, alive = psutil.wait_procs([parent] + children, timeout=3)
                    QApplication.processEvents()
                    
                    # 额外检查确保进程已结束
                    time.sleep(1)  # 短暂等待
                    QApplication.processEvents()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # 2. 重置 ID
            self.statusBar().showMessage("正在重置 ID...")
            QApplication.processEvents()
            self.refresh_ids()
            
            # 3. 启动 Cursor
            if cursor_path and os.path.exists(cursor_path):
                self.statusBar().showMessage("正在启动 Cursor...")
                QApplication.processEvents()
                
                # 确保没有残留的 Cursor 进程
                for proc in psutil.process_iter(['name']):
                    try:
                        if proc.info['name'].lower() == 'cursor.exe':
                            proc.kill()
                            proc.wait(timeout=3)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        continue
                
                # 启动新进程
                subprocess.Popen([cursor_path])
                self.statusBar().showMessage("操作完成")
            else:
                self.statusBar().showMessage("ID 已重置，请手动启动 Cursor")
                
        except Exception as e:
            self.statusBar().showMessage(f"操作失败：{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernUI()
    window.show()
    sys.exit(app.exec())
