#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询记录记忆功能模块
支持短期记忆（Redis）和长期记忆（SQLite）
"""

import os
import json
import redis
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_EXPIRE_DAYS = 7  # 短期记忆过期时间：7天

# SQLite 配置
SQLITE_DB = "/www/wwwroot/impactAPI/query_history.db"

# 日志配置
logger = logging.getLogger('impact-api')


class QueryMemory:
    """查询记录记忆管理类"""
    
    def __init__(self):
        """初始化记忆管理类"""
        self.redis_client = None
        self._init_redis()
        self._create_sqlite_table()
    
    def _init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.redis_client = None
    
    def _get_sqlite_conn(self):
        """获取SQLite连接"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(SQLITE_DB), exist_ok=True)
            conn = sqlite3.connect(SQLITE_DB)
            return conn
        except Exception as e:
            logger.error(f"获取SQLite连接失败: {e}")
            return None
    
    def _create_sqlite_table(self):
        """创建SQLite表"""
        conn = self._get_sqlite_conn()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            # 创建查询记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT NOT NULL,
                    query_time TIMESTAMP NOT NULL,
                    result_count INTEGER NOT NULL,
                    execution_time FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_query_records_query_time 
                ON query_records (query_time)
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("SQLite表创建成功")
        except Exception as e:
            logger.error(f"创建SQLite表失败: {e}")
            if conn:
                conn.rollback()
                conn.close()
    
    def store_short_term_memory(self, query_text: str, result_count: int, execution_time: float):
        """存储短期记忆
        
        Args:
            query_text: 查询文本
            result_count: 结果数量
            execution_time: 执行时间（秒）
        """
        if not self.redis_client:
            logger.warning("Redis未连接，无法存储短期记忆")
            return
        
        try:
            # 生成唯一键
            key = f"query:{datetime.now().timestamp()}"
            # 存储查询记录
            query_record = {
                "query_text": query_text,
                "query_time": datetime.now().isoformat(),
                "result_count": result_count,
                "execution_time": execution_time
            }
            # 存储到Redis
            self.redis_client.setex(
                key,
                timedelta(days=REDIS_EXPIRE_DAYS),
                json.dumps(query_record)
            )
            # 添加到查询历史列表
            self.redis_client.lpush("query_history", key)
            # 限制列表长度
            self.redis_client.ltrim("query_history", 0, 999)  # 保留最近1000条
            logger.info(f"短期记忆存储成功: {query_text}")
        except Exception as e:
            logger.error(f"短期记忆存储失败: {e}")
    
    def store_long_term_memory(self, query_text: str, result_count: int, execution_time: float, query_time: datetime):
        """存储长期记忆
        
        Args:
            query_text: 查询文本
            result_count: 结果数量
            execution_time: 执行时间（秒）
            query_time: 查询时间
        """
        conn = self._get_sqlite_conn()
        if not conn:
            logger.warning("SQLite未连接，无法存储长期记忆")
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO query_records (query_text, query_time, result_count, execution_time)
                VALUES (?, ?, ?, ?)
            ''', (query_text, query_time, result_count, execution_time))
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"长期记忆存储成功: {query_text}")
        except Exception as e:
            logger.error(f"长期记忆存储失败: {e}")
            if conn:
                conn.rollback()
                conn.close()
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict]:
        """获取最近的查询记录（短期记忆）
        
        Args:
            limit: 返回记录数量
            
        Returns:
            最近的查询记录列表
        """
        if not self.redis_client:
            logger.warning("Redis未连接，无法获取最近查询记录")
            return []
        
        try:
            # 获取最近的查询记录键
            keys = self.redis_client.lrange("query_history", 0, limit-1)
            queries = []
            for key in keys:
                query_data = self.redis_client.get(key)
                if query_data:
                    query = json.loads(query_data)
                    queries.append(query)
            logger.info(f"获取最近查询记录成功: {len(queries)} 条")
            return queries
        except Exception as e:
            logger.error(f"获取最近查询记录失败: {e}")
            return []
    
    def search_history_queries(self, keyword: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, limit: int = 10) -> List[Dict]:
        """搜索历史查询记录（长期记忆）
        
        Args:
            keyword: 搜索关键词
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回记录数量
            
        Returns:
            符合条件的历史查询记录列表
        """
        conn = self._get_sqlite_conn()
        if not conn:
            logger.warning("SQLite未连接，无法搜索历史查询记录")
            return []
        
        try:
            cursor = conn.cursor()
            # 构建查询
            query = '''
                SELECT id, query_text, query_time, result_count, execution_time
                FROM query_records
                WHERE 1=1
            '''
            params = []
            
            # 添加关键词搜索
            if keyword:
                query += " AND query_text LIKE ?"
                params.append(f"%{keyword}%")
            
            # 添加时间范围
            if start_time:
                query += " AND query_time >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND query_time <= ?"
                params.append(end_time)
            
            # 添加排序和限制
            query += " ORDER BY query_time DESC LIMIT ?"
            params.append(limit)
            
            # 执行查询
            cursor.execute(query, params)
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "query_text": row[1],
                    "query_time": row[2],
                    "result_count": row[3],
                    "execution_time": row[4]
                })
            cursor.close()
            conn.close()
            logger.info(f"搜索历史查询记录成功: {len(results)} 条")
            return results
        except Exception as e:
            logger.error(f"搜索历史查询记录失败: {e}")
            if conn:
                conn.close()
            return []
    
    def archive_short_term_to_long_term(self):
        """将短期记忆归档到长期记忆
        
        归档策略：将超过3天的短期记忆归档到长期记忆
        """
        if not self.redis_client:
            logger.warning("Redis未连接，无法归档")
            return
        
        try:
            # 获取所有短期记忆键
            keys = self.redis_client.lrange("query_history", 0, -1)
            archived_count = 0
            
            logger.info(f"开始归档，共有 {len(keys)} 条记录")
            
            for key in keys:
                query_data = self.redis_client.get(key)
                if query_data:
                    query = json.loads(query_data)
                    query_time = datetime.fromisoformat(query["query_time"])
                    # 检查是否超过3天
                    if (datetime.now() - query_time).days >= 3:
                        logger.info(f"归档记录: {query['query_text']}")
                        # 归档到长期记忆
                        self.store_long_term_memory(
                            query["query_text"],
                            query["result_count"],
                            query["execution_time"],
                            query_time
                        )
                        # 从短期记忆中删除
                        self.redis_client.delete(key)
                        self.redis_client.lrem("query_history", 1, key)
                        archived_count += 1
            
            logger.info(f"短期记忆归档完成: {archived_count} 条记录")
        except Exception as e:
            logger.error(f"短期记忆归档失败: {e}")
    
    def close(self):
        """关闭连接"""
        if self.redis_client:
            try:
                self.redis_client.close()
            except Exception as e:
                logger.error(f"关闭Redis连接失败: {e}")


# 全局记忆管理实例
query_memory = QueryMemory()


if __name__ == "__main__":
    """测试记忆功能"""
    # 测试存储短期记忆
    query_memory.store_short_term_memory("测试查询", 5, 0.1)
    
    # 测试获取最近查询记录
    recent_queries = query_memory.get_recent_queries()
    print("最近查询记录:", recent_queries)
    
    # 测试归档
    query_memory.archive_short_term_to_long_term()
    
    # 测试搜索历史查询记录
    history_queries = query_memory.search_history_queries("测试")
    print("历史查询记录:", history_queries)
    
    # 关闭连接
    query_memory.close()