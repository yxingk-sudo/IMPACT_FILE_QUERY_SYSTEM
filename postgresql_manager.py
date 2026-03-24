#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL管理器占位模块
"""
import psycopg2
from psycopg2 import pool

class PostgreSQLManager:
    def __init__(self):
        self.connection_pool = None
        self.connected = False
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,
                host="127.0.0.1",
                port=5432,
                database="impactfileindex",
                user="postgres",
                password="postgres"
            )
            self.connected = True
        except Exception as e:
            print(f"PostgreSQL连接池创建失败: {e}")
            self.connected = False
    
    def connect(self):
        """检查是否连接成功"""
        return self.connected
    
    def get_connection(self):
        """获取数据库连接"""
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None
    
    def return_connection(self, conn):
        """归还数据库连接"""
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)
    
    def get_file_by_path(self, file_path):
        """根据文件路径获取文件信息"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, file_path, file_name, file_type, file_size, file_hash, 
                          content_preview, full_content, indexed_at, modified_at, 
                          status, duplicate_of, is_deleted, category_id
                   FROM file_index WHERE file_path = %s""",
                (file_path,)
            )
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                # 转换为字典格式
                return {
                    'id': row[0],
                    'file_path': row[1],
                    'file_name': row[2],
                    'file_type': row[3],
                    'file_size': row[4],
                    'file_hash': row[5],
                    'content_preview': row[6],
                    'full_content': row[7],
                    'indexed_at': row[8],
                    'modified_at': row[9],
                    'status': row[10],
                    'duplicate_of': row[11],
                    'is_deleted': row[12],
                    'category_id': row[13]
                }
            return None
        except Exception as e:
            print(f"查询文件失败: {e}")
            return None
        finally:
            self.return_connection(conn)
    
    def insert_file(self, file_data):
        """插入文件索引"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            # 这里需要根据实际表结构调整
            cursor.execute(
                """INSERT INTO file_index 
                   (file_path, file_name, file_hash, indexed_at) 
                   VALUES (%s, %s, %s, %s)""",
                (file_data.get('path'), file_data.get('name'), 
                 file_data.get('hash'), file_data.get('indexed_at'))
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"插入文件失败: {e}")
            return False
        finally:
            self.return_connection(conn)
    
    def update_file(self, file_path, file_data):
        """更新文件索引"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE file_index 
                   SET file_hash = %s, indexed_at = %s 
                   WHERE file_path = %s""",
                (file_data.get('hash'), file_data.get('indexed_at'), file_path)
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"更新文件失败: {e}")
            return False
        finally:
            self.return_connection(conn)
    
    def index_file(self, file_info):
        """索引文件到数据库"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM file_index WHERE file_path = %s",
                (file_info['file_path'],)
            )
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute(
                    """UPDATE file_index SET 
                       file_name = %s, file_type = %s, file_size = %s, file_hash = %s,
                       content_preview = %s, full_content = %s, modified_at = %s,
                       indexed_at = NOW(), category_id = %s, status = 'indexed'
                       WHERE file_path = %s""",
                    (file_info['file_name'], file_info['file_type'], file_info['file_size'],
                     file_info['file_hash'], file_info['content_preview'], file_info['full_content'],
                     file_info['modified_at'], file_info['category_id'], file_info['file_path'])
                )
            else:
                # 插入新记录
                cursor.execute(
                    """INSERT INTO file_index 
                       (file_path, file_name, file_type, file_size, file_hash, content_preview, 
                        full_content, modified_at, indexed_at, category_id, status, is_deleted)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, 'indexed', 0)""",
                    (file_info['file_path'], file_info['file_name'], file_info['file_type'],
                     file_info['file_size'], file_info['file_hash'], file_info['content_preview'],
                     file_info['full_content'], file_info['modified_at'], file_info['category_id'])
                )
            
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"索引文件失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.return_connection(conn)
    
    def remove_file(self, file_path):
        """从索引中移除文件"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE file_index SET is_deleted = 1, status = 'deleted' WHERE file_path = %s",
                (file_path,)
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"移除文件失败: {e}")
            return False
        finally:
            self.return_connection(conn)
    
    def search_files(self, query, limit=10):
        """搜索文件"""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT file_path, file_name, content_preview 
                   FROM file_index 
                   WHERE (file_name LIKE %s OR full_content LIKE %s) 
                   AND is_deleted = 0
                   LIMIT %s""",
                (f'%{query}%', f'%{query}%', limit)
            )
            results = cursor.fetchall()
            cursor.close()
            
            return [{'file_path': r[0], 'file_name': r[1], 'preview': r[2]} for r in results]
        except Exception as e:
            print(f"搜索文件失败: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    def list_all_files(self, limit=1000):
        """列出所有文件"""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT file_path, file_name, file_type, file_size, indexed_at 
                   FROM file_index 
                   WHERE is_deleted = 0
                   ORDER BY indexed_at DESC
                   LIMIT %s""",
                (limit,)
            )
            results = cursor.fetchall()
            cursor.close()
            
            return [{
                'file_path': r[0], 
                'file_name': r[1], 
                'file_type': r[2],
                'file_size': r[3],
                'indexed_at': r[4]
            } for r in results]
        except Exception as e:
            print(f"列出文件失败: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    def get_duplicate_files(self):
        """获取重复文件"""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT file_hash, COUNT(*) as count 
                   FROM file_index 
                   WHERE is_deleted = 0 AND file_hash IS NOT NULL AND file_hash != ''
                   GROUP BY file_hash 
                   HAVING COUNT(*) > 1"""
            )
            results = cursor.fetchall()
            cursor.close()
            
            return [{'file_hash': r[0], 'count': r[1]} for r in results]
        except Exception as e:
            print(f"获取重复文件失败: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection_pool:
            self.connection_pool.closeall()
            self.connected = False
    
    def save_keywords(self, file_id, keywords):
        """保存文件关键词"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # 先删除旧关键词
            cursor.execute(
                "DELETE FROM file_keywords WHERE file_id = %s",
                (file_id,)
            )
            
            # 插入新关键词
            if keywords:
                for keyword in keywords:
                    if isinstance(keyword, str) and keyword.strip():
                        cursor.execute(
                            """INSERT INTO file_keywords (file_id, keyword, weight) 
                               VALUES (%s, %s, %s)
                               ON CONFLICT (file_id, keyword) DO NOTHING""",
                            (file_id, keyword.strip()[:255], 1.0)
                        )
            
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"保存关键词失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.return_connection(conn)
    
    def get_keywords(self, file_id):
        """获取文件的关键词"""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT keyword, weight FROM file_keywords 
                   WHERE file_id = %s ORDER BY weight DESC""",
                (file_id,)
            )
            results = cursor.fetchall()
            cursor.close()
            
            return [{'keyword': r[0], 'weight': r[1]} for r in results]
        except Exception as e:
            print(f"获取关键词失败: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    def search_by_keywords(self, keywords, limit=20):
        """根据关键词搜索文件"""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            if not keywords:
                return []
            
            # 构建查询条件
            keyword_conditions = ' OR '.join(['keyword ILIKE %s'] * len(keywords))
            keyword_params = [f'%{k}%' for k in keywords]
            
            cursor.execute(
                f"""SELECT fi.id, fi.file_path, fi.file_name, fi.content_preview, 
                           fi.indexed_at, COUNT(fk.id) as match_count
                   FROM file_index fi
                   INNER JOIN file_keywords fk ON fi.id = fk.file_id
                   WHERE ({keyword_conditions}) AND fi.is_deleted = 0
                   GROUP BY fi.id, fi.file_path, fi.file_name, fi.content_preview, fi.indexed_at
                   ORDER BY match_count DESC, fi.indexed_at DESC
                   LIMIT %s""",
                keyword_params + [limit]
            )
            results = cursor.fetchall()
            cursor.close()
            
            return [{
                'id': r[0],
                'file_path': r[1],
                'file_name': r[2],
                'preview': r[3],
                'indexed_at': r[4],
                'match_count': r[5]
            } for r in results]
        except Exception as e:
            print(f"关键词搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            self.return_connection(conn)

# 创建全局实例
pg_manager = PostgreSQLManager()
