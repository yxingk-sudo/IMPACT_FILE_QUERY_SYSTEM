# 文件查询API系统查询记录记忆功能 - 系统说明文档

## 1. 系统概述

文件查询API系统的查询记录记忆功能是一个为提升用户体验而设计的功能模块，它能够：

- **短期记忆**：实时保存用户最近的查询记录，支持快速访问和展示
- **长期记忆**：持久化存储历史查询记录，支持按关键词等条件进行检索
- **智能归档**：自动将超过3天的短期记忆归档到长期记忆
- **Dify集成**：提供API接口供Dify智能体调用使用

## 2. 功能说明

### 2.1 短期记忆
- **存储方式**：使用Redis实现，设置7天过期时间
- **存储内容**：查询关键词、查询时间、结果数量、执行时间
- **访问方式**：通过`/api/memory/recent`接口获取
- **特点**：响应速度快，适合存储最近的查询记录

### 2.2 长期记忆
- **存储方式**：使用SQLite实现，持久化存储
- **存储内容**：查询关键词、查询时间、结果数量、执行时间
- **访问方式**：通过`/api/memory/history`接口获取
- **特点**：存储空间大，适合存储历史查询记录

### 2.3 记忆管理
- **自动归档**：当短期记忆中的记录超过3天时，自动归档到长期记忆
- **自动清理**：短期记忆通过Redis的过期时间自动清理
- **手动管理**：通过API接口手动管理查询记录

### 2.4 Dify集成
- **工具配置**：在`dify_impact_tool_config.json`中添加了两个新工具
- **工具名称**：`get_recent_queries`和`search_history_queries`
- **功能**：Dify智能体可以通过这些工具访问记忆功能

## 3. 技术实现

### 3.1 核心模块
- **query_memory.py**：实现记忆管理的核心模块
  - `QueryMemory`类：管理短期记忆和长期记忆
  - `store_short_term_memory`：存储短期记忆
  - `store_long_term_memory`：存储长期记忆
  - `get_recent_queries`：获取最近查询记录
  - `search_history_queries`：搜索历史查询记录
  - `archive_short_term_to_long_term`：将短期记忆归档到长期记忆

### 3.2 存储方案
- **短期记忆**：Redis
  - 主机：localhost
  - 端口：6379
  - 数据库：0
  - 过期时间：7天

- **长期记忆**：SQLite
  - 数据库文件：`/www/wwwroot/impactAPI/query_history.db`
  - 表结构：
    ```sql
    CREATE TABLE query_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT NOT NULL,
        query_time TIMESTAMP NOT NULL,
        result_count INTEGER NOT NULL,
        execution_time FLOAT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ```

### 3.3 API接口
- **`POST /api/search`**：搜索文件，自动存储查询记录到短期记忆
- **`POST /api/query`**：智能查询，自动存储查询记录到短期记忆
- **`GET /api/memory/recent`**：获取最近的查询记录
- **`GET /api/memory/history`**：搜索历史查询记录

## 4. API接口说明

### 4.1 获取最近查询记录
- **接口**：`GET /api/memory/recent`
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

### 4.2 搜索历史查询记录
- **接口**：`GET /api/memory/history`
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
      },
      {
        "id": 1,
        "query_text": "测试查询4",
        "query_time": "2026-03-03 11:56:25.590683",
        "result_count": 0,
        "execution_time": 0.000973
      }
    ]
  }
  ```

## 5. 部署和配置

### 5.1 依赖安装
- **Redis**：确保Redis服务已安装并运行
- **Python依赖**：
  ```bash
  pip install redis
  ```

### 5.2 配置修改
- **query_memory.py**：
  - `REDIS_HOST`：Redis主机地址
  - `REDIS_PORT`：Redis端口
  - `REDIS_DB`：Redis数据库
  - `REDIS_EXPIRE_DAYS`：短期记忆过期时间
  - `SQLITE_DB`：SQLite数据库文件路径

### 5.3 权限设置
- 确保SQLite数据库文件有正确的权限：
  ```bash
  chown www:www /www/wwwroot/impactAPI/query_history.db
  chmod 755 /www/wwwroot/impactAPI/query_history.db
  ```

## 6. 使用方法

### 6.1 基本使用
1. **发送查询请求**：通过`/api/search`或`/api/query`接口发送查询请求
2. **查看最近查询**：通过`/api/memory/recent`接口查看最近的查询记录
3. **搜索历史查询**：通过`/api/memory/history`接口搜索历史查询记录

### 6.2 Dify智能体使用
1. **配置工具**：在Dify中配置`impact_file_query`工具
2. **调用工具**：使用`get_recent_queries`和`search_history_queries`工具访问记忆功能
3. **处理结果**：根据返回的查询记录提供个性化服务

## 7. 故障排除

### 7.1 常见问题
1. **Redis连接失败**：
   - 检查Redis服务是否运行
   - 检查Redis配置是否正确

2. **SQLite权限错误**：
   - 检查数据库文件权限
   - 确保www用户有读写权限

3. **归档失败**：
   - 检查数据库文件权限
   - 检查磁盘空间

### 7.2 日志查看
- **API日志**：`/www/wwwroot/impactAPI/api.log`
- **系统日志**：使用`journalctl`查看系统日志

## 8. 性能优化

- **Redis缓存**：使用Redis作为短期记忆，提高访问速度
- **SQLite索引**：为查询记录表添加索引，提高查询速度
- **异步归档**：归档操作在后台执行，不影响API响应速度
- **批量操作**：使用批量操作减少数据库访问次数

## 9. 未来扩展

- **用户认证**：支持多用户场景，为每个用户维护独立的查询记录
- **高级搜索**：支持更复杂的搜索条件，如时间范围、结果数量等
- **数据分析**：提供查询行为分析，优化搜索结果
- **导出功能**：支持导出查询记录为CSV或其他格式

## 10. 总结

文件查询API系统的查询记录记忆功能为用户提供了更好的搜索体验，通过短期记忆和长期记忆的结合，既保证了最近查询的快速访问，又实现了历史查询的持久化存储。同时，通过Dify集成，智能体可以利用这些记忆功能提供更个性化的服务。

该功能设计合理，实现简洁，性能优化得当，为文件查询API系统增添了重要的用户体验提升。