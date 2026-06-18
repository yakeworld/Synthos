#!/usr/bin/env python3
"""MedData 3-step download with CORRECT workflow (app.meddata.com.cn:8878).

Usage: python3 meddata-correct-download.py <DOI_NO_SLASH> <DOI> <output.pdf>

Example: python3 meddata-correct-download.py 10.3389fneur.2020.00602 10.3389/fneur.2020.00602 output.pdf
"""
import subprocess
import hashlib
import json
import os
import sys
import time

PLACEHOLDER_MD5 = "fd469bd7cd29446f2800f099e3b71457"

def meddata_download(doi_no_slash, doi, output_pdf):
    """Complete 3-step MedData download."""
    
    # Step 1: SSO login
    sso = subprocess.run(
        ["curl", "-s", "-X", "POST", "https://uuct.medbooks.com.cn:9443/sso/login",
         "-H", "Content-Type: application/json",
         '-d', '{"username":"MEDDATA_USERNAME_PLACEHOLDER","password":"MEDDATA_PASSWORD_PLACEHOLDER","type":"0"}'],
        capture_output=True, text=True, timeout=10
    )
    sso_data = json.loads(sso.stdout)
    if sso_data.get("code") != "200":
        print(f"SSO FAILED: {sso_data}")
        return False
    buc_token = sso_data["data"]["url"].split("bucToken=")[1]
    
    # Step 2: Token exchange
    time.sleep(0.5)
    token_resp = subprocess.run(
        ["curl", "-s", f"http://www.meddata.com.cn/api/sso/user/login?bucToken={buc_token}"],
        capture_output=True, text=True, timeout=10
    )
    token_data = json.loads(token_resp.stdout)
    token = token_data.get("responseData", "")
    if not token:
        print("TOKEN EXCHANGE FAILED")
        return False
    
    # Step 3: full_look (CORRECT: access responseData.fileName)
    fl_result = subprocess.run(
        [f'curl -s "http://www.meddata.com.cn/api/abstract/full_look?token={token}&abstractId={doi_no_slash}&pmid=1&doi={doi}"'],
        shell=True, capture_output=True, text=True, timeout=10
    )
    fl_data = json.loads(fl_result.stdout)
    # CRITICAL: fileName is nested under responseData
    fname = fl_data.get("responseData", {}).get("fileName", "")
    fstatus = fl_data.get("responseData", {}).get("status")
    
    if not fname:
        print(f"NO FILENAME from full_look (status={fstatus})")
        return False
    
    # Small delay before viewtext
    time.sleep(1)
    
    # Step 4: viewtext (CORRECT: app.meddata.com.cn:8878)
    vt_url = f"http://app.meddata.com.cn:8878/api/abstract/viewtext?fileName={fname}&token={token}"
    vt_result = subprocess.run(
        ["curl", "-s", "-o", output_pdf, vt_url, "-H", "User-Agent: Mozilla/5.0"],
        capture_output=True, text=True, timeout=30
    )
    
    if not os.path.exists(output_pdf):
        print("NO FILE CREATED")
        return False
    
    # Verify
    sz = os.path.getsize(output_pdf)
    with open(output_pdf, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    
    is_placeholder = md5 == PLACEHOLDER_MD5
    is_pdf = open(output_pdf, 'rb').read()[:4] == b'%PDF'
    
    if is_placeholder:
        print(f"PLACEHOLDER {sz}B md5={md5}")
        return False
    elif not is_pdf:
        print(f"NOT PDF {sz}B md5={md5}")
        return False
    else:
        print(f"SUCCESS {sz}B md5={md5}")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <DOI_NO_SLASH> <DOI> <OUTPUT_PDF>")
        sys.exit(1)
    
    success = meddata_download(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)
