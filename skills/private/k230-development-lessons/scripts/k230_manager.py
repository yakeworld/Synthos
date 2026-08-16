#!/usr/bin/env python3
"""K230 设备自动管理器 - 不依赖 ampy run，直接使用 ampy 的 pyboard 协议"""

import serial, time, sys, subprocess, os
sys.path.insert(0, '/home/yakeworld/.local/lib/python3.12/site-packages')
from ampy.pyboard import Pyboard, PyboardError

K230_PORT = '/dev/openmvcam'
K230_BAUD = 115200

def k230_exec(code):
    """通过 raw REPL 执行代码并返回输出"""
    board = Pyboard(K230_PORT, baudrate=K230_BAUD)
    try:
        board.enter_raw_repl()
        result = board.exec_(code)
        board.exit_raw_repl()
        return result
    except Exception as e:
        try:
            board.exit_raw_repl()
        except:
            pass
        return f"ERROR: {e}"
    finally:
        board.close()

def k230_execfile(local_path, remote_path):
    """上传并执行脚本（模拟 ampy put + ampy run）"""
    board = Pyboard(K230_PORT, baudrate=K230_BAUD)
    try:
        board.enter_raw_repl()
        with open(local_path, 'rb') as f:
            code = f.read()
        # Read the file and send it via raw REPL
        result = board.exec_(code)
        board.exit_raw_repl()
        return result
    except Exception as e:
        try:
            board.exit_raw_repl()
        except:
            pass
        return f"ERROR: {e}"
    finally:
        board.close()

def k230_reboot():
    """通过 machine.reset() 软重启设备"""
    board = Pyboard(K230_PORT, baudrate=K230_BAUD)
    try:
        board.enter_raw_repl()
        result = board.exec_('import machine; machine.reset()')
        board.exit_raw_repl()
        time.sleep(3)
        return result
    except Exception as e:
        try:
            board.exit_raw_repl()
        except:
            pass
        return f"ERROR: {e}"
    finally:
        board.close()

def k230_listdir(path='/'):
    """列出目录内容"""
    board = Pyboard(K230_PORT, baudrate=K230_BAUD)
    try:
        board.enter_raw_repl()
        code = f"""import os
r = []
for f in sorted(os.listdir('{path}')):
    try:
        s = os.stat(f if f.startswith('/') else ('/' + f if not '/' in f else f))
        r.append(f + ' - ' + str(s[6]) + ' bytes')
    except:
        r.append(f)
print(r)
"""
        result = board.exec_(code)
        board.exit_raw_repl()
        return result
    except Exception as e:
        try:
            board.exit_raw_repl()
        except:
            pass
        return f"ERROR: {e}"
    finally:
        board.close()

def k230_get(remote_path, local_path):
    """从设备下载文件"""
    board = Pyboard(K230_PORT, baudrate=K230_BAUD)
    try:
        board.enter_raw_repl()
        code = f"""
import sys
import ubinascii
with open('{remote_path}', 'rb') as infile:
    while True:
        result = infile.read(32)
        if result == b'':
            break
        len = sys.stdout.write(ubinascii.hexlify(result))
"""
        result = board.exec_(code)
        board.exit_raw_repl()
        # Decode hex
        with open(local_path, 'wb') as f:
            f.write(bytes.fromhex(result.decode('utf-8').strip()))
        return True
    except Exception as e:
        try:
            board.exit_raw_repl()
        except:
            pass
        return False
    finally:
        board.close()

def k230_put(local_path, remote_path):
    """上传文件到设备"""
    board = Pyboard(K230_PORT, baudrate=K230_BAUD)
    try:
        board.enter_raw_repl()
        # Read local file and create it on device
        with open(local_path, 'rb') as f:
            content = f.read()
        
        # Create file on device
        code = f"""f = open('{remote_path}', 'wb')
f.write({repr(content)}
)
f.close()
print('WRITTEN')
"""
        result = board.exec_(code)
        board.exit_raw_repl()
        return 'WRITTEN' in result.decode('utf-8') if result else False
    except Exception as e:
        try:
            board.exit_raw_repl()
        except:
            pass
        return False
    finally:
        board.close()


# ==================== 测试 ====================
if __name__ == '__main__':
    print("=== K230 设备管理器测试 ===\n")
    
    # Test 1: Basic exec
    print("1. 基本执行测试:")
    result = k230_exec('print("HELLO K230")')
    print(f"   Output: {result}")
    
    # Test 2: List directories
    print("\n2. 列出 /data/320p_photos/ 目录:")
    result = k230_listdir('/data/320p_photos')
    print(f"   Output: {result}")
    
    # Test 3: State check
    print("\n3. 检查设备状态:")
    result = k230_exec('import state; print("mode:", state.current_mode); print("running:", state.is_running)')
    print(f"   Output: {result}")
    
    # Test 4: Run cleanup
    print("\n4. 运行清理脚本:")
    cleanup_code = """import os
dirs = ['025','026','027','028','029','030','031','032','033','034']
for d in dirs:
    p = '/data/320p_photos/' + d
    try:
        fs = os.listdir(p)
        if len(fs) == 0:
            os.rmdir(p)
            print('DEL ' + d)
        else:
            print('SKIP ' + d + ' has ' + str(len(fs)) + ' files')
    except:
        pass
print('REMAINING:', os.listdir('/data/320p_photos'))
"""
    result = k230_exec(cleanup_code)
    print(f"   Output: {result}")
