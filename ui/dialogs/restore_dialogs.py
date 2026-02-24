from PySide6.QtWidgets import (QDialog, QFrame, QVBoxLayout, QLabel, 
                               QLineEdit, QProgressBar, QHBoxLayout, QPushButton,
                               QGraphicsDropShadowEffect, QWidget)
from PySide6.QtCore import Qt, QTimer, QPoint, QSize
from PySide6.QtGui import QColor, QCursor

class BaseVortexDialog(QDialog):
    """
    Base class for consistent modal styling and centering.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def showEvent(self, event):
        self.center_window()
        super().showEvent(event)
        
    def center_window(self):
        if self.parent():
            parent_geo = self.parent().geometry()
            my_geo = self.geometry()
            x = parent_geo.x() + (parent_geo.width() - my_geo.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - my_geo.height()) // 2
            self.move(x, y)
    
    def add_shadow(self, target_widget):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        target_widget.setGraphicsEffect(shadow)

class VortexCreationDialog(BaseVortexDialog):
    """
    Custom Frameless Creation Dialog with indeterminate progress bar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 380)
        
        self.state = "INPUT" # INPUT -> CONFIRM -> PROGRESS
        self.result_name = None
        self.success = False
        self.error_msg = ""

        # Container Frame
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 500, 380)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e; 
                border: 1px solid #7aa2f7;
                border-radius: 12px;
            }
            QLabel { 
                color: #c0caf5; 
                border: none;
                background: transparent;
            }
            QLineEdit {
                background-color: #24283b;
                color: #c0caf5;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                padding: 10px;
                border: 1px solid #414868;
                border-radius: 8px;
            }
            QLineEdit:focus { border: 1px solid #7aa2f7; }
        """)
        
        self.add_shadow(self.container)

        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        # 1. Header
        self.lbl_title = QLabel("ЗАЩИТА СИСТЕМЫ")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; letter-spacing: 1px; border: none;")
        
        # 2. Warning / Desc
        self.lbl_desc = QLabel(
            "Внимание! Рекомендуется создавать точку перед любыми изменениями. Это ваш страховочный трос."
        )
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setAlignment(Qt.AlignCenter)
        self.lbl_desc.setStyleSheet("color: #94a3b8; font-size: 14px; line-height: 1.4; border: none;")

        # 3. Input
        self.prefix = "VORTEX-"
        self.input_field = QLineEdit(self.prefix)
        self.input_field.textChanged.connect(self.on_text_changed)
        self.input_field.cursorPositionChanged.connect(self.on_cursor_changed)
        
        # 4. Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #24283b;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #bb9af7, stop:1 #7aa2f7);
                border-radius: 3px;
            }
        """)
        self.progress.hide()

        # 5. Buttons
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(15)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setFixedHeight(40)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #2f334d;
                border: 1px solid #414868;
                color: #a9b1d6;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover { 
                background-color: #3b4261;
                border: 1px solid #7aa2f7;
                color: white;
            }
            QPushButton:pressed {
                background-color: #7aa2f7;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_action = QPushButton("Далее")
        self.btn_action.setCursor(Qt.PointingHandCursor)
        self.btn_action.setFixedHeight(40)
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: #7aa2f7;
                color: #1a1b26;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { 
                background-color: #89b4fa;
            }
            QPushButton:pressed {
                background-color: #619af5;
                margin-top: 1px;
            }
        """)
        self.btn_action.clicked.connect(self.handle_action)
        
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addWidget(self.btn_action)
        
        self.layout.addWidget(self.lbl_title)
        self.layout.addWidget(self.lbl_desc)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(self.progress)
        self.layout.addStretch()
        self.layout.addLayout(self.btn_layout)

    def on_text_changed(self, text):
        if not text.startswith(self.prefix):
            self.input_field.setText(self.prefix)
            
    def on_cursor_changed(self, old, new):
        if new < len(self.prefix):
            self.input_field.setCursorPosition(len(self.prefix))

    def handle_action(self):
        if self.state == "INPUT":
            self.state = "CONFIRM"
            self.input_field.hide()
            self.lbl_title.setText("ПОДТВЕРЖДЕНИЕ")
            self.lbl_desc.setText("Вы точно уверены? Процесс займет около 30 секунд.")
            self.lbl_desc.setStyleSheet("color: #c0caf5; font-size: 16px; font-weight: 500; border: none;")
            
            self.btn_action.setText("ПОДТВЕРДИТЬ")
            self.btn_action.setStyleSheet("""
                QPushButton {
                    background-color: #9ece6a; color: #1a1b26; border: none; border-radius: 8px; font-weight: bold;
                }
                QPushButton:hover { background-color: #b9f27c; }
                QPushButton:pressed { background-color: #89c55b; margin-top: 2px; }
            """)
            
        elif self.state == "CONFIRM":
            self.state = "PROGRESS"
            self.result_name = self.input_field.text()
            
            self.lbl_title.setText("СОЗДАНИЕ")
            self.lbl_desc.setText("Создание снимка системы...\nПожалуйста, подождите.")
            self.lbl_desc.setStyleSheet("color: #7aa2f7; font-size: 14px; border: none;")
            
            self.btn_action.hide()
            self.btn_cancel.hide()
            self.progress.show()
            
            from ui.workers.restore_workers import CreateThread
            self.thread = CreateThread(self.result_name)
            self.thread.finished.connect(self.on_creation_finished)
            self.thread.start()

    def on_creation_finished(self, success, msg):
        self.success = success
        self.error_msg = msg
        self.accept()

    def get_result(self):
        return self.success, self.error_msg

class VortexConfirmDialog(BaseVortexDialog):
    """
    Styled confirmation dialog for actions like Delete/Restore.
    """
    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 220)
        
        # Determine strictness/color based on title usually
        is_delete = "Удалить" in title or "Удаление" in title
        accent_color = "#f7768e" if is_delete else "#7aa2f7"
        
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 400, 220)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e2e;
                border: 1px solid {accent_color};
                border-radius: 12px;
            }}
            QLabel {{ 
                color: #c0caf5; 
                background: transparent; 
                border: none;
            }}
        """)
        self.add_shadow(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30,30,30,30)
        layout.setSpacing(15)
        
        l_title = QLabel("Подтверждение")
        l_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        l_title.setAlignment(Qt.AlignCenter)
        
        l_text = QLabel(text)
        l_text.setWordWrap(True)
        l_text.setAlignment(Qt.AlignCenter)
        l_text.setStyleSheet("font-size: 14px; color: #a9b1d6;")
        
        layout.addWidget(l_title)
        layout.addWidget(l_text)
        layout.addStretch()
        
        btns = QHBoxLayout()
        btns.setSpacing(15)
        
        b_ca = QPushButton("Отмена")
        b_ca.setCursor(Qt.PointingHandCursor)
        b_ca.setFixedSize(120, 40)
        b_ca.clicked.connect(self.reject)
        b_ca.setStyleSheet(f"""
            QPushButton {{
                background-color: #414868;
                color: #ffffff;
                border-radius: 8px;
                font-weight: 500;
                border: 1px solid transparent;
            }}
            QPushButton:hover {{
                background-color: #565f89;
                border: 1px solid {accent_color};
            }}
            QPushButton:pressed {{
                background-color: #3b4261;
            }}
        """)
        
        b_ok = QPushButton(title) # Use title as action name e.g. "Удалить"
        if "Подтверждение" in title: b_ok.setText("OK")
        
        b_ok.setCursor(Qt.PointingHandCursor)
        b_ok.setFixedSize(120, 40)
        b_ok.clicked.connect(self.accept)
        b_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: #1a1b26;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {accent_color}DD; 
            }}
            QPushButton:pressed {{
                background-color: {accent_color}AA;
                margin-top: 2px;
            }}
        """)
        
        btns.addWidget(b_ca)
        btns.addWidget(b_ok)
        layout.addLayout(btns)

class VortexMessageDialog(BaseVortexDialog):
    """
    Styled message dialog (Info/Error).
    """
    def __init__(self, title, text, is_error=False, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 200)
        
        color = "#f7768e" if is_error else "#7aa2f7"
        
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 400, 200)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e2e;
                border: 1px solid {color};
                border-radius: 12px;
            }}
            QLabel {{ 
                color: #c0caf5; 
                background: transparent;
                border: none;
            }}
        """)
        self.add_shadow(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30,30,30,30)
        
        l_title = QLabel(title)
        l_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        l_title.setAlignment(Qt.AlignCenter)
        
        l_text = QLabel(text)
        l_text.setWordWrap(True)
        l_text.setAlignment(Qt.AlignCenter)
        l_text.setStyleSheet("font-size: 14px; margin-top: 10px;")
        
        layout.addWidget(l_title)
        layout.addWidget(l_text)
        layout.addStretch()
        
        b_ok = QPushButton("OK")
        b_ok.setCursor(Qt.PointingHandCursor)
        b_ok.clicked.connect(self.accept)
        b_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #1a1b26;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px 20px;
                min-width: 100px;
            }}
            QPushButton:hover {{ background-color: {color}DD; }}
            QPushButton:pressed {{ padding-top: 10px; }} /* Simple press effect */
        """)
        
        layout.addWidget(b_ok, 0, Qt.AlignCenter)
