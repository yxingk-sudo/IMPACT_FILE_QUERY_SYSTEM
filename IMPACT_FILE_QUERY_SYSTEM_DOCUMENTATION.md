# Impact 文件查询系统 - 系统说明文档

## 1. 系统概述

Impact 文件查询系统是一个专为提升文件检索效率而设计的API服务系统，它能够：

- **文件索引**：对指定目录下的文件进行索引，支持快速搜索
- **全文搜索**：支持对文件内容的全文搜索
- **智能查询**：根据用户问题智能匹配相关文件
- **查询记忆**：记录用户查询历史，支持短期和长期记忆
- **Dify集成**：提供API接口供Dify智能体调用使用
- **系统监控**：监控系统运行状态，确保服务稳定

## 2. 系统架构

### 2.1 核心组件

| 组件名称 | 说明 | 路径 |
|---------|------|------|
| 主API服务 | 提供HTTP API接口 | `/www/wwwroot/impactAPI/impact_query_api.py` |
| 文件查询服务 | 处理文件搜索和内容获取 | `/www/wwwroot/impactAPI/impact_query_api.py` (FileQueryService类) |
| 查询记忆服务 | 管理查询记录的短期和长期记忆 | `/www/wwwroot/impactAPI/query_memory.py` |
| 系统监控服务 | 监控系统运行状态 | `/www/wwwroot/impact_monitor/impact_system_monitor.py` |
| 自动清理脚本 | 清理系统垃圾文件 | `/www/wwwroot/auto_cleanup.sh` |

### 2.2 存储架构

- **文件索引数据库**：SQLite，存储文件索引信息
  - 路径：`/www/wwwroot/impactAPI/impact_file_index.db`

- **查询记忆存储**：
  - 短期记忆：Redis，存储最近7天的查询记录
  - 长期记忆：SQLite，持久化存储历史查询记录
    - 路径：`/www/wwwroot/impactAPI/query_history.db`

- **日志存储**：
  - API日志：`/www/wwwroot/impactAPI/logs/api.log`
  - 监控日志：`/www/wwwroot/impact_monitor/logs/monitor.log`

## 3. 核心功能

### 3.1 文件搜索
- **全文搜索**：根据关键词搜索文件内容
- **文件类型筛选**：支持按文件类型筛选
- **结果排序**：按相关度排序

### 3.2 文件内容获取
- **完整内容**：获取文件的完整内容
- **内容预览**：获取文件的内容预览

### 3.3 智能查询
- **问题理解**：理解用户问题的意图
- **文件匹配**：匹配与问题相关的文件
- **上下文构建**：构建回答上下文

### 3.4 查询记忆
- **短期记忆**：存储最近7天的查询记录
- **长期记忆**：持久化存储历史查询记录
- **自动归档**：自动将超过3天的短期记忆归档到长期记忆
- **记忆查询**：支持查询最近和历史查询记录

### 3.5 系统监控
- **API服务监控**：监控API服务的运行状态
- **文件监控**：监控文件目录的变化
- **数据库监控**：监控数据库的运行状态
- **系统资源监控**：监控系统资源使用情况

## 4. API接口说明

### 4.1 健康检查
- **接口**：`GET /health`
- **功能**：检查API服务的健康状态
- **响应**：
  ```json
  {
    "status": "ok",
    "service": "impact-query-api"
  }
  ```

### 4.2 搜索文件
- **接口**：`POST /api/search`
- **功能**：搜索文件
- **参数**：
  - `query`：搜索关键词（必填）
  - `limit`：返回数量（默认10，可选）
- **响应**：
  ```json
  {
    "success": true,
    "count": 5,
    "results": [
      {
        "file_path": "/path/to/file",
        "file_name": "file.txt",
        "file_type": ".txt",
        "file_size": 1024,
        "preview": "文件内容预览",
        "modified_at": "2026-03-03 12:00:00"
      }
    ]
  }
  ```

### 4.3 获取文件内容
- **接口**：`GET /api/file/<path>`
- **功能**：获取文件的完整内容
- **参数**：
  - `path`：文件路径（URL路径参数）
- **响应**：
  ```json
  {
    "success": true,
    "file": {
      "file_path": "/path/to/file",
      "file_name": "file.txt",
      "file_type": ".txt",
      "file_size": 1024,
      "content": "文件完整内容",
      "preview": "文件内容预览",
      "modified_at": "2026-03-03 12:00:00"
    }
  }
  ```

### 4.4 列出文件
- **接口**：`GET /api/files`
- **功能**：列出所有已索引的文件
- **参数**：
  - `file_type`：文件类型（可选）
  - `limit`：返回数量（默认100，可选）
- **响应**：
  ```json
  {
    "success": true,
    "count": 21,
    "files": [
      {
        "file_path": "/path/to/file",
        "file_name": "file.txt",
        "file_type": ".txt",
        "file_size": 1024,
        "preview": "文件内容预览",
        "modified_at": "2026-03-03 12:00:00"
      }
    ]
  }
  ```

### 4.5 获取统计信息
- **接口**：`GET /api/stats`
- **功能**：获取文件库的统计信息
- **响应**：
  ```json
  {
    "success": true,
    "stats": {
      "total_files": 21,
      "total_size": 13322874,
      "total_size_mb": 12.71,
      "type_distribution": {
        ".doc": 2,
        ".docx": 7,
        ".pdf": 6,
        ".txt": 6
      }
    }
  }
  ```

### 4.6 智能查询
- **接口**：`POST /api/query`
- **功能**：根据问题智能匹配相关文件
- **参数**：
  - `question`：用户问题（必填）
  - `max_results`：最大匹配文件数（默认5，可选）
- **响应**：
  ```json
  {
    "success": true,
    "question": "用户问题",
    "matched_files": 3,
    "context": [
      {
        "file_name": "file.txt",
        "file_type": ".txt",
        "preview": "文件内容预览",
        "content": "文件内容"
      }
    ]
  }
  ```

### 4.7 获取最近查询记录
- **接口**：`GET /api/memory/recent`
- **功能**：获取最近的查询记录
- **参数**：
  - `limit`：返回记录数量（默认10，可选）
- **响应**：
  ```json
  {
    "success": true,
    "count": 1,
    "queries": [
      {
        "query_text": "测试查询",
        "query_time": "2026-03-03T11:56:57.987908",
        "result_count": 0,
        "execution_time": 0.000856
      }
    ]
  }
  ```

### 4.8 搜索历史查询记录
- **接口**：`GET /api/memory/history`
- **功能**：搜索历史查询记录
- **参数**：
  - `keyword`：搜索关键词（可选）
  - `limit`：返回记录数量（默认10，可选）
- **响应**：
  ```json
  {
    "success": true,
    "count": 2,
    "queries": [
      {
        "id": 2,
        "query_text": "测试查询5",
        "query_time": "2026-03-03 11:56:57.987908",
        "result_count": 0,
        "execution_time": 0.000856
      }
    ]
  }
  ```

## 5. 部署和配置

### 5.1 系统要求
- **操作系统**：Linux
- **Python**：3.7+
- **依赖**：
  - Flask
  - Flask-CORS
  - Redis
  - SQLite

### 5.2 安装步骤
1. **克隆代码**：将代码克隆到服务器
2. **安装依赖**：
   ```bash
   pip install flask flask-cors redis
   ```
3. **配置Redis**：确保Redis服务已安装并运行
4. **配置API服务**：
   - 编辑 `impact_query_api.py` 中的配置参数
   - 设置 `INDEX_DB` 为文件索引数据库路径
   - 设置 `API_PORT` 和 `API_HOST`
5. **启动服务**：
   ```bash
   cd /www/wwwroot/impactAPI && nohup python3 impact_query_api.py > api.log 2>&1 &
   ```
6. **配置监控服务**：
   ```bash
   cd /www/wwwroot/impact_monitor && nohup python3 impact_system_monitor.py > impact_monitor.log 2>&1 &
   ```

### 5.3 配置文件
- **`impact_query_api.py`**：主API服务配置
- **`query_memory.py`**：查询记忆服务配置
- **`impact_system_monitor.py`**：系统监控服务配置
- **`dify_impact_tool_config.json`**：Dify工具配置

## 6. 使用方法

### 6.1 基本使用
1. **发送查询请求**：通过`/api/search`接口搜索文件
2. **获取文件内容**：通过`/api/file/<path>`接口获取文件内容
3. **列出文件**：通过`/api/files`接口列出所有文件
4. **获取统计信息**：通过`/api/stats`接口获取统计信息
5. **智能查询**：通过`/api/query`接口进行智能查询
6. **查看查询记录**：通过`/api/memory/recent`和`/api/memory/history`接口查看查询记录

### 6.2 Dify智能体使用
1. **配置工具**：在Dify中配置`impact_file_query`工具
2. **调用工具**：使用以下工具访问系统功能：
   - `search_files`：搜索文件
   - `get_file_content`：获取文件内容
   - `list_all_files`：列出所有文件
   - `smart_query`：智能查询
   - `get_stats`：获取统计信息
   - `get_recent_queries`：获取最近查询记录
   - `search_history_queries`：搜索历史查询记录
3. **处理结果**：根据返回的结果提供智能服务

### 6.3 系统监控
1. **查看监控日志**：`/www/wwwroot/impact_monitor/logs/monitor.log`
2. **查看API日志**：`/www/wwwroot/impactAPI/logs/api.log`
3. **手动执行监控**：
   ```bash
   cd /www/wwwroot/impact_monitor && python3 impact_system_monitor.py
   ```

## 7. 故障排除

### 7.1 常见问题
1. **API服务无法启动**：
   - 检查端口是否被占用
   - 检查依赖是否安装
   - 检查配置文件是否正确

2. **搜索无结果**：
   - 检查文件是否已索引
   - 检查搜索关键词是否正确
   - 检查文件权限

3. **记忆功能不工作**：
   - 检查Redis服务是否运行
   - 检查SQLite数据库权限
   - 检查内存是否足够

4. **监控服务失败**：
   - 检查监控配置
   - 检查系统资源
   - 检查日志文件权限

### 7.2 日志查看
- **API日志**：`/www/wwwroot/impactAPI/logs/api.log`
- **监控日志**：`/www/wwwroot/impact_monitor/logs/monitor.log`
- **系统日志**：使用`journalctl`查看系统日志

## 8. 性能优化

### 8.1 索引优化
- **增量索引**：只索引新增或修改的文件
- **索引缓存**：缓存索引数据，减少数据库访问
- **索引优化**：优化索引结构，提高搜索速度

### 8.2 查询优化
- **查询缓存**：缓存查询结果，减少重复查询
- **分页查询**：使用分页减少返回数据量
- **异步查询**：使用异步处理提高并发性能

### 8.3 存储优化
- **Redis配置**：优化Redis配置，提高缓存性能
- **SQLite优化**：优化SQLite配置，提高数据库性能
- **文件系统优化**：优化文件系统，提高文件访问速度

## 9. 安全措施

### 9.1 访问控制
- **API访问控制**：限制API访问权限
- **文件访问控制**：限制文件访问权限
- **数据库访问控制**：限制数据库访问权限

### 9.2 数据保护
- **数据加密**：加密敏感数据
- **日志保护**：保护日志文件
- **备份策略**：定期备份数据

### 9.3 安全审计
- **访问日志**：记录API访问日志
- **操作日志**：记录系统操作日志
- **安全审计**：定期进行安全审计

## 10. 未来扩展

### 10.1 功能扩展
- **用户认证**：支持多用户场景
- **高级搜索**：支持更复杂的搜索条件
- **文件分析**：提供文件内容分析功能
- **数据可视化**：提供数据可视化界面

### 10.2 技术扩展
- **分布式部署**：支持分布式部署
- **容器化**：使用Docker容器化部署
- **云服务**：支持云服务部署
- **微服务架构**：采用微服务架构

### 10.3 集成扩展
- **更多平台集成**：支持更多智能平台集成
- **第三方服务集成**：集成第三方服务
- **API网关**：使用API网关管理API

## 11. 总结

Impact 文件查询系统是一个功能完善、性能优化的文件检索API服务系统，它通过全文搜索、智能查询、查询记忆等功能，为用户提供了高效、便捷的文件检索体验。同时，通过Dify集成，智能体可以利用这些功能提供更智能的服务。

该系统设计合理，实现简洁，性能优化得当，为文件检索领域提供了一个强大的解决方案。未来，通过持续的功能扩展和技术升级，该系统将能够更好地满足用户的需求，为文件检索带来更多便利。