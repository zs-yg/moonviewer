"""
缓存管理模块
实现LRU缓存以提高图片加载性能
"""

import os
from typing import Any, Optional, Dict, Tuple
from collections import OrderedDict
import numpy as np


class CacheManager:
    """
    LRU缓存管理器
    用于缓存已加载的图片数据，提高重复加载性能
    """
    
    def __init__(self, max_size_mb: float = 100.0, max_items: int = 100):
        """
        初始化缓存管理器
        
        Args:
            max_size_mb: 最大缓存大小（MB）
            max_items: 最大缓存项目数
        """
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.max_items = max_items
        self.cache = OrderedDict()  # 使用OrderedDict实现LRU
        self.current_size_bytes = 0
        self.hits = 0
        self.misses = 0
        
    def _get_item_size(self, item: Any) -> int:
        """
        估算项目大小（字节）
        
        Args:
            item: 缓存项目
            
        Returns:
            int: 项目大小（字节）
        """
        if isinstance(item, np.ndarray):
            # numpy数组的大小
            return item.nbytes
        elif hasattr(item, 'nbytes'):
            # 其他有nbytes属性的对象
            return item.nbytes
        elif hasattr(item, '__sizeof__'):
            # 使用__sizeof__方法
            return item.__sizeof__()
        else:
            # 默认大小估计
            return 1024  # 1KB估计
    
    def _make_key(self, file_path: str, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            file_path: 文件路径
            **kwargs: 其他参数（如处理参数）
            
        Returns:
            str: 缓存键
        """
        # 使用文件路径和参数生成键
        key_parts = [file_path]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return "|".join(key_parts)
    
    def get(self, file_path: str, **kwargs) -> Optional[Any]:
        """
        从缓存获取项目
        
        Args:
            file_path: 文件路径
            **kwargs: 其他参数（如处理参数）
            
        Returns:
            Optional[Any]: 如果找到则返回缓存项目，否则返回None
        """
        key = self._make_key(file_path, **kwargs)
        
        if key in self.cache:
            # 命中缓存，将项目移到最前面（最近使用）
            item = self.cache.pop(key)
            self.cache[key] = item
            self.hits += 1
            return item
        else:
            self.misses += 1
            return None
    
    def put(self, file_path: str, item: Any, **kwargs) -> None:
        """
        将项目添加到缓存
        
        Args:
            file_path: 文件路径
            item: 要缓存的项目
            **kwargs: 其他参数（如处理参数）
        """
        key = self._make_key(file_path, **kwargs)
        item_size = self._get_item_size(item)
        
        # 如果项目太大，不缓存
        if item_size > self.max_size_bytes:
            return
        
        # 如果键已存在，先移除旧项目
        if key in self.cache:
            old_item = self.cache.pop(key)
            old_size = self._get_item_size(old_item)
            self.current_size_bytes -= old_size
        
        # 确保有足够空间
        while (self.current_size_bytes + item_size > self.max_size_bytes or 
               len(self.cache) >= self.max_items):
            if not self.cache:
                break
            # 移除最旧的项目（LRU）
            old_key, old_item = self.cache.popitem(last=False)
            old_size = self._get_item_size(old_item)
            self.current_size_bytes -= old_size
        
        # 添加新项目
        self.cache[key] = item
        self.current_size_bytes += item_size
    
    def clear(self) -> None:
        """清除所有缓存"""
        self.cache.clear()
        self.current_size_bytes = 0
        self.hits = 0
        self.misses = 0
    
    def remove(self, file_path: str, **kwargs) -> bool:
        """
        从缓存移除特定项目
        
        Args:
            file_path: 文件路径
            **kwargs: 其他参数
            
        Returns:
            bool: 如果成功移除则返回True
        """
        key = self._make_key(file_path, **kwargs)
        if key in self.cache:
            item = self.cache.pop(key)
            item_size = self._get_item_size(item)
            self.current_size_bytes -= item_size
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'current_size_bytes': self.current_size_bytes,
            'current_size_mb': self.current_size_bytes / (1024 * 1024),
            'max_size_bytes': self.max_size_bytes,
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'item_count': len(self.cache),
            'max_items': self.max_items
        }
    
    def get_memory_usage(self) -> Tuple[float, float]:
        """
        获取内存使用情况
        
        Returns:
            Tuple[float, float]: (当前使用量MB, 最大限制MB)
        """
        current_mb = self.current_size_bytes / (1024 * 1024)
        max_mb = self.max_size_bytes / (1024 * 1024)
        return current_mb, max_mb
    
    def __contains__(self, key: str) -> bool:
        """检查键是否在缓存中"""
        return key in self.cache
    
    def __len__(self) -> int:
        """返回缓存项目数"""
        return len(self.cache)
    
    def __repr__(self) -> str:
        """返回缓存的字符串表示"""
        stats = self.get_stats()
        return (f"CacheManager(items={stats['item_count']}, "
                f"size={stats['current_size_mb']:.2f}MB/{stats['max_size_mb']:.2f}MB, "
                f"hit_rate={stats['hit_rate']:.2%})")


# 全局默认缓存实例
_default_cache = CacheManager()


def get_default_cache() -> CacheManager:
    """
    获取全局默认缓存实例
    
    Returns:
        CacheManager: 默认缓存管理器
    """
    return _default_cache


def clear_default_cache() -> None:
    """清除全局默认缓存"""
    _default_cache.clear()


def get_default_cache_stats() -> Dict[str, Any]:
    """
    获取全局默认缓存的统计信息
    
    Returns:
        Dict[str, Any]: 统计信息字典
    """
    return _default_cache.get_stats()