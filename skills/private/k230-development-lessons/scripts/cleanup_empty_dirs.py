import os

# K230 清理空目录脚本
# 清理 /data/320p_photos/ 下所有空子目录

def cleanup():
    print("=== K230 Empty Directory Cleanup ===")
    
    base = '/data/320p_photos'
    try:
        dirs = os.listdir(base)
    except:
        print("Cannot list", base)
        return
    
    print(f"Found {len(dirs)} directories")
    
    for d in dirs:
        path = base + '/' + d
        try:
            files = os.listdir(path)
            if len(files) == 0:
                os.rmdir(path)
                print(f"DELETED: {d}")
            else:
                print(f"KEPT: {d} ({len(files)} files)")
        except Exception as e:
            print(f"ERROR: {d}: {e}")
    
    print("=== Cleanup Complete ===")

if __name__ == '__main__':
    cleanup()
