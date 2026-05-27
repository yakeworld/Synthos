"""
API响应缓存

提供基于文件的API响应缓存，避免重复请求
支持：
- 自动缓存和读取
- TTL（Time To Live）过期
- 缓存大小限制
- 手动清除
"""

import os
import json
import hashlib
import time
import logging
from typing import Optional, Any, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class APICache:
    """
    基于文件的API响应缓存
    
    使用：
        cache = APICache(cache_dir="./api_cache")
        
        # 读取缓存
        result = cache.get("search:ADHD:eye:tracking")
        
        # 写入缓存
        cache.set("search:ADHD:eye:tracking", data, ttl=3600)
        
        # 清除缓存
        cache.clear()
    """
    
    def __init__(
        self,
        cache_dir: str = "./api_cache",
        default_ttl: int = 3600,  # 默认1小时
        max_size_mb: int = 100,    # 最大100MB
        enabled: bool = True
    ):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.max_size_mb = max_size_mb
        self.enabled = enabled
        
        # 创建缓存目录
        if enabled:
            os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """生成缓存文件路径"""
        # 使用hash作为文件名，避免文件系统限制
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.json")
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        从缓存读取数据
        
        Args:
            key: 缓存键
            ttl: 超时时间（秒）
            
        Returns:
            缓存数据，不存在或过期返回None
        """
        if not self.enabled:
            return None
        
        try:
            cache_path = self._get_cache_key(key)
            if not os.path.exists(cache_path):
                return None
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否过期
            current_time = time.time()
            stored_ttl = ttl or self.default_ttl
            if current_time - data.get('timestamp', 0) > stored_ttl:
                logger.debug(f"Cache expired for key: {key}")
                os.remove(cache_path)
                return None
            
            return data.get('data')
        
        except Exception as e:
            logger.error(f"Cache read error for {key}: {e}")
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        写入缓存
        
        Args:
            key: 缓存键
            data: 数据
            ttl: 超时时间（秒）
            
        Returns:
            是否写入成功
        """
        if not self.enabled:
            return False
        
        try:
            cache_path = self._get_cache_key(key)
            
            cache_entry = {
                'data': data,
                'timestamp': time.time(),
                'ttl': ttl or self.default_ttl
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, ensure_ascii=False, default=str)
            
            logger.debug(f"Cache set for key: {key}")
            return True
        
        except Exception as e:
            logger.error(f"Cache write error for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        try:
            cache_path = self._get_cache_key(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                logger.debug(f"Cache deleted for key: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Cache delete error for {key}: {e}")
            return False
    
    def clear(self) -> int:
        """
        清除所有缓存
        
        Returns:
            删除的文件数
        """
        try:
            if not os.path.exists(self.cache_dir):
                return 0
            
            count = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
                    count += 1
            
            logger.info(f"Cleared {count} cache files")
            return count
        
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def cleanup(self) -> int:
        """
        清理过期缓存
        
        Returns:
            删除的文件数
        """
        try:
            if not os.path.exists(self.cache_dir):
                return 0
            
            count = 0
            current_time = time.time()
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(cache_path, 'r') as f:
                            data = json.load(f)
                        
                        if current_time - data.get('timestamp', 0) > data.get('ttl', self.default_ttl):
                            os.remove(cache_path)
                            count += 1
                    
                    except:
                        os.remove(cache_path)
                        count += 1
            
            logger.info(f"Cleaned up {count} expired cache files")
            return count
        
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            return 0
    
    def get_size(self) -> int:
        """获取缓存大小（MB）"""
        try:
            if not os.path.exists(self.cache_dir):
                return 0
            
            total_size = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    total_size += os.path.getsize(cache_path)
            
            return total_size / (1024 * 1024)
        
        except Exception as e:
            logger.error(f"Cache size error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            if not os.path.exists(self.cache_dir):
                return {
                    'total_files': 0,
                    'total_size_mb': 0,
                    'max_size_mb': self.max_size_mb
                }
            
            total_files = 0
            total_size = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    total_files += 1
                    total_size += os.path.getsize(cache_path)
            
            return {
                'total_files': total_files,
                'total_size_mb': total_size / (1024 * 1024),
                'max_size_mb': self.max_size_mb
            }
        
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {}
    
    def should_refresh(self, key: str, force: bool = False) -> bool:
        """
        判断是否需要刷新缓存
        
        Args:
            key: 缓存键
            force: 是否强制刷新
            
        Returns:
            True表示需要刷新
        """
        if force:
            return True
        
        return self.get(key) is None