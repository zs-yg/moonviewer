"""
工具函数模块
提供图片加载和处理相关的工具函数
"""

import os
from pathlib import Path
from typing import Tuple, Dict, Optional, Union

import numpy as np
from PIL import Image, ImageOps
from PySide6.QtGui import QImage, QPixmap


def is_supported_image(file_path: Union[str, Path]) -> bool:
    """
    检查文件是否为支持的图片格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 如果文件是支持的图片格式则返回True
    """
    supported_extensions = {
        '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp',
        '.PNG', '.JPG', '.JPEG', '.BMP', '.GIF', '.TIFF', '.WEBP'
    }
    
    ext = os.path.splitext(str(file_path))[1]
    return ext in supported_extensions


def get_image_info(file_path: Union[str, Path]) -> Dict:
    """
    获取图片的基本信息
    
    Args:
        file_path: 图片文件路径
        
    Returns:
        Dict: 包含图片信息的字典
    """
    try:
        with Image.open(file_path) as img:
            info = {
                'width': img.width,
                'height': img.height,
                'mode': img.mode,
                'format': img.format,
                'format_description': img.format_description,
                'size_bytes': os.path.getsize(file_path),
                'filename': os.path.basename(file_path),
                'filepath': str(file_path),
            }
            return info
    except Exception as e:
        raise ValueError(f"无法获取图片信息: {str(e)}")


def convert_to_qimage(numpy_array: np.ndarray) -> QImage:
    """
    将numpy数组转换为QImage
    
    Args:
        numpy_array: 形状为 (height, width, channels) 的numpy数组，
                     channels可以是3(RGB)或4(RGBA)
                     
    Returns:
        QImage: 转换后的QImage对象
        
    Raises:
        ValueError: 如果数组形状或数据类型不支持
    """
    if len(numpy_array.shape) != 3:
        raise ValueError(f"期望3维数组，得到 {len(numpy_array.shape)} 维")
    
    height, width, channels = numpy_array.shape
    
    if channels not in (3, 4):
        raise ValueError(f"期望3或4通道，得到 {channels} 通道")
    
    # 确保数据类型为uint8且内存连续
    if numpy_array.dtype != np.uint8:
        numpy_array = numpy_array.astype(np.uint8)
    
    # 确保数组在内存中是连续的
    numpy_array = np.ascontiguousarray(numpy_array)
    
    # 根据通道数设置QImage格式
    if channels == 3:
        # RGB格式，每个通道8位
        qimage_format = QImage.Format_RGB888
    else:  # channels == 4
        # RGBA格式，每个通道8位
        qimage_format = QImage.Format_RGBA8888
    
    # 创建QImage
    # 注意：QImage不会复制数据，所以需要保持numpy_array的引用
    qimage = QImage(
        numpy_array.data,
        width,
        height,
        width * channels,  # 每行的字节数
        qimage_format
    )
    
    # 确保数据不会被垃圾回收
    qimage.ndarray = numpy_array
    
    return qimage


def convert_to_qpixmap(numpy_array: np.ndarray) -> QPixmap:
    """
    将numpy数组转换为QPixmap
    
    Args:
        numpy_array: 形状为 (height, width, channels) 的numpy数组
        
    Returns:
        QPixmap: 转换后的QPixmap对象
    """
    qimage = convert_to_qimage(numpy_array)
    return QPixmap.fromImage(qimage)


def load_pil_image(file_path: Union[str, Path]) -> Image.Image:
    """
    使用Pillow加载图片
    
    Args:
        file_path: 图片文件路径
        
    Returns:
        Image.Image: PIL图像对象
    """
    try:
        return Image.open(file_path)
    except Exception as e:
        raise IOError(f"无法加载图片 {file_path}: {str(e)}")


def normalize_array(array: np.ndarray) -> np.ndarray:
    """
    标准化numpy数组到0-255范围并转换为uint8
    
    Args:
        array: 输入数组
        
    Returns:
        np.ndarray: 标准化后的uint8数组
    """
    if array.dtype != np.uint8:
        # 归一化到0-255范围
        array_min = array.min()
        array_max = array.max()
        
        if array_max > array_min:
            array = (array - array_min) / (array_max - array_min) * 255
        else:
            array = np.zeros_like(array)
        
        array = array.astype(np.uint8)
    
    return array