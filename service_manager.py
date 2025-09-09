#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
以太坊私钥猎手服务管理工具
提供服务的启动、停止、重启和状态查询功能
"""

import os
import sys
import time
import subprocess
from pathlib import Path


def run_service_command(command):
    """
    运行服务命令
    """
    current_dir = Path(__file__).parent.absolute()
    service_script = current_dir / "eth_service.py"
    
    if not service_script.exists():
        print(f"错误: 找不到服务脚本 {service_script}")
        return False
    
    try:
        cmd = [sys.executable, str(service_script), command]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(current_dir))
        
        if result.returncode == 0:
            print(f"命令 '{command}' 执行成功")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"命令 '{command}' 执行失败")
            if result.stderr:
                print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return False


def get_service_status():
    """
    获取服务状态
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
            
            status_text = state_map.get(state, f'未知状态({state})')
            print(f"服务状态: {status_text}")
            
            return state == win32service.SERVICE_RUNNING
            
        except Exception as e:
            print(f"服务未安装或无法访问: {e}")
            return False
            
    except ImportError:
        print("无法导入win32service模块，请先安装pywin32")
        return False


def start_service():
    """
    启动服务
    """
    print("正在启动以太坊私钥猎手服务...")
    
    if run_service_command("start"):
        # 等待服务启动
        print("等待服务启动...")
        time.sleep(3)
        
        # 检查状态
        if get_service_status():
            print("服务启动成功!")
            return True
        else:
            print("服务启动可能失败，请检查日志")
            return False
    else:
        return False


def stop_service():
    """
    停止服务
    """
    print("正在停止以太坊私钥猎手服务...")
    
    if run_service_command("stop"):
        # 等待服务停止
        print("等待服务停止...")
        time.sleep(3)
        
        # 检查状态
        get_service_status()
        print("服务停止完成")
        return True
    else:
        return False


def restart_service():
    """
    重启服务
    """
    print("正在重启以太坊私钥猎手服务...")
    
    # 先停止
    if stop_service():
        time.sleep(2)
        # 再启动
        return start_service()
    else:
        return False


def view_logs():
    """
    查看日志文件
    """
    current_dir = Path(__file__).parent.absolute()
    log_dir = current_dir / "logs"
    
    if not log_dir.exists():
        print("日志目录不存在")
        return
    
    log_files = {
        "1": ("主日志", log_dir / "eth_hunter.log"),
        "2": ("成功记录", log_dir / "success_records.log")
    }
    
    print("\n可用的日志文件:")
    for key, (name, path) in log_files.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"{key}. {name} ({path.name}) - {size} 字节")
    
    choice = input("\n请选择要查看的日志文件 (1-2): ").strip()
    
    if choice in log_files:
        name, log_file = log_files[choice]
        
        if not log_file.exists():
            print(f"{name}文件不存在")
            return
        
        try:
            lines = input("显示最后多少行? (默认50): ").strip()
            lines = int(lines) if lines else 50
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.readlines()
                
            if len(content) > lines:
                content = content[-lines:]
            
            print(f"\n=== {name} (最后{len(content)}行) ===")
            for line in content:
                print(line.rstrip())
            print("=" * 50)
            
        except Exception as e:
            print(f"读取日志文件失败: {e}")
    else:
        print("无效选择")


def show_service_info():
    """
    显示服务信息
    """
    print("\n=== 服务信息 ===")
    print("服务名称: EthBalanceHunter")
    print("显示名称: Ethereum Balance Hunter Service")
    print("描述: 以太坊私钥生成和余额检查服务")
    
    # 检查服务状态
    get_service_status()
    
    # 检查配置文件
    current_dir = Path(__file__).parent.absolute()
    config_file = current_dir / "config.json"
    
    if config_file.exists():
        print(f"配置文件: {config_file} (存在)")
    else:
        print(f"配置文件: {config_file} (不存在)")
    
    # 检查日志目录
    log_dir = current_dir / "logs"
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        print(f"日志目录: {log_dir} ({len(log_files)} 个日志文件)")
    else:
        print(f"日志目录: {log_dir} (不存在)")
    
    print("=" * 30)


def main():
    """
    主函数
    """
    print("="*60)
    print("以太坊私钥猎手服务管理工具")
    print("Ethereum Balance Hunter Service Manager")
    print("="*60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            start_service()
        elif command == "stop":
            stop_service()
        elif command == "restart":
            restart_service()
        elif command == "status":
            get_service_status()
        elif command == "info":
            show_service_info()
        elif command == "logs":
            view_logs()
        else:
            print(f"未知命令: {command}")
            print("可用命令: start, stop, restart, status, info, logs")
    else:
        # 交互式菜单
        while True:
            print("\n请选择操作:")
            print("1. 启动服务")
            print("2. 停止服务")
            print("3. 重启服务")
            print("4. 查看服务状态")
            print("5. 查看服务信息")
            print("6. 查看日志")
            print("7. 退出")
            
            choice = input("\n请输入选择 (1-7): ").strip()
            
            if choice == "1":
                start_service()
            elif choice == "2":
                stop_service()
            elif choice == "3":
                restart_service()
            elif choice == "4":
                get_service_status()
            elif choice == "5":
                show_service_info()
            elif choice == "6":
                view_logs()
            elif choice == "7":
                print("退出")
                break
            else:
                print("无效选择，请重试")


if __name__ == "__main__":
    main()