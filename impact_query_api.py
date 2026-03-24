#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Impact 文件查询 API 服务
提供 HTTP API 供 Dify 智能体查询文件内容
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

# 导入查询记忆模块
from query_memory import query_memory

# 配置
INDEX_DB = "/www/wwwroot/impactAPI/impact_file_index.db"
API_PORT = 8899
API_HOST = "0.0.0.0"

# 日志配置
LOG_DIR = "/www/wwwroot/impactAPI/logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = f"{LOG_DIR}/api.log"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('impact-api')

app = Flask(__name__)
CORS(app)  # 允许跨域


class FileQueryService:
    """文件查询服务"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def search_files(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索文件"""
        try:
            logger.info(f"开始搜索文件: 查询={query}, 限制={limit}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 搜索文件名
            cursor.execute('''
                SELECT file_path, file_name, file_type, file_size,
                       content_preview, modified_at
                FROM file_index
                WHERE file_name LIKE ? AND status = 'active'
                LIMIT ?
            ''', ('%' + query + '%', limit))
            
            # 收集文件名匹配的结果
            results = []
            file_paths = set()
            
            for row in cursor.fetchall():
                file_path = row[0]
                if file_path not in file_paths:
                    file_paths.add(file_path)
                    results.append({
                        'file_path': row[0],
                        'file_name': row[1],
                        'file_type': row[2],
                        'file_size': row[3],
                        'preview': row[4],
                        'modified_at': row[5]
                    })
            
            # 如果还需要更多结果，搜索文件内容
            if len(results) < limit:
                remaining_limit = limit - len(results)
                cursor.execute('''
                    SELECT f.file_path, f.file_name, f.file_type, f.file_size,
                           f.content_preview, f.modified_at
                    FROM file_search s
                    JOIN file_index f ON s.file_path = f.file_path
                    WHERE s.content MATCH ? AND f.status = 'active'
                    ORDER BY rank
                    LIMIT ?
                ''', (query, remaining_limit))
                
                for row in cursor.fetchall():
                    file_path = row[0]
                    if file_path not in file_paths:
                        file_paths.add(file_path)
                        results.append({
                            'file_path': row[0],
                            'file_name': row[1],
                            'file_type': row[2],
                            'file_size': row[3],
                            'preview': row[4],
                            'modified_at': row[5]
                        })
            
            conn.close()
            logger.info(f"搜索完成: 找到 {len(results)} 个文件")
            return results
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def get_file_content(self, file_path: str) -> Optional[Dict]:
        """获取文件完整内容"""
        try:
            logger.info(f"开始获取文件内容: {file_path}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT file_name, file_type, file_size, full_content, 
                       content_preview, modified_at
                FROM file_index 
                WHERE file_path = ? AND status = 'active'
            ''', (file_path,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                logger.info(f"成功获取文件内容: {file_path}")
                return {
                    'file_path': file_path,
                    'file_name': row[0],
                    'file_type': row[1],
                    'file_size': row[2],
                    'content': row[3],
                    'preview': row[4],
                    'modified_at': row[5]
                }
            logger.warning(f"文件不存在或未索引: {file_path}")
            return None
        except Exception as e:
            logger.error(f"获取文件内容失败: {e}")
            return None
    
    def list_files(self, file_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """列出文件"""
        try:
            logger.info(f"开始列出文件: 类型={file_type}, 限制={limit}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if file_type:
                cursor.execute('''
                    SELECT file_path, file_name, file_type, file_size, 
                           content_preview, modified_at
                    FROM file_index
                    WHERE status = 'active' AND file_type = ?
                    ORDER BY modified_at DESC
                    LIMIT ?
                ''', (file_type, limit))
            else:
                cursor.execute('''
                    SELECT file_path, file_name, file_type, file_size, 
                           content_preview, modified_at
                    FROM file_index
                    WHERE status = 'active'
                    ORDER BY modified_at DESC
                    LIMIT ?
                ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'file_path': row[0],
                    'file_name': row[1],
                    'file_type': row[2],
                    'file_size': row[3],
                    'preview': row[4],
                    'modified_at': row[5]
                })
            
            conn.close()
            logger.info(f"列出文件完成: 找到 {len(results)} 个文件")
            return results
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        try:
            logger.info("开始获取统计信息")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM file_index WHERE status = 'active'")
            total_files = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT file_type, COUNT(*) 
                FROM file_index 
                WHERE status = 'active' 
                GROUP BY file_type
            ''')
            type_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            cursor.execute("SELECT SUM(file_size) FROM file_index WHERE status = 'active'")
            total_size = cursor.fetchone()[0] or 0
            
            conn.close()
            
            stats = {
                'total_files': total_files,
                'total_size': total_size,
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'type_distribution': type_counts
            }
            logger.info(f"获取统计信息完成: {stats}")
            return stats
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}


# 初始化服务
query_service = FileQueryService(INDEX_DB)


# API 路由

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    logger.info("健康检查请求")
    return jsonify({'status': 'ok', 'service': 'impact-query-api'})


@app.route('/api/search', methods=['POST'])
def search():
    """搜索文件
    
    请求体:
    {
        "query": "搜索关键词",
        "limit": 10
    }
    """
    logger.info("搜索文件请求")
    data = request.get_json()
    query_text = data.get('query', '')
    limit = data.get('limit', 10)
    
    if not query_text:
        logger.warning("搜索请求缺少query参数")
        return jsonify({'error': 'query 参数不能为空'}), 400
    
    # 记录开始时间
    start_time = datetime.now()
    
    results = query_service.search_files(query_text, limit)
    
    # 计算执行时间
    execution_time = (datetime.now() - start_time).total_seconds()
    
    # 存储查询记录到短期记忆
    query_memory.store_short_term_memory(query_text, len(results), execution_time)
    
    # 尝试归档短期记忆到长期记忆
    try:
        query_memory.archive_short_term_to_long_term()
    except Exception as e:
        logger.error(f"归档失败: {e}")
    
    response = {
        'success': True,
        'count': len(results),
        'results': results
    }
    logger.info(f"搜索请求完成: {response}")
    return jsonify(response)


@app.route('/api/file/<path:file_path>', methods=['GET'])
def get_file(file_path):
    """获取文件内容
    
    URL: /api/file/{file_path}
    """
    logger.info(f"获取文件内容请求: {file_path}")
    # 构建完整路径
    full_path = f"/www/cosfs/impact/{file_path}"
    
    result = query_service.get_file_content(full_path)
    
    if result:
        logger.info(f"获取文件内容成功: {file_path}")
        return jsonify({
            'success': True,
            'file': result
        })
    else:
        logger.warning(f"文件不存在或未索引: {file_path}")
        return jsonify({
            'success': False,
            'error': '文件不存在或未索引'
        }), 404


@app.route('/api/files', methods=['GET'])
def list_files():
    """列出文件
    
    查询参数:
    - file_type: 文件类型（可选）
    - limit: 返回数量限制（默认100）
    """
    logger.info("列出文件请求")
    file_type = request.args.get('file_type')
    limit = int(request.args.get('limit', 100))
    
    results = query_service.list_files(file_type, limit)
    
    response = {
        'success': True,
        'count': len(results),
        'files': results
    }
    logger.info(f"列出文件请求完成: {response}")
    return jsonify(response)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    logger.info("获取统计信息请求")
    stats = query_service.get_stats()
    
    response = {
        'success': True,
        'stats': stats
    }
    logger.info(f"获取统计信息请求完成: {response}")
    return jsonify(response)


@app.route('/api/query', methods=['POST'])
def smart_query():
    """智能查询（供 Dify 工具调用）
    
    请求体:
    {
        "question": "用户问题",
        "max_results": 5
    }
    
    返回匹配的文件及相关内容
    """
    logger.info("智能查询请求")
    data = request.get_json()
    question = data.get('question', '')
    max_results = data.get('max_results', 5)
    
    if not question:
        logger.warning("智能查询请求缺少question参数")
        return jsonify({'error': 'question 参数不能为空'}), 400
    
    # 记录开始时间
    start_time = datetime.now()
    
    # 搜索相关文件
    results = query_service.search_files(question, max_results)
    
    # 构建回答上下文
    context = []
    for result in results:
        file_content = query_service.get_file_content(result['file_path'])
        if file_content:
            context.append({
                'file_name': result['file_name'],
                'file_type': result['file_type'],
                'preview': result['preview'],
                'content': file_content['content'][:1000]  # 限制内容长度
            })
    
    # 计算执行时间
    execution_time = (datetime.now() - start_time).total_seconds()
    
    # 存储查询记录到短期记忆
    query_memory.store_short_term_memory(question, len(context), execution_time)
    
    # 尝试归档短期记忆到长期记忆
    try:
        query_memory.archive_short_term_to_long_term()
    except Exception as e:
        logger.error(f"归档失败: {e}")
    
    response = {
        'success': True,
        'question': question,
        'matched_files': len(context),
        'context': context
    }
    logger.info(f"智能查询请求完成: {response}")
    return jsonify(response)


@app.route('/api/memory/recent', methods=['GET'])
def get_recent_queries():
    """获取最近的查询记录（短期记忆）
    
    查询参数:
    - limit: 返回记录数量（默认10）
    """
    logger.info("获取最近查询记录请求")
    limit = int(request.args.get('limit', 10))
    
    recent_queries = query_memory.get_recent_queries(limit)
    
    response = {
        'success': True,
        'count': len(recent_queries),
        'queries': recent_queries
    }
    logger.info(f"获取最近查询记录完成: {response}")
    return jsonify(response)


@app.route('/api/memory/history', methods=['GET'])
def search_history_queries():
    """搜索历史查询记录（长期记忆）
    
    查询参数:
    - keyword: 搜索关键词（可选）
    - start_time: 开始时间（ISO格式，可选）
    - end_time: 结束时间（ISO格式，可选）
    - limit: 返回记录数量（默认10）
    """
    logger.info("搜索历史查询记录请求")
    keyword = request.args.get('keyword', '')
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    limit = int(request.args.get('limit', 10))
    
    # 解析时间参数
    start_time = None
    end_time = None
    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str)
        except Exception as e:
            logger.error(f"解析开始时间失败: {e}")
    if end_time_str:
        try:
            end_time = datetime.fromisoformat(end_time_str)
        except Exception as e:
            logger.error(f"解析结束时间失败: {e}")
    
    history_queries = query_memory.search_history_queries(keyword, start_time, end_time, limit)
    
    response = {
        'success': True,
        'count': len(history_queries),
        'queries': history_queries
    }
    logger.info(f"搜索历史查询记录完成: {response}")
    return jsonify(response)


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Impact 文件查询 API 服务")
    logger.info(f"监听地址: http://{API_HOST}:{API_PORT}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("可用端点:")
    logger.info(f"  - GET  /health             健康检查")
    logger.info(f"  - POST /api/search         搜索文件")
    logger.info(f"  - GET  /api/file/<path>    获取文件内容")
    logger.info(f"  - GET  /api/files          列出所有文件")
    logger.info(f"  - GET  /api/stats          获取统计信息")
    logger.info(f"  - POST /api/query          智能查询（供 Dify 调用）")
    logger.info(f"  - GET  /api/memory/recent  获取最近查询记录")
    logger.info(f"  - GET  /api/memory/history 搜索历史查询记录")
    logger.info("")
    
    app.run(host=API_HOST, port=API_PORT, debug=False)
