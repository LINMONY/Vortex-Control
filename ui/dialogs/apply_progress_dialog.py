from PySide6.QtWidgets import (QDialog, QFrame, QVBoxLayout, QLabel, 
                               QHBoxLayout, QPushButton, QProgressBar, QListWidget, QListWidgetItem,
                               QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from ui.dialogs.restore_dialogs import BaseVortexDialog
from core.i18n import I18n as _

class ApplyProgressDialog(BaseVortexDialog):
    """
    Shows real progress of tweak application/reversion.
    """
    cancelRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(550, 450)
        self.aborted = False
        self.log_items: dict[str, QListWidgetItem] = {}
        
        # Container
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 550, 450)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1a1b26; 
                border: 1px solid #3b4261;
                border-radius: 4px;
            }
            QLabel { 
                color: #c0caf5; border: none; background: transparent; 
            }
            QListWidget {
                background-color: #15161e;
                border: 1px solid #292e42;
                border-radius: 4px;
                color: #cbd5e1;
                font-family: Consolas, monospace;
                font-size: 13px;
                padding: 10px;
            }
            QProgressBar {
                background-color: #15161e;
                border: 1px solid #292e42;
                border-radius: 2px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #7aa2f7;
            }
        """)
        self.add_shadow(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Title
        self.lbl_title = QLabel(_.get("applying_changes"))
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        
        # Total Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        
        # Logs
        self.list_widget = QListWidget()
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setAttribute(Qt.WA_MacShowFocusRect, False)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_cancel = QPushButton(_.get("cancel"))
        self.btn_cancel.setFixedSize(120, 32)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #565f89;
                border: 1px solid #3b4261;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #292e42; color: #a9b1d6; }
        """)
        self.btn_cancel.clicked.connect(self.request_abort)
        
        self.btn_close = QPushButton(_.get("close"))
        self.btn_close.setFixedSize(120, 32)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #7aa2f7;
                color: #15161e;
                border: none;
                border-radius: 4px;
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

    def add_log(self, text: str, status: str = "WAIT", process_id: str = None):
        """
        status: WAIT, DONE, ERROR, INFO
        process_id: unique identifier to update the same row
        """
        if process_id and process_id in self.log_items:
            item = self.log_items[process_id]
        else:
            item = QListWidgetItem()
            if process_id:
                self.log_items[process_id] = item
            self.list_widget.addItem(item)
            
        if status == "DONE":
            item.setForeground(QColor("#9ece6a")) # Green
            item.setText(f"[OK]    {text}")
        elif status == "ERROR":
            item.setForeground(QColor("#f7768e")) # Red
            item.setText(f"[ERROR] {text}")
        elif status == "INFO":
            item.setForeground(QColor("#7aa2f7")) # Blue
            item.setText(f"[INFO]  {text}")
        else:
            item.setForeground(QColor("#a9b1d6")) # Gray
            item.setText(f"[WAIT]  {text}")
            
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
            self.lbl_title.setText(_.get("success_finished"))
            self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ade80;")
        else:
            self.lbl_title.setText(f"{_.get('finished_errors')} ({error_count})")
            self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #eab308;")

    def request_abort(self):
        self.aborted = True
        self.add_log(_.get("aborting_operation"), "Warn")
        self.btn_cancel.setEnabled(False)
        self.cancelRequested.emit()
