#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片预处理模块 - 优化OCR识别效果
"""
import cv2
import numpy as np
from PIL import Image
import os

class ImagePreprocessor:
    """图片预处理器，提升OCR识别准确率"""
    
    def __init__(self):
        self.debug = False
    
    def preprocess(self, image_path, output_path=None):
        """
        综合预处理流程
        
        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径（可选，用于调试）
        
        Returns:
            PIL.Image: 预处理后的图片对象
        """
        try:
            # 读取图片
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"无法读取图片: {image_path}")
            
            # 1. 去噪
            img = self.denoise(img)
            
            # 2. 倾斜校正
            img = self.deskew(img)
            
            # 3. 增强对比度
            img = self.enhance_contrast(img)
            
            # 4. 二值化
            img = self.binarize(img)
            
            # 5. 锐化（可选）
            img = self.sharpen(img)
            
            # 保存调试图片
            if output_path:
                cv2.imwrite(output_path, img)
            
            # 转换为PIL Image
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            
            return pil_img
            
        except Exception as e:
            print(f"图片预处理失败: {e}")
            # 返回原图
            return Image.open(image_path)
    
    def denoise(self, img):
        """去噪处理 - 使用非局部均值去噪"""
        try:
            # 使用fastNlMeansDenoisingColored去噪
            denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
            return denoised
        except:
            return img
    
    def deskew(self, img):
        """倾斜校正 - 自动检测并校正图片倾斜"""
        try:
            # 转灰度
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # 霍夫变换检测直线
            lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
            
            if lines is not None and len(lines) > 0:
                # 计算平均角度
                angles = []
                for rho, theta in lines[:10, 0]:
                    angle = np.rad2deg(theta) - 90
                    if abs(angle) < 45:  # 只考虑小角度倾斜
                        angles.append(angle)
                
                if angles:
                    avg_angle = np.median(angles)
                    
                    # 如果倾斜角度超过阈值，进行旋转
                    if abs(avg_angle) > 0.5:
                        h, w = img.shape[:2]
                        center = (w // 2, h // 2)
                        M = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
                        rotated = cv2.warpAffine(img, M, (w, h), 
                                                 flags=cv2.INTER_CUBIC,
                                                 borderMode=cv2.BORDER_REPLICATE)
                        return rotated
            
            return img
        except:
            return img
    
    def enhance_contrast(self, img):
        """增强对比度 - 使用CLAHE自适应直方图均衡化"""
        try:
            # 转换到LAB色彩空间
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # 对L通道应用CLAHE
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # 合并通道
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            return enhanced
        except:
            return img
    
    def binarize(self, img):
        """二值化 - 自适应阈值"""
        try:
            # 转灰度
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 自适应阈值二值化
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 转回BGR用于后续处理
            binary_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            
            return binary_bgr
        except:
            return img
    
    def sharpen(self, img):
        """锐化 - 使用USM锐化"""
        try:
            # 创建锐化核
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]])
            
            sharpened = cv2.filter2D(img, -1, kernel)
            return sharpened
        except:
            return img
    
    def resize_for_ocr(self, img, target_height=2000):
        """调整图片大小以优化OCR - 保持宽高比"""
        try:
            h, w = img.shape[:2]
            if h < target_height:
                # 放大图片
                scale = target_height / h
                new_w = int(w * scale)
                resized = cv2.resize(img, (new_w, target_height), 
                                    interpolation=cv2.INTER_CUBIC)
                return resized
            return img
        except:
            return img

# 创建全局实例
image_preprocessor = ImagePreprocessor()
