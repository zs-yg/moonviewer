import os
import sys
from pathlib import Path


def get_file_from_command_line():
    # sys.argv[0] 是脚本名称，后续参数是拖放的文件
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"警告: 文件不存在: {file_path}")
            return None
        
        # 检查是否为文件（不是目录）
        if not os.path.isfile(file_path):
            print(f"警告: 路径不是文件: {file_path}")
            return None
        
        # 检查文件扩展名是否为支持的图片格式
        if is_supported_image(file_path):
            return file_path
        else:
            print(f"警告: 不支持的图片格式: {file_path}")
            return None
    
    return None


def is_supported_image(file_path):
    # 支持的图片扩展名
    supported_extensions = {
        '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp',
        '.PNG', '.JPG', '.JPEG', '.BMP', '.GIF', '.TIFF', '.WEBP'
    }
    
    # 获取文件扩展名
    ext = os.path.splitext(file_path)[1]
    
    return ext in supported_extensions


def validate_image_file(file_path):
    if not os.path.exists(file_path):
        return False, f"文件不存在: {file_path}"
    
    if not os.path.isfile(file_path):
        return False, f"路径不是文件: {file_path}"
    
    if not is_supported_image(file_path):
        return False, f"不支持的图片格式: {file_path}"
    
    # 检查文件是否可读
    try:
        with open(file_path, 'rb') as f:
            f.read(1)  # 尝试读取一个字节
    except IOError as e:
        return False, f"无法读取文件: {str(e)}"
    
    return True, "文件有效"


if __name__ == "__main__":
    # 测试代码
    file_path = get_file_from_command_line()
    if file_path:
        print(f"从命令行获取的文件路径: {file_path}")
        valid, message = validate_image_file(file_path)
        print(f"验证结果: {valid}, 信息: {message}")
    else:
        print("没有从命令行获取到有效的文件路径")