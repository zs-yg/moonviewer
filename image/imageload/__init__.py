"""
图片加载加速模块
使用numpy和Pillow加速图片加载和处理
"""

from .image_loader import ImageLoader
from .cache_manager import CacheManager
from .utils import (
    is_supported_image,
    get_image_info,
    convert_to_qimage,
    convert_to_qpixmap
)
from .numpy_processor import (
    fast_resize,
    rgb_to_grayscale,
    adjust_brightness_contrast,
    apply_gaussian_blur,
    normalize_histogram
)

__all__ = [
    'ImageLoader',
    'CacheManager',
    'is_supported_image',
    'get_image_info',
    'convert_to_qimage',
    'convert_to_qpixmap',
    'fast_resize',
    'rgb_to_grayscale',
    'adjust_brightness_contrast',
    'apply_gaussian_blur',
    'normalize_histogram'
]

__version__ = '1.0.0'