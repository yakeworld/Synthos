"""meddata.com.cn full-text download source.

Supports two auth modes:
1. Direct token: set MEDDATA_TOKEN env var
2. Auto-login: set MEDDATA_USERNAME + MEDDATA_PASSWORD env vars

Auth flow: SSO login → bucToken → meddata token → viewtext PDF download

fileName format: {DOI_no_slash} (e.g. 10.3389fneur.2020.00602)
The fileName can be arbitrary; DOI_no_slash is a convenient convention.
"""
import logging, os, re
import requests as _req

logger = logging.getLogger(__name__)

BASE_URL = "http://www.meddata.com.cn"
SSO_URL = "https://uuct.medbooks.com.cn:9443/sso/login"
APP_URL = "http://app.meddata.com.cn:8878"

_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def _make_abstract_id(doi: str) -> str:
    """Convert DOI to meddata fileName.
    
    Format: {DOI_no_slash}
    e.g. DOI=10.3389/fneur.2020.00602
         → fileName=10.3389fneur.2020.00602
    
    Note: fileName can be any arbitrary string; DOI_no_slash is a convenient choice.
    The `doi` parameter in full_look must be the real DOI of the target paper.
    The `pmid` parameter in full_look can be any number.
    """
    return doi.replace('/', '')


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
        # Step 1: SSO login → bucToken
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
        
        # Step 2: Exchange bucToken → meddata token
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
    """
    Download full-text PDF from meddata.com.cn.
    
    Requires MEDDATA_TOKEN or MEDDATA_USERNAME+MEDDATA_PASSWORD.
    
    Primary: viewtext API (returns raw PDF)
    Fallback: full_look API → fileUrl
    
    Returns {'success': True, 'file': output_path} or None.
    """
    token = _get_token()
    if not token:
        logger.debug("meddata: no token available (set MEDDATA_TOKEN or MEDDATA_USERNAME)")
        return None
    
    abstract_id = _make_abstract_id(doi)
    headers = {"User-Agent": _USER_AGENT}
    
    try:
        # Primary path: viewtext (returns raw PDF)
        r = _req.get(f"{BASE_URL}/api/abstract/viewtext",
                    params={'fileName': abstract_id, 'token': token},
                    headers=headers, timeout=30)
        
        if r.status_code == 200 and r.content[:4] == b'%PDF':
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(r.content)
            logger.info(f"meddata: ✅ PDF ({len(r.content)} bytes)")
            return {'success': True, 'file': output_path, 'source': 'meddata', 'size': len(r.content)}
        
        # Fallback: try full_look API for fileUrl
        logger.debug(f"meddata viewtext returned HTTP {r.status_code}, trying full_look...")
        r2 = _req.get(f"{BASE_URL}/api/abstract/full_look",
                     params={'token': token, 'abstractId': abstract_id, 'pmid': '1', 'doi': doi},
                     headers=headers, timeout=15)
        
        if r2.status_code == 200:
            rd = r2.json().get('responseData', {})
            file_url = rd.get('fileUrl')
            if file_url:
                logger.info(f"meddata full_look: {file_url[:60]}...")
                r3 = _req.get(file_url, headers=headers, timeout=60)
                if r3.status_code == 200 and r3.content[:4] == b'%PDF':
                    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(r3.content)
                    logger.info(f"meddata: ✅ PDF via full_look ({len(r3.content)} bytes)")
                    return {'success': True, 'file': output_path, 'source': 'meddata-full_look', 'size': len(r3.content)}
        
    except Exception as e:
        logger.debug(f"meddata error: {e}")
    
    return None
