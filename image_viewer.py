import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QFileDialog, QTreeView, QListView,
    QMenuBar, QToolBar, QStatusBar, QMessageBox, QScrollArea,
    QFrame, QSizePolicy, QApplication
)
from PySide6.QtCore import (
    Qt, QSize, QDir, QFileInfo, QStandardPaths, 
    QItemSelectionModel, QModelIndex
)
from PySide6.QtGui import (
    QAction, QIcon, QPixmap, QImage, QImageReader, QStandardItemModel,
    QStandardItem, QFont, QPalette, QColor, QKeySequence
)
from PySide6.QtWidgets import QFileSystemModel

class ImageViewer(QMainWindow):
    """图片查看器主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.image_files = []  # 当前文件夹中的所有图片文件
        self.current_image_index = -1
        self.folders = []  # 已添加的文件夹列表
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("图片查看器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置应用程序样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QTreeView, QListView {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
            }
            QTreeView::item:selected, QListView::item:selected {
                background-color: #3a6ea5;
                color: #ffffff;
            }
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QStatusBar {
                background-color: #2b2b2b;
                color: #cccccc;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板：文件夹和文件列表
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 中间面板：图片显示
        center_panel = self.create_center_panel()
        splitter.addWidget(center_panel)
        
        # 右侧面板：图片信息和缩略图
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([300, 600, 300])
        
        main_layout.addWidget(splitter)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建状态栏
        self.create_status_bar()
        
    def create_left_panel(self):
        """创建左侧面板：文件夹树和文件列表"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # 文件夹树
        folder_label = QLabel("文件夹")
        folder_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(folder_label)
        
        self.folder_tree = QTreeView()
        self.folder_model = QFileSystemModel()
        self.folder_model.setRootPath("")
        self.folder_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        self.folder_tree.setModel(self.folder_model)
        self.folder_tree.setRootIndex(self.folder_model.index(""))
        self.folder_tree.setHeaderHidden(True)
        self.folder_tree.setAnimated(True)
        self.folder_tree.setIndentation(15)
        left_layout.addWidget(self.folder_tree)
        
        # 添加文件夹按钮
        add_folder_btn = QPushButton("添加文件夹")
        add_folder_btn.setIcon(QIcon.fromTheme("folder-add"))
        left_layout.addWidget(add_folder_btn)
        add_folder_btn.clicked.connect(self.add_folder)
        
        # 文件列表
        file_label = QLabel("文件列表")
        file_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(file_label)
        
        self.file_list = QListView()
        self.file_model = QStandardItemModel()
        self.file_list.setModel(self.file_model)
        left_layout.addWidget(self.file_list)
        
        return left_widget
        
    def create_center_panel(self):
        """创建中间面板：图片显示区域"""
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)
        
        # 图片显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 2px solid #444444;
                border-radius: 8px;
            }
        """)
        
        # 使用滚动区域以便查看大图
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignCenter)
        
        center_layout.addWidget(scroll_area)
        
        # 导航按钮
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        self.prev_btn = QPushButton("上一张")
        self.prev_btn.setIcon(QIcon.fromTheme("go-previous"))
        self.prev_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("下一张")
        self.next_btn.setIcon(QIcon.fromTheme("go-next"))
        self.next_btn.setEnabled(False)
        nav_layout.addWidget(self.next_btn)
        
        nav_layout.addStretch()
        
        center_layout.addWidget(nav_widget)
        
        return center_widget
        
    def create_right_panel(self):
        """创建右侧面板：图片信息和缩略图"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # 图片信息
        info_label = QLabel("图片信息")
        info_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(info_label)
        
        self.info_text = QLabel("未选择图片")
        self.info_text.setWordWrap(True)
        self.info_text.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 10px;
                min-height: 100px;
            }
        """)
        right_layout.addWidget(self.info_text)
        
        # 缩略图
        thumb_label = QLabel("缩略图")
        thumb_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(thumb_label)
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setFixedSize(200, 200)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 2px solid #444444;
                border-radius: 8px;
            }
        """)
        right_layout.addWidget(self.thumbnail_label)
        
        right_layout.addStretch()
        
        return right_widget
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        open_action = QAction("打开图片", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)
        
        open_folder_action = QAction("打开文件夹", self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 查看菜单
        view_menu = menubar.addMenu("查看")
        
        zoom_in_action = QAction("放大", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("重置缩放", self)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 打开图片按钮
        open_btn = QAction(QIcon.fromTheme("document-open"), "打开图片", self)
        open_btn.triggered.connect(self.open_image)
        toolbar.addAction(open_btn)
        
        # 打开文件夹按钮
        open_folder_btn = QAction(QIcon.fromTheme("folder-open"), "打开文件夹", self)
        open_folder_btn.triggered.connect(self.open_folder)
        toolbar.addAction(open_folder_btn)
        
        toolbar.addSeparator()
        
        # 上一张按钮
        prev_btn = QAction(QIcon.fromTheme("go-previous"), "上一张", self)
        prev_btn.triggered.connect(self.prev_image)
        toolbar.addAction(prev_btn)
        
        # 下一张按钮
        next_btn = QAction(QIcon.fromTheme("go-next"), "下一张", self)
        next_btn.triggered.connect(self.next_image)
        toolbar.addAction(next_btn)
        
        toolbar.addSeparator()
        
        # 放大按钮
        zoom_in_btn = QAction(QIcon.fromTheme("zoom-in"), "放大", self)
        zoom_in_btn.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_btn)
        
        # 缩小按钮
        zoom_out_btn = QAction(QIcon.fromTheme("zoom-out"), "缩小", self)
        zoom_out_btn.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_btn)
        
        # 重置缩放按钮
        reset_zoom_btn = QAction(QIcon.fromTheme("zoom-original"), "重置缩放", self)
        reset_zoom_btn.triggered.connect(self.reset_zoom)
        toolbar.addAction(reset_zoom_btn)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.statusBar().showMessage("就绪")
        
    def setup_connections(self):
        """设置信号和槽连接"""
        # 文件夹树选择变化
        self.folder_tree.selectionModel().selectionChanged.connect(self.on_folder_selected)
        
        # 文件列表选择变化
        self.file_list.selectionModel().selectionChanged.connect(self.on_file_selected)
        
        # 导航按钮
        self.prev_btn.clicked.connect(self.prev_image)
        self.next_btn.clicked.connect(self.next_image)
        
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