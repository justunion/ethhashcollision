#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
以太坊私钥猎手服务安装脚本
用于安装、卸载和管理Windows服务
"""

import os
import sys
import subprocess
from pathlib import Path


def check_admin():
    """
    检查是否以管理员权限运行
    """
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """
    以管理员权限重新运行脚本
    """
    if check_admin():
        return True
    else:
        print("需要管理员权限来安装/卸载服务")
        print("正在请求管理员权限...")
        try:
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            return False
        except:
            print("无法获取管理员权限")
            return False


def install_dependencies():
    """
    安装依赖包
    """
    print("正在安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def install_service():
    """
    安装Windows服务
    """
    print("正在安装以太坊私钥猎手服务...")
    
    # 获取当前脚本目录
    current_dir = Path(__file__).parent.absolute()
    service_script = current_dir / "eth_service.py"
    
    if not service_script.exists():
        print(f"错误: 找不到服务脚本 {service_script}")
        return False
    
    try:
        # 安装服务
        cmd = [sys.executable, str(service_script), "install"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(current_dir))
        
        if result.returncode == 0:
            print("服务安装成功!")
            print("服务名称: EthBalanceHunter")
            print("服务显示名称: Ethereum Balance Hunter Service")
            
            # 尝试启动服务
            print("\n正在启动服务...")
            start_cmd = [sys.executable, str(service_script), "start"]
            start_result = subprocess.run(start_cmd, capture_output=True, text=True, cwd=str(current_dir))
            
            if start_result.returncode == 0:    
                print("服务启动成功!")
                print("\n服务管理命令:")
                print(f"  启动服务: python {service_script} start")
                print(f"  停止服务: python {service_script} stop")
                print(f"  重启服务: python {service_script} restart")
                print(f"  卸载服务: python {service_script} remove")
            else:
                print(f"服务启动失败: {start_result.stderr}")
                print("请检查配置文件和日志")
            
            return True
        else:
            print(f"服务安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"安装服务时出错: {e}")
        return False


def uninstall_service():
    """
    卸载Windows服务
    """
    print("正在卸载以太坊私钥猎手服务...")
    
    current_dir = Path(__file__).parent.absolute()
    service_script = current_dir / "eth_service.py"
    
    if not service_script.exists():
        print(f"错误: 找不到服务脚本 {service_script}")
        return False
    
    try:
        # 先停止服务
        print("正在停止服务...")
        stop_cmd = [sys.executable, str(service_script), "stop"]
        subprocess.run(stop_cmd, capture_output=True, text=True, cwd=str(current_dir))
        
        # 卸载服务
        cmd = [sys.executable, str(service_script), "remove"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(current_dir))
        
        if result.returncode == 0:
            print("服务卸载成功!")
            return True
        else:
            print(f"服务卸载失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"卸载服务时出错: {e}")
        return False


def check_service_status():
    """
    检查服务状态
    """
    try:
        import win32service
        import win32serviceutil
        
        service_name = "EthBalanceHunter"
        
        try:
            status = win32serviceutil.QueryServiceStatus(service_name)
            state = status[1]
            
            state_map = {
                win32service.SERVICE_STOPPED: "已停止",
                win32service.SERVICE_START_PENDING: "正在启动",
                win32service.SERVICE_STOP_PENDING: "正在停止",
                win32service.SERVICE_RUNNING: "正在运行",
                win32service.SERVICE_CONTINUE_PENDING: "正在继续",
                win32service.SERVICE_PAUSE_PENDING: "正在暂停",
                win32service.SERVICE_PAUSED: "已暂停"
            }
            
            print(f"服务状态: {state_map.get(state, f'未知状态({state})')}")
            return True
            
        except Exception:
            print("服务未安装或无法访问")
            return False
            
    except ImportError:
        print("无法导入win32service模块，请先安装pywin32")
        return False


def main():
    """
    主函数
    """
    print("="*60)
    print("以太坊私钥猎手服务安装工具")
    print("Ethereum Balance Hunter Service Installer")
    print("="*60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install":
            if not run_as_admin():
                return
            
            # 安装依赖
            if not install_dependencies():
                print("依赖安装失败，无法继续")
                return
            
            # 安装服务
            install_service()
            
        elif command == "uninstall" or command == "remove":
            if not run_as_admin():
                return
            uninstall_service()
            
        elif command == "status":
            check_service_status()
            
        else:
            print(f"未知命令: {command}")
            print("可用命令: install, uninstall, status")
    else:
        # 交互式菜单
        while True:
            print("\n请选择操作:")
            print("1. 安装服务")
            print("2. 卸载服务")
            print("3. 检查服务状态")
            print("4. 退出")
            
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == "1":
                if not run_as_admin():
                    break
                
                # 安装依赖
                if not install_dependencies():
                    print("依赖安装失败，无法继续")
                    continue
                
                # 安装服务
                install_service()
                
            elif choice == "2":
                if not run_as_admin():
                    break
                uninstall_service()
                
            elif choice == "3":
                check_service_status()
                
            elif choice == "4":
                print("退出")
                break
                
            else:
                print("无效选择，请重试")


if __name__ == "__main__":
    main()