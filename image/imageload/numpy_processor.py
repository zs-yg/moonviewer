"""
numpy图片处理模块
使用numpy进行高效的图片处理操作
"""

import numpy as np
from typing import Tuple, Optional, Union
from PIL import Image, ImageOps


def resize_nearest_neighbor(
    image_array: np.ndarray,
    target_size: Tuple[int, int]
) -> np.ndarray:
    """
    使用最近邻插值缩放图片数组
    
    Args:
        image_array: 输入图片数组，形状为 (height, width, channels)
        target_size: 目标尺寸 (width, height)
        
    Returns:
        np.ndarray: 缩放后的图片数组
    """
    if len(image_array.shape) != 3:
        raise ValueError("输入数组必须是3维 (height, width, channels)")
    
    height, width, channels = image_array.shape
    target_width, target_height = target_size
    
    # 计算缩放比例
    x_ratio = width / target_width
    y_ratio = height / target_height
    
    # 创建输出数组
    output = np.zeros((target_height, target_width, channels), dtype=image_array.dtype)
    
    # 最近邻插值
    for y in range(target_height):
        for x in range(target_width):
            src_x = int(x * x_ratio)
            src_y = int(y * y_ratio)
            output[y, x] = image_array[src_y, src_x]
    
    return output


def resize_bilinear(
    image_array: np.ndarray,
    target_size: Tuple[int, int]
) -> np.ndarray:
    """
    使用双线性插值缩放图片数组
    
    Args:
        image_array: 输入图片数组，形状为 (height, width, channels)
        target_size: 目标尺寸 (width, height)
        
    Returns:
        np.ndarray: 缩放后的图片数组
    """
    if len(image_array.shape) != 3:
        raise ValueError("输入数组必须是3维 (height, width, channels)")
    
    height, width, channels = image_array.shape
    target_width, target_height = target_size
    
    # 计算缩放比例
    x_ratio = (width - 1) / target_width if target_width > 1 else 0
    y_ratio = (height - 1) / target_height if target_height > 1 else 0
    
    # 创建输出数组
    output = np.zeros((target_height, target_width, channels), dtype=image_array.dtype)
    
    # 双线性插值
    for y in range(target_height):
        for x in range(target_width):
            x_low = int(x * x_ratio)
            y_low = int(y * y_ratio)
            x_high = min(x_low + 1, width - 1)
            y_high = min(y_low + 1, height - 1)
            
            x_weight = (x * x_ratio) - x_low
            y_weight = (y * y_ratio) - y_low
            
            # 四个角点
            a = image_array[y_low, x_low]
            b = image_array[y_low, x_high]
            c = image_array[y_high, x_low]
            d = image_array[y_high, x_high]
            
            # 双线性插值
            output[y, x] = (
                a * (1 - x_weight) * (1 - y_weight) +
                b * x_weight * (1 - y_weight) +
                c * (1 - x_weight) * y_weight +
                d * x_weight * y_weight
            ).astype(image_array.dtype)
    
    return output


def fast_resize(
    image_array: np.ndarray,
    target_size: Tuple[int, int],
    method: str = 'bilinear'
) -> np.ndarray:
    """
    快速缩放图片数组，使用numpy向量化操作
    
    Args:
        image_array: 输入图片数组
        target_size: 目标尺寸 (width, height)
        method: 缩放方法，'nearest' 或 'bilinear'
        
    Returns:
        np.ndarray: 缩放后的图片数组
    """
    if method == 'nearest':
        return resize_nearest_neighbor(image_array, target_size)
    elif method == 'bilinear':
        return resize_bilinear(image_array, target_size)
    else:
        raise ValueError(f"不支持的缩放方法: {method}")


def rgb_to_grayscale(image_array: np.ndarray) -> np.ndarray:
    """
    将RGB图片数组转换为灰度图
    
    Args:
        image_array: RGB图片数组，形状为 (height, width, 3)
        
    Returns:
        np.ndarray: 灰度图片数组，形状为 (height, width)
    """
    if len(image_array.shape) != 3 or image_array.shape[2] != 3:
        raise ValueError("输入数组必须是RGB格式 (height, width, 3)")
    
    # 使用标准灰度转换公式: Y = 0.299R + 0.587G + 0.114B
    grayscale = np.dot(image_array[..., :3], [0.299, 0.587, 0.114])
    return grayscale.astype(image_array.dtype)


def adjust_brightness_contrast(
    image_array: np.ndarray,
    brightness: float = 0.0,
    contrast: float = 1.0
) -> np.ndarray:
    """
    调整图片的亮度和对比度
    
    Args:
        image_array: 输入图片数组
        brightness: 亮度调整值 (-1.0 到 1.0)
        contrast: 对比度调整值 (0.0 到 2.0)
        
    Returns:
        np.ndarray: 调整后的图片数组
    """
    # 确保值在合理范围内
    brightness = max(-1.0, min(1.0, brightness))
    contrast = max(0.0, min(2.0, contrast))
    
    # 转换为浮点数进行计算
    if image_array.dtype != np.float32:
        image_float = image_array.astype(np.float32) / 255.0
    else:
        image_float = image_array.copy()
    
    # 调整对比度
    if contrast != 1.0:
        image_float = (image_float - 0.5) * contrast + 0.5
    
    # 调整亮度
    if brightness != 0.0:
        image_float = image_float + brightness
    
    # 裁剪到 [0, 1] 范围
    image_float = np.clip(image_float, 0.0, 1.0)
    
    # 转换回原始数据类型
    if image_array.dtype != np.float32:
        result = (image_float * 255.0).astype(image_array.dtype)
    else:
        result = image_float
    
    return result


def apply_gaussian_blur(
    image_array: np.ndarray,
    kernel_size: int = 3,
    sigma: float = 1.0
) -> np.ndarray:
    """
    应用高斯模糊
    
    Args:
        image_array: 输入图片数组
        kernel_size: 卷积核大小（奇数）
        sigma: 高斯核的标准差
        
    Returns:
        np.ndarray: 模糊后的图片数组
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # 确保是奇数
    
    # 创建高斯核
    ax = np.arange(-kernel_size // 2 + 1., kernel_size // 2 + 1.)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2. * sigma**2))
    kernel = kernel / np.sum(kernel)
    
    # 对每个通道应用卷积
    if len(image_array.shape) == 3:
        result = np.zeros_like(image_array)
        for c in range(image_array.shape[2]):
            result[:, :, c] = convolve2d(image_array[:, :, c], kernel, mode='same')
    else:
        result = convolve2d(image_array, kernel, mode='same')
    
    return result.astype(image_array.dtype)


def convolve2d(image: np.ndarray, kernel: np.ndarray, mode: str = 'same') -> np.ndarray:
    """
    2D卷积实现
    
    Args:
        image: 输入图像
        kernel: 卷积核
        mode: 卷积模式
        
    Returns:
        np.ndarray: 卷积结果
    """
    # 简单的2D卷积实现（对于小核足够快）
    kernel_height, kernel_width = kernel.shape
    image_height, image_width = image.shape
    
    pad_height = kernel_height // 2
    pad_width = kernel_width // 2
    
    # 填充图像
    padded = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='edge')
    
    # 执行卷积
    result = np.zeros_like(image)
    for y in range(image_height):
        for x in range(image_width):
            region = padded[y:y + kernel_height, x:x + kernel_width]
            result[y, x] = np.sum(region * kernel)
    
    return result


def normalize_histogram(image_array: np.ndarray) -> np.ndarray:
    """
    直方图均衡化
    
    Args:
        image_array: 输入图片数组
        
    Returns:
        np.ndarray: 均衡化后的图片数组
    """
    if len(image_array.shape) == 3:
        # 对每个通道分别进行直方图均衡化
        result = np.zeros_like(image_array)
        for c in range(image_array.shape[2]):
            channel = image_array[:, :, c]
            hist, bins = np.histogram(channel.flatten(), 256, [0, 256])
            cdf = hist.cumsum()
            cdf_normalized = cdf * 255 / cdf[-1]
            result[:, :, c] = np.interp(channel.flatten(), bins[:-1], cdf_normalized).reshape(channel.shape)
    else:
        # 灰度图
        hist, bins = np.histogram(image_array.flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        cdf_normalized = cdf * 255 / cdf[-1]
        result = np.interp(image_array.flatten(), bins[:-1], cdf_normalized).reshape(image_array.shape)
    
    return result.astype(image_array.dtype)