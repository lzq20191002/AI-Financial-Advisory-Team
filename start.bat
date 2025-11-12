@echo off

rem 金融市场分析系统启动脚本
rem 适用于Windows环境

setlocal enabledelayedexpansion

rem 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未安装Python或Python未添加到系统路径
    echo 请先安装Python 3.6或更高版本
    pause
    exit /b 1
)

echo 正在初始化金融市场分析系统...
echo.

rem 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 创建虚拟环境中...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
)

rem 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate

rem 升级pip
echo 升级pip...
pip install --upgrade pip

rem 安装依赖包
echo 安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 安装依赖包失败
    pause
    exit /b 1
)

rem 检查.env文件是否存在
if not exist ".env" (
    echo 警告: .env文件不存在，将使用.env.example作为模板
    if exist ".env.example" (
        copy .env.example .env
        echo 已创建.env文件，请根据需要修改配置
    ) else (
        echo 错误: .env.example文件也不存在
        pause
        exit /b 1
    )
)

rem 创建必要的目录
if not exist "reports" mkdir reports
if not exist "static\charts" mkdir static\charts
if not exist "user_data" mkdir user_data

echo.
echo 初始化完成，启动应用程序...
echo.

rem 启动应用程序
set FLASK_APP=app.py
set FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000

rem 等待用户输入
pause