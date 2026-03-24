#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Impact 文件查询工具（轻量版）
直接通过命令行查询文件，无需 web 服务
"""

import os
import sys
import json
from pathlib import Path

# 导入PostgreSQL管理器
from postgresql_manager import pg_manager


def search_files(query, limit=10):
    """搜索文件"""
    try:
        # 使用PostgreSQL搜索
        results = pg_manager.search_files(query, limit)
        return results
    except Exception as e:
        return [{'error': str(e)}]


def get_file_content(file_name):
    """获取文件内容"""
    try:
        # 先搜索文件
        results = pg_manager.search_files(file_name, limit=1)
        if results:
            return {
                'file_name': results[0]['file_name'],
                'content': results[0]['full_content']
            }
        return {'error': '文件未找到'}
    except Exception as e:
        return {'error': str(e)}


def list_files(limit=20):
    """列出文件"""
    try:
        # 使用PostgreSQL列出文件
        results = pg_manager.list_all_files(limit=limit)
        return results
    except Exception as e:
        return [{'error': str(e)}]


if __name__ == "__main__":
    # 连接到PostgreSQL数据库
    if not pg_manager.connect():
        print(json.dumps({'error': '无法连接到PostgreSQL数据库'}, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': '用法: python3 impact_query_tool.py <action> [args]',
            'actions': {
                'search': 'python3 impact_query_tool.py search "关键词"',
                'get': 'python3 impact_query_tool.py get "文件名"',
                'list': 'python3 impact_query_tool.py list'
            }
        }, ensure_ascii=False, indent=2))
        pg_manager.disconnect()
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'search':
        if len(sys.argv) > 2:
            query = sys.argv[2]
        else:
            query = ""  # 空查询返回所有
        results = search_files(query) if query else list_files(10)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif action == 'get':
        if len(sys.argv) > 2:
            file_name = sys.argv[2]
        else:
            print(json.dumps({'error': '缺少文件名参数'}, ensure_ascii=False))
            pg_manager.disconnect()
            sys.exit(1)
        result = get_file_content(file_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == 'list':
        results = list_files()
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    else:
        print(json.dumps({'error': f'未知操作: {action}'}, ensure_ascii=False))
        pg_manager.disconnect()
        sys.exit(1)
    
    # 断开数据库连接
    pg_manager.disconnect()

