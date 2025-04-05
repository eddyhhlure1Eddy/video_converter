@echo off
echo 正在下载FFmpeg...
powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg-temp.zip'"

echo 正在解压FFmpeg...
powershell -Command "Expand-Archive -Path 'ffmpeg-temp.zip' -DestinationPath 'ffmpeg-temp' -Force"

echo 正在提取ffmpeg.exe...
powershell -Command "Get-ChildItem -Path 'ffmpeg-temp' -Recurse -Filter 'ffmpeg.exe' | Copy-Item -Destination '.'"

echo 清理临时文件...
powershell -Command "Remove-Item -Path 'ffmpeg-temp' -Recurse -Force; Remove-Item -Path 'ffmpeg-temp.zip' -Force"

echo 完成！
echo FFmpeg已成功下载并安装到当前目录。
pause 