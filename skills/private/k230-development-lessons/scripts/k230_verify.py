import subprocess

# K230 设备状态验证脚本
# 检查设备是否响应、目录状态、拍照计数

def verify():
    print("=== K230 Device Verification ===")
    
    # Check if device responds
    print("Step 1: Device response test")
    result = subprocess.run(
        ['ampy', '-p', '/dev/openmvcam', 'run', '-r', 'print("OK")'],
        capture_output=True, timeout=10
    )
    print("  Response:", result.stdout.decode('utf-8', errors='replace'))
    
    # Check photo directory
    print("Step 2: Photo directory")
    result2 = subprocess.run(
        ['ampy', '-p', '/dev/openmvcam', 'run', '-r', 'print(__import__("os").listdir("/data/320p_photos"))'],
        capture_output=True, timeout=10
    )
    print("  Photos:", result2.stdout.decode('utf-8', errors='replace'))
    
    print("=== Verification Complete ===")

if __name__ == '__main__':
    verify()
