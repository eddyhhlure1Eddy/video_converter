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
        self.root.geometry("900x650")  # 增加窗口尺寸
        self.root.resizable(True, True)
        
        # 设置窗口图标（如果可用）
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # 设置应用风格主题
        self.setup_styles()
        
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
    
    def setup_styles(self):
        """设置应用程序的视觉风格"""
        style = ttk.Style()
        
        # 尝试设置更现代的主题
        available_themes = style.theme_names()
        preferred_themes = ['vista', 'clam', 'winnative', 'default']
        
        for theme in preferred_themes:
            if theme in available_themes:
                style.theme_use(theme)
                break
        
        # 定制组件样式 - 确保可见性
        bg_color = "#f0f0f0"
        button_bg = "#d0d0d0"
        accent_color = "#2c6eaf"
        text_color = "#000000"
        
        # 确保组件样式清晰可见
        style.configure('TLabelframe', padding=8, relief='solid', borderwidth=1, background=bg_color)
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'), foreground=text_color, background=bg_color)
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', font=('Arial', 9), foreground=text_color, background=bg_color)
        
        # 使按钮更加醒目
        style.configure('TButton', 
                        font=('Arial', 9, 'bold'), 
                        foreground=text_color,
                        padding=8, 
                        background=button_bg, 
                        relief='raised',
                        borderwidth=2)
        
        # 鼠标悬停效果
        style.map('TButton',
                  foreground=[('active', text_color)],
                  background=[('active', button_bg)],
                  relief=[('pressed', 'sunken')])
                 
        # 主要操作按钮
        style.configure('Accent.TButton', 
                        background=accent_color, 
                        foreground='white',
                        padding=8,
                        font=('Arial', 10, 'bold'))
        
        # 鼠标悬停效果 (主要按钮)
        style.map('Accent.TButton',
                  background=[('active', '#1d5a98')],
                  foreground=[('active', 'white')])
        
        style.configure('TCheckbutton', font=('Arial', 9), foreground=text_color, background=bg_color)
        style.configure('TCombobox', padding=2)
        style.configure('Horizontal.TProgressbar', background=accent_color)
        
        # 确保ScrolledText也有好的可读性
        self.root.option_add("*Text.Background", "#ffffff")
        self.root.option_add("*Text.Foreground", "#000000")
        
        # 区域边框颜色
        style.configure('Card.TFrame', background="#ffffff", relief="solid", borderwidth=1)
    
    def setup_ui(self):
        # 创建主框架，使用两列布局
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左右布局
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 0), ipadx=5)
        right_panel.configure(width=280)  # 固定右侧面板宽度
        
        # ===== 左侧面板 =====
        # 顶部信息区域 - 使用鲜明的背景色
        info_frame = ttk.Frame(left_panel, style='Card.TFrame')
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 使标题更加突出
        info_label = ttk.Label(
            info_frame, 
            text="视频批量转码与超分辨率工具",
            font=('Arial', 12, 'bold'),
            foreground="#2c6eaf",
            padding=8
        )
        info_label.pack(anchor=tk.W)
        
        # 增强描述文本对比度
        desc_label = ttk.Label(
            info_frame, 
            text="此工具可以修复iPhone录制的绿屏视频，并支持批量转码与超分辨率处理",
            foreground="#000000",
            background="#ffffff",
            padding=(8, 0, 8, 8),
            wraplength=550
        )
        desc_label.pack(anchor=tk.W)
        
        # 创建拖放区域
        drop_frame = ttk.LabelFrame(left_panel, text="文件列表", padding=8)
        drop_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 添加一个文件操作工具栏
        file_toolbar = ttk.Frame(drop_frame)
        file_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.drop_label = ttk.Label(file_toolbar, text="拖放视频文件到此处或使用下方按钮添加文件")
        self.drop_label.pack(side=tk.LEFT)
        
        # 添加文件数量指示器
        self.file_count_var = tk.StringVar(value="0 个文件")
        ttk.Label(file_toolbar, textvariable=self.file_count_var).pack(side=tk.RIGHT)
        
        # 拖放区
        self.drop_area = ScrolledText(drop_frame, height=12, width=70, state='disabled')
        self.drop_area.pack(fill=tk.BOTH, expand=True)
        self.drop_area.configure(font=('Consolas', 10), background='#f9f9f9')
        
        # 文件操作按钮行 - 增加padding确保按钮可见
        file_actions = ttk.Frame(drop_frame)
        file_actions.pack(fill=tk.X, pady=(5, 0))
        
        # 给按钮添加更明显的样式和间距 - 使用标准tk.Button提高兼容性
        add_button = tk.Button(
            file_actions, 
            text="添加文件", 
            command=self.add_files,
            font=('Arial', 9, 'bold'),
            relief='raised',
            bg='#e1e1e1',
            borderwidth=2,
            padx=10,
            pady=5
        )
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        clear_button = tk.Button(
            file_actions, 
            text="清空列表", 
            command=self.clear_files,
            font=('Arial', 9, 'bold'),
            relief='raised',
            bg='#e1e1e1',
            borderwidth=2,
            padx=10,
            pady=5
        ) 
        clear_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 使用标准tk.Button代替ttk.Button确保颜色正确显示
        start_button = tk.Button(
            file_actions, 
            text="开始处理", 
            command=self.start_conversion,
            font=('Arial', 10, 'bold'),
            bg='#2c6eaf',  # 确保使用鲜明的蓝色
            fg='white',
            relief='raised',
            borderwidth=2,
            padx=10,
            pady=5
        )
        start_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 设置按钮悬停效果
        start_button.bind("<Enter>", lambda e: e.widget.config(bg='#1d5a98'))
        start_button.bind("<Leave>", lambda e: e.widget.config(bg='#2c6eaf'))
        
        # 进度与日志区域 - 使用Notebook标签页组织
        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 进度标签页
        progress_frame = ttk.Frame(notebook, padding=10)
        notebook.add(progress_frame, text="处理进度")
        
        self.progress_var = tk.DoubleVar()
        progress_label_frame = ttk.Frame(progress_frame)
        progress_label_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(progress_label_frame, text="转码进度:").pack(side=tk.LEFT)
        self.progress_percent = tk.StringVar(value="0%")
        ttk.Label(progress_label_frame, textvariable=self.progress_percent, font=('Arial', 9, 'bold')).pack(side=tk.RIGHT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, style='Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))
        
        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=tk.W, pady=(0, 10))
        
        # 输出预览区域
        preview_frame = ttk.LabelFrame(progress_frame, text="输出预览")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = ScrolledText(preview_frame, height=6, width=70)
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.preview_text.config(state='disabled', font=('Consolas', 9))
        
        # 日志标签页
        log_frame = ttk.Frame(notebook, padding=10)
        notebook.add(log_frame, text="处理日志")
        
        self.log_text = ScrolledText(log_frame, height=12, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state='disabled', font=('Consolas', 9))
        
        # ===== 右侧面板 - 设置区域 =====
        # 基本设置框架
        settings_frame = ttk.LabelFrame(right_panel, text="基本设置", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 输出目录设置 - 确保按钮明显
        ttk.Label(settings_frame, text="输出目录:", foreground="#000000").pack(anchor=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.output_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.output_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        # 使用tk.Button确保颜色一致
        browse_button = tk.Button(
            dir_frame, 
            text="浏览", 
            command=self.browse_output_dir,
            font=('Arial', 9, 'bold'),
            bg='#e1e1e1',
            relief='raised',
            borderwidth=2,
            width=6
        )
        browse_button.pack(side=tk.RIGHT)
        
        # 输出格式设置
        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="mp4")
        ttk.Combobox(format_frame, textvariable=self.format_var, values=["mp4", "mov", "avi", "mkv"], width=8, state="readonly").pack(side=tk.RIGHT)
        
        # 质量设置
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(quality_frame, text="输出质量:").pack(side=tk.LEFT)
        self.quality_var = tk.StringVar(value="高")
        ttk.Combobox(quality_frame, textvariable=self.quality_var, values=["低", "中", "高"], width=8, state="readonly").pack(side=tk.RIGHT)
        
        # 超分辨率设置框架
        sr_frame = ttk.LabelFrame(right_panel, text="超分辨率设置", padding=10)
        sr_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 启用超分辨率
        self.sr_enabled_var = tk.BooleanVar(value=False)
        sr_check = ttk.Checkbutton(
            sr_frame, 
            text="启用超分辨率处理", 
            variable=self.sr_enabled_var,
            command=self.toggle_sr_options
        )
        sr_check.pack(anchor=tk.W, pady=(0, 5))
        
        # 超分辨率控制区
        sr_controls = ttk.Frame(sr_frame)
        sr_controls.pack(fill=tk.X)
        
        # 超分倍率
        scale_frame = ttk.Frame(sr_controls)
        scale_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(scale_frame, text="超分倍率:").pack(side=tk.LEFT)
        self.sr_scale_var = tk.StringVar(value="2x")
        self.sr_scale_combo = ttk.Combobox(
            scale_frame, 
            textvariable=self.sr_scale_var,
            values=["1.5x", "2x", "3x", "4x"], 
            width=8, 
            state="disabled"
        )
        self.sr_scale_combo.pack(side=tk.RIGHT)
        
        # 超分算法
        algorithm_frame = ttk.Frame(sr_controls)
        algorithm_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(algorithm_frame, text="超分算法:").pack(side=tk.LEFT)
        self.sr_algorithm_var = tk.StringVar(value="lanczos")
        self.sr_algorithm_combo = ttk.Combobox(
            algorithm_frame, 
            textvariable=self.sr_algorithm_var,
            values=["lanczos", "bicubic", "bilinear", "neighbor"],
            width=8, 
            state="disabled"
        )
        self.sr_algorithm_combo.pack(side=tk.RIGHT)
        
        # 添加警告标签
        warning_frame = ttk.Frame(sr_frame, style='Card.TFrame')
        warning_frame.pack(fill=tk.X, pady=(5, 0))
        warning_frame.configure(padding=5)
        
        warning_label = ttk.Label(
            warning_frame, 
            text="⚠️ 警告: 高倍率可能导致转码失败或内存不足",
            foreground="red",
            font=('Arial', 8)
        )
        warning_label.pack(anchor=tk.W)
        
        # 提示框
        tip_frame = ttk.LabelFrame(right_panel, text="使用提示", padding=10)
        tip_frame.pack(fill=tk.X, pady=(0, 10))
        
        tips = [
            "• 推荐使用1.5x-2x超分辨率获得最佳效果",
            "• 超分辨率会显著增加处理时间和文件大小",
            "• 如果转码失败，请尝试降低超分倍率",
            "• 高质量转码参数适合用于最终输出",
            "• 中低质量选项处理速度更快，文件更小"
        ]
        
        for tip in tips:
            ttk.Label(tip_frame, text=tip, wraplength=250, justify=tk.LEFT, font=('Arial', 8)).pack(anchor=tk.W, pady=1)
        
        # 添加关于/版本信息
        version_frame = ttk.Frame(right_panel)
        version_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        ttk.Label(version_frame, text="视频批量转码工具 v1.1", font=('Arial', 8), foreground='gray').pack(side=tk.LEFT)
        
    def setup_drag_drop(self):
        """设置拖放功能"""
        if TKDND_AVAILABLE:
            try:
                # 使用TkinterDnD库实现拖放
                self.dnd_handler = DragDropHandler(self.root, self.drop_area, self.handle_dropped_files)
                if self.dnd_handler.tkdnd_available:
                    self.drop_label.config(text="拖放视频文件到此处")
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
        
        # 更新文件计数
        count = len(self.video_files)
        self.file_count_var.set(f"{count} 个文件")
        
        # 更新预览窗口
        self.update_preview()
    
    def update_preview(self):
        """更新输出预览窗口"""
        if not self.video_files:
            return
        
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        
        # 显示最多3个示例输出
        samples = min(3, len(self.video_files))
        
        for i in range(samples):
            filename = os.path.basename(self.video_files[i])
            name, ext = os.path.splitext(filename)
            output_format = self.format_var.get()
            
            # 如果启用了超分，展示效果
            if self.sr_enabled_var.get():
                name = f"{name}_SR{self.sr_scale_var.get()}"
            
            output_file = f"{name}_fixed.{output_format}"
            
            self.preview_text.insert(tk.END, f"输入: {filename}\n")
            self.preview_text.insert(tk.END, f"输出: {output_file}\n")
            
            if i < samples - 1:
                self.preview_text.insert(tk.END, f"\n")
        
        if len(self.video_files) > 3:
            self.preview_text.insert(tk.END, f"...(还有 {len(self.video_files) - 3} 个文件)\n")
        
        self.preview_text.config(state='disabled')
    
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
    
    def get_sr_params(self):
        """获取超分辨率参数"""
        if not self.sr_enabled_var.get():
            return []
        
        # 解析超分倍率
        scale_str = self.sr_scale_var.get().replace('x', '')
        try:
            scale = float(scale_str)
        except ValueError:
            scale = 2.0  # 默认值
        
        # 获取视频文件信息，检查原始分辨率
        try:
            # 使用ffprobe获取当前处理的视频尺寸（假设只处理一个文件）
            if len(self.video_files) > 0:
                input_file = self.video_files[0]  # 使用第一个文件作为检查对象
                cmd = [
                    self.ffmpeg_path.replace("ffmpeg", "ffprobe") if "ffmpeg" in self.ffmpeg_path else self.ffmpeg_path,
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "csv=p=0",
                    input_file
                ]
                
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    width, height = map(int, result.stdout.strip().split(','))
                    
                    # 检查超分后的分辨率是否过大
                    target_width = int(width * scale)
                    target_height = int(height * scale)
                    
                    # 计算所需内存（估算值，假设YUV420格式，每像素1.5字节，30fps，5秒缓冲）
                    est_memory_mb = (target_width * target_height * 1.5 * 30 * 5) / (1024 * 1024)
                    
                    # 如果估计内存使用超过2GB或分辨率超过4K，发出警告并降低超分倍率
                    if est_memory_mb > 2048 or target_width > 3840 or target_height > 2160:
                        original_scale = scale
                        # 降低超分倍率至安全值
                        max_scale = min(3840 / width, 2160 / height, 2.0)
                        scale = min(scale, max_scale)
                        
                        # 记录警告日志
                        self.log(f"警告: 源视频分辨率{width}x{height}，应用{original_scale}x超分后分辨率过大")
                        self.log(f"自动调整超分倍率为{scale:.1f}x以确保稳定性")
                        
                        # 更新UI显示
                        self.sr_scale_var.set(f"{scale:.1f}x")
        except Exception as e:
            self.log(f"分辨率检查错误: {str(e)}")
        
        # 获取超分算法
        algorithm = self.sr_algorithm_var.get()
        
        # 附加线程限制以避免内存溢出
        threads_param = ["-threads", "4"]  # 限制使用的线程数
        
        # 计算新的宽度和高度 (在ffmpeg中使用过滤器进行计算)
        filter_complex = f"scale=iw*{scale}:ih*{scale}:flags={algorithm}"
        
        return threads_param + ["-filter_complex", filter_complex]

    def toggle_sr_options(self):
        """启用或禁用超分选项"""
        state = "readonly" if self.sr_enabled_var.get() else "disabled"
        self.sr_scale_combo.config(state=state)
        self.sr_algorithm_combo.config(state=state)
        
        # 更新预览
        self.update_preview()

    def fix_iphone_video(self, input_file, output_file):
        """修复iPhone绿屏视频并转码到指定格式，可选超分辨率处理"""
        if not self.ffmpeg_path:
            self.log("错误: 未找到FFmpeg，无法进行转码")
            return False
        
        try:
            # 获取质量设置的参数
            quality_params = self.get_ffmpeg_params()
            
            # 获取超分辨率参数(如果启用)
            sr_params = self.get_sr_params() if self.sr_enabled_var.get() else []
            
            # 指定内存使用限制
            memory_params = []
            if self.sr_enabled_var.get():
                # 当使用超分辨率时，设置较低的缓冲大小，避免内存溢出
                memory_params = [
                    "-max_muxing_queue_size", "1024",  # 减少多路复用队列大小
                ]
            
            # 构建FFmpeg命令
            cmd = [
                self.ffmpeg_path,
                "-i", input_file,
                "-pix_fmt", "yuv420p",  # 修复绿屏问题
            ]
            
            # 添加内存参数(如果需要)
            cmd.extend(memory_params)
            
            # 添加超分辨率参数(如果有)
            if sr_params:
                cmd.extend(sr_params)
            
            # 添加质量参数和输出文件
            cmd.extend(quality_params)
            cmd.extend([
                "-y",  # 自动覆盖输出文件
                output_file
            ])
            
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
                if self.sr_enabled_var.get():
                    self.log(f"应用了{self.sr_scale_var.get()}超分辨率，算法: {self.sr_algorithm_var.get()}")
                return True
            elif return_code == 3221225477 and self.sr_enabled_var.get():
                # 这是Windows中的内存访问错误（0xC0000005）
                self.log(f"转码失败: 可能是因为内存不足导致FFmpeg崩溃")
                self.log(f"建议: 请尝试使用较低的超分辨率倍率（1.5x或2x）")
                return False
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
        
        # 禁用所有按钮，防止重复点击 - 递归查找所有按钮
        def disable_buttons(parent):
            for widget in parent.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.config(state='disabled')
                # 递归检查子框架
                if widget.winfo_children():
                    disable_buttons(widget)
        
        disable_buttons(self.root)
        
        # 创建输出目录（如果不存在）
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except Exception as e:
                messagebox.showerror("错误", f"创建输出目录失败: {str(e)}")
                
                # 重新启用所有按钮
                def enable_buttons(parent):
                    for widget in parent.winfo_children():
                        if isinstance(widget, tk.Button):
                            widget.config(state='normal')
                        # 递归检查子框架
                        if widget.winfo_children():
                            enable_buttons(widget)
                
                enable_buttons(self.root)
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
                self.progress_percent.set(f"{int(progress_percent)}%")
                self.status_var.set(f"正在处理 {i+1}/{total_files}: {os.path.basename(input_file)}")
                
                # 确定输出文件名
                filename = os.path.basename(input_file)
                name, _ = os.path.splitext(filename)
                output_format = self.format_var.get()
                
                # 如果启用了超分，在文件名中添加标记
                if self.sr_enabled_var.get():
                    name = f"{name}_SR{self.sr_scale_var.get()}"
                
                output_file = os.path.join(self.output_dir, f"{name}_fixed.{output_format}")
                
                # 执行转码
                self.log(f"开始处理: {filename} -> {os.path.basename(output_file)}")
                success = self.fix_iphone_video(input_file, output_file)
                
                if success:
                    successful_count += 1
            
            # 完成转码
            self.progress_var.set(100)
            self.progress_percent.set("100%")
            self.status_var.set(f"转码完成: {successful_count}/{total_files} 个文件成功转码")
            messagebox.showinfo("完成", f"转码完成\n成功: {successful_count}/{total_files}")
            
        except Exception as e:
            self.log(f"转码过程中发生错误: {str(e)}")
            messagebox.showerror("错误", f"转码过程中发生错误: {str(e)}")
        
        finally:
            # 重新启用所有按钮
            def enable_buttons(parent):
                for widget in parent.winfo_children():
                    if isinstance(widget, tk.Button):
                        widget.config(state='normal')
                    # 递归检查子框架
                    if widget.winfo_children():
                        enable_buttons(widget)
            
            enable_buttons(self.root)

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