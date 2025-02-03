@echo off
setlocal enabledelayedexpansion



:: 配置基础参数
set BLOG_DIR=%~dp0
set PYTHON=python
set GIT=git
set HTTP_SERVER=http-server
set GITHUB_REPO=https://github.com/uukuu/uukuu.github.io.git

:: 初始化操作标志
set DEPLOY=0
set SERVER=0
set GENERATE=0

:: 解析命令行参数
:PARSE_ARGS
if "%~1"=="" goto END_ARGS
if /i "%~1"=="-d" set DEPLOY=1
if /i "%~1"=="-s" set SERVER=1
if /i "%~1"=="-g" set GENERATE=1
shift
goto PARSE_ARGS
:END_ARGS

:: 参数有效性检查
if %DEPLOY% equ 0 if %SERVER% equ 0 if %GENERATE% equ 0 (
    echo please specify the operation parameter:
    echo   -g generate blog content
    echo   -d deploy to GitHub
    echo   -s start local server
    pause
    exit /b 1
)

:: 生成博客内容
if %GENERATE% equ 1 (
    echo generating blog content...
    %PYTHON% "%BLOG_DIR%blog-gen.py"
    if errorlevel 1 (
        echo blog generation failed!
        pause
        exit /b 1
    )
    echo blog content generated successfully!
)

:: 部署到 GitHub 的流程
if %DEPLOY% equ 1 (
    :: 依赖检查
    %GIT% --version >nul 2>&1 || (
        echo Git is not installed or not added to the PATH environment variable
        pause
        exit /b 1
    )

    :: 执行部署操作
    pushd "%BLOG_DIR%public"
    echo  pushing to GitHub...
    %GIT% add . 
    %GIT% commit -m "auto update by blog.bat: %date% %time%"
    %GIT% push -f origin master
    popd
    echo success to push to GitHub!
)

:: 启动本地服务器的流程
if %SERVER% equ 1 (
    :: 依赖检查
    %HTTP_SERVER% --version >nul 2>&1 || (
        echo installing http-server...
        npm install -g http-server
        if errorlevel 1 (
            echo installation failed, please execute npm install -g http-server manually
            pause
            exit /b 1
        )
    )

    :: 启动服务器
    pushd "%BLOG_DIR%local"
    start "" %HTTP_SERVER% -p 8080 -o
    popd
    echo local server is running: http://localhost:8080
)

:: 完成提示
echo operation completed