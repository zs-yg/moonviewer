"""
主图片加载器模块
提供使用numpy加速的图片加载功能
"""

import os
from pathlib import Path
from typing import Optional, Tuple, Union, Dict, Any
import numpy as np
from PIL import Image

from .utils import (
    is_supported_image,
    get_image_info,
    convert_to_qimage,
    convert_to_qpixmap,
    load_pil_image,
    normalize_array
)
from .numpy_processor import (
    fast_resize,
    rgb_to_grayscale,
    adjust_brightness_contrast,
    apply_gaussian_blur,
    normalize_histogram
)
from .cache_manager import CacheManager, get_default_cache


class ImageLoader:
    """
    图片加载器类
    使用numpy和Pillow加速图片加载和处理
    """
    
    def __init__(self, cache: Optional[CacheManager] = None):
        """
        初始化图片加载器
        
        Args:
            cache: 缓存管理器实例，如果为None则使用默认缓存
        """
        self.cache = cache if cache is not None else get_default_cache()
        
    def load_as_array(
        self,
        file_path: Union[str, Path],
        target_size: Optional[Tuple[int, int]] = None,
        resize_method: str = 'bilinear',
        convert_to_rgb: bool = True,
        use_cache: bool = True
    ) -> np.ndarray:
        """
        加载图片为numpy数组
        
        Args:
            file_path: 图片文件路径
            target_size: 目标尺寸 (width, height)，如果为None则保持原尺寸
            resize_method: 缩放方法，'nearest' 或 'bilinear'
            convert_to_rgb: 是否转换为RGB格式
            use_cache: 是否使用缓存
            
        Returns:
            np.ndarray: 图片数组
            
        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果文件不是支持的图片格式
            IOError: 如果无法加载图片
        """
        file_path = str(file_path)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 检查是否为支持的图片格式
        if not is_supported_image(file_path):
            raise ValueError(f"不支持的图片格式: {file_path}")
        
        # 生成缓存键
        cache_key_kwargs = {
            'target_size': target_size,
            'resize_method': resize_method,
            'convert_to_rgb': convert_to_rgb
        }
        
        # 尝试从缓存获取
        if use_cache:
            cached = self.cache.get(file_path, **cache_key_kwargs)
            if cached is not None:
                return cached.copy()  # 返回副本以避免修改缓存数据
        
        try:
            # 使用Pillow加载图片
            pil_image = load_pil_image(file_path)
            
            # 转换为RGB（如果需要）
            if convert_to_rgb:
                if pil_image.mode == 'RGBA':
                    # 保持RGBA格式
                    pass
                elif pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
            
            # 转换为numpy数组
            image_array = np.array(pil_image)
            
            # 缩放图片（如果需要）
            if target_size is not None:
                image_array = fast_resize(image_array, target_size, resize_method)
            
            # 添加到缓存
            if use_cache:
                self.cache.put(file_path, image_array.copy(), **cache_key_kwargs)
            
            return image_array
            
        except Exception as e:
            raise IOError(f"无法加载图片 {file_path}: {str(e)}")
    
    def load_as_qimage(
        self,
        file_path: Union[str, Path],
        target_size: Optional[Tuple[int, int]] = None,
        resize_method: str = 'bilinear',
        convert_to_rgb: bool = True,
        use_cache: bool = True
    ) -> 'QImage':
        """
        加载图片为QImage
        
        Args:
            file_path: 图片文件路径
            target_size: 目标尺寸 (width, height)
            resize_method: 缩放方法
            convert_to_rgb: 是否转换为RGB格式
            use_cache: 是否使用缓存
            
        Returns:
            QImage: 图片对象
        """
        # 加载为numpy数组
        image_array = self.load_as_array(
            file_path, target_size, resize_method, convert_to_rgb, use_cache
        )
        
        # 转换为QImage
        return convert_to_qimage(image_array)
    
    def load_as_qpixmap(
        self,
        file_path: Union[str, Path],
        target_size: Optional[Tuple[int, int]] = None,
        resize_method: str = 'bilinear',
        convert_to_rgb: bool = True,
        use_cache: bool = True
    ) -> 'QPixmap':
        """
        加载图片为QPixmap
        
        Args:
            file_path: 图片文件路径
            target_size: 目标尺寸 (width, height)
            resize_method: 缩放方法
            convert_to_rgb: 是否转换为RGB格式
            use_cache: 是否使用缓存
            
        Returns:
            QPixmap: 图片对象
        """
        # 加载为numpy数组
        image_array = self.load_as_array(
            file_path, target_size, resize_method, convert_to_rgb, use_cache
        )
        
        # 转换为QPixmap
        return convert_to_qpixmap(image_array)
    
    def process_image(
        self,
        image_array: np.ndarray,
        operations: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """
        对图片数组进行处理
        
        Args:
            image_array: 输入图片数组
            operations: 处理操作字典，键为操作名，值为参数
            
        Returns:
            np.ndarray: 处理后的图片数组
        """
        if operations is None:
            return image_array.copy()
        
        result = image_array.copy()
        
        for operation, params in operations.items():
            if operation == 'resize' and isinstance(params, tuple):
                # 调整大小
                result = fast_resize(result, params)
                
            elif operation == 'grayscale':
                # 转换为灰度图
                if len(result.shape) == 3 and result.shape[2] == 3:
                    result = rgb_to_grayscale(result)
                    # 将单通道转换为3通道以便后续处理
                    result = np.stack([result, result, result], axis=2)
                    
            elif operation == 'brightness_contrast':
                # 调整亮度和对比度
                brightness = params.get('brightness', 0.0)
                contrast = params.get('contrast', 1.0)
                result = adjust_brightness_contrast(result, brightness, contrast)
                
            elif operation == 'gaussian_blur':
                # 高斯模糊
                kernel_size = params.get('kernel_size', 3)
                sigma = params.get('sigma', 1.0)
                result = apply_gaussian_blur(result, kernel_size, sigma)
                
            elif operation == 'histogram_equalization':
                # 直方图均衡化
                result = normalize_histogram(result)
                
            elif operation == 'normalize':
                # 标准化
                result = normalize_array(result)
        
        return result
    
    def get_image_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        获取图片信息
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            Dict[str, Any]: 图片信息字典
        """
        return get_image_info(file_path)
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 缓存统计信息
        """
        return self.cache.get_stats()
    
    def preload_images(
        self,
        file_paths: list,
        target_size: Optional[Tuple[int, int]] = None,
        max_workers: Optional[int] = None
    ) -> None:
        """
        预加载多个图片到缓存
        
        Args:
            file_paths: 图片文件路径列表
            target_size: 目标尺寸
            max_workers: 最大工作线程数，如果为None则使用单线程
        """
        # 简单实现：顺序预加载
        # 在实际应用中可以使用多线程/多进程加速
        for file_path in file_paths:
            try:
                self.load_as_array(
                    file_path,
                    target_size=target_size,
                    use_cache=True
                )
            except Exception as e:
                print(f"预加载图片失败 {file_path}: {str(e)}")


# 全局默认加载器实例
_default_loader = ImageLoader()


def get_default_loader() -> ImageLoader:
    """
    获取全局默认图片加载器
    
    Returns:
        ImageLoader: 默认图片加载器
    """
    return _default_loader


def load_image(
    file_path: Union[str, Path],
    as_format: str = 'qpixmap',
    **kwargs
) -> Union[np.ndarray, 'QImage', 'QPixmap']:
    """
    快速加载图片的便捷函数
    
    Args:
        file_path: 图片文件路径
        as_format: 返回格式，可选 'array', 'qimage', 'qpixmap'
        **kwargs: 传递给ImageLoader.load_*方法的参数
        
    Returns:
        根据as_format返回相应格式的图片
        
    Raises:
        ValueError: 如果as_format不是有效的格式
    """
    loader = get_default_loader()
    
    if as_format == 'array':
        return loader.load_as_array(file_path, **kwargs)
    elif as_format == 'qimage':
        return loader.load_as_qimage(file_path, **kwargs)
    elif as_format == 'qpixmap':
        return loader.load_as_qpixmap(file_path, **kwargs)
    else:
        raise ValueError(f"不支持的格式: {as_format}，可选 'array', 'qimage', 'qpixmap'")