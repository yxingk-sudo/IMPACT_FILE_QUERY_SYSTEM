#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
身份证专用OCR识别模块
"""
import pytesseract
from PIL import Image
import re

try:
    from image_preprocessor import image_preprocessor
    from ocr_postprocessor import ocr_postprocessor
    PREPROCESS_AVAILABLE = True
except ImportError:
    PREPROCESS_AVAILABLE = False
    print("警告: 图片预处理模块不可用")

class IDCardOCR:
    """身份证专用OCR识别器"""
    
    def __init__(self):
        self.use_preprocessing = PREPROCESS_AVAILABLE
    
    def recognize(self, image_path):
        """
        识别身份证信息
        
        Args:
            image_path: 身份证图片路径
        
        Returns:
            dict: 识别结果，包含原始文本和结构化信息
        """
        result = {
            'success': False,
            'raw_text': '',
            'processed_text': '',
            'structured_info': {},
            'confidence': 0.0
        }
        
        try:
            # 1. 图片预处理
            if self.use_preprocessing:
                img = image_preprocessor.preprocess(image_path)
            else:
                img = Image.open(image_path)
            
            # 2. 使用多种PSM模式尝试识别
            psm_modes = [6, 3, 11]  # 6=单列文本, 3=自动, 11=稀疏文本
            best_text = ''
            best_confidence = 0.0
            
            for psm in psm_modes:
                # 配置Tesseract参数
                custom_config = f'--psm {psm} --oem 1'
                
                # 使用中文+英文混合识别
                text = pytesseract.image_to_string(
                    img, 
                    lang='chi_sim+eng',
                    config=custom_config
                )
                
                # 计算置信度（基于文本长度和关键词）
                confidence = self._calculate_confidence(text)
                
                if confidence > best_confidence:
                    best_text = text
                    best_confidence = confidence
            
            result['raw_text'] = best_text
            result['confidence'] = best_confidence
            
            # 3. 后处理
            if PREPROCESS_AVAILABLE:
                processed_text = ocr_postprocessor.process(best_text)
                result['processed_text'] = processed_text
                
                # 4. 提取结构化信息
                result['structured_info'] = ocr_postprocessor.extract_id_card_info(processed_text)
            else:
                result['processed_text'] = best_text
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            print(f"身份证识别失败: {e}")
        
        return result
    
    def _calculate_confidence(self, text):
        """
        计算OCR识别置信度
        
        基于以下因素:
        1. 文本长度（更长的文本通常更可靠）
        2. 包含的身份证关键词数量
        3. 是否包含日期格式
        4. 是否包含地名
        """
        if not text:
            return 0.0
        
        score = 0.0
        
        # 文本长度因子（最多30分）
        score += min(len(text) / 10, 30)
        
        # 身份证关键词（每个10分）
        keywords = ['身份证', '姓名', '性别', '民族', '出生', '住址', '公民', '签发机关', '有效期']
        for keyword in keywords:
            if keyword in text:
                score += 10
        
        # 日期格式（20分）
        if re.search(r'\d{4}[年.-]\d{1,2}[月.-]\d{1,2}', text):
            score += 20
        
        # 地名（20分）
        locations = ['省', '市', '区', '县', '镇', '路', '街', '号']
        if any(loc in text for loc in locations):
            score += 20
        
        # 归一化到0-1
        return min(score / 100, 1.0)

# 创建全局实例
id_card_ocr = IDCardOCR()
