@echo off
setlocal enabledelayedexpansion
title Word2PPT-Assistant 一键打包
chcp 65001 >nul

echo =========================================================
echo [INFO] 开始一键打包流程 (Word2PPT-Assistant)
echo =========================================================
echo.

set ROOT=%~dp0
cd /d "%ROOT%"

echo [INFO] 配置 Python 解释器...
rem 可在此修改为您的虚拟环境 Python 路径
set "PYTHON_EXE=C:\Users\chenc\anaconda3\envs\Chen\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

%PYTHON_EXE% --version >nul 2>&1 || (
    echo [ERROR] 未检测到可用的 Python，请检查虚拟环境路径或系统 PATH。
    goto :end_fail
)

echo [INFO] 升级 pip 并安装/升级 PyInstaller...
%PYTHON_EXE% -m pip install -U pip pyinstaller || goto :end_fail

echo [INFO] 执行构建脚本 (build_release.py)...
%PYTHON_EXE% build_release.py --yes
if errorlevel 1 (
    echo [ERROR] 构建脚本执行失败。
    goto :end_fail
)

echo [INFO] 验证构建产物...
set EXE_PATH=dist\Word2PPT-Assistant\Word2PPT-Assistant.exe
if exist "%EXE_PATH%" (
    echo [SUCCESS] 构建成功，已生成: %EXE_PATH%
) else (
    echo [ERROR] 未发现可执行文件: %EXE_PATH%
    goto :end_fail
)

echo.
echo [INFO] 您可以直接运行以下程序进行验证:
echo        %EXE_PATH%
echo.
echo [SUCCESS] 一键打包流程完成！
goto :end_ok

:end_fail
echo.
echo [ERROR] 一键打包流程失败，请检查以上日志信息。
exit /b 1

:end_ok
exit /b 0

