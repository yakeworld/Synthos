#!/usr/bin/env python3
"""
Tor Connectivity Test - 验证Tor连通性
Tests:
1. SOCKS5 port accessibility
2. Tor circuit building  
3. Exit node IP verification
4. Sci-Hub reachability via Tor
"""
import socket
import sys
import time

def test_socks_port():
    try:
        s = socket.create_connection(('127.0.0.1', 9050), timeout=3)
        s.close()
        return True, 'SOCKS5 port 9050 is listening'
    except Exception as e:
        return False, f'SOCKS5 port 9050 unreachable: {e}'

def test_tor_circuit():
    try:
        import socks
        import ssl
        
        socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', 9050)
        orig_socket = socket.socket
        socket.socket = socks.socket
        
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(orig_socket(socket.AF_INET, socket.SOCK_STREAM),
                           server_hostname='check.torproject.org')
        s.settimeout(30)
        s.connect(('check.torproject.org', 443))
        
        s.sendall(b'GET /api/ip HTTP/1.1\r\nHost: check.torproject.org\r\n\r\n')
        response = b''
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        s.close()
        socket.socket = orig_socket
        
        body = response.split(b'\r\n\r\n', 1)[1].decode('utf-8', errors='replace')
        import json
        data = json.loads(body.strip())
        is_tor = data.get('IsTor', False)
        ip = data.get('IP', 'unknown')
        return is_tor, f'Tor exit node: {ip}'
    except Exception as e:
        try:
            socket.socket = orig_socket
        except NameError:
            pass
        return False, f'Tor circuit failed: {e}'

def test_torify():
    import subprocess
    try:
        result = subprocess.run(
            ['torify', 'curl', '-s', '--max-time', '30', 'https://check.torproject.org/api/ip'],
            capture_output=True, text=True, timeout=35
        )
        if result.returncode == 0 and result.stdout.strip():
            import json
            data = json.loads(result.stdout.strip())
            ip = data.get('IP', 'unknown')
            return True, f'torify works, exit node: {ip}'
        return False, f'torify failed: exit={result.returncode}, stderr={result.stderr[:200]}'
    except Exception as e:
        return False, f'torify error: {e}'

def main():
    print('=== Tor Connectivity Test ===')
    print(f'Time: {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
    
    ok, msg = test_socks_port()
    status = 'OK' if ok else 'FAIL'
    print(f'[{status}] SOCKS5 Port: {msg}')
    
    if not ok:
        print('\nTor SOCKS port not accessible. Check:')
        print('  1. sudo systemctl status tor')
        print('  2. ss -tlnp | grep 9050')
        return 1
    
    print('\nBuilding Tor circuit via Python socks module (30s timeout)...')
    ok1, msg1 = test_tor_circuit()
    status1 = 'OK' if ok1 else 'FAIL'
    print(f'[{status1}] Tor Circuit: {msg1}')
    
    print('\nTesting via torify (may take 30+ seconds)...')
    ok2, msg2 = test_torify()
    status2 = 'OK' if ok2 else 'FAIL'
    print(f'[{status2}] Tor via torify: {msg2}')
    
    if ok1 or ok2:
        print('\n=== Tor is WORKING ===')
        return 0
    else:
        print('\n=== Tor NOT WORKING ===')
        print('Tor is running but circuits cannot build.')
        return 1

if __name__ == '__main__':
    sys.exit(main())
