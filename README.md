# 视频批量转码工具

这是一个用于修复和转码视频文件的图形界面工具，特别适合修复iPhone录制的显示为绿色的损坏MP4文件。

## 功能特点

- 批量处理多个视频文件
- 支持拖放操作（或使用文件选择对话框）
- 可选择输出格式（MP4、MOV、AVI、MKV）
- 可调整输出视频质量（低、中、高）
- **视频超分辨率**功能，可提高视频清晰度
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
4. 可选：启用超分辨率功能并选择超分倍率和算法
5. 可选：修改输出目录
6. 点击"开始转码"按钮开始处理

### 超分辨率功能

超分辨率功能可以提高视频的分辨率和清晰度：

1. 勾选"启用超分辨率"复选框启用该功能
2. 选择超分倍率：
   - 1.5x - 将视频分辨率提高50%
   - 2x - 将视频分辨率提高一倍（推荐）
   - 3x - 将视频分辨率提高三倍
   - 4x - 将视频分辨率提高四倍
3. 选择超分算法：
   - lanczos - 高质量算法，锐化效果好（推荐）
   - bicubic - 平滑算法，适合一般用途
   - bilinear - 线性算法，速度较快
   - neighbor - 最邻近算法，速度最快但质量最低

注意：启用超分辨率功能会显著增加处理时间和输出文件大小。

## 故障排除

- 如果程序无法找到 FFmpeg，请确保 FFmpeg 已正确安装并添加到系统 PATH 变量中，或将 ffmpeg.exe 放在程序同目录下。
- 对于某些特别损坏的视频文件，可能需要尝试不同的转码参数。
- 如果拖放功能不工作，请确保已安装tkinterdnd2库。
- 如果超分辨率处理失败，可能是因为视频分辨率过高或FFmpeg版本过低，请尝试降低超分倍率。

## 技术说明

本程序使用 Python 的 Tkinter 库创建图形界面，使用 FFmpeg 进行视频转码。对于 iPhone 录制的绿色损坏视频，主要通过设置 `-pix_fmt yuv420p` 参数进行修复。

超分辨率功能使用FFmpeg的scale滤镜实现，通过调整视频帧的大小并使用高级插值算法来提高清晰度。

## 许可证

本项目采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。 