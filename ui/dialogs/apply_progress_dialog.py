from PySide6.QtWidgets import (QDialog, QFrame, QVBoxLayout, QLabel, 
                               QHBoxLayout, QPushButton, QProgressBar, QListWidget, QListWidgetItem,
                               QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal
from ui.dialogs.restore_dialogs import BaseVortexDialog

class ApplyProgressDialog(BaseVortexDialog):
    """
    Shows real progress of tweak application/reversion.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 400)
        self.aborted = False
        
        # Container
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 500, 400)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e; 
                border: 1px solid #7aa2f7;
                border-radius: 12px;
            }
            QLabel { 
                color: #c0caf5; border: none; background: transparent; 
            }
            QListWidget {
                background-color: #24283b;
                border: 1px solid #414868;
                border-radius: 8px;
                color: #cbd5e1;
            }
            QProgressBar {
                background-color: #24283b;
                border: 1px solid #414868;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4ade80;
                border-radius: 4px;
            }
        """)
        self.add_shadow(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Title
        self.lbl_title = QLabel("Применение изменений...")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        
        # Total Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(24)
        
        # Logs
        self.list_widget = QListWidget()
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setAttribute(Qt.WA_MacShowFocusRect, False)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setFixedSize(120, 36)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #414868;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #565f89; }
        """)
        self.btn_cancel.clicked.connect(self.request_abort)
        
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.setFixedSize(120, 36)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #7aa2f7;
                color: #1a1b26;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #89b4fa; }
        """)
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.hide() # Hidden until finished

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_close)
        btn_layout.addStretch()

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.list_widget)
        layout.addLayout(btn_layout)

    def add_log(self, text: str, status: str = "WAIT"):
        """
        status: WAIT, DONE, ERROR, INFO
        """
        item = QListWidgetItem(text)
        
        if status == "DONE":
            item.setForeground(QColor("#4ade80")) # Green
            item.setText(f"✓ {text}")
        elif status == "ERROR":
            item.setForeground(QColor("#f7768e")) # Red
            item.setText(f"✗ {text}")
        elif status == "INFO":
            item.setForeground(QColor("#7aa2f7")) # Blue
            item.setText(f"ℹ {text}")
        else:
            item.setForeground(QColor("#94a3b8")) # Gray
            item.setText(f"⏳ {text}")
            
        self.list_widget.addItem(item)
        self.list_widget.scrollToBottom()

    def update_progress(self, current, total):
        pct = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"{pct}% ({current}/{total})")

    def finish_process(self, success_count, error_count):
        self.progress_bar.setValue(100)
        self.btn_cancel.hide()
        self.btn_close.show()
        
        if error_count == 0:
            self.lbl_title.setText("Успешно завершено!")
            self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ade80;")
        else:
            self.lbl_title.setText(f"Завершено с ошибками ({error_count})")
            self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #eab308;")

    def request_abort(self):
        self.aborted = True
        self.add_log("Прерывание операции...", "Warn")
        self.btn_cancel.setEnabled(False)
