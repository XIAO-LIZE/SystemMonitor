#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控工具 v2.2 - 主程序入口

一个实时监控系统资源的桌面工具，支持 CPU、内存、磁盘、网络监控和进程管理。

使用方法：
    python main.py

依赖安装：
    pip install psutil matplotlib
"""
import sys
import os

# 确保可以正确导入 src 模块
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def check_dependencies():
    """检查依赖是否安装"""
    missing = []
    try:
        import psutil
    except ImportError:
        missing.append("psutil")
    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")

    if missing:
        print(f"[错误] 缺少依赖: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False
    return True


def main():
    """主函数"""
    if not check_dependencies():
        input("按回车键退出...")
        return 1

    from src.gui import MainWindow

    print("正在启动系统监控工具...")
    app = MainWindow()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
