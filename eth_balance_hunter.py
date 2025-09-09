#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
以太坊私钥生成和余额检查工具
随机生成私钥，检查对应地址的ETH余额
如果发现有余额的地址，记录到成功日志文件中
"""

import os
import sys
import time
import json
import logging
import secrets
from datetime import datetime
from logging.handlers import RotatingFileHandler

from web3 import Web3
from eth_account import Account
from eth_keys import keys


class EthBalanceHunter:
    def __init__(self, config_file="config.json"):
        """
        初始化以太坊余额猎手
        
        Args:
            config_file (str): 配置文件路径
        """
        # 加载配置
        self.config = self._load_config(config_file)
        self.rpc_urls = self.config.get('rpc_urls', ["https://eth-mainnet.public.blastapi.io"])
        self.log_dir = self.config.get('log_settings', {}).get('log_dir', 'logs')
        self.max_log_size = self.config.get('log_settings', {}).get('max_log_size_mb', 10) * 1024 * 1024
        self.backup_count = self.config.get('log_settings', {}).get('backup_count', 5)
        
        self.w3 = None
        self.logger = None
        self.success_logger = None
        self.total_checked = 0
        self.start_time = time.time()
        
        # 创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 初始化日志系统
        self._setup_logging()
        
        # 初始化Web3连接
        self._setup_web3()
    
    def _load_config(self, config_file):
        """
        加载配置文件
        
        Args:
            config_file (str): 配置文件路径
            
        Returns:
            dict: 配置字典
        """
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"配置文件 {config_file} 不存在，使用默认配置")
                return {}
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            return {}
    
    def _setup_logging(self):
        """
        设置日志系统 - 支持按日期轮转
        """
        from logging.handlers import TimedRotatingFileHandler
        from datetime import datetime
        
        # 从配置获取日志设置
        log_level = self.config.get('logging_settings', {}).get('log_level', 'INFO')
        main_retention_days = self.config.get('logging_settings', {}).get('main_log_retention_days', 30)
        success_retention_days = self.config.get('logging_settings', {}).get('success_log_retention_days', 365)
        
        # 主运行日志
        self.logger = logging.getLogger('eth_hunter')
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # 清除现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 创建按日期轮转的文件处理器
        log_file = os.path.join(self.log_dir, f'eth_hunter_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='midnight',
            interval=1,
            backupCount=main_retention_days,
            encoding='utf-8'
        )
        file_handler.suffix = '%Y%m%d'
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 成功记录日志 - 按日期轮转
        self.success_logger = logging.getLogger('success_records')
        self.success_logger.setLevel(logging.INFO)
        
        # 清除现有的处理器
        for handler in self.success_logger.handlers[:]:
            self.success_logger.removeHandler(handler)
        
        success_file = os.path.join(self.log_dir, f'success_records_{datetime.now().strftime("%Y%m%d")}.log')
        success_handler = TimedRotatingFileHandler(
            filename=success_file,
            when='midnight',
            interval=1,
            backupCount=success_retention_days,
            encoding='utf-8'
        )
        success_handler.suffix = '%Y%m%d'
        success_formatter = logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        success_handler.setFormatter(success_formatter)
        self.success_logger.addHandler(success_handler)
        
        # 防止日志重复
        self.success_logger.propagate = False
    
    def _setup_web3(self):
        """
        设置Web3连接，尝试多个RPC节点
        """
        for rpc_url in self.rpc_urls:
            try:
                self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 30}))
                if self.w3.is_connected():
                    self.logger.info(f"成功连接到以太坊节点: {rpc_url}")
                    # 获取当前区块号
                    latest_block = self.w3.eth.block_number
                    self.logger.info(f"当前区块高度: {latest_block}")
                    self.current_rpc = rpc_url
                    return
                else:
                    self.logger.warning(f"无法连接到节点: {rpc_url}")
            except Exception as e:
                self.logger.warning(f"连接节点失败 {rpc_url}: {e}")
        
        self.logger.error("所有RPC节点连接失败")
        sys.exit(1)
    
    def generate_private_key(self):
        """
        生成随机私钥
        
        Returns:
            str: 64位十六进制私钥字符串
        """
        # 生成32字节的随机数作为私钥
        private_key_bytes = secrets.token_bytes(32)
        private_key_hex = private_key_bytes.hex()
        return private_key_hex
    
    def private_key_to_address(self, private_key_hex):
        """
        从私钥生成以太坊地址
        
        Args:
            private_key_hex (str): 私钥十六进制字符串
            
        Returns:
            tuple: (address, public_key_hex)
        """
        try:
            # 使用eth_account生成账户
            account = Account.from_key(private_key_hex)
            address = account.address
            
            # 获取公钥
            private_key_obj = keys.PrivateKey(bytes.fromhex(private_key_hex))
            public_key = private_key_obj.public_key
            public_key_hex = public_key.to_hex()
            
            return address, public_key_hex
        except Exception as e:
            self.logger.error(f"从私钥生成地址失败: {e}")
            return None, None
    
    def get_balance(self, address, max_retries=3, delay=0.1):
        """
        获取地址的ETH余额，带重试机制
        
        Args:
            address (str): 以太坊地址
            max_retries (int): 最大重试次数
            delay (float): 请求间隔时间（秒）
            
        Returns:
            float: ETH余额，如果查询失败返回None
        """
        for attempt in range(max_retries):
            try:
                # 添加请求间隔，避免速率限制
                if attempt > 0:
                    time.sleep(delay * (2 ** attempt))  # 指数退避
                
                balance_wei = self.w3.eth.get_balance(address)
                balance_eth = self.w3.from_wei(balance_wei, 'ether')
                return float(balance_eth)
            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    if attempt < max_retries - 1:
                        self.logger.debug(f"遇到速率限制，等待重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(delay * (2 ** attempt))
                        continue
                    else:
                        self.logger.warning(f"查询余额失败，已达最大重试次数 {address}: 速率限制")
                        return None
                else:
                    self.logger.warning(f"查询余额失败 {address}: {e}")
                    return None
        return None
    
    def log_success(self, private_key, public_key, address, balance):
        """
        记录成功找到有余额的地址
        
        Args:
            private_key (str): 私钥
            public_key (str): 公钥
            address (str): 地址
            balance (float): 余额
        """
        success_data = {
            "timestamp": datetime.now().isoformat(),
            "private_key": private_key,
            "public_key": public_key,
            "address": address,
            "balance_eth": balance,
            "total_checked": self.total_checked
        }
        
        # 记录到成功日志文件（包含完整信息）
        self.success_logger.info(json.dumps(success_data, ensure_ascii=False, indent=2))
        
        # 同时在控制台显示
        self.logger.info("="*80)
        self.logger.info("🎉 发现有余额的地址！")
        self.logger.info(f"地址: {address}")
        self.logger.info(f"余额: {balance} ETH")
        self.logger.info(f"私钥: {private_key}")
        self.logger.info(f"公钥: {public_key}")
        self.logger.info(f"已检查地址数量: {self.total_checked}")
        self.logger.info("="*80)
        

    
    def hunt_service_mode(self):
        """
        服务模式的猎取方法 - 静默运行，只记录日志
        """
        # 从配置获取设置
        hunting_config = self.config.get('hunting_settings', {})
        stats_interval = hunting_config.get('stats_interval', 1000)
        stop_on_first = hunting_config.get('stop_on_first_find', False)
        request_delay = hunting_config.get('request_delay', 0.05)
        max_retries = hunting_config.get('max_retries', 3)
        
        self.logger.info("服务模式：开始猎取有余额的以太坊地址...")
        self.logger.info(f"RPC节点: {self.current_rpc}")
        self.logger.info(f"统计间隔: {stats_interval} 地址")
        
        try:
            while True:
                # 生成私钥
                private_key = self.generate_private_key()
                
                # 生成地址和公钥
                address, public_key = self.private_key_to_address(private_key)
                if not address:
                    continue
                
                # 查询余额（添加基础延迟避免速率限制）
                time.sleep(request_delay)
                balance = self.get_balance(address, max_retries=max_retries)
                if balance is None:
                    continue
                
                self.total_checked += 1
                
                # 记录每次检查的地址、私钥和公钥信息
                self.logger.debug(f"检查地址 #{self.total_checked}: {address} (私钥: {private_key} | 公钥: {public_key})")
                
                # 定期记录统计信息
                log_interval = self.config.get('logging_settings', {}).get('log_public_key_interval', 1000)
                if self.total_checked % log_interval == 0:
                    self.logger.info(f"已检查 {self.total_checked} 个地址")
                
                # 如果有余额，记录成功
                if balance > 0:
                    self.log_success(private_key, public_key, address, balance)
                    
                    # 根据配置决定是否停止
                    if stop_on_first:
                        self.logger.info("根据配置，找到第一个有余额地址后停止")
                        break
                
                # 定期打印统计信息到日志
                if self.total_checked % stats_interval == 0:
                    self.log_stats()
                    
        except Exception as e:
            self.logger.error(f"服务模式运行出错: {e}")
            raise
    
    def log_stats(self):
        """
        记录统计信息到日志
        """
        elapsed_time = time.time() - self.start_time
        rate = self.total_checked / elapsed_time if elapsed_time > 0 else 0
        
        stats_msg = f"统计信息 | 已检查地址: {self.total_checked:,} | " \
                   f"运行时间: {elapsed_time:.1f} 秒 | " \
                   f"检查速度: {rate:.2f} 地址/秒 | " \
                   f"当前RPC: {self.current_rpc}"
        
        self.logger.info(stats_msg)
    
    def print_stats(self):
        """
        打印统计信息
        """
        elapsed_time = time.time() - self.start_time
        rate = self.total_checked / elapsed_time if elapsed_time > 0 else 0
        
        self.logger.info(
            f"统计信息 - 已检查: {self.total_checked} | "
            f"运行时间: {elapsed_time:.1f}秒 | "
            f"检查速度: {rate:.2f} 地址/秒"
        )
    
    def hunt(self, max_attempts=None, stats_interval=None):
        """
        开始猎取有余额的地址
        
        Args:
            max_attempts (int): 最大尝试次数，None表示无限制
            stats_interval (int): 统计信息打印间隔
        """
        # 从配置文件获取设置
        hunting_config = self.config.get('hunting_settings', {})
        if max_attempts is None:
            max_attempts = hunting_config.get('max_attempts')
        if stats_interval is None:
            stats_interval = hunting_config.get('stats_interval', 1000)
        stop_on_first = hunting_config.get('stop_on_first_find', False)
        request_delay = hunting_config.get('request_delay', 0.05)
        max_retries = hunting_config.get('max_retries', 3)
        
        self.logger.info("开始猎取有余额的以太坊地址...")
        self.logger.info(f"RPC节点: {self.current_rpc}")
        self.logger.info(f"统计间隔: {stats_interval} 地址")
        if max_attempts:
            self.logger.info(f"最大尝试次数: {max_attempts}")
        
        try:
            while max_attempts is None or self.total_checked < max_attempts:
                # 生成私钥
                private_key = self.generate_private_key()
                
                # 生成地址和公钥
                address, public_key = self.private_key_to_address(private_key)
                if not address:
                    continue
                
                # 查询余额（添加基础延迟避免速率限制）
                time.sleep(request_delay)
                balance = self.get_balance(address, max_retries=max_retries)
                if balance is None:
                    continue
                
                self.total_checked += 1
                
                # 记录每次检查的地址、私钥和公钥信息
                self.logger.debug(f"检查地址 #{self.total_checked}: {address} (私钥: {private_key} | 公钥: {public_key})")
                
                # 定期记录统计信息
                log_interval = self.config.get('logging_settings', {}).get('log_public_key_interval', 1000)
                if self.total_checked % log_interval == 0:
                    self.logger.info(f"已检查 {self.total_checked} 个地址")                
                
                # 如果有余额，记录成功
                if balance > 0:
                    self.log_success(private_key, public_key, address, balance)
                    # 根据配置决定是否在找到第一个有余额的地址后停止
                    if stop_on_first:
                        self.logger.info("根据配置，找到第一个有余额地址后停止")
                        break
                
                # 定期打印统计信息
                if self.total_checked % stats_interval == 0:
                    self.print_stats()
                
        except KeyboardInterrupt:
            self.logger.info("\n用户中断程序")
        except Exception as e:
            self.logger.error(f"程序运行出错: {e}")
        finally:
            self.print_stats()
            self.logger.info("程序结束")


def main():
    """
    主函数 - 支持控制台模式和服务模式
    """
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='以太坊私钥生成和余额检查工具')
    parser.add_argument('--service', action='store_true', help='以服务模式运行（无输出）')
    parser.add_argument('--config', default='config.json', help='配置文件路径')
    args = parser.parse_args()
    
    if not args.service:
        # 控制台模式 - 显示标题
        print("="*60)
        print("以太坊私钥生成和余额检查工具")
        print("Ethereum Private Key Generator and Balance Hunter")
        print("="*60)
    
    # 使用配置文件初始化
    hunter = EthBalanceHunter(args.config)
    
    try:
        if args.service:
            # 服务模式 - 静默运行
            hunter.hunt_service_mode()
        else:
            # 控制台模式 - 正常运行
            hunter.hunt()
    except KeyboardInterrupt:
        if not args.service:
            print("\n程序被用户中断")
        hunter.logger.info("程序被用户中断")
    except Exception as e:
        if not args.service:
            print(f"程序运行出错: {e}")
        hunter.logger.error(f"程序运行出错: {e}")
    finally:
        hunter.print_stats()


if __name__ == "__main__":
    main()