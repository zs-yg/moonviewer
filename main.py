#!/usr/bin/env python3
"""
图片查看器 - 主应用程序入口
支持PNG格式，多文件实现，多文件夹存储
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from image_viewer import ImageViewer

def main():
    """应用程序主函数"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName("图片查看器")
    app.setOrganizationName("ImageViewer")
    
    # 创建主窗口
    window = ImageViewer()
    window.show()
    
    # 启动应用程序事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()