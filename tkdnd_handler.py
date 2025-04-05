"""
TkinterDnD 拖放处理模块
此模块提供了与 TkinterDnD2 库的集成，以启用更高级的拖放功能。
如果没有安装 TkinterDnD2，程序仍然可以工作，但不会有拖放功能。
"""

import os
import sys
import tkinter as tk

class DragDropHandler:
    """处理拖放操作的类，与TkinterDnD库集成"""
    
    def __init__(self, root, drop_target, callback_function):
        """
        初始化拖放处理器
        
        参数:
            root: Tkinter根窗口
            drop_target: 要接收拖放的组件
            callback_function: 接收文件路径列表的回调函数
        """
        self.root = root
        self.drop_target = drop_target
        self.callback = callback_function
        self.tkdnd_available = False
        
        # 尝试导入TkinterDnD
        try:
            # Python 3中TkinterDnD2的导入路径
            from tkinterdnd2 import TkinterDnD, DND_FILES
            self.TkinterDnD = TkinterDnD
            self.DND_FILES = DND_FILES
            self.tkdnd_available = True
        except ImportError:
            try:
                # 尝试其他可能的导入路径
                from TkinterDnD2 import TkinterDnD, DND_FILES
                self.TkinterDnD = TkinterDnD
                self.DND_FILES = DND_FILES
                self.tkdnd_available = True
            except ImportError:
                self.tkdnd_available = False
        
        if self.tkdnd_available:
            self.setup_tkdnd()
    
    def setup_tkdnd(self):
        """设置TkinterDnD拖放功能"""
        if not self.tkdnd_available:
            return False
        
        try:
            # 确保根窗口是TkinterDnD.Tk的实例
            if not isinstance(self.root, self.TkinterDnD.Tk):
                # 如果root不是TkinterDnD.Tk的实例，需要使用TkDnD初始化它
                # 注意：这个步骤可能不必要，因为应该在创建窗口时就使用TkinterDnD.Tk()
                print("根窗口不是TkinterDnD.Tk的实例，尝试进行兼容处理")
            
            # 直接尝试注册拖放目标和源
            self.TkinterDnD.Tk.drop_target_register(self.root, self.DND_FILES)
            
            # 注册拖放目标
            try:
                self.drop_target.drop_target_register(self.DND_FILES)
                self.drop_target.dnd_bind('<<Drop>>', self.handle_drop)
                print("成功注册拖放目标")
                return True
            except Exception as e:
                print(f"注册拖放目标时出错: {str(e)}")
                # 尝试备用方法 - 有些版本的TkinterDnD需要不同的注册方式
                try:
                    self.root.drop_target_register(self.drop_target, self.DND_FILES)
                    self.drop_target.bind('<<Drop>>', self.handle_drop)
                    print("使用备用方法成功注册拖放目标")
                    return True
                except Exception as e2:
                    print(f"备用注册方法也失败: {str(e2)}")
                    return False
        except Exception as e:
            print(f"设置TkinterDnD时出错: {str(e)}")
            return False
    
    def handle_drop(self, event):
        """处理拖放事件"""
        try:
            # 获取拖放的文件路径
            print(f"收到拖放事件: {event.data}")
            file_paths = self.parse_drop_data(event.data)
            
            # 调用回调函数处理文件
            if file_paths and callable(self.callback):
                print(f"找到文件: {file_paths}")
                self.callback(file_paths)
            else:
                print(f"未能解析到有效文件或回调函数不可用")
        except Exception as e:
            print(f"处理拖放时出错: {str(e)}")
    
    @staticmethod
    def parse_drop_data(data):
        """
        解析拖放数据，提取文件路径
        
        参数:
            data: 从拖放事件获取的数据
            
        返回:
            文件路径列表
        """
        files = []
        
        print(f"原始拖放数据: {data}")
        
        # 处理不同操作系统的换行符和路径格式
        for item in data.split():
            item = item.strip()
            
            # 处理Windows中的路径格式 {C:/path/to/file.mp4}
            if item.startswith('{') and item.endswith('}'):
                item = item[1:-1]
            
            # 规范化路径分隔符
            item = os.path.normpath(item)
            
            print(f"处理后的路径: {item}")
            
            if os.path.exists(item):
                files.append(item)
                print(f"添加有效文件: {item}")
            else:
                print(f"文件不存在: {item}")
        
        return files

def install_tkdnd_guide():
    """返回安装TkinterDnD2的指南"""
    return """
要启用拖放功能，请安装TkinterDnD2库:

使用pip安装:
pip install tkinterdnd2

或者从GitHub下载:
https://github.com/pmgagne/tkinterdnd2

安装后重启程序以启用拖放功能。
""" 