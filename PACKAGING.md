# 封装说明文档

本文档说明如何将视频批量转码工具封装为可执行程序和安装包。

## 前置要求

1. Python 3.6+ 环境
2. 以下工具:
   - PyInstaller (打包为可执行文件)
   - Inno Setup (可选，创建安装程序)

## 封装脚本说明

项目包含以下几个封装相关的脚本：

### 1. build.bat

基本的PyInstaller打包脚本，它会：
- 创建Python虚拟环境(如果不存在)
- 安装必要依赖
- 使用PyInstaller将程序打包为单个可执行文件
- 在dist目录下创建输出文件夹和复制必要的辅助文件

使用方法：直接运行 `build.bat`

### 2. video_converter.spec

PyInstaller的规范文件，定义了打包过程的详细配置：
- 指定要包含的数据文件
- 设置隐式导入的模块
- 配置生成的可执行文件属性

### 3. package.bat

完整打包流程脚本，它会：
- 运行PyInstaller打包
- 使用Inno Setup创建安装程序(如果已安装)

使用方法：运行 `package.bat`，按提示操作

### 4. installer.iss

Inno Setup脚本文件，用于创建Windows安装程序：
- 配置安装程序界面和选项
- 指定要包含的文件和快捷方式
- 设置安装后操作

使用方法：需要先安装Inno Setup，然后通过 `package.bat` 调用或直接运行 `iscc installer.iss`

### 5. test.bat

测试打包后程序的脚本，它会：
- 检查可执行文件是否存在
- 确保ffmpeg可用
- 启动程序进行测试

使用方法：运行 `test.bat`

## 常见问题

1. **中文路径问题**：避免在包含中文字符的路径下进行打包操作
2. **依赖缺失**：如果运行时出现模块缺失错误，编辑spec文件添加到 `hiddenimports` 列表中
3. **ffmpeg找不到**：确保 `download_ffmpeg.bat` 已经成功下载并放置ffmpeg到正确位置

## 发布版本

打包完成后，可以发布以下文件：

1. 单文件版本：dist目录下的可执行文件和download_ffmpeg.bat
2. 安装包版本：installer目录下的安装程序

## 更新版本

修改版本号的位置：
- `installer.iss` 文件中的 `#define MyAppVersion` 
- 更新版本后需要重新运行打包脚本 