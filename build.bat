@echo off
chcp 65001
echo 正在打包视频转码工具...

rem 创建虚拟环境目录(如果不存在)
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    pip install pyinstaller
) else (
    call venv\Scripts\activate.bat
)

rem 清理之前的构建
echo 清理之前的构建...
if exist "build" rd /s /q build
if exist "dist" rd /s /q dist

rem 开始打包
echo 开始打包程序...
pyinstaller video_converter.spec

echo 复制辅助文件...
if not exist "dist\converted_videos" mkdir "dist\converted_videos"
copy download_ffmpeg.bat dist\

echo 打包完成！
echo 可执行文件位于 dist 目录下
pause