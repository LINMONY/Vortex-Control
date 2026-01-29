from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import QIcon, QCursor
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

class FramelessWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.draggable = True
        self.dragging_threshold = 5
        self._drag_pos = None

    def mousePressEvent(self, event):
        self._drag_pos = None
        if self.draggable and event.button() == Qt.LeftButton:
            # Check if click is in title bar area (approx height 32)
            if event.position().y() < 32:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.draggable and event.buttons() == Qt.LeftButton and not self.isMaximized():
             if self._drag_pos is not None:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() < 32:
            self.toggle_maximize()
            event.accept()
        super().mouseDoubleClickEvent(event)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            if os.path.exists(self.max_icon):
                self.btn_max.setIcon(QIcon(self.max_icon))
        else:
            self.showMaximized()
            if os.path.exists(self.restore_icon):
                self.btn_max.setIcon(QIcon(self.restore_icon))

    def setup_custom_titlebar(self, layout, title="App"):
        title_bar = QFrame()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(32)
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(10, 0, 10, 0)
        tb_layout.setSpacing(10)

        # Title/Logo
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7aa2f7; font-weight: bold;")
        tb_layout.addWidget(lbl_title)
        tb_layout.addStretch()

        # Window Controls
        min_icon = os.path.join(ASSETS_DIR, "icons/minimize.svg")
        close_icon = os.path.join(ASSETS_DIR, "icons/close.svg")

        btn_min = QPushButton()
        btn_min.setObjectName("titleBarBtn")
        if os.path.exists(min_icon):
            btn_min.setIcon(QIcon(min_icon))
        btn_min.setFixedSize(30, 30)
        btn_min.clicked.connect(self.showMinimized)

        self.btn_max = QPushButton()
        self.btn_max.setObjectName("titleBarBtn")
        self.max_icon = os.path.join(ASSETS_DIR, "icons/maximize.svg")
        self.restore_icon = os.path.join(ASSETS_DIR, "icons/restore.svg")
        
        if os.path.exists(self.max_icon):
            self.btn_max.setIcon(QIcon(self.max_icon))
        self.btn_max.setFixedSize(30, 30)
        self.btn_max.clicked.connect(self.toggle_maximize)
        
        btn_close = QPushButton()
        btn_close.setObjectName("titleBarBtnClose") # Special ID for red hover
        if os.path.exists(close_icon):
            btn_close.setIcon(QIcon(close_icon))
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.close)

        tb_layout.addWidget(btn_min)
        tb_layout.addWidget(self.btn_max)
        tb_layout.addWidget(btn_close)

        layout.addWidget(title_bar)
        return title_bar
