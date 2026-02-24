"""
Worker threads for restore point operations.
"""
from PySide6.QtCore import QThread, Signal
from core.wmi_manager import RestorePointManager
from core.system import delete_restore_point_system
from core.system import create_restore_point

class CreateThread(QThread):
    finished = Signal(bool, str)
    def __init__(self, name):
        super().__init__()
        self.name = name
    def run(self):
        success, msg = create_restore_point(self.name)
        self.finished.emit(success, msg)

class DeleteThread(QThread):
    finished = Signal(bool, str)
    def __init__(self, point_data):
        super().__init__()
        self.point_data = point_data
    def run(self):
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
