# 以太坊私钥生成和余额检查工具

这是一个用于随机生成以太坊私钥并检查对应地址余额的工具。当发现有余额的地址时，会将私钥、公钥和余额信息记录到成功日志文件中。

## 功能特性

- 🔐 随机生成32字节以太坊私钥
- 🏠 从私钥生成对应的公钥和地址
- 💰 查询地址的ETH余额
- 📝 完整的日志记录系统
- 🔄 日志文件自动轮转，防止文件过大
- 🎯 发现有余额地址时的特殊记录
- ⚙️ 支持多个RPC节点自动切换
- 📊 实时统计信息显示

## 安装依赖

1. 确保已安装Python 3.7+
2. 安装所需依赖包：

```bash
pip install -r requirements.txt
```

## 配置文件

程序使用 `config.json` 文件进行配置，主要包含以下设置：

### RPC节点配置
```json
{
  "rpc_urls": [
    "https://eth-mainnet.g.alchemy.com/v2/demo",
    "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
    "https://eth-mainnet.public.blastapi.io",
    "https://rpc.ankr.com/eth"
  ]
}
```

### 日志设置
```json
{
  "log_settings": {
    "log_dir": "logs",
    "max_log_size_mb": 10,
    "backup_count": 5
  }
}
```

### 猎取设置
```json
{
  "hunting_settings": {
    "stats_interval": 1000,
    "max_attempts": null,
    "stop_on_first_find": false
  }
}
```

## 使用方法

### 控制台模式

1. **基本运行**：
   ```bash
   python eth_balance_hunter.py
   ```

2. **指定配置文件**：
   ```bash
   python eth_balance_hunter.py --config custom_config.json
   ```

3. **服务模式运行**（静默，无控制台输出）：
   ```bash
   python eth_balance_hunter.py --service
   ```

### Windows服务模式

#### 快速开始（推荐）

使用批处理脚本进行服务管理：
```bash
service_control.bat
```

#### 手动安装和管理

1. **安装服务**：
   ```bash
   # 需要管理员权限
   python install_service.py install
   ```

2. **服务管理**：
   ```bash
   # 启动服务
   python service_manager.py start
   
   # 停止服务
   python service_manager.py stop
   
   # 重启服务
   python service_manager.py restart
   
   # 查看状态
   python service_manager.py status
   
   # 查看服务信息
   python service_manager.py info
   
   # 查看日志
   python service_manager.py logs
   ```

3. **卸载服务**：
   ```bash
   # 需要管理员权限
   python install_service.py uninstall
   ```

#### 服务特性

- **后台运行**：服务安装后会在Windows后台持续运行
- **自动启动**：系统重启后服务会自动启动
- **日志记录**：所有活动都会记录到日志文件
- **事件日志**：重要事件会记录到Windows事件查看器
- **优雅停止**：服务停止时会安全保存所有数据

### 程序输出

程序运行时会显示：
- 连接的RPC节点信息
- 当前区块高度
- 实时统计信息（每1000次检查显示一次）
- 发现有余额地址时的详细信息

### 示例输出

```
以太坊私钥生成和余额检查工具
==================================================
2024-01-15 10:30:00 - INFO - 成功连接到以太坊节点: https://eth-mainnet.g.alchemy.com/v2/demo
2024-01-15 10:30:01 - INFO - 当前区块高度: 18925000
2024-01-15 10:30:01 - INFO - 开始猎取有余额的以太坊地址...
2024-01-15 10:30:01 - INFO - RPC节点: https://eth-mainnet.g.alchemy.com/v2/demo
2024-01-15 10:30:01 - INFO - 统计间隔: 1000 地址

2024-01-15 10:31:00 - INFO - 统计信息 - 已检查: 1000 | 运行时间: 59.2秒 | 检查速度: 16.89 地址/秒
2024-01-15 10:32:00 - INFO - 统计信息 - 已检查: 2000 | 运行时间: 118.5秒 | 检查速度: 16.88 地址/秒

================================================================================
🎉 发现有余额的地址！
地址: 0x1234567890123456789012345678901234567890
余额: 0.5 ETH
私钥: abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
公钥: 04abcdef...
已检查地址数量: 2500
================================================================================
```

## 日志文件

程序会在 `logs/` 目录下生成两种日志文件：

### 1. 运行日志 (`eth_hunter.log`)
- 记录程序运行过程中的所有信息
- 包括连接状态、统计信息、错误信息等
- 支持自动轮转，单个文件最大10MB
- 保留5个备份文件

### 2. 成功记录日志 (`success_records.log`)
- 专门记录发现有余额地址的详细信息
- JSON格式，包含完整的私钥、公钥、地址、余额信息
- 不进行轮转，永久保存所有成功记录

成功记录示例：
```json
{
  "timestamp": "2024-01-15T10:32:15.123456",
  "private_key": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
  "public_key": "04abcdef...",
  "address": "0x1234567890123456789012345678901234567890",
  "balance_eth": 0.5,
  "total_checked": 2500
}
```

## 安全注意事项

⚠️ **重要安全提醒**：

1. **私钥安全**：成功日志文件包含完整的私钥信息，请妥善保管
2. **文件权限**：建议设置适当的文件权限，防止未授权访问
3. **网络安全**：使用可信的RPC节点，避免泄露查询信息
4. **合法使用**：本工具仅用于教育和研究目的，请遵守相关法律法规

## 性能优化

- 程序使用异步方式查询余额，提高检查效率
- 支持多个RPC节点，自动切换提高可用性
- 日志轮转机制防止磁盘空间耗尽
- 内存使用优化，适合长时间运行

## 故障排除

### 停止程序

- **控制台模式**：按 `Ctrl+C` 停止程序
- **服务模式**：使用服务管理工具停止

## 故障排除

### 常见问题

1. **连接RPC节点失败**
   - 检查网络连接
   - 尝试更换RPC节点
   - 检查防火墙设置

2. **依赖包安装失败**
   - 升级pip：`pip install --upgrade pip`
   - 使用国内镜像：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`

3. **权限错误**
   - 确保对日志目录有写入权限
   - Windows用户可能需要以管理员身份运行

4. **Windows服务相关问题**
   - 服务安装需要管理员权限
   - 检查Windows事件查看器中的服务日志
   - 确保Python路径正确配置

## 技术实现

- **私钥生成**：使用 `secrets` 模块生成加密安全的随机数
- **地址生成**：基于 `eth-account` 和 `eth-keys` 库
- **余额查询**：通过 `web3.py` 连接以太坊节点
- **日志系统**：使用Python标准库 `logging` 模块

## 项目结构

```
eth_balance_hunter/
├── eth_balance_hunter.py    # 主程序文件
├── eth_service.py          # Windows服务包装器
├── install_service.py      # 服务安装脚本
├── service_manager.py      # 服务管理工具
├── service_control.bat     # 服务控制批处理脚本
├── config.json             # 配置文件
├── requirements.txt        # Python依赖包
├── logs/                   # 日志目录
│   ├── eth_hunter.log     # 主日志文件
│   └── success_records.log # 成功记录文件
└── README.md              # 说明文档
```

## 许可证

本项目仅供学习和研究使用。使用者需自行承担使用风险。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持私钥生成和余额检查
- 完整的日志记录系统
- 配置文件支持