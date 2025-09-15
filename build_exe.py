#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将NAS路径转换工具打包成exe
作者：Sallos
"""

import os
import subprocess
import sys

def build_exe():
    """打包成exe文件"""
    print("开始打包NAS路径转换工具 喵~")
    
    # PyInstaller命令参数
    cmd = [
        sys.executable, "-m", "pyinstaller",
        "--onefile",  # 打包成单个exe文件
        "--windowed",  # 不显示控制台窗口
        "--name=NAS路径转换工具",  # 指定exe文件名
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",  # 如果有图标文件
        "--add-data=README.md;.",  # 包含README文件
        "--distpath=dist",  # 输出目录
        "--workpath=build",  # 临时文件目录
        "--specpath=.",  # spec文件位置
        "main.py"  # 主程序文件
    ]
    
    # 移除空字符串参数
    cmd = [arg for arg in cmd if arg]
    
    try:
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("打包成功 喵~")
        print("输出信息:")
        print(result.stdout)
        
        # 检查生成的exe文件
        exe_path = os.path.join("dist", "NAS路径转换工具.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"\n✅ 打包完成！")
            print(f"📁 文件位置: {exe_path}")
            print(f"📊 文件大小: {file_size:.2f} MB")
            print(f"\n🎉 现在可以直接运行 {exe_path} 喵~")
        else:
            print("❌ 未找到生成的exe文件")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🐱 NAS路径转换工具 - EXE打包脚本")
    print("=" * 50)
    
    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 检测到虚拟环境")
    else:
        print("⚠️  未检测到虚拟环境，建议在虚拟环境中运行")
    
    # 开始打包
    success = build_exe()
    
    if success:
        print("\n🎊 打包完成！可以分发exe文件了 喵~")
    else:
        print("\n😿 打包失败，请检查错误信息")
    
    input("\n按回车键退出...")