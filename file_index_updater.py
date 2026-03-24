#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件索引更新模块
用于重新索引文件并提取内容
"""

import os
import sqlite3
import hashlib
from datetime import datetime
from file_content_extractor import file_extractor

class FileIndexUpdater:
    """文件索引更新器"""
    
    def __init__(self, db_path: str, target_dir: str):
        """
        初始化索引更新器
        
        Args:
            db_path: 数据库路径
            target_dir: 目标目录
        """
        self.db_path = db_path
        self.target_dir = target_dir
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建file_index表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_index (
                file_path TEXT PRIMARY KEY,
                file_name TEXT,
                file_type TEXT,
                file_size INTEGER,
                content_preview TEXT,
                full_content TEXT,
                modified_at TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # 创建file_search表（全文搜索表）
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS file_search USING fts5(
                file_path,
                content
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(65536)
                    if not data:
                        break
                    hasher.update(data)
            return hasher.hexdigest()
        except Exception:
            return ''
    
    def update_index(self):
        """更新文件索引"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 遍历目录
        for root, dirs, files in os.walk(self.target_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                # 计算相对路径
                relative_path = os.path.relpath(file_path, self.target_dir)
                
                # 获取文件信息
                try:
                    file_stat = os.stat(file_path)
                    file_size = file_stat.st_size
                    modified_at = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    file_type = os.path.splitext(file_name)[1].lower()
                    
                    # 提取文件内容
                    success, content, error = file_extractor.extract_content(file_path)
                    
                    if success and content:
                        # 生成内容预览
                        content_preview = content[:500] + '...' if len(content) > 500 else content
                        
                        # 检查文件是否已存在
                        cursor.execute('SELECT file_path FROM file_index WHERE file_path = ?', (file_path,))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # 更新现有记录
                            cursor.execute('''
                                UPDATE file_index SET 
                                    file_name = ?, file_type = ?, file_size = ?, 
                                    content_preview = ?, full_content = ?, modified_at = ?
                                WHERE file_path = ?
                            ''', (file_name, file_type, file_size, content_preview, content, modified_at, file_path))
                        else:
                            # 插入新记录
                            cursor.execute('''
                                INSERT INTO file_index 
                                (file_path, file_name, file_type, file_size, content_preview, full_content, modified_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (file_path, file_name, file_type, file_size, content_preview, content, modified_at))
                        
                        # 更新全文搜索表
                        cursor.execute('DELETE FROM file_search WHERE file_path = ?', (file_path,))
                        cursor.execute('INSERT INTO file_search (file_path, content) VALUES (?, ?)', (file_path, content))
                        
                        print(f"已更新文件: {file_name}")
                    else:
                        print(f"无法提取文件内容: {file_name}, 错误: {error}")
                        
                except Exception as e:
                    print(f"处理文件时出错: {file_name}, 错误: {str(e)}")
        
        conn.commit()
        conn.close()
        print("索引更新完成！")
    
    def get_index_stats(self):
        """获取索引统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM file_index')
        total_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM file_search')
        indexed_files = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_files': total_files,
            'indexed_files': indexed_files
        }

# 示例用法
if __name__ == '__main__':
    db_path = '/www/wwwroot/impactAPI/impact_file_index.db'
    target_dir = '/www/cosfs/impact'
    
    updater = FileIndexUpdater(db_path, target_dir)
    updater.update_index()
    stats = updater.get_index_stats()
    print(f"索引统计: {stats}")
