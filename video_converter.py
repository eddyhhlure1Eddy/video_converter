import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import shutil

# 尝试导入拖放处理模块
try:
    from tkdnd_handler import DragDropHandler, install_tkdnd_guide
    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False

class VideoConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("视频批量转码工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.setup_ui()
        self.video_files = []
        self.ffmpeg_path = self.check_ffmpeg()
        
        # 初始化输出目录为 "converted_videos" 子文件夹
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "converted_videos")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.output_dir_var.set(self.output_dir)
        
        # 设置文件拖放处理
        self.setup_drag_drop()
        
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部信息区域
        info_frame = ttk.LabelFrame(main_frame, text="信息", padding=5)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="此工具用于修复和转码视频文件，特别是修复iPhone录制的显示为绿色的MP4文件").pack(anchor=tk.W)
        
        # 创建拖放区域
        drop_frame = ttk.LabelFrame(main_frame, text="拖放区域", padding=10)
        drop_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.drop_area = ScrolledText(drop_frame, height=10, width=70, state='disabled')
        self.drop_area.pack(fill=tk.BOTH, expand=True)
        
        # 创建提示标签
        self.drop_label = ttk.Label(drop_frame, text="拖放视频文件到此处或点击\"添加文件\"按钮")
        self.drop_label.pack(pady=5)
        
        # 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="设置", padding=5)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 输出路径设置
        path_frame = ttk.Frame(settings_frame)
        path_frame.pack(fill=tk.X, expand=True, pady=5)
        
        ttk.Label(path_frame, text="输出目录:").pack(side=tk.LEFT, padx=5)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.output_dir_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(path_frame, text="浏览...", command=self.browse_output_dir).pack(side=tk.LEFT, padx=5)
        
        # 转码格式选择
        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill=tk.X, expand=True, pady=5)
        
        ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT, padx=5)
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, values=["mp4", "mov", "avi", "mkv"], width=10)
        format_combo.pack(side=tk.LEFT, padx=5)
        
        # 质量设置
        ttk.Label(format_frame, text="质量:").pack(side=tk.LEFT, padx=5)
        self.quality_var = tk.StringVar(value="高")
        quality_combo = ttk.Combobox(format_frame, textvariable=self.quality_var, values=["低", "中", "高"], width=10)
        quality_combo.pack(side=tk.LEFT, padx=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="添加文件", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空列表", command=self.clear_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="开始转码", command=self.start_conversion).pack(side=tk.RIGHT, padx=5)
        
        # 进度区域
        progress_frame = ttk.LabelFrame(main_frame, text="进度", padding=5)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, expand=True, pady=5)
        
        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = ScrolledText(log_frame, height=5, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state='disabled')
        
    def setup_drag_drop(self):
        """设置拖放功能"""
        if TKDND_AVAILABLE:
            try:
                # 使用TkinterDnD库实现拖放
                self.dnd_handler = DragDropHandler(self.root, self.drop_area, self.handle_dropped_files)
                if self.dnd_handler.tkdnd_available:
                    self.drop_label.config(text="将视频文件拖放到此处")
                    self.log("已启用拖放功能")
                else:
                    self.setup_fallback_drop()
            except Exception as e:
                self.log(f"设置拖放功能时出错: {str(e)}")
                self.setup_fallback_drop()
        else:
            # 使用备用方法
            self.setup_fallback_drop()
            self.log("拖放功能未启用。如需启用，请安装TkinterDnD2库")
    
    def setup_fallback_drop(self):
        """设置备用拖放方法（实际上只是绑定点击事件）"""
        self.drop_area.config(state='normal')
        self.drop_area.bind("<Button-1>", lambda e: self.add_files())
        self.drop_area.config(state='disabled')
    
    def handle_dropped_files(self, file_paths):
        """处理拖放的文件列表"""
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.video_files and self.is_video_file(file_path):
                    self.video_files.append(file_path)
            self.update_drop_area()
    
    @staticmethod
    def is_video_file(file_path):
        """检查文件是否为视频文件"""
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.webm']
        _, ext = os.path.splitext(file_path.lower())
        return ext in video_extensions
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)
            self.output_dir = directory
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="选择视频文件",
            filetypes=(
                ("视频文件", "*.mp4 *.mov *.avi *.mkv *.m4v *.wmv *.flv *.webm"),
                ("所有文件", "*.*")
            )
        )
        
        if files:
            for file in files:
                if file not in self.video_files:
                    self.video_files.append(file)
            self.update_drop_area()
    
    def clear_files(self):
        self.video_files = []
        self.update_drop_area()
    
    def update_drop_area(self):
        self.drop_area.config(state='normal')
        self.drop_area.delete(1.0, tk.END)
        
        for i, file in enumerate(self.video_files, 1):
            filename = os.path.basename(file)
            self.drop_area.insert(tk.END, f"{i}. {filename}\n")
        
        self.drop_area.config(state='disabled')
    
    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        print(message)
    
    def check_ffmpeg(self):
        """检查系统中是否安装了ffmpeg"""
        try:
            # 尝试查找ffmpeg
            if os.name == 'nt':  # Windows
                # 尝试在当前目录和PATH中查找
                local_ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg.exe')
                if os.path.exists(local_ffmpeg):
                    self.log(f"找到本地ffmpeg: {local_ffmpeg}")
                    return local_ffmpeg
                
                # 在PATH中查找
                result = subprocess.run(['where', 'ffmpeg'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, 
                                      text=True, 
                                      creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    ffmpeg_path = result.stdout.strip().split('\n')[0]
                    self.log(f"找到系统ffmpeg: {ffmpeg_path}")
                    return ffmpeg_path
            else:  # Linux/Mac
                result = subprocess.run(['which', 'ffmpeg'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, 
                                      text=True)
                if result.returncode == 0:
                    ffmpeg_path = result.stdout.strip()
                    self.log(f"找到系统ffmpeg: {ffmpeg_path}")
                    return ffmpeg_path
            
            # 如果没有找到ffmpeg，显示警告并提供下载链接
            messagebox.showwarning(
                "未找到FFmpeg", 
                "在系统中未找到FFmpeg。请下载并安装FFmpeg，或将它放在程序同目录下。\n"
                "FFmpeg下载链接: https://ffmpeg.org/download.html"
            )
            return None
        except Exception as e:
            self.log(f"检查ffmpeg出错: {str(e)}")
            return None
    
    def get_ffmpeg_params(self):
        """根据质量设置返回ffmpeg参数"""
        quality = self.quality_var.get()
        
        if quality == "高":
            return ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-c:a", "aac", "-b:a", "192k"]
        elif quality == "中":
            return ["-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "128k"]
        else:  # 低
            return ["-c:v", "libx264", "-preset", "fast", "-crf", "28", "-c:a", "aac", "-b:a", "96k"]

    def fix_iphone_video(self, input_file, output_file):
        """修复iPhone绿屏视频并转码到指定格式"""
        if not self.ffmpeg_path:
            self.log("错误: 未找到FFmpeg，无法进行转码")
            return False
        
        try:
            # 获取质量设置的参数
            quality_params = self.get_ffmpeg_params()
            
            # 构建FFmpeg命令
            cmd = [
                self.ffmpeg_path,
                "-i", input_file,
                "-pix_fmt", "yuv420p",  # 修复绿屏问题
                *quality_params,
                "-y",  # 自动覆盖输出文件
                output_file
            ]
            
            self.log(f"执行命令: {' '.join(cmd)}")
            
            # 创建子进程并捕获输出
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # 读取输出
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                # 在日志中记录进度信息（可选择性过滤掉一些信息）
                if "frame=" in line or "speed=" in line:
                    self.status_var.set(line.strip())
                else:
                    self.log(line.strip())
            
            # 等待进程完成
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                self.log(f"成功转码: {os.path.basename(input_file)}")
                return True
            else:
                self.log(f"转码失败: {os.path.basename(input_file)}, 返回代码: {return_code}")
                return False
                
        except Exception as e:
            self.log(f"转码错误: {str(e)}")
            return False

    def start_conversion(self):
        if not self.video_files:
            messagebox.showinfo("提示", "请先添加视频文件")
            return
        
        if not self.ffmpeg_path:
            messagebox.showerror("错误", "未找到FFmpeg，无法进行转码")
            return
        
        # 禁用按钮，防止重复点击
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(state='disabled')
        
        # 创建输出目录（如果不存在）
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except Exception as e:
                messagebox.showerror("错误", f"创建输出目录失败: {str(e)}")
                return
        
        # 在新线程中执行转码，避免阻塞UI
        threading.Thread(target=self.conversion_thread, daemon=True).start()
    
    def conversion_thread(self):
        try:
            total_files = len(self.video_files)
            successful_count = 0
            
            for i, input_file in enumerate(self.video_files):
                # 更新进度
                progress_percent = (i / total_files) * 100
                self.progress_var.set(progress_percent)
                self.status_var.set(f"正在处理 {i+1}/{total_files}: {os.path.basename(input_file)}")
                
                # 确定输出文件名
                filename = os.path.basename(input_file)
                name, _ = os.path.splitext(filename)
                output_format = self.format_var.get()
                output_file = os.path.join(self.output_dir, f"{name}_fixed.{output_format}")
                
                # 执行转码
                self.log(f"开始处理: {filename} -> {os.path.basename(output_file)}")
                success = self.fix_iphone_video(input_file, output_file)
                
                if success:
                    successful_count += 1
            
            # 完成转码
            self.progress_var.set(100)
            self.status_var.set(f"转码完成: {successful_count}/{total_files} 个文件成功转码")
            messagebox.showinfo("完成", f"转码完成\n成功: {successful_count}/{total_files}")
            
        except Exception as e:
            self.log(f"转码过程中发生错误: {str(e)}")
            messagebox.showerror("错误", f"转码过程中发生错误: {str(e)}")
        
        finally:
            # 重新启用按钮
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.config(state='normal')

def main():
    # 尝试使用TkinterDnD初始化窗口
    try:
        from tkinterdnd2 import TkinterDnD
        print("使用TkinterDnD初始化窗口")
        root = TkinterDnD.Tk()
    except ImportError:
        print("未找到TkinterDnD库，使用标准Tk")
        root = tk.Tk()
    
    app = VideoConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main() 