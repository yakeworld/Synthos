"""Parallel racing engine — try multiple sources concurrently, first success wins."""
import logging, time, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

# Source function signature: fn(doi: str, output_path: str, **kwargs) -> dict or None
SourceFn = Callable[..., Optional[dict]]

def race_sources(
    doi: str,
    output_path: str,
    tier_sources: List[Tuple[SourceFn, str]],
    timeout: int = 15,
    pool_size: int = 5,
    **kwargs
) -> Optional[dict]:
    """
    Race multiple sources in parallel.
    Returns the first successful result or None.
    
    Args:
        doi: DOI to download
        output_path: where to save the PDF
        tier_sources: list of (function, label) tuples
        timeout: max seconds to wait for all sources
        pool_size: max parallel workers
        **kwargs: extra args passed to each source function
    """
    if not tier_sources:
        return None
    
    if len(tier_sources) == 1:
        fn, label = tier_sources[0]
        logger.info(f"  [{label}] Trying single source...")
        try:
            result = fn(doi, output_path, **kwargs)
            if result and result.get('success'):
                logger.info(f"  ✅ {label}")
                return result
        except Exception as e:
            logger.warning(f"  ❌ {label}: {e}")
        return None
    
    logger.info(f"  Racing {len(tier_sources)} sources ({timeout}s timeout)...")
    results = {}
    with ThreadPoolExecutor(max_workers=min(pool_size, len(tier_sources))) as pool:
        futures = {}
        for fn, label in tier_sources:
            futures[pool.submit(_try_source, fn, doi, output_path, label, **kwargs)] = label
        
        try:
            for future in as_completed(futures, timeout=timeout):
                label = futures[future]
                try:
                    result = future.result(timeout=1)
                except Exception:
                    result = None
                
                if result and result.get('success'):
                    logger.info(f"  ✅ {label} wins")
                    # Cancel remaining futures
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    return result
                else:
                    logger.info(f"  ❌ {label}")
        except TimeoutError:
            logger.info(f"  ⏱ Timeout after {timeout}s")
    
    return None

def _try_source(fn, doi, output_path, label, **kwargs):
    """Wrapper to catch and log exceptions per source."""
    try:
        return fn(doi, output_path, **kwargs)
    except Exception as e:
        logger.debug(f"  {label} error: {e}")
        return None

def build_download_tiers(doi: str) -> List[Tuple[List[Tuple[SourceFn, str]], str, int]]:
    """
    Build tier structure:
    [(tier_sources, label, timeout), ...]
    
    Tiers run sequentially; sources within a tier run in parallel.
    """
    from sources.scihub_racing import try_scihub_curl
    from sources.libgen import try_libgen
    from sources.meddata import try_meddata
    
    tiers = []
    
    # Tier 1: Fastest — Sci-Hub via curl_cffi (usually 3-5s)
    tier1 = [(try_scihub_curl, "SciHub-curl")]
    tiers.append((tier1, "Fast (curl_cffi)", 15))
    
    # Tier 2: LibGen
    tier2 = [(try_libgen, "LibGen")]
    tiers.append((tier2, "LibGen", 20))
    
    # Tier 3: meddata.com.cn (Chinese medical data platform, requires MEDDATA_TOKEN)
    tier3 = [(try_meddata, "MedData")]
    tiers.append((tier3, "MedData", 20))
    
    return tiers
