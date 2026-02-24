from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QPoint, QSize, QTime
from PySide6.QtGui import QIcon, QCursor
from utils.paths import get_assets_dir
import os

class FramelessWindow(QMainWindow):
    def __init__(self, draggable=True):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.draggable = draggable
        self.dragging_threshold = 5
        self._drag_pos = None
        self._titlebar_controls = {}
        self._last_click_time = QTime.currentTime()

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
        btn_max = self._titlebar_controls.get('max_btn')
        max_icon = self._titlebar_controls.get('max_icon')
        restore_icon = self._titlebar_controls.get('restore_icon')
        
        if self.isMaximized():
            self.showNormal()
            if btn_max and max_icon and max_icon.exists():
                btn_max.setIcon(QIcon(str(max_icon)))
                btn_max.setToolTip("Развернуть")
        else:
            self.showMaximized()
            if btn_max and restore_icon and restore_icon.exists():
                btn_max.setIcon(QIcon(str(restore_icon)))
                btn_max.setToolTip("Восстановить")

    def setup_custom_titlebar(self, layout, title="App"):
        title_bar = QFrame()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(32)
        # Double click hint via tooltip on the bar itself? 
        title_bar.setToolTip("Двойной клик для разворачивания")
        
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(10, 0, 10, 0)
        tb_layout.setSpacing(10)

        # Title/Logo
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7aa2f7; font-weight: bold;")
        tb_layout.addWidget(lbl_title)
        tb_layout.addStretch()

        # Window Controls
        assets = get_assets_dir()
        min_icon = assets / "icons/minimize.svg"
        close_icon = assets / "icons/close.svg"
        max_icon = assets / "icons/maximize.svg"
        restore_icon = assets / "icons/restore.svg"
        
        # Store for toggle usage
        self._titlebar_controls['max_icon'] = max_icon
        self._titlebar_controls['restore_icon'] = restore_icon

        btn_min = QPushButton()
        btn_min.setObjectName("titleBarBtn")
        if min_icon.exists():
            btn_min.setIcon(QIcon(str(min_icon)))
        btn_min.setFixedSize(30, 30)
        btn_min.clicked.connect(self.showMinimized)
        btn_min.setToolTip("Свернуть")

        btn_max = QPushButton()
        btn_max.setObjectName("titleBarBtn")
        if max_icon.exists():
            btn_max.setIcon(QIcon(str(max_icon)))
        btn_max.setFixedSize(30, 30)
        btn_max.clicked.connect(self.toggle_maximize)
        btn_max.setToolTip("Развернуть")
        self._titlebar_controls['max_btn'] = btn_max
        
        btn_close = QPushButton()
        btn_close.setObjectName("titleBarBtnClose") # Special ID for red hover
        if close_icon.exists():
            btn_close.setIcon(QIcon(str(close_icon)))
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.close)
        btn_close.setToolTip("Закрыть")

        tb_layout.addWidget(btn_min)
        tb_layout.addWidget(btn_max)
        tb_layout.addWidget(btn_close)

        layout.addWidget(title_bar)
        return title_bar
