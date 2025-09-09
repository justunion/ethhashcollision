@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 以太坊私钥猎手服务控制脚本
REM Ethereum Balance Hunter Service Control Script

echo ============================================================
echo 以太坊私钥猎手服务控制面板
echo Ethereum Balance Hunter Service Control Panel
echo ============================================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    echo Error: Python not found, please ensure Python is installed and added to PATH
    pause
    exit /b 1
)

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 检查必要文件
if not exist "service_manager.py" (
    echo 错误: 找不到service_manager.py文件
    echo Error: service_manager.py file not found
    pause
    exit /b 1
)

if not exist "install_service.py" (
    echo 错误: 找不到install_service.py文件
    echo Error: install_service.py file not found
    pause
    exit /b 1
)

:MENU
echo.
echo 请选择操作 / Please select an operation:
echo.
echo 1. 安装服务 / Install Service
echo 2. 卸载服务 / Uninstall Service
echo 3. 启动服务 / Start Service
echo 4. 停止服务 / Stop Service
echo 5. 重启服务 / Restart Service
echo 6. 查看服务状态 / Check Service Status
echo 7. 查看服务信息 / View Service Info
echo 8. 查看日志 / View Logs
echo 9. 退出 / Exit
echo.
set /p choice=请输入选择 (1-9) / Enter choice (1-9): 

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto UNINSTALL
if "%choice%"=="3" goto START
if "%choice%"=="4" goto STOP
if "%choice%"=="5" goto RESTART
if "%choice%"=="6" goto STATUS
if "%choice%"=="7" goto INFO
if "%choice%"=="8" goto LOGS
if "%choice%"=="9" goto EXIT

echo 无效选择，请重试 / Invalid choice, please try again
goto MENU

:INSTALL
echo.
echo 正在安装服务... / Installing service...
echo 注意：需要管理员权限 / Note: Administrator privileges required
echo.
python install_service.py install
echo.
echo 按任意键返回菜单... / Press any key to return to menu...
pause >nul
goto MENU

:UNINSTALL
echo.
echo 正在卸载服务... / Uninstalling service...
echo 注意：需要管理员权限 / Note: Administrator privileges required
echo.
python install_service.py uninstall
echo.
echo 按任意键返回菜单... / Press any key to return to menu...
pause >nul
goto MENU

:START
echo.
echo 正在启动服务... / Starting service...
echo.
python service_manager.py start
echo.
echo 按任意键返回菜单... / Press any key to return to menu...
pause >nul
goto MENU

:STOP
echo.
echo 正在停止服务... / Stopping service...
echo.
python service_manager.py stop
echo.
echo 按任意键返回菜单... / Press any key to return to menu...
pause >nul
goto MENU

:RESTART
echo.
echo 正在重启服务... / Restarting service...
echo.
python service_manager.py restart
echo.
echo 按任意键返回菜单... / Press any key to return to menu...
pause >nul
goto MENU

:STATUS
echo.
echo 查看服务状态... / Checking service status...
echo.
python service_manager.py status
echo.
echo 按任意键返回菜单... / Press any key to return to menu...
pause >nul
goto MENU

:INFO
echo.
echo 查看服务信息... / Viewing service info...
echo.
python service_manager.py info
echo.
echo 按任意键返回菜单... / Press any key to return to menu...
pause >nul
goto MENU

:LOGS
echo.
echo 查看日志... / Viewing logs...
echo.
python service_manager.py logs
echo.
echo 按任意键返回菜单... / Press any key to return to menu...
pause >nul
goto MENU

:EXIT
echo.
echo 退出 / Exiting...
exit /b 0
