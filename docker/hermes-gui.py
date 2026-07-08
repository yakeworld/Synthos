#!/usr/bin/env python3
"""
Hermes Agent — Windows 交互式启动器
用法: python hermes-gui.py
"""
import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("  Hermes Agent — Windows 便携版")
    print("=" * 60)
    print()
    
    # 检查 hermes 是否在 PATH
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "hermes-agent"],
                              capture_output=True, text=True)
    except:
        pass
    
    print("输入你的问题，直接回车结束输入:")
    print("-" * 60)
    print()
    
    lines = []
    while True:
        try:
            line = input(">> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        
        if line.strip().lower() in ("exit", "quit", "q", ""):
            break
        
        lines.append(line)
    
    if lines:
        question = "\n".join(lines)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "hermes.chat", "-q", question, "-Q"],
                capture_output=True, text=True, timeout=300
            )
            print()
            print("-" * 60)
            print(result.stdout)
            if result.stderr:
                print("⚠️  警告:", result.stderr)
            print("-" * 60)
        except FileNotFoundError:
            print("错误: 未找到 hermes 命令")
            print("请先运行 hermes-windows-setup.ps1 完成安装")
        except subprocess.TimeoutExpired:
            print("错误: 请求超时")

if __name__ == "__main__":
    main()