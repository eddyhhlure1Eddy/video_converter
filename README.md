# 视频批量转码工具

这是一个用于修复和转码视频文件的图形界面工具，特别适合修复iPhone录制的显示为绿色的损坏MP4文件。

## 功能特点

- 批量处理多个视频文件
- 支持拖放操作（或使用文件选择对话框）
- 可选择输出格式（MP4、MOV、AVI、MKV）
- 可调整输出视频质量（低、中、高）
- 自定义输出目录
- 实时显示转码进度和日志

## 安装说明

### 依赖项

1. Python 3.6 或更高版本
2. FFmpeg（必需）
3. tkinterdnd2（可选，用于增强拖放功能）

#### 安装 FFmpeg

本程序依赖于 FFmpeg 进行视频转码。您可以通过以下方式获取 FFmpeg：

**Windows 用户**：
- 运行包含的`download_ffmpeg.bat`脚本自动下载并安装ffmpeg到程序目录
- 或下载预编译的 FFmpeg：https://ffmpeg.org/download.html
- 或者，将 ffmpeg.exe 放在程序同目录下

**使用包管理器**：
- Windows (使用 Chocolatey)：`choco install ffmpeg`
- Windows (使用 Scoop)：`scoop install ffmpeg`

#### 安装 tkinterdnd2（增强拖放功能）

```
pip install tkinterdnd2
```

### 安装步骤

1. 克隆或下载此仓库
2. 安装必要的Python依赖：`pip install -r requirements.txt`
3. 运行`download_ffmpeg.bat`下载ffmpeg（仅Windows用户）
4. 启动程序：`python video_converter.py`

## 使用方法

1. 运行 `python video_converter.py`
2. 点击"添加文件"按钮选择要转码的视频文件，或拖放文件到界面中
3. 选择所需输出格式和质量设置
4. 可选：修改输出目录
5. 点击"开始转码"按钮开始处理

## 故障排除

- 如果程序无法找到 FFmpeg，请确保 FFmpeg 已正确安装并添加到系统 PATH 变量中，或将 ffmpeg.exe 放在程序同目录下。
- 对于某些特别损坏的视频文件，可能需要尝试不同的转码参数。
- 如果拖放功能不工作，请确保已安装tkinterdnd2库。

## 技术说明

本程序使用 Python 的 Tkinter 库创建图形界面，使用 FFmpeg 进行视频转码。对于 iPhone 录制的绿色损坏视频，主要通过设置 `-pix_fmt yuv420p` 参数进行修复。

## 许可证

本项目采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。 