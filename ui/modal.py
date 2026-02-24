from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGraphicsBlurEffect, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QFont
from enum import Enum, auto

class SafetyState(Enum):
    IDLE = auto()
    PROMPT = auto()
    CONFIRM_GENERIC = auto()

class ModalOverlay(QWidget):
    """
    Overlays the entire parent window with a semi-transparent background.
    Blocks interaction with underlying widgets.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setFocusPolicy(Qt.StrongFocus)
        self.hide()
        
    def showEvent(self, event):
        self.setGeometry(self.parent().rect())
        self.raise_()
        self.setFocus()
        super().showEvent(event)
        
    def mousePressEvent(self, event):
        # Consume event
        event.accept()

    def paintEvent(self, event):
        # Semi-transparent dark overlay
        from PySide6.QtGui import QPainter, QBrush
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(0, 0, 0, 150))) 
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

class RestorePointDialog(QFrame):
    """
    The actual modal content window for Restore Suggestion.
    """
    accepted = Signal()
    rejected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("restoreDialog")
        self.setFixedSize(500, 350)
        
        self.setStyleSheet("""
            #restoreDialog {
                background-color: #1e1e2e;
                border: 1px solid #7aa2f7;
                border-radius: 12px;
            }
            QLabel { color: #e2e8f0; border: none; background: transparent; }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Рекомендуем создать точку восстановления")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        f_title = QFont()
        f_title.setPixelSize(20)
        f_title.setBold(True)
        title.setFont(f_title)
        
        desc = QLabel("Создать точку перед изменениями?")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #cbd5e1; font-size: 16px; margin-bottom: 20px;")

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_reject = QPushButton("Отклонить")
        btn_reject.setCursor(Qt.PointingHandCursor)
        btn_reject.setStyleSheet("""
            QPushButton {
                background-color: #2f334d;
                color: #94a3b8;
                border: 1px solid #414868;
            }
            QPushButton:hover {
                background-color: #3b4261;
                border: 1px solid #565f89;
                color: #cbd5e1;
            }
            QPushButton:pressed { background-color: #7aa2f7; }
        """)
        btn_reject.clicked.connect(self.rejected.emit)

        btn_create = QPushButton("Создать")
        btn_create.setCursor(Qt.PointingHandCursor)
        btn_create.setStyleSheet("""
            QPushButton {
                background-color: #7aa2f7;
                color: #1a1b26;
            }
            QPushButton:hover {
                background-color: #89b4fa;
            }
            QPushButton:pressed {
                background-color: #619af5;
                padding-top: 12px;
            }
        """)
        btn_create.clicked.connect(self.accepted.emit)

        btn_layout.addWidget(btn_reject)
        btn_layout.addWidget(btn_create)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()
        layout.addLayout(btn_layout)

class ConfirmationDialog(QFrame):
    accepted = Signal()
    rejected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("confirmDialog")
        self.setFixedSize(400, 200)
        
        self.setStyleSheet("""
            #confirmDialog {
                background-color: #1e1e2e;
                border: 1px solid #f7768e; 
                border-radius: 12px;
            }
            QLabel { color: #e2e8f0; border: none; background: transparent; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        self.lbl_title = QLabel("Подтверждение")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f7768e;")
        
        self.lbl_text = QLabel("Вы уверены?")
        self.lbl_text.setAlignment(Qt.AlignCenter)
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setStyleSheet("color: #cbd5e1; font-size: 14px;")

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #414868;
                border: 1px solid transparent;
                color: #ffffff;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover { 
                background-color: #565f89;
                border: 1px solid #f7768e;
            }
            QPushButton:pressed { background-color: #3b4261; }
        """)
        btn_cancel.clicked.connect(self.rejected.emit)

        btn_ok = QPushButton("Да, продолжить")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #f7768e;
                border: none;
                color: #1a1b26;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #ff9e64; }
            QPushButton:pressed { background-color: #d6647a; margin-top: 2px; }
        """)
        btn_ok.clicked.connect(self.accepted.emit)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_text)
        layout.addLayout(btn_layout)
    
    def set_content(self, title, text):
        self.lbl_title.setText(title)
        self.lbl_text.setText(text)

class SafetyManager(QWidget):
    """
    Manages modal dialogs for critical actions.
    Uses reusable dialog instances and proper overlay blocking.
    """
    restore_point_created = Signal()
    
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.resize(parent_window.size())
        self.hide()
        
        self.state = SafetyState.IDLE
        self._pending_action = None
        self._confirm_action = None
        
        self.overlay = ModalOverlay(self)
        
        # Init dialogs once and reuse
        self.restore_dialog = RestorePointDialog(self)
        self.restore_dialog.hide()
        self.restore_dialog.accepted.connect(self.on_create)
        self.restore_dialog.rejected.connect(self.on_reject)
        
        self.confirm_dialog = ConfirmationDialog(self)
        self.confirm_dialog.hide()
        self.confirm_dialog.accepted.connect(self.on_confirm_accepted)
        self.confirm_dialog.rejected.connect(self.close_all)
        
        self.center_dialogs()

    def center_dialogs(self):
        cx = self.width() // 2
        cy = self.height() // 2
        
        self.restore_dialog.move(cx - self.restore_dialog.width() // 2, cy - self.restore_dialog.height() // 2)
        self.confirm_dialog.move(cx - self.confirm_dialog.width() // 2, cy - self.confirm_dialog.height() // 2)

    def verify_and_run(self, action):
        from core.config import config
        if config.get("restore_point_suggested"):
            action()
        else:
            self._pending_action = action
            self.show_prompt()

    def show_prompt(self):
        self.state = SafetyState.PROMPT
        self.show()
        self.overlay.show()
        self.raise_()
        self.confirm_dialog.hide()
        
        self.restore_dialog.show()
        self.animate_window(self.restore_dialog)

    def show_confirmation(self, title, text, on_yes):
        """Shows generic confirmation reusing the dialog"""
        self.state = SafetyState.CONFIRM_GENERIC
        self._confirm_action = on_yes
        
        self.show()
        self.overlay.show()
        self.raise_()
        self.restore_dialog.hide()
        
        self.confirm_dialog.set_content(title, text)
        self.center_dialogs()
        
        self.confirm_dialog.show()
        self.animate_window(self.confirm_dialog)

    def animate_window(self, widget):
        self.anim = QPropertyAnimation(widget, b"windowOpacity")
        self.anim.setDuration(200)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def resizeEvent(self, event):
        self.overlay.resize(self.size())
        self.center_dialogs()
        super().resizeEvent(event)

    def on_create(self):
        from core.system import create_restore_point
        from core.config import config # imported locally to avoid circular import issues at toplevel if any
        
        # In a real async UI, we might want a progress spinner here in the modal
        # For this refactor we accept the synchronous call or move to thread if we had one here
        # But this method is usually fast enough for a modal unless creating specific point
        # Let's assume sync for now as per original code structure, or minimal blockage.
        
        success, msg = create_restore_point()
        if success:
            config.set("restore_point_suggested", True)
            self.restore_point_created.emit()
            self.close_all()
            if self._pending_action: self._pending_action()
        else:
            # We could show an error dialog on top, but for now we just close or log
            print(f"Error creating point: {msg}")
            self.close_all()
            if self._pending_action: self._pending_action()

    def on_reject(self):
        from core.config import config
        config.set("restore_point_suggested", True)
        self.close_all()
        if self._pending_action: self._pending_action()

    def on_confirm_accepted(self):
        self.close_all()
        if self._confirm_action:
            self._confirm_action()

    def close_all(self):
        self.state = SafetyState.IDLE
        self._pending_action = None
        self._confirm_action = None
        self.hide()
        self.overlay.hide()
        self.restore_dialog.hide()
        self.confirm_dialog.hide()

