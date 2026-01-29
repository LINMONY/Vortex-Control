from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGraphicsBlurEffect, QGraphicsOpacityEffect, QLineEdit)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QFont

class ModalOverlay(QWidget):
    """
    Overlays the entire parent window with a semi-transparent background.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False) # Catch clicks
        self.hide()
        
    def showEvent(self, event):
        self.setGeometry(self.parent().rect())
        super().showEvent(event)

    def paintEvent(self, event):
        # Semi-transparent dark overlay
        from PySide6.QtGui import QPainter, QBrush
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(0, 0, 0, 150))) # Darken properly
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

class RestorePointDialog(QFrame):
    """
    The actual modal content window.
    """
    accepted = Signal()
    rejected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("restoreDialog")
        self.setFixedSize(500, 350)
        
        # Style logic to look like glass
        self.setStyleSheet("""
            #restoreDialog {
                background-color: #1e1b4b; /* Deep Indigo Background */
                border: 1px solid #4f46e5;
                border-radius: 16px;
            }
            QLabel {
                color: #e2e8f0;
            }
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

        # Title
        title = QLabel("Рекомендуем создать точку восстановления")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        f_title = QFont()
        f_title.setPixelSize(20)
        f_title.setBold(True)
        title.setFont(f_title)
        
        # Content
        # Content
        # Minimalist approach
        desc = QLabel("Создать точку перед изменениями?")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #cbd5e1; font-size: 16px; margin-bottom: 20px;")

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_reject = QPushButton("Отклонить")
        btn_reject.setCursor(Qt.PointingHandCursor)
        btn_reject.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: 1px solid #334155;
            }
            QPushButton:hover {
                border: 1px solid #475569;
                color: #cbd5e1;
            }
        """)
        btn_reject.clicked.connect(self.rejected.emit)

        btn_create = QPushButton("Создать")
        btn_create.setCursor(Qt.PointingHandCursor)
        btn_create.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
            }
            QPushButton:hover {
                background-color: #4338ca;
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
    """
    Generic confirmation modal.
    """
    accepted = Signal()
    rejected = Signal()

    def __init__(self, parent=None, title="Подтверждение", text="Вы уверены?"):
        super().__init__(parent)
        self.setObjectName("confirmDialog")
        self.setFixedSize(400, 200)
        
        self.setStyleSheet("""
            #confirmDialog {
                background-color: #1e1b4b;
                border: 1px solid #ef4444; /* Red border for alert */
                border-radius: 16px;
            }
            QLabel { color: #e2e8f0; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ef4444;")
        
        lbl_text = QLabel(text)
        lbl_text.setAlignment(Qt.AlignCenter)
        lbl_text.setWordWrap(True)
        lbl_text.setStyleSheet("color: #cbd5e1; font-size: 14px;")

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #475569;
                color: #cbd5e1;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.05); }
        """)
        btn_cancel.clicked.connect(self.rejected.emit)

        btn_ok = QPushButton("Да, удалить")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                border: none;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #dc2626; }
        """)
        btn_ok.clicked.connect(self.accepted.emit)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_text)
        layout.addLayout(btn_layout)

class SafetyManager(QWidget):
    """
    Manager widget - Updated to handle custom confirmations too.
    """
    restore_point_created = Signal()
    
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.resize(parent_window.size())
        self.hide()
        
        self._pending_action = None
        self._confirm_action = None
        
        self.overlay = ModalOverlay(self)
        
        # Restore Dialog
        self.restore_dialog = RestorePointDialog(self)
        self.restore_dialog.hide()
        self.restore_dialog.accepted.connect(self.on_create)
        self.restore_dialog.rejected.connect(self.on_reject)
        
        # Confirmation Dialog (Lazy init or generic hidden)
        self.confirm_dialog = ConfirmationDialog(self)
        self.confirm_dialog.hide()
        self.confirm_dialog.accepted.connect(self.on_confirm_accepted)
        self.confirm_dialog.rejected.connect(self.close_all)
        
        # Center dialogs
        self.center_dialogs()

    def center_dialogs(self):
        cx = self.width() // 2
        cy = self.height() // 2
        
        self.restore_dialog.move(cx - self.restore_dialog.width() // 2, cy - self.restore_dialog.height() // 2)
        self.confirm_dialog.move(cx - self.confirm_dialog.width() // 2, cy - self.confirm_dialog.height() // 2)

    def verify_and_run(self, action):
        from core.config import ConfigManager
        if ConfigManager().get("restore_point_suggested"):
            action()
        else:
            self._pending_action = action
            self.show_prompt()

    def show_prompt(self):
        self.show()
        self.overlay.show()
        self.raise_()
        self.confirm_dialog.hide()
        
        self.restore_dialog.show()
        self.animate_window(self.restore_dialog)

    def show_confirmation(self, title, text, on_yes):
        """Shows generic confirmation"""
        self._confirm_action = on_yes
        self.show()
        self.overlay.show()
        self.raise_()
        self.restore_dialog.hide()
        
        # Update text
        # Since we instantiated it once, we might want to recreate or update labels? 
        # For simplicity, we assume fixed text or quick hacks to findChildren if dynamic needed.
        # But better: Just recreate it or update it.
        # Recreating for flexibility in prototype:
        self.confirm_dialog.deleteLater()
        self.confirm_dialog = ConfirmationDialog(self, title, text)
        self.confirm_dialog.accepted.connect(self.on_confirm_accepted)
        self.confirm_dialog.rejected.connect(self.close_all)
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
        from core.config import ConfigManager
        print("Creating restore point...")
        success, msg = create_restore_point()
        if success:
            print("Done!", msg)
            ConfigManager().set("restore_point_suggested", True)
            self.restore_point_created.emit()
            self.close_all()
            if self._pending_action: self._pending_action()
        else:
            print("Error:", msg)
            self.close_all()
            if self._pending_action: self._pending_action()

    def on_reject(self):
        from core.config import ConfigManager
        ConfigManager().set("restore_point_suggested", True)
        self.close_all()
        if self._pending_action: self._pending_action()

    def on_confirm_accepted(self):
        self.close_all()
        if self._confirm_action:
            self._confirm_action()

    def close_all(self):
        self._pending_action = None
        self._confirm_action = None
        self.hide()
        self.overlay.hide()
        self.restore_dialog.hide()
        self.confirm_dialog.hide()
