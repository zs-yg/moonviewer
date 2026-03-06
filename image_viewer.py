import os
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Qt, QFileInfo, QStandardPaths
from PySide6.QtGui import QPixmap, QImage, QImageReader, QStandardItem
from ui.main_window import UIMainWindow


class ImageViewer(UIMainWindow):
    """图片查看器主窗口类，继承自UIMainWindow"""
    
    def __init__(self):
        super().__init__()
        self.setup_connections()
        
    def setup_connections(self):
        """设置信号和槽连接"""
        # 文件夹树选择变化
        self.folder_tree.selectionModel().selectionChanged.connect(self.on_folder_selected)
        
        # 文件列表选择变化
        self.file_list.selectionModel().selectionChanged.connect(self.on_file_selected)
        
        # 导航按钮
        self.prev_btn.clicked.connect(self.prev_image)
        self.next_btn.clicked.connect(self.next_image)
        
        # 添加文件夹按钮
        self.add_folder_btn.clicked.connect(self.add_folder)
        
        # 菜单栏动作
        self.open_action.triggered.connect(self.open_image)
        self.open_folder_action.triggered.connect(self.open_folder)
        self.exit_action.triggered.connect(self.close)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.reset_zoom_action.triggered.connect(self.reset_zoom)
        
        # 工具栏动作
        self.open_btn.triggered.connect(self.open_image)
        self.open_folder_btn.triggered.connect(self.open_folder)
        self.toolbar_prev_btn.triggered.connect(self.prev_image)
        self.toolbar_next_btn.triggered.connect(self.next_image)
        self.zoom_in_btn.triggered.connect(self.zoom_in)
        self.zoom_out_btn.triggered.connect(self.zoom_out)
        self.reset_zoom_btn.triggered.connect(self.reset_zoom)
        
    def open_image(self):
        """打开单个图片文件"""
        file_filter = "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;所有文件 (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", 
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation),
            file_filter
        )
        
        if file_path:
            self.load_image(file_path)
            
    def open_folder(self):
        """打开文件夹并加载其中的图片"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择文件夹",
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        )
        
        if folder_path:
            # 直接加载文件夹中的图片，不清除文件夹列表
            self.load_folder_images(folder_path)
            
    def add_folder(self):
        """添加文件夹到树状视图"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择要添加的文件夹",
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        )
        
        if folder_path:
            self.add_folder_path(folder_path)
            
    def add_folder_path(self, folder_path):
        """添加文件夹路径到树状视图"""
        if folder_path not in self.folders:
            self.folders.append(folder_path)
            # 展开到该文件夹
            index = self.folder_model.index(folder_path)
            self.folder_tree.expand(index)
            self.folder_tree.setCurrentIndex(index)
            
            # 加载该文件夹中的图片
            self.load_folder_images(folder_path)
            
    def on_folder_selected(self):
        """文件夹选择变化时的处理"""
        indexes = self.folder_tree.selectedIndexes()
        if indexes:
            index = indexes[0]
            folder_path = self.folder_model.filePath(index)
            self.load_folder_images(folder_path)
            
    def load_folder_images(self, folder_path):
        """加载文件夹中的图片文件"""
        # 清除当前显示
        self.image_label.clear()
        self.info_text.setText("未选择图片")
        self.thumbnail_label.clear()
        self.current_image_path = None
        self.current_image_index = -1
        
        # 清空文件列表
        self.file_model.clear()
        self.image_files = []
        
        # 更新导航按钮状态
        self.update_navigation_buttons()
        
        # 支持的图片格式
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']
        
        try:
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file_name)[1].lower()
                    if ext in image_extensions:
                        self.image_files.append(file_path)
                        item = QStandardItem(file_name)
                        item.setData(file_path, Qt.UserRole)
                        self.file_model.appendRow(item)
                        
            if self.image_files:
                self.statusBar().showMessage(f"找到 {len(self.image_files)} 张图片")
                # 选择第一个文件
                if self.file_model.rowCount() > 0:
                    self.file_list.setCurrentIndex(self.file_model.index(0, 0))
            else:
                self.statusBar().showMessage("文件夹中没有找到图片文件")
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取文件夹: {str(e)}")
            
    def on_file_selected(self):
        """文件选择变化时的处理"""
        indexes = self.file_list.selectedIndexes()
        if indexes:
            index = indexes[0]
            file_path = self.file_model.data(index, Qt.UserRole)
            if file_path:
                self.load_image(file_path)
                
    def load_image(self, file_path):
        """加载并显示图片"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "错误", f"文件不存在: {file_path}")
                return
                
            # 使用QImageReader检查图片格式
            reader = QImageReader(file_path)
            if not reader.canRead():
                QMessageBox.warning(self, "错误", f"无法读取图片文件: {file_path}")
                return
                
            # 加载图片
            image = QImage(file_path)
            if image.isNull():
                QMessageBox.warning(self, "错误", f"无法加载图片: {file_path}")
                return
            
            # 如果文件不在image_files列表中，则添加它（用于命令行拖放支持）
            if file_path not in self.image_files:
                self.image_files.append(file_path)
                # 同时添加到文件模型，以便在文件列表中显示
                file_name = os.path.basename(file_path)
                item = QStandardItem(file_name)
                item.setData(file_path, Qt.UserRole)
                self.file_model.appendRow(item)
                
            # 显示图片
            pixmap = QPixmap.fromImage(image)
            self.display_image(pixmap)
            
            # 更新当前图片信息
            self.current_image_path = file_path
            self.current_image_index = self.get_current_file_index()
            
            # 更新图片信息
            self.update_image_info(image, file_path)
            
            # 更新缩略图
            self.update_thumbnail(pixmap)
            
            # 更新导航按钮状态
            self.update_navigation_buttons()
            
            # 更新状态栏
            file_name = os.path.basename(file_path)
            self.statusBar().showMessage(f"已加载: {file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载图片时出错: {str(e)}")
            
    def display_image(self, pixmap):
        """显示图片到标签"""
        # 调整图片大小以适应显示区域，同时保持宽高比
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
    def update_image_info(self, image, file_path):
        """更新图片信息"""
        try:
            file_info = QFileInfo(file_path)
            file_size = file_info.size()
            file_size_mb = file_size / (1024 * 1024)
            
            info_text = f"""
            <b>文件名:</b> {os.path.basename(file_path)}<br>
            <b>路径:</b> {file_path}<br>
            <b>大小:</b> {file_size_mb:.2f} MB ({file_size} 字节)<br>
            <b>尺寸:</b> {image.width()} × {image.height()}<br>
            <b>格式:</b> {image.format().name if hasattr(image.format(), 'name') else '未知'}<br>
            <b>颜色深度:</b> {image.depth()} 位<br>
            <b>修改时间:</b> {file_info.lastModified().toString("yyyy-MM-dd hh:mm:ss")}<br>
            """
            
            self.info_text.setText(info_text)
            
        except Exception as e:
            self.info_text.setText(f"无法获取图片信息: {str(e)}")
            
    def update_thumbnail(self, pixmap):
        """更新缩略图"""
        # 创建缩略图
        thumbnail = pixmap.scaled(
            180, 180, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.thumbnail_label.setPixmap(thumbnail)
        
    def get_current_file_index(self):
        """获取当前文件在列表中的索引"""
        if not self.current_image_path or not self.image_files:
            return -1
            
        try:
            return self.image_files.index(self.current_image_path)
        except ValueError:
            return -1
            
    def update_navigation_buttons(self):
        """更新导航按钮状态"""
        has_prev = self.current_image_index > 0
        has_next = self.current_image_index < len(self.image_files) - 1 if self.image_files else False
        
        self.prev_btn.setEnabled(has_prev)
        self.next_btn.setEnabled(has_next)
        self.toolbar_prev_btn.setEnabled(has_prev)
        self.toolbar_next_btn.setEnabled(has_next)
        
    def prev_image(self):
        """显示上一张图片"""
        if self.current_image_index > 0:
            prev_index = self.current_image_index - 1
            if prev_index < len(self.image_files):
                self.load_image(self.image_files[prev_index])
                
    def next_image(self):
        """显示下一张图片"""
        if self.current_image_index >= 0 and self.current_image_index < len(self.image_files) - 1:
            next_index = self.current_image_index + 1
            if next_index < len(self.image_files):
                self.load_image(self.image_files[next_index])
                
    def zoom_in(self):
        """放大图片"""
        current_pixmap = self.image_label.pixmap()
        if current_pixmap and not current_pixmap.isNull():
            new_size = current_pixmap.size() * 1.2
            scaled_pixmap = current_pixmap.scaled(
                new_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
    def zoom_out(self):
        """缩小图片"""
        current_pixmap = self.image_label.pixmap()
        if current_pixmap and not current_pixmap.isNull():
            new_size = current_pixmap.size() * 0.8
            scaled_pixmap = current_pixmap.scaled(
                new_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
    def reset_zoom(self):
        """重置缩放"""
        if self.current_image_path and os.path.exists(self.current_image_path):
            pixmap = QPixmap(self.current_image_path)
            if not pixmap.isNull():
                self.display_image(pixmap)
                
    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        # 重新调整图片大小
        if self.current_image_path and os.path.exists(self.current_image_path):
            pixmap = QPixmap(self.current_image_path)
            if not pixmap.isNull():
                self.display_image(pixmap)