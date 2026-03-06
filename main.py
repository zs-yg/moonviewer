import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from image_viewer import ImageViewer
from core.file_handler import get_file_from_command_line

def main():
    """应用程序主函数"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName("图片查看器")
    app.setOrganizationName("ImageViewer")
    
    # 创建主窗口
    window = ImageViewer()
    window.show()
    
    # 检查命令行参数，处理文件拖放
    file_path = get_file_from_command_line()
    if file_path:
        # 使用单次定时器确保窗口完全显示后再加载图片
        QTimer.singleShot(0, lambda: window.load_image(file_path))
    
    # 启动应用程序事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()