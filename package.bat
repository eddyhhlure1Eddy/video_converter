@echo off
echo ======================================
echo   视频批量转码工具 - 完整打包流程
echo ======================================

rem 确认是否继续
set /p continue=确定要开始打包流程吗? (Y/N): 
if /i not "%continue%"=="Y" goto :end

rem 第一步：运行PyInstaller打包
echo.
echo [第1步/2] 使用PyInstaller打包程序...
call build.bat

rem 第二步：创建安装程序 (需要Inno Setup)
echo.
echo [第2步/2] 创建安装程序...

rem 检查Inno Setup是否安装
where iscc >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到Inno Setup编译器(ISCC)
    echo 请安装Inno Setup: https://jrsoftware.org/isdl.php
    echo 并确保其安装路径已添加到PATH环境变量中
    goto :end
)

rem 创建installer目录
if not exist "installer" mkdir "installer"

rem 编译安装程序
iscc installer.iss
if %errorlevel% neq 0 (
    echo 安装程序创建失败!
    goto :end
)

echo.
echo 打包和安装程序创建已完成!
echo 安装程序位于 installer 目录
echo.

:end
pause 