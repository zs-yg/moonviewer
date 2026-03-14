import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QTreeView, QListView,
    QMenuBar, QToolBar, QStatusBar, QScrollArea
)
from PySide6.QtCore import Qt, QSize, QDir
from PySide6.QtGui import (
    QAction, QIcon, QFont, QStandardItemModel, QKeySequence
)
from PySide6.QtWidgets import QFileSystemModel


class UIMainWindow(QMainWindow):
    """主窗口UI类，包含所有UI组件创建方法"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.image_files = []  # 当前文件夹中的所有图片文件
        self.current_image_index = -1
        self.folders = []  # 已添加的文件夹列表
        
        # UI组件引用
        self.folder_tree = None
        self.folder_model = None
        self.file_list = None
        self.file_model = None
        self.image_label = None
        self.prev_btn = None
        self.next_btn = None
        self.info_text = None
        self.thumbnail_label = None
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("图片查看器")
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
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
            QPushButton::icon {
                color: #87CEEB;  /* 天蓝色图标 */
            }
            QToolButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QToolButton:hover {
                background-color: #4a4a4a;
                border-color: #666666;
            }
            QToolButton:pressed {
                background-color: #2a2a2a;
            }
            QToolButton::icon {
                color: #87CEEB;  /* 天蓝色图标 */
            }
            QAction {
                color: #ffffff;
            }
            QAction::icon {
                color: #87CEEB;  /* 天蓝色图标 */
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
        self.add_folder_btn = QPushButton("添加文件夹")
        self.add_folder_btn.setIcon(QIcon.fromTheme("folder-add"))
        left_layout.addWidget(self.add_folder_btn)
        
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
        
        self.open_action = QAction("打开图片", self)
        self.open_action.setShortcut(QKeySequence.Open)
        file_menu.addAction(self.open_action)
        
        self.open_folder_action = QAction("打开文件夹", self)
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        file_menu.addAction(self.open_folder_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction("退出", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        file_menu.addAction(self.exit_action)
        
        # 查看菜单
        view_menu = menubar.addMenu("查看")
        
        self.zoom_in_action = QAction("放大", self)
        self.zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        view_menu.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction("缩小", self)
        self.zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        view_menu.addAction(self.zoom_out_action)
        
        self.reset_zoom_action = QAction("重置缩放", self)
        self.reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        view_menu.addAction(self.reset_zoom_action)
        
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 打开图片按钮
        self.open_btn = QAction(QIcon.fromTheme("document-open"), "打开图片", self)
        toolbar.addAction(self.open_btn)
        
        # 打开文件夹按钮
        self.open_folder_btn = QAction(QIcon.fromTheme("folder-open"), "打开文件夹", self)
        toolbar.addAction(self.open_folder_btn)
        
        toolbar.addSeparator()
        
        # 上一张按钮
        self.toolbar_prev_btn = QAction(QIcon.fromTheme("go-previous"), "上一张", self)
        toolbar.addAction(self.toolbar_prev_btn)
        
        # 下一张按钮
        self.toolbar_next_btn = QAction(QIcon.fromTheme("go-next"), "下一张", self)
        toolbar.addAction(self.toolbar_next_btn)
        
        toolbar.addSeparator()
        
        # 放大按钮
        self.zoom_in_btn = QAction(QIcon.fromTheme("zoom-in"), "放大", self)
        toolbar.addAction(self.zoom_in_btn)
        
        # 缩小按钮
        self.zoom_out_btn = QAction(QIcon.fromTheme("zoom-out"), "缩小", self)
        toolbar.addAction(self.zoom_out_btn)
        
        # 重置缩放按钮
        self.reset_zoom_btn = QAction(QIcon.fromTheme("zoom-original"), "重置缩放", self)
        toolbar.addAction(self.reset_zoom_btn)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.statusBar().showMessage("就绪")