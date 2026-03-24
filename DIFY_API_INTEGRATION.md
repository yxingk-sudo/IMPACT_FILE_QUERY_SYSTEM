# Dify平台API集成文档

## 1. 概述

本文档整理了Impact文件查询系统中与Dify平台相关的API接口信息，用于Dify平台的API集成开发。

## 2. API接口详情

### 2.1 健康检查
- **接口路径**：`GET /health`
- **请求方法**：GET
- **请求参数**：无
- **响应数据格式**：
  ```json
  {
    "status": "ok",
    "service": "impact-query-api"
  }
  ```
- **接口认证**：无需认证

### 2.2 搜索文件
- **接口路径**：`POST /api/search`
- **请求方法**：POST
- **请求参数**：
  | 参数名称 | 类型 | 是否必填 | 描述 |
  |---------|------|---------|------|
  | query | string | 是 | 搜索关键词 |
  | limit | integer | 否 | 返回数量（默认10） |
- **响应数据格式**：
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
- **接口认证**：无需认证

### 2.3 获取文件内容
- **接口路径**：`GET /api/file/<path>`
- **请求方法**：GET
- **请求参数**：
  | 参数名称 | 类型 | 是否必填 | 描述 |
  |---------|------|---------|------|
  | path | string | 是 | 文件路径（URL路径参数） |
- **响应数据格式**：
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
- **接口认证**：无需认证

### 2.4 列出文件
- **接口路径**：`GET /api/files`
- **请求方法**：GET
- **请求参数**：
  | 参数名称 | 类型 | 是否必填 | 描述 |
  |---------|------|---------|------|
  | file_type | string | 否 | 文件类型 |
  | limit | integer | 否 | 返回数量（默认100） |
- **响应数据格式**：
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
- **接口认证**：无需认证

### 2.5 获取统计信息
- **接口路径**：`GET /api/stats`
- **请求方法**：GET
- **请求参数**：无
- **响应数据格式**：
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
- **接口认证**：无需认证

### 2.6 智能查询
- **接口路径**：`POST /api/query`
- **请求方法**：POST
- **请求参数**：
  | 参数名称 | 类型 | 是否必填 | 描述 |
  |---------|------|---------|------|
  | question | string | 是 | 用户问题 |
  | max_results | integer | 否 | 最大匹配文件数（默认5） |
- **响应数据格式**：
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
- **接口认证**：无需认证

### 2.7 获取最近查询记录
- **接口路径**：`GET /api/memory/recent`
- **请求方法**：GET
- **请求参数**：
  | 参数名称 | 类型 | 是否必填 | 描述 |
  |---------|------|---------|------|
  | limit | integer | 否 | 返回记录数量（默认10） |
- **响应数据格式**：
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
- **接口认证**：无需认证

### 2.8 搜索历史查询记录
- **接口路径**：`GET /api/memory/history`
- **请求方法**：GET
- **请求参数**：
  | 参数名称 | 类型 | 是否必填 | 描述 |
  |---------|------|---------|------|
  | keyword | string | 否 | 搜索关键词 |
  | limit | integer | 否 | 返回记录数量（默认10） |
- **响应数据格式**：
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
- **接口认证**：无需认证

## 3. Dify工具配置

在Dify中配置`impact_file_query`工具时，可以使用以下功能：

| 工具名称 | 对应API接口 | 功能描述 |
|---------|------------|----------|
| search_files | POST /api/search | 搜索文件 |
| get_file_content | GET /api/file/<path> | 获取文件内容 |
| list_all_files | GET /api/files | 列出所有文件 |
| smart_query | POST /api/query | 智能查询 |
| get_stats | GET /api/stats | 获取统计信息 |
| get_recent_queries | GET /api/memory/recent | 获取最近查询记录 |
| search_history_queries | GET /api/memory/history | 搜索历史查询记录 |

## 4. 集成注意事项

1. **认证方式**：根据文档，所有API接口均无需认证，可直接调用。
2. **请求格式**：POST请求使用JSON格式提交数据。
3. **响应格式**：所有API接口均返回JSON格式数据，包含`success`字段表示请求是否成功。
4. **错误处理**：接口可能返回错误信息，集成时需处理相应的错误情况。
5. **性能考虑**：对于大量文件的查询，建议使用分页和合理的limit参数，避免返回过多数据。

## 5. 部署信息

- **API服务地址**：根据部署配置而定，默认为服务运行的主机和端口
- **依赖**：Flask, Flask-CORS, Redis, SQLite
- **部署路径**：`/www/wwwroot/impactAPI`

## 6. 示例调用

### 搜索文件示例
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 5}'
```

### 智能查询示例
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "如何使用这个系统", "max_results": 3}'
```

### 获取文件内容示例
```bash
curl http://localhost:5000/api/file/path/to/file.txt
```
