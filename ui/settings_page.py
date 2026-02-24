from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QPushButton, QListWidget, QListWidgetItem)
from PySide6.QtGui import QIcon, QColor
import platform

from ui.workers.restore_workers import DeleteThread, WmiScanThread, StorageScanThread
from ui.dialogs.restore_dialogs import VortexCreationDialog, VortexConfirmDialog, VortexMessageDialog
from core.i18n import I18n as _

class RestorePointWidget(QWidget):
    """
    Custom widget for restore point list items.
    Handles layout, styling, and signals for Restore/Delete actions.
    """
    restoreRequested = Signal(dict)
    deleteRequested = Signal(dict)

    def __init__(self, point_data, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.point_data = point_data
        
        # Main Horizontal Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(0)
        
        # Vertical Layout for Text (Name and Date)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        name = point_data.get('name', 'Unknown')
        timestamp = str(point_data.get('timestamp', 'Unknown Date'))
        
        self.lbl_name = QLabel(name)
        self.lbl_name.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; background: transparent;")
        
        self.lbl_date = QLabel(timestamp)
        self.lbl_date.setStyleSheet("color: #888888; font-size: 11px; font-weight: normal; background: transparent;")
        
        text_layout.addWidget(self.lbl_name)
        text_layout.addWidget(self.lbl_date)
        
        main_layout.addLayout(text_layout)
        
        # Stretch separates text and buttons
        main_layout.addStretch()
        
        # Buttons Horizontal Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.btn_restore = QPushButton(_.get("restore"))
        self.btn_restore.setCursor(Qt.PointingHandCursor)
        self.btn_restore.setMinimumWidth(100)
        self.btn_restore.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 2px solid #4ade80;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(74, 222, 128, 0.15);
            }
            QPushButton:pressed {
                background-color: rgba(74, 222, 128, 0.3);
            }
        """)
        self.btn_restore.clicked.connect(lambda: self.restoreRequested.emit(self.point_data))
        
        self.btn_delete = QPushButton(_.get("delete"))
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setMinimumWidth(100)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 2px solid #ff4d4d;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 77, 77, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(255, 77, 77, 0.4);
            }
        """)
        self.btn_delete.clicked.connect(lambda: self.deleteRequested.emit(self.point_data))
        
        btn_layout.addWidget(self.btn_restore)
        btn_layout.addWidget(self.btn_delete)
        
        main_layout.addLayout(btn_layout)

    def sizeHint(self):
        # Pixel perfect height for the list item
        return QSize(200, 64)

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 30, 40, 40)
        self.main_layout.setSpacing(25)
        
        self._active_threads = []

        # Header Row (Title + Storage)
        header_row = QHBoxLayout()
        header_text = QLabel(_.get("settings_title"))
        header_text.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        self.lbl_storage = QLabel(_.get("scanning_storage"))
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
        
        # 1. Restore Point Section
        self.create_restore_section()

        self.main_layout.addWidget(self.content_container)
        self.main_layout.addStretch()
        
        self.refresh_logs()
        self.refresh_storage()

    def get_dynamic_drives(self) -> str:
        """Returns string of Logical Disks e.g. (C, D)"""
        try:
            # Safe Fallback:
            import string
            from ctypes import windll
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter)
                bitmask >>= 1
            return ", ".join(drives)
        except:
            return "C"

    def refresh_storage(self):
        thread = StorageScanThread()
        thread.info_ready.connect(self.on_storage_info_ready)
        self._start_thread(thread)

    def on_storage_info_ready(self, info):
        gb = info.get('total_gb', 0)
        details = info.get('details', "")
        
        text = f"{_.get('storage_used')}: {gb:.2f} GB"
        self.lbl_storage.setText(text)
        self.lbl_storage.setToolTip(details)
        
        if gb > 20:
            self.lbl_storage.setStyleSheet("color: #eab308; font-size: 13px; font-weight: bold;")
        else:
            self.lbl_storage.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")

    def create_restore_section(self):
        # Section Title
        sec_title = QLabel(_.get("restore_manager"))
        sec_title.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: bold; text-transform: uppercase;")
        
        # Header Row
        header_row = QHBoxLayout()
        header_row.addWidget(sec_title)
        header_row.addStretch()
        
        btn_refresh = QPushButton(_.get("refresh"))
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
        
        drives_str = self.get_dynamic_drives()
        lbl_name = QLabel(f"{_.get('create_point_btn')} ({drives_str})")
        lbl_name.setStyleSheet("color: #e2e8f0; font-size: 16px; font-weight: 600;")
        
        btn_create = QPushButton(_.get("create"))
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

        # --- Points List using QListWidget ---
        self.logs_list = QListWidget()
        self.logs_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                margin-top: 10px;
            }
            QListWidget::item {
                background-color: rgba(30, 41, 59, 0.2);
                border-radius: 8px;
                border: 1px solid rgba(148, 163, 184, 0.05);
                margin-bottom: 8px;
            }
            QListWidget::item:hover {
                border: 1px solid rgba(129, 140, 248, 0.3);
            }
        """)
        self.content_layout.addWidget(self.logs_list)

    def refresh_logs(self):
        self.logs_list.clear()
        
        # Loading item
        item = QListWidgetItem(_.get("scan_system"))
        item.setTextAlignment(Qt.AlignCenter)
        self.logs_list.addItem(item)
        
        thread = WmiScanThread()
        thread.points_found.connect(self.on_points_loaded)
        self._start_thread(thread)

    def on_points_loaded(self, points):
        self.logs_list.clear() # Removes "Loading..."
        
        if not points:
            item = QListWidgetItem(_.get("system_ready"))
            item.setTextAlignment(Qt.AlignCenter)
            self.logs_list.addItem(item)
            return

        for p in points:
            # Reconstruct point_data for signals
            point_data = {
                'id': p.get('id'),
                'shadow_id': p.get('shadow_id'),
                'name': p.get('name'),
                'timestamp': p.get('timestamp')
            }
            
            # Use the new custom widget
            row_widget = RestorePointWidget(p)
            row_widget.restoreRequested.connect(self.request_restore_point)
            row_widget.deleteRequested.connect(self.request_delete_point)
            
            item = QListWidgetItem(self.logs_list)
            item.setSizeHint(row_widget.sizeHint())
            self.logs_list.setItemWidget(item, row_widget)

    def request_restore_point(self, point_data):
        if not point_data: return
        dlg = VortexConfirmDialog(_.get("restore"), 
                                f"{_.get('are_you_sure')} ({point_data.get('name')})", 
                                self)
        if dlg.exec():
            # Restoration logic would go here
            VortexMessageDialog(_.get("restore"), "Функция восстановления находится в разработке.", parent=self).exec()

    def request_create_point(self):
        dlg = VortexCreationDialog(self)
        if dlg.exec():
            success, msg = dlg.get_result()
            if success:
                self.refresh_logs()
                self.refresh_storage()
            else:
                VortexMessageDialog(_.get("error"), f"{msg}", is_error=True, parent=self).exec()
                self.refresh_logs()

    def request_delete_point(self, point_data):
        if not point_data: return
        # Adapt point_data to what perform_delete expects if needed
        # perform_delete expects {'shadow_id': ..., 'sequence_number': ...}
        adapted_data = {
            'shadow_id': point_data.get('shadow_id'),
            'sequence_number': point_data.get('id')
        }
        dlg = VortexConfirmDialog(_.get("delete"), _.get("are_you_sure"), self)
        if dlg.exec():
            self.perform_delete(adapted_data)

    def perform_delete(self, point_data):
        thread = DeleteThread(point_data)
        thread.finished.connect(self.on_delete_finished)
        self._start_thread(thread)
        
    def on_delete_finished(self, success, msg):
        if success:
            self.refresh_logs()
            self.refresh_storage()
        else:
            VortexMessageDialog(_.get("error"), f"{msg}", is_error=True, parent=self).exec()

    def _start_thread(self, thread):
        """Track and start a thread."""
        self._active_threads.append(thread)
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        thread.start()

    def _cleanup_thread(self, thread):
        if thread in self._active_threads:
            self._active_threads.remove(thread)
        thread.deleteLater()

