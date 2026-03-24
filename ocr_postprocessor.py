#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR后处理模块 - 纠正识别错误，提取结构化信息
"""
import re

class OCRPostprocessor:
    """OCR结果后处理器"""
    
    def __init__(self):
        # 常见误识别字符映射
        self.char_corrections = {
            # 数字误识别
            'O': '0', 'o': '0', 'I': '1', 'l': '1', 'Z': '2', 'S': '5',
            # 中文常见误识别
            '雪人族': '汉族', '村': '民', '局': '族',
            '本人局': '居民', '身份.证': '身份证',
            # 英文常见误识别
            'th': '微', 'AY8': '月8', '=': '年',
        }
        
        # 中国省市区词典（部分）
        self.locations = [
            '北京', '上海', '天津', '重庆',
            '广东省', '浙江省', '江苏省', '福建省', '湖南省', '湖北省',
            '深圳市', '广州市', '杭州市', '南京市', '武汉市', '成都市',
            '福田区', '南山区', '罗湖区', '龙岗区', '宝安区'
        ]
        
        # 中国姓氏（百家姓前100）
        self.surnames = [
            '赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈',
            '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许',
            '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏',
            '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦', '章',
            '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦',
            '昌', '马', '苗', '凤', '花', '方', '俞', '任', '袁', '柳',
            '谷', '唐', '罗', '伍', '余', '米', '贝', '史', '黄', '雷'
        ]
    
    def process(self, text):
        """
        综合后处理流程
        
        Args:
            text: OCR识别的原始文本
        
        Returns:
            str: 处理后的文本
        """
        if not text:
            return text
        
        # 1. 字符纠正
        text = self.correct_characters(text)
        
        # 2. 空格规范化
        text = self.normalize_spaces(text)
        
        # 3. 地名修正
        text = self.correct_locations(text)
        
        return text
    
    def correct_characters(self, text):
        """纠正常见误识别字符"""
        for wrong, correct in self.char_corrections.items():
            text = text.replace(wrong, correct)
        return text
    
    def normalize_spaces(self, text):
        """规范化空格"""
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        # 中文字符间不应有空格
        text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
        return text.strip()
    
    def correct_locations(self, text):
        """修正地名"""
        for location in self.locations:
            # 使用模糊匹配修正地名
            pattern = ''.join([f'{c}[^{c}]?' for c in location])
            matches = re.finditer(pattern, text)
            for match in matches:
                if self._similarity(match.group(), location) > 0.7:
                    text = text.replace(match.group(), location)
        return text
    
    def _similarity(self, s1, s2):
        """计算字符串相似度"""
        if not s1 or not s2:
            return 0.0
        matches = sum(1 for a, b in zip(s1, s2) if a == b)
        return matches / max(len(s1), len(s2))
    
    def extract_id_card_info(self, text):
        """
        从文本中提取身份证信息
        
        Returns:
            dict: 包含姓名、身份证号、地址等信息
        """
        info = {
            'name': None,
            'id_number': None,
            'address': None,
            'birth_date': None,
            'gender': None,
            'nation': None,
            'issue_authority': None,
            'validity_period': None
        }
        
        # 提取身份证号（18位）
        id_pattern = r'\b\d{17}[\dXx]\b'
        id_match = re.search(id_pattern, text)
        if id_match:
            info['id_number'] = id_match.group()
        
        # 提取出生日期（多种格式）
        date_patterns = [
            r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
            r'(\d{4})\.(\d{2})\.(\d{2})',
            r'(\d{4})-(\d{2})-(\d{2})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                info['birth_date'] = f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
                break
        
        # 提取地址（包含"省"、"市"、"区"、"路"等）
        address_pattern = r'[\u4e00-\u9fff]+(?:省|市|区|县|镇|乡|路|街|道|巷|号|室|楼|栋|单元)[\u4e00-\u9fff\d\s]+'
        address_match = re.search(address_pattern, text)
        if address_match:
            info['address'] = address_match.group().strip()
        
        # 提取民族
        nation_pattern = r'(汉|回|蒙古|藏|维吾尔|苗|彝|壮|布依|朝鲜|满|侗|瑶|白|土家|哈尼|哈萨克|傣|黎|傈僳|佤|畲|高山|拉祜|水|东乡|纳西|景颇|柯尔克孜|土|达斡尔|仫佬|羌|布朗|撒拉|毛南|仡佬|锡伯|阿昌|普米|塔吉克|怒|乌孜别克|俄罗斯|鄂温克|德昂|保安|裕固|京|塔塔尔|独龙|鄂伦春|赫哲|门巴|珞巴|基诺)族'
        nation_match = re.search(nation_pattern, text)
        if nation_match:
            info['nation'] = nation_match.group()
        
        # 提取签发机关
        authority_pattern = r'签发机关[:\s]*([^\n]+(?:公安局|派出所)[^\n]*)'
        authority_match = re.search(authority_pattern, text)
        if authority_match:
            info['issue_authority'] = authority_match.group(1).strip()
        
        # 提取有效期限
        validity_pattern = r'有效期限[:\s]*(\d{4}\.\d{2}\.\d{2})\s*[-至到]\s*(\d{4}\.\d{2}\.\d{2}|长期)'
        validity_match = re.search(validity_pattern, text)
        if validity_match:
            info['validity_period'] = f"{validity_match.group(1)} 至 {validity_match.group(2)}"
        
        # 尝试从文本开头提取姓名（通常在第一行）
        lines = text.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            # 检查是否为常见姓氏开头的2-4个汉字
            for surname in self.surnames:
                if first_line.startswith(surname):
                    # 提取姓氏后的2-3个字符作为名字
                    name_match = re.match(rf'{surname}([\u4e00-\u9fff]{{1,3}})', first_line)
                    if name_match:
                        info['name'] = name_match.group()
                        break
        
        return info
    
    def validate_id_number(self, id_number):
        """
        验证身份证号码格式和校验码
        
        Args:
            id_number: 18位身份证号
        
        Returns:
            bool: 是否有效
        """
        if not id_number or len(id_number) != 18:
            return False
        
        # 验证前17位是否为数字
        if not id_number[:17].isdigit():
            return False
        
        # 验证最后一位（校验码）
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        total = sum(int(id_number[i]) * weights[i] for i in range(17))
        check_code = check_codes[total % 11]
        
        return id_number[-1].upper() == check_code

# 创建全局实例
ocr_postprocessor = OCRPostprocessor()
