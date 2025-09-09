#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows服务包装器
将以太坊私钥生成和余额检查工具包装为Windows服务
"""

import os
import sys
import time
import threading
import servicemanager
import win32event
import win32service
import win32serviceutil
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from eth_balance_hunter import EthBalanceHunter


class EthHunterService(win32serviceutil.ServiceFramework):
    """
    以太坊私钥猎手Windows服务类
    """
    
    # 服务名称
    _svc_name_ = "EthBalanceHunter"
    # 服务显示名称
    _svc_display_name_ = "Ethereum Balance Hunter Service"
    # 服务描述
    _svc_description_ = "以太坊私钥生成和余额检查服务，在后台持续运行寻找有余额的地址"
    # 服务启动类型（自动启动）
    _svc_start_type_ = win32service.SERVICE_AUTO_START
    
    def __init__(self, args):
        """
        初始化服务
        """
        win32serviceutil.ServiceFramework.__init__(self, args)
        # 创建停止事件
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        # 服务运行标志
        self.is_running = False
        # 工作线程
        self.worker_thread = None
        # 猎手实例
        self.hunter = None
        
        # 设置工作目录
        os.chdir(current_dir)
        
        # 记录服务启动
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
    
    def SvcStop(self):
        """
        停止服务
        """
        # 报告服务正在停止
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        # 设置停止标志
        self.is_running = False
        
        # 触发停止事件
        win32event.SetEvent(self.hWaitStop)
        
        # 记录服务停止
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, '')
        )
    
    def SvcDoRun(self):
        """
        运行服务主逻辑
        """
        try:
            # 记录服务开始运行
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '服务开始运行')
            )
            
            # 设置运行标志
            self.is_running = True
            
            # 启动工作线程
            self.worker_thread = threading.Thread(target=self._run_hunter, daemon=True)
            self.worker_thread.start()
            
            # 等待停止信号
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
            # 等待工作线程结束
            if self.worker_thread and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=10)
            
        except Exception as e:
            # 记录错误
            servicemanager.LogErrorMsg(f"服务运行出错: {str(e)}")
            raise
    
    def _run_hunter(self):
        """
        运行猎手程序的工作线程
        """
        try:
            # 创建猎手实例
            config_file = os.path.join(current_dir, 'config.json')
            self.hunter = EthBalanceHunter(config_file)
            
            # 记录开始猎取
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                0,
                f"开始猎取以太坊地址，RPC节点: {self.hunter.current_rpc}"
            )
            
            # 开始猎取（修改为支持服务模式）
            self._hunt_with_service_control()
            
        except Exception as e:
            # 记录错误
            servicemanager.LogErrorMsg(f"猎手程序运行出错: {str(e)}")
            # 停止服务
            self.SvcStop()
    
    def _hunt_with_service_control(self):
        """
        带服务控制的猎取逻辑
        """
        # 从配置获取设置
        hunting_config = self.hunter.config.get('hunting_settings', {})
        stats_interval = hunting_config.get('stats_interval', 1000)
        stop_on_first = hunting_config.get('stop_on_first_find', False)
        request_delay = hunting_config.get('request_delay', 0.05)
        max_retries = hunting_config.get('max_retries', 3)
        
        self.hunter.logger.info("服务模式：开始猎取有余额的以太坊地址...")
        self.hunter.logger.info(f"RPC节点: {self.hunter.current_rpc}")
        self.hunter.logger.info(f"统计间隔: {stats_interval} 地址")
        
        try:
            while self.is_running:
                # 生成私钥
                private_key = self.hunter.generate_private_key()
                
                # 生成地址和公钥
                address, public_key = self.hunter.private_key_to_address(private_key)
                if not address:
                    continue
                
                # 检查服务是否应该停止
                if not self.is_running:
                    break
                
                # 查询余额（添加基础延迟避免速率限制）
                time.sleep(request_delay)
                balance = self.hunter.get_balance(address, max_retries=max_retries)
                if balance is None:
                    continue
                
                self.hunter.total_checked += 1
                
                # 如果有余额，记录成功
                if balance > 0:
                    self.hunter.log_success(private_key, public_key, address, balance)
                    
                    # 记录到Windows事件日志
                    servicemanager.LogMsg(
                        servicemanager.EVENTLOG_INFORMATION_TYPE,
                        0,
                        f"发现有余额地址: {address}, 余额: {balance} ETH"
                    )
                    
                    # 根据配置决定是否停止
                    if stop_on_first:
                        self.hunter.logger.info("根据配置，找到第一个有余额地址后停止")
                        break
                
                # 定期打印统计信息
                if self.hunter.total_checked % stats_interval == 0:
                    self.hunter.print_stats()
                
                # 检查服务是否应该停止
                if not self.is_running:
                    break
                    
        except KeyboardInterrupt:
            self.hunter.logger.info("服务收到停止信号")
        except Exception as e:
            self.hunter.logger.error(f"服务运行出错: {e}")
            servicemanager.LogErrorMsg(f"猎取过程出错: {str(e)}")
        finally:
            if self.hunter:
                self.hunter.print_stats()
                self.hunter.logger.info("服务停止")


def main():
    """
    主函数 - 处理服务安装、卸载和运行
    """
    if len(sys.argv) == 1:
        # 没有参数时，尝试启动服务
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(EthHunterService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # 有参数时，处理服务管理命令
        win32serviceutil.HandleCommandLine(EthHunterService)


if __name__ == '__main__':
    main()