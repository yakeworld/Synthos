"""meddata.com.cn full-text download source.

Supports two auth modes:
1. Direct token: set MEDDATA_TOKEN env var
2. Auto-login: set MEDDATA_USERNAME + MEDDATA_PASSWORD env vars

Auth flow: SSO login → bucToken → meddata token → full_look申请 → viewtext下载

下载核心规律（2026-06-23 最终确认）:
  ① full_look(abstractId=随机11位号, pmid=真实PMID, doi=真实DOI)
     → 系统将全文复制到 abstractId 名下
  ② 等待 10 秒让系统处理
  ③ viewtext(fileName=abstractId) → 取回全文PDF

  abstractId = 任意唯一号（生成11位随机数），不能重复
  pmid       = 论文的真实PMID（不是固定值'1'）

滥用防护（2026-06-23 新增）:
  - 同一进程内连续调用间隔 >= 15 秒
  - 每24小时 <= 200 次尝试（自动计数，超限返回None）
  - 绝不自动重试失败的full_look
  - MedData是机构资源，仅作为最后降级通道
"""
import logging, os, re, time as _time
import requests as _req

logger = logging.getLogger(__name__)

BASE_URL = "http://www.meddata.com.cn"
SSO_URL = "https://uuct.medbooks.com.cn:9443/sso/login"
APP_URL = "http://app.meddata.com.cn:8878"

_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# ── 滥用防护 ─────────────────────────────────────────────────────────────
_LAST_CALL_TIME = 0.0
_CALL_COUNT_24H = 0
_CALL_COUNT_RESET = _time.time()
_MIN_INTERVAL = 15       # 最小间隔秒数
_MAX_CALLS_24H = 200     # 24小时上限
_MEDDATA_WARNED = False  # 只警告一次


def _check_abuse() -> bool:
    """检查是否超出速率限制。返回True=允许调用，False=拒绝。
    
    规则：
    - 连续调用间隔 ≥15秒
    - 每24小时 ≤200次
    """
    global _LAST_CALL_TIME, _CALL_COUNT_24H, _CALL_COUNT_RESET, _MEDDATA_WARNED

    now = _time.time()
    
    # 重置24小时计数
    if now - _CALL_COUNT_RESET > 86400:
        _CALL_COUNT_24H = 0
        _CALL_COUNT_RESET = now
        _MEDDATA_WARNED = False

    # 检查24小时上限
    if _CALL_COUNT_24H >= _MAX_CALLS_24H:
        if not _MEDDATA_WARNED:
            logger.warning(f"meddata: 24h call limit reached ({_MAX_CALLS_24H}), blocking further calls")
            _MEDDATA_WARNED = True
        return False

    # 检查最小间隔
    elapsed = now - _LAST_CALL_TIME
    if elapsed < _MIN_INTERVAL and _LAST_CALL_TIME > 0:
        wait = _MIN_INTERVAL - elapsed
        logger.debug(f"meddata: rate limit, waiting {wait:.1f}s")
        _time.sleep(wait)

    _LAST_CALL_TIME = _time.time()
    _CALL_COUNT_24H += 1
    return True


def _get_token() -> str:
    """Get a valid meddata token.

    Priority:
    1. MEDDATA_TOKEN env var (direct)
    2. MEDDATA_USERNAME + MEDDATA_PASSWORD (auto-login)
    """
    token = os.environ.get('MEDDATA_TOKEN', '')
    if token:
        return token

    username = os.environ.get('MEDDATA_USERNAME', '')
    password = os.environ.get('MEDDATA_PASSWORD', '')
    if not username or not password:
        return ''

    try:
        headers = {"User-Agent": _USER_AGENT, "Content-Type": "application/json"}
        r = _req.post(SSO_URL, json={
            "username": username, "password": password,
            "type": "0",
        }, headers=headers, timeout=15, verify=False)

        if r.status_code != 200:
            logger.warning(f"meddata SSO login failed: HTTP {r.status_code}")
            return ''

        data = r.json()
        if data.get('code') != '200':
            logger.warning(f"meddata SSO login failed: {data.get('message','?')}")
            return ''

        redirect_url = data['data']['url']
        buc_token = re.search(r'bucToken=([^&]+)', redirect_url)
        if not buc_token:
            logger.warning("meddata: no bucToken in SSO response")
            return ''
        buc_token = buc_token.group(1)

        r2 = _req.get(f"{APP_URL}/api/sso/user/login",
                     params={"bucToken": buc_token},
                     headers={"User-Agent": _USER_AGENT}, timeout=10)

        if r2.status_code != 200:
            logger.warning(f"meddata token exchange failed: HTTP {r2.status_code}")
            return ''

        data2 = r2.json()
        meddata_token = data2.get('responseData', '')
        if not meddata_token:
            logger.warning("meddata: no token in exchange response")
            return ''

        logger.info(f"meddata: auto-login success, token obtained")
        return meddata_token

    except Exception as e:
        logger.warning(f"meddata auto-login error: {e}")
        return ''


def try_meddata(doi: str, output_path: str, **kwargs) -> dict | None:
    """Download full-text PDF from meddata.com.cn.

    核心流程（两步不可省略）:
      1. full_look(abstractId=随机11位号, pmid=真实PMID, doi=DOI)
         → 系统把全文复制到 abstractId 名下
      2. 等待 10秒 → viewtext(fileName=abstractId) → 取回PDF

    前置快速尝试（不保证成功）:
      - PMID 直接作为 fileName
      - DOI_NO_SLASH 直接作为 fileName

    Args:
        doi: 论文DOI
        output_path: PDF保存路径
        **kwargs: 可传 extra={'pmid': '真实PMID'}

    Returns:
        {'success': True, 'file': output_path, 'source': ..., 'size': ...} or None
    """
    token = _get_token()
    if not token:
        logger.debug("meddata: no token available")
        return None

    # ── 滥用检查 ──────────────────────────────────────────────────────
    if not _check_abuse():
        logger.warning(f"meddata: rate limited, skipping {doi[:45]}")
        return None

    headers = {"User-Agent": _USER_AGENT}

    # ── 从 kwargs 提取 PMID ───────────────────────────────────────────
    _pmid_from_kwargs = None
    extra_val = kwargs.get('extra', None)
    if isinstance(extra_val, dict):
        _pmid_from_kwargs = extra_val.get('pmid')
    elif extra_val:
        pmid_match = re.search(r'pmid[=_ \'](\d+)', str(extra_val))
        if pmid_match:
            _pmid_from_kwargs = pmid_match.group(1)

    PH = "fd469bd7cd29446f2800f099e3b71457"

    def _try_viewtext(fname: str) -> dict | None:
        r = _req.get(f"{BASE_URL}/api/abstract/viewtext",
                    params={'fileName': fname, 'token': token},
                    headers=headers, timeout=30)
        if r.status_code == 200 and r.content[:4] == b'%PDF':
            import hashlib
            if hashlib.md5(r.content).hexdigest() == PH:
                logger.debug(f"meddata viewtext({fname[:30]}...): placeholder PDF")
                return None
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(r.content)
            logger.info(f"meddata: PDF ({len(r.content)} bytes)")
            return {'success': True, 'file': output_path, 'source': 'meddata', 'size': len(r.content)}
        return None

    # Step 0: PMID 直试
    if _pmid_from_kwargs:
        result = _try_viewtext(_pmid_from_kwargs)
        if result:
            return result

    # Step 1: DOI_NO_SLASH 直试
    result = _try_viewtext(doi.replace('/', ''))
    if result:
        return result

    # Step 2: full_look 核心流程
    import hashlib as _hl, random as _random
    try:
        lookup_id = str(_random.randint(10000000000, 99999999999))
        real_pmid = _pmid_from_kwargs if _pmid_from_kwargs else '1'

        logger.info(f"meddata full_look: abstractId={lookup_id}, pmid={real_pmid}")
        r2 = _req.get(f"{BASE_URL}/api/abstract/full_look",
                     params={'token': token, 'abstractId': lookup_id,
                             'pmid': real_pmid, 'doi': doi},
                     headers=headers, timeout=15)
        if r2.status_code == 200:
            rd = r2.json().get('responseData', {})
            logger.info(f"meddata full_look: status={rd.get('status')}")

            _time.sleep(10)

            r3 = _req.get(f"{BASE_URL}/api/abstract/viewtext",
                         params={'fileName': lookup_id, 'token': token},
                         headers=headers, timeout=60)
            if r3.status_code == 200 and r3.content[:4] == b'%PDF':
                if _hl.md5(r3.content).hexdigest() != PH:
                    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(r3.content)
                    logger.info(f"meddata: PDF via full_look ({len(r3.content)} bytes)")
                    return {'success': True, 'file': output_path,
                            'source': 'meddata-full_look', 'size': len(r3.content)}

            file_url = rd.get('fileUrl')
            if file_url:
                r4 = _req.get(file_url, headers=headers, timeout=60)
                if r4.status_code == 200 and r4.content[:4] == b'%PDF':
                    if _hl.md5(r4.content).hexdigest() != PH:
                        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(r4.content)
                        logger.info(f"meddata: PDF via fileUrl ({len(r4.content)} bytes)")
                        return {'success': True, 'file': output_path,
                                'source': 'meddata-fileUrl', 'size': len(r4.content)}
    except Exception as e:
        logger.debug(f"meddata full_look error: {e}")

    return None
