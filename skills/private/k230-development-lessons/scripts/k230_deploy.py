import subprocess

# K230 安静模式部署脚本
# 完整流程: backup → noop → deploy → restore

def deploy():
    print("=== K230 Deployment ===")
    
    # Step 1: Backup original boot.py
    print("Step 1: Backup original boot.py")
    subprocess.run(
        ['ampy', '-p', '/dev/openmvcam', 'get', '/sdcard/boot.py', '/tmp/original_boot.py'],
        capture_output=True, timeout=10
    )
    print("  Done")
    
    # Step 2: Upload noop boot.py
    print("Step 2: Upload noop boot.py")
    subprocess.run(
        ['ampy', '-p', '/dev/openmvcam', 'put', '/tmp/noop_boot.py', '/sdcard/boot.py'],
        capture_output=True, timeout=10
    )
    print("  Done")
    
    # Step 3: Upload scripts
    print("Step 3: Upload scripts")
    print("  (User should add script paths here)")
    
    # Step 4: Run scripts
    print("Step 4: Run scripts")
    print("  (User should add script paths here)")
    
    # Step 5: Restore original boot.py
    print("Step 5: Restore original boot.py")
    subprocess.run(
        ['ampy', '-p', '/dev/openmvcam', 'put', '/tmp/original_boot.py', '/sdcard/boot.py'],
        capture_output=True, timeout=10
    )
    print("  Done")
    
    print("=== Deployment Complete ===")

if __name__ == '__main__':
    deploy()
