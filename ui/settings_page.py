from PySide6.QtCore import Qt, QSize, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QPushButton, QDialog, QLineEdit, QGraphicsDropShadowEffect, QProgressBar)
from PySide6.QtGui import QIcon, QColor
from core.wmi_manager import RestorePointManager
from core.system import delete_restore_point_system
import os

class CreateThread(QThread):
    finished = Signal(bool, str)
    def __init__(self, name):
        super().__init__()
        self.name = name
    def run(self):
        from core.system import create_restore_point
        success, msg = create_restore_point(self.name)
        self.finished.emit(success, msg)

class DeleteThread(QThread):
    finished = Signal(bool, str)
    def __init__(self, point_data):
        super().__init__()
        self.point_data = point_data
    def run(self):
        from core.system import delete_restore_point_system
        success, msg = delete_restore_point_system(self.point_data)
        self.finished.emit(success, msg)

class WmiScanThread(QThread):
    points_found = Signal(list)
    
    def run(self):
        points = RestorePointManager.get_all_restore_points()
        self.points_found.emit(points)

class StorageScanThread(QThread):
    info_ready = Signal(dict)
    def run(self):
        info = RestorePointManager.get_vss_storage_info()
        self.info_ready.emit(info)

class VortexCreationDialog(QDialog):
    """
    Custom Frameless Creation Dialog with indeterminate progress bar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 380)
        
        self.state = "INPUT" # INPUT -> CONFIRM -> PROGRESS
        self.result_name = None
        self.success = False
        self.error_msg = ""

        # Container Frame for styling
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 500, 380)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1a1b26; 
                border: 1px solid #414868;
                border-radius: 20px;
            }
            QLabel { color: #c0caf5; }
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
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        # 1. Header
        self.lbl_title = QLabel("ЗАЩИТА СИСТЕМЫ")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; letter-spacing: 1px;")
        
        # 2. Warning / Desc
        self.lbl_desc = QLabel(
            "Внимание! Рекомендуется создавать точку перед любыми изменениями. Это ваш страховочный трос."
        )
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setAlignment(Qt.AlignCenter)
        self.lbl_desc.setStyleSheet("color: #94a3b8; font-size: 14px; line-height: 1.4;")

        # 3. Input
        self.prefix = "VORTEX-"
        self.input_field = QLineEdit(self.prefix)
        self.input_field.textChanged.connect(self.on_text_changed)
        self.input_field.cursorPositionChanged.connect(self.on_cursor_changed)
        
        # 4. Progress (Animated Purple Gradient)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate mode
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
                background-color: transparent;
                border: 1px solid #565f89;
                color: #a9b1d6;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.05); color: white; }
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
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #89b4fa; }
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
            self.lbl_desc.setStyleSheet("color: #c0caf5; font-size: 16px; font-weight: 500;")
            
            self.btn_action.setText("ПОДТВЕРДИТЬ")
            self.btn_action.setStyleSheet("""
                QPushButton {
                    background-color: #9ece6a; color: #1a1b26; border: none; border-radius: 10px; font-weight: bold;
                }
                QPushButton:hover { background-color: #b9f27c; }
            """)
            self.btn_cancel.setStyleSheet("""
                QPushButton {
                    background-color: transparent; border: 1px solid #f7768e; color: #f7768e; border-radius: 10px; font-weight: bold;
                }
                QPushButton:hover { background-color: rgba(247, 118, 142, 0.1); }
            """)
            
        elif self.state == "CONFIRM":
            self.state = "PROGRESS"
            self.result_name = self.input_field.text()
            
            self.lbl_title.setText("СОЗДАНИЕ")
            self.lbl_desc.setText("Создание снимка системы (C, E, F)...\nПожалуйста, подождите.")
            self.lbl_desc.setStyleSheet("color: #7aa2f7; font-size: 14px;")
            
            self.btn_action.hide()
            self.btn_cancel.hide()
            self.progress.show()
            
            self.thread = CreateThread(self.result_name)
            self.thread.finished.connect(self.on_creation_finished)
            self.thread.start()

    def on_creation_finished(self, success, msg):
        self.success = success
        self.error_msg = msg
        self.accept()

    def get_result(self):
        return self.success, self.error_msg

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 30, 40, 40)
        self.main_layout.setSpacing(25)

        # Header Row (Title + Storage)
        header_row = QHBoxLayout()
        header_text = QLabel("Настройки системы")
        header_text.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        self.lbl_storage = QLabel("Место: сканирование...")
        self.lbl_storage.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
        
        header_row.addWidget(header_text)
        header_row.addStretch()
        header_row.addWidget(self.lbl_storage)
        self.main_layout.addLayout(header_row)

        # Content Container
        self.content_container = QFrame()
        self.content_container.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(15)
        
        # Threads
        self.scan_thread = WmiScanThread()
        self.scan_thread.points_found.connect(self.on_points_loaded)
        
        self.storage_thread = StorageScanThread()
        self.storage_thread.info_ready.connect(self.on_storage_info_ready)

        # 1. Restore Point Section
        self.create_restore_section()

        self.main_layout.addWidget(self.content_container)
        self.main_layout.addStretch()
        
        self.refresh_logs()
        self.refresh_storage()

    def refresh_storage(self):
        self.storage_thread.start()

    def on_storage_info_ready(self, info):
        gb = info.get('total_gb', 0)
        details = info.get('details', "")
        
        text = f"Занято точками: {gb:.2f} GB"
        self.lbl_storage.setText(text)
        self.lbl_storage.setToolTip(details)
        
        if gb > 20:
            self.lbl_storage.setStyleSheet("color: #eab308; font-size: 13px; font-weight: bold;") # Amber/Yellow
        else:
            self.lbl_storage.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")

    def create_restore_section(self):
        # Section Title
        sec_title = QLabel("Менеджер точек восстановления (System Restore)")
        sec_title.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: bold; text-transform: uppercase;")
        
        # Header Row
        header_row = QHBoxLayout()
        header_row.addWidget(sec_title)
        header_row.addStretch()
        
        btn_refresh = QPushButton("Обновить")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setStyleSheet("color: #7aa2f7; border: 1px solid #7aa2f7; border-radius: 4px; padding: 4px 10px; background: transparent;")
        btn_refresh.clicked.connect(self.refresh_logs)
        header_row.addWidget(btn_refresh)
        
        self.content_layout.addLayout(header_row)

        # --- Main Action Row (Create New) ---
        self.action_row = QFrame()
        self.action_row.setObjectName("settingRow")
        self.action_row.setStyleSheet("""
            #settingRow {
                background-color: rgba(30, 41, 59, 0.4);
                border-radius: 12px;
                border: 1px solid rgba(148, 163, 184, 0.1);
            }
            #settingRow:hover {
                background-color: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(129, 140, 248, 0.3);
            }
        """)
        
        ar_layout = QHBoxLayout(self.action_row)
        ar_layout.setContentsMargins(20, 15, 20, 15)
        
        lbl_name = QLabel("Создать новую точку")
        lbl_name.setStyleSheet("color: #e2e8f0; font-size: 16px; font-weight: 600;")
        
        btn_create = QPushButton("Создать")
        btn_create.setCursor(Qt.PointingHandCursor)
        btn_create.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4338ca; }
        """)
        btn_create.clicked.connect(self.request_create_point)

        ar_layout.addWidget(lbl_name)
        ar_layout.addStretch()
        ar_layout.addWidget(btn_create)

        self.content_layout.addWidget(self.action_row)

        # --- Points List ---
        self.logs_container = QFrame()
        self.logs_container.setObjectName("logsContainer")
        self.logs_container.setStyleSheet("background: transparent;")
        self.logs_layout = QVBoxLayout(self.logs_container)
        self.logs_layout.setContentsMargins(10, 0, 10, 0)
        self.logs_layout.setSpacing(10)
        
        self.content_layout.addWidget(self.logs_container)

    def refresh_logs(self):
        while self.logs_layout.count():
            item = self.logs_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
                
        lbl_loading = QLabel("Сканирование системы...")
        lbl_loading.setStyleSheet("color: #64748b; font-style: italic;")
        lbl_loading.setAlignment(Qt.AlignCenter)
        self.logs_layout.addWidget(lbl_loading)
        
        self.scan_thread.start()

    def on_points_loaded(self, points):
        while self.logs_layout.count():
            item = self.logs_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
                
        if not points:
            lbl = QLabel("Система готова к созданию первой точки")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #64748b; font-style: italic;")
            self.logs_layout.addWidget(lbl)
            return

        for p in points:
            row = self.create_point_row(p)
            self.logs_layout.addWidget(row)

    def create_point_row(self, point):
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.2);
                border-radius: 8px;
                border: 1px solid rgba(148, 163, 184, 0.05);
            }
        """)
        row.setFixedHeight(50)
        
        lyt = QHBoxLayout(row)
        lyt.setContentsMargins(25, 0, 25, 0)
        lyt.setAlignment(Qt.AlignVCenter)
        
        # Name
        lbl_name = QLabel(point.get('name'))
        lbl_name.setStyleSheet("color: #cbd5e1; font-weight: 600; font-size: 14px;")
        
        # Timestamp
        lbl_time = QLabel(str(point.get('timestamp')))
        lbl_time.setFixedWidth(180) # 180px fixed
        lbl_time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_time.setStyleSheet("color: #7aa2f7; font-weight: 500; font-family: 'Consolas', monospace; padding-right: 15px;")
        
        # Identifiers
        point_data = {
            'shadow_id': point.get('shadow_id'),
            'sequence_number': point.get('id')
        }

        # Delete Button
        btn_del = QPushButton("Удалить")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setFixedSize(70, 28)
        btn_del.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ef4444;
                border: 1px solid #ef4444;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: white;
            }
        """)
        btn_del.clicked.connect(lambda checked=False, p=point_data: self.request_delete_point(p))

        lyt.addWidget(lbl_name)
        lyt.addStretch()
        lyt.addWidget(lbl_time)
        lyt.addSpacing(40)
        lyt.addWidget(btn_del)
        
        return row

    def request_create_point(self):
        dlg = VortexCreationDialog(self)
        if dlg.exec():
            # Dialog handles creation and thread now
            success, msg = dlg.get_result()
            if success:
                self.refresh_logs()
                self.refresh_storage()
            else:
                err_dlg = VortexMessageDialog("Ошибка создания", f"Не удалось создать точку:\n{msg}", is_error=True, parent=self)
                err_dlg.exec()
                self.refresh_logs()

    def request_delete_point(self, point_data):
        if not point_data:
             return

        # Local Custom Confirm Dialog
        dlg = VortexConfirmDialog("Удаление", "Вы уверены? Это действие удалит выбранную точку восстановления навсегда.", self)
        if dlg.exec():
             self.perform_delete(point_data)

    def perform_delete(self, point_data):
        # Run in background to prevent freeze
        self._del_thread = DeleteThread(point_data)
        self._del_thread.finished.connect(self.on_delete_finished)
        self._del_thread.start()
        
    def on_delete_finished(self, success, msg):
        if success:
            self.refresh_logs()
            self.refresh_storage()
        else:
            # Show error nicely
            dlg = VortexMessageDialog("Ошибка удаления", f"Не удалось удалить точку:\n{msg}", is_error=True, parent=self)
            dlg.exec()

class VortexConfirmDialog(QDialog):
    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1b26;
                border: 1px solid #f7768e;
                border-radius: 15px;
            }
            QLabel { color: #c0caf5; }
            QPushButton {
                 border-radius: 8px; font-weight: bold; padding: 8px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        
        l_title = QLabel(title)
        l_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f7768e;")
        l_title.setAlignment(Qt.AlignCenter)
        
        l_text = QLabel(text)
        l_text.setWordWrap(True)
        l_text.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(l_title)
        layout.addWidget(l_text)
        
        btns = QHBoxLayout()
        b_ca = QPushButton("Отмена")
        b_ca.clicked.connect(self.reject)
        b_ca.setStyleSheet("background: transparent; color: #a9b1d6; border: 1px solid #565f89;")
        
        b_ok = QPushButton("Удалить")
        b_ok.clicked.connect(self.accept)
        b_ok.setStyleSheet("background: #f7768e; color: #1a1b26; border: none;")
        
        btns.addWidget(b_ca)
        btns.addWidget(b_ok)
        layout.addLayout(btns)

class VortexMessageDialog(QDialog):
    def __init__(self, title, text, is_error=False, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(400, 200)
        
        color = "#f7768e" if is_error else "#7aa2f7"
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #1a1b26;
                border: 1px solid {color};
                border-radius: 15px;
            }}
            QLabel {{ color: #c0caf5; }}
            QPushButton {{
                 border-radius: 8px; font-weight: bold; padding: 8px;
                 background-color: {color}; color: #1a1b26; border: none;
            }}
            QPushButton:hover {{ background-color: {color}99; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        
        l_title = QLabel(title)
        l_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        l_title.setAlignment(Qt.AlignCenter)
        
        l_text = QLabel(text)
        l_text.setWordWrap(True)
        l_text.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(l_title)
        layout.addWidget(l_text)
        
        b_ok = QPushButton("OK")
        b_ok.clicked.connect(self.accept)
        layout.addWidget(b_ok)
