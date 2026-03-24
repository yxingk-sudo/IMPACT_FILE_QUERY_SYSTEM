#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件分类器模块
用于识别和分类不同类型的文件
"""
import os
from pathlib import Path
from typing import Dict

class FileClassifier:
    """文件分类器"""
    
    def __init__(self):
        # 定义文件类型映射
        self.file_types = {
            # 文档类
            'document': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt'],
            # 表格类
            'spreadsheet': ['.xls', '.xlsx', '.csv', '.ods'],
            # 演示文稿
            'presentation': ['.ppt', '.pptx', '.odp'],
            # 图片类
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
            # 代码类
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.php', '.rb', '.sh'],
            # 压缩包
            'archive': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            # 视频类
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
            # 音频类
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
        }
    
    def classify(self, file_path: str) -> str:
        """
        分类文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件类型字符串
        """
        if not os.path.exists(file_path):
            return 'unknown'
        
        # 获取文件扩展名
        ext = Path(file_path).suffix.lower()
        
        # 查找对应的类型
        for file_type, extensions in self.file_types.items():
            if ext in extensions:
                return file_type
        
        return 'other'
    
    def is_text_file(self, file_path: str) -> bool:
        """
        判断是否为文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为文本文件
        """
        file_type = self.classify(file_path)
        return file_type in ['document', 'code']
    
    def is_indexable(self, file_path: str) -> bool:
        """
        判断文件是否可索引
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否可索引
        """
        file_type = self.classify(file_path)
        # 可索引的文件类型
        indexable_types = ['document', 'spreadsheet', 'presentation', 'code']
        return file_type in indexable_types
    
    def get_file_category(self, file_path: str) -> Dict[str, str]:
        """
        获取文件详细分类信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件分类信息字典
        """
        file_type = self.classify(file_path)
        ext = Path(file_path).suffix.lower()
        
        return {
            'type': file_type,
            'extension': ext,
            'is_text': self.is_text_file(file_path),
            'is_indexable': self.is_indexable(file_path)
        }
    
    def classify_file(self, file_path: str, file_name: str = None, content: str = None) -> int:
        """
        智能分类文件，返回分类ID
        
        Args:
            file_path: 文件路径
            file_name: 文件名
            content: 文件内容
            
        Returns:
            分类ID
        """
        file_type = self.classify(file_path)
        
        # 简单的ID映射
        type_to_id = {
            'document': 1,
            'spreadsheet': 2,
            'presentation': 3,
            'image': 4,
            'code': 5,
            'archive': 6,
            'video': 7,
            'audio': 8,
            'other': 9,
            'unknown': 0
        }
        
        return type_to_id.get(file_type, 0)
    
    def get_category_name(self, category_id: int) -> str:
        """
        根据ID获取分类名称
        
        Args:
            category_id: 分类ID
            
        Returns:
            分类名称
        """
        id_to_name = {
            0: '未知',
            1: '文档',
            2: '表格',
            3: '演示文稿',
            4: '图片',
            5: '代码',
            6: '压缩包',
            7: '视频',
            8: '音频',
            9: '其他'
        }
        
        return id_to_name.get(category_id, '未知')

# 创建全局实例
file_classifier = FileClassifier()
