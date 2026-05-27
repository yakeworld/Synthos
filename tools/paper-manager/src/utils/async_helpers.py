import asyncio
import logging
from typing import List, Any, Callable, Coroutine
from functools import wraps

logger = logging.getLogger(__name__)

def _flatten(lst):
    """扁平化嵌套列表"""
    for x in lst:
        if isinstance(x, list):
            yield from _flatten(x)
        else:
            yield x


async def run_with_semaphore(semaphore: asyncio.Semaphore, coro: Coroutine) -> Any:
    """
    使用信号量运行协程
    
    Args:
        semaphore: 信号量
        coro: 协程
        
    Returns:
        协程结果
    """
    async with semaphore:
        return await coro


async def batch_process(
    items: List[Any], 
    process_func: Callable[[Any], Coroutine], 
    batch_size: int = 10,
    max_concurrent: int = 5
) -> List[Any]:
    """
    批量处理项目
    
    Args:
        items: 项目列表
        process_func: 处理函数
        batch_size: 批次大小
        max_concurrent: 最大并发数
        
    Returns:
        处理结果列表
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        tasks = [run_with_semaphore(semaphore, process_func(item)) for item in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(batch_results)
        
        # 批次间短暂停顿，防止API限流
        if i + batch_size < len(items):
            await asyncio.sleep(0.1)
    
    return results


def async_retry(max_attempts: int = 3, delay: float = 1.0):
    """
    异步重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 重试延迟（秒）
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay * (attempt + 1))  # 指数退避
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
            raise last_exception
        return wrapper
    return decorator


async def timeout_after(timeout: float, coro: Coroutine) -> Any:
    """
    为协程设置超时
    
    Args:
        timeout: 超时时间（秒）
        coro: 协程
        
    Returns:
        协程结果
        
    Raises:
        asyncio.TimeoutError: 超时时抛出
    """
    return await asyncio.wait_for(coro, timeout)


class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.tasks = []
    
    async def add_task(self, coro: Coroutine) -> Any:
        """添加任务并等待结果"""
        async with self.semaphore:
            return await coro
    
    async def add_tasks(self, coros: List[Coroutine]) -> List[Any]:
        """批量添加任务并等待结果"""
        tasks = [self.add_task(coro) for coro in coros]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def create_task(self, coro: Coroutine) -> asyncio.Task:
        """创建任务但不立即等待"""
        task = asyncio.create_task(self.add_task(coro))
        self.tasks.append(task)
        return task
    
    async def wait_all(self) -> List[Any]:
        """等待所有任务完成"""
        if not self.tasks:
            return []
        results = await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
        return results


async def progress_callback_wrapper(
    items: List[Any],
    process_func: Callable[[Any, int, int], Coroutine],
    callback: Callable[[int, int, str], None] = None
) -> List[Any]:
    """
    带进度回调的包装器
    
    Args:
        items: 项目列表
        process_func: 处理函数，接受(item, index, total)参数
        callback: 进度回调函数，接受(current, total, message)参数
        
    Returns:
        处理结果列表
    """
    results = []
    total = len(items)
    
    for index, item in enumerate(items):
        if callback:
            callback(index, total, f"Processing item {index + 1}/{total}")
        
        result = await process_func(item, index, total)
        results.append(result)
    
    if callback:
        callback(total, total, "Processing complete")
    
    return results


def sync_to_async(func: Callable) -> Callable:
    """
    将同步函数转换为异步函数
    
    Args:
        func: 同步函数
        
    Returns:
        异步函数
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper