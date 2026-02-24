from PySide6.QtWidgets import (QDialog, QFrame, QVBoxLayout, QLabel, 
                               QHBoxLayout, QPushButton, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from ui.components import AnimatedButton
from ui.dialogs.restore_dialogs import BaseVortexDialog

class ApplyConfirmationDialog(BaseVortexDialog):
    """
    Dialog asking user how to apply tweaks: with or without restore point.
    """
    def __init__(self, count: int, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 380)
        self.result_action = None # 'apply', 'create_and_apply', 'cancel'
        
        # Container
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 500, 380)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e; 
                border: 2px solid #7aa2f7;
                border-radius: 12px;
            }
            QLabel { 
                color: #c0caf5; border: none; background: transparent; 
            }
        """)
        self.add_shadow(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        lbl_title = QLabel("Подтверждение применения")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        
        # Content
        lbl_text = QLabel(
            f"Выбрано изменений: {count}.\n\n"
            "Это изменит системные настройки Windows. "
            "Некорректные твики могут повлиять на работу системы."
        )
        lbl_text.setWordWrap(True)
        lbl_text.setAlignment(Qt.AlignCenter)
        lbl_text.setStyleSheet("color: #a9b1d6; font-size: 14px; line-height: 1.4;")
        
        # Warning
        lbl_warn = QLabel("Рекомендуется создать точку восстановления вручную или автоматически.")
        lbl_warn.setWordWrap(True)
        lbl_warn.setAlignment(Qt.AlignCenter)
        lbl_warn.setStyleSheet("color: #eab308; font-size: 13px; font-weight: 500;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_text)
        layout.addWidget(lbl_warn)
        layout.addStretch()

        # Buttons Container
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(12)
        
        # Green: Create & Apply
        btn_create = QPushButton("Создать точку и применить (Рекомендуется)")
        btn_create.setCursor(Qt.PointingHandCursor)
        btn_create.setMinimumHeight(45)
        btn_create.setStyleSheet("""
            QPushButton {
                background-color: #4ade80;
                color: #1a1b26;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 0 15px;
            }
            QPushButton:hover { background-color: #22c55e; }
        """)
        btn_create.clicked.connect(lambda: self.done_with("create_and_apply"))
        
        # Blue: Just Apply
        btn_apply = QPushButton("Применить без точки восстановления")
        btn_apply.setCursor(Qt.PointingHandCursor)
        btn_apply.setMinimumHeight(45)
        btn_apply.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #7aa2f7;
                color: #7aa2f7;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 15px;
            }
            QPushButton:hover { background-color: rgba(122, 162, 247, 0.1); }
        """)
        btn_apply.clicked.connect(lambda: self.done_with("apply"))
        
        # Cancel
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setMinimumHeight(35)
        btn_cancel.setStyleSheet("""
            QPushButton {
                color: #64748b; 
                background: transparent; 
                border: none; 
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover { color: #94a3b8; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_create)
        btn_layout.addWidget(btn_apply)
        btn_layout.addWidget(btn_cancel, 0, Qt.AlignCenter)
        
        layout.addLayout(btn_layout)

    def done_with(self, action):
        self.result_action = action
        self.accept()
