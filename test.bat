@echo off
chcp 65001
echo 测试打包后的程序...

rem 检查可执行文件是否存在
if not exist "dist\视频批量转码工具.exe" (
    echo 错误：未找到打包后的可执行文件！
    echo 请先运行 build.bat 打包程序。
    goto :end
)

rem 检查ffmpeg
if not exist "dist\ffmpeg.exe" (
    echo 正在为测试环境下载ffmpeg...
    cd dist
    call download_ffmpeg.bat
    cd ..
)

echo 所有准备工作已完成，现在可以测试程序：

echo 1. 启动程序并确认界面正常显示
echo 2. 测试文件拖放功能
echo 3. 测试点击添加文件功能
echo 4. 测试转码功能

echo 开始运行程序...
start "" "dist\视频批量转码工具.exe"

:end
pause 