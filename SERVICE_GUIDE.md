# Windows服务使用指南

## 概述

以太坊私钥猎手现在支持作为Windows服务运行，可以在后台持续工作，无需保持控制台窗口打开。

## 快速开始

### 方法一：使用批处理脚本（推荐）

1. 双击运行 `service_control.bat`
2. 选择 "1. 安装服务"
3. 等待安装完成
4. 服务将自动启动

### 方法二：使用命令行

```bash
# 安装服务（需要管理员权限）
python install_service.py install

# 启动服务
python service_manager.py start
```

## 服务管理

### 使用批处理脚本

运行 `service_control.bat` 后可以进行以下操作：

- **安装服务**：首次使用时需要安装
- **卸载服务**：完全移除服务
- **启动服务**：开始后台运行
- **停止服务**：停止后台运行
- **重启服务**：重新启动服务
- **查看状态**：检查服务是否正在运行
- **查看信息**：显示服务详细信息
- **查看日志**：查看运行日志

### 使用命令行工具

#### 服务安装/卸载

```bash
# 安装服务
python install_service.py install

# 卸载服务
python install_service.py uninstall

# 检查服务状态
python install_service.py status
```

#### 服务管理

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

## 服务特性

### 自动启动

- 服务安装后会设置为自动启动
- 系统重启后服务会自动运行
- 无需手动干预

### 后台运行

- 服务在后台静默运行
- 不会显示控制台窗口
- 不影响其他程序使用

### 日志记录

- 所有活动记录到 `logs/eth_hunter.log`
- 成功发现记录到 `logs/success_records.log`
- 重要事件记录到Windows事件日志

### 配置管理

- 使用相同的 `config.json` 配置文件
- 支持所有控制台模式的配置选项
- 可以随时修改配置并重启服务

## 监控和维护

### 查看运行状态

1. **使用服务管理工具**：
   ```bash
   python service_manager.py status
   ```

2. **使用Windows服务管理器**：
   - 按 `Win + R`，输入 `services.msc`
   - 查找 "Ethereum Balance Hunter Service"

3. **查看Windows事件日志**：
   - 按 `Win + R`，输入 `eventvwr.msc`
   - 导航到 "Windows日志" > "应用程序"
   - 查找来源为 "EthBalanceHunter" 的事件

### 查看日志文件

1. **使用服务管理工具**：
   ```bash
   python service_manager.py logs
   ```

2. **直接查看文件**：
   - 主日志：`logs/eth_hunter.log`
   - 成功记录：`logs/success_records.log`

### 性能监控

- 日志中会定期记录统计信息
- 包括检查速度、发现数量等
- 可以通过日志分析程序性能

## 故障排除

### 服务无法启动

1. **检查依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **检查配置文件**：
   - 确保 `config.json` 存在且格式正确
   - 检查RPC节点配置是否有效

3. **查看错误日志**：
   - 检查 `logs/eth_hunter.log`
   - 查看Windows事件日志

### 服务运行异常

1. **重启服务**：
   ```bash
   python service_manager.py restart
   ```

2. **检查网络连接**：
   - 确保能够访问以太坊RPC节点
   - 检查防火墙设置

3. **查看日志**：
   - 分析错误信息
   - 检查是否有速率限制警告

### 权限问题

- 服务安装和卸载需要管理员权限
- 右键点击命令提示符，选择"以管理员身份运行"
- 或者使用批处理脚本，它会自动请求管理员权限

## 最佳实践

### 配置优化

1. **调整请求间隔**：
   - 根据RPC节点限制调整 `request_delay`
   - 避免过于频繁的请求

2. **设置合理的重试次数**：
   - 配置 `max_retries` 处理网络异常
   - 平衡稳定性和性能

3. **配置统计间隔**：
   - 设置合适的 `stats_interval`
   - 避免日志文件过大

### 维护建议

1. **定期检查日志**：
   - 监控程序运行状态
   - 及时发现问题

2. **备份重要数据**：
   - 定期备份成功记录
   - 保存重要的私钥信息

3. **更新配置**：
   - 根据需要调整RPC节点
   - 优化性能参数

## 安全注意事项

1. **私钥安全**：
   - 成功记录包含私钥信息
   - 确保日志文件安全存储
   - 定期备份重要数据

2. **网络安全**：
   - 使用可信的RPC节点
   - 注意网络流量监控

3. **系统安全**：
   - 保持系统更新
   - 使用防病毒软件
   - 定期检查系统安全

## 常见问题

**Q: 服务安装后无法启动？**
A: 检查Python路径、依赖包安装和配置文件是否正确。

**Q: 如何修改服务配置？**
A: 修改 `config.json` 文件后重启服务即可。

**Q: 服务占用资源过多？**
A: 调整配置中的请求间隔和统计间隔，减少资源使用。

**Q: 如何完全卸载？**
A: 先停止并卸载服务，然后删除程序文件夹。

**Q: 服务日志在哪里？**
A: 程序日志在 `logs/` 目录，系统日志在Windows事件查看器中。