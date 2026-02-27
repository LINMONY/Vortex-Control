from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QScrollArea, QCheckBox, QSpacerItem, QSizePolicy, QPushButton)
from PySide6.QtCore import Qt, QThread, Signal
from typing import List, Dict
from core.tweak_models import TweakDefinition
from core.tweaks_registry import registry
from core.wmi_manager import RestorePointManager
from ui.components.toggle_switch import AnimatedToggleSwitch
from ui.components import AnimatedButton
from ui.dialogs import ApplyConfirmationDialog, ApplyProgressDialog, VortexMessageDialog
from core.hw_manager import HardwareManager

class TweaksApplyThread(QThread):
    # Detailed progress signals
    tweak_started = Signal(str, str, str)  # tid, name, status('WAIT')
    tweak_finished = Signal(str, str, str) # tid, name, status('DONE' or 'ERROR')
    batch_finished = Signal(int, int) # success_count, error_count
    restore_point_status = Signal(str, str, str) # id, text, status

    def __init__(self, target_states: Dict[str, bool], create_point: bool = False):
        super().__init__()
        self.target_states = target_states
        self.create_point = create_point
        self._is_aborted = False

    def abort(self):
        self._is_aborted = True

    def run(self):
        changes = {}
        for tid, desired in self.target_states.items():
            current = registry.get_status(tid)
            if current != desired:
                changes[tid] = desired

        if not changes:
            self.batch_finished.emit(0, 0)
            return

        success_count = 0
        error_count = 0
        total = len(changes)

        try:
            # 1. Restore Point if requested
            if self.create_point:
                self.restore_point_status.emit("restore", "Создание точки восстановления...", "WAIT")
                success, msg = RestorePointManager.create_point_wmi("Vortex Optimization Manual")
                if success:
                    self.restore_point_status.emit("restore", "Точка восстановления создана", "DONE")
                else:
                    self.restore_point_status.emit("restore", f"Ошибка создания точки: {msg}", "ERROR")
                    # We continue anyway if user just wants the tweaks, but we logged it.
            
            # 2. Iterate and apply
            for i, (tid, enable) in enumerate(changes.items()):
                if self._is_aborted:
                    break
                    
                tweak_def = registry.get(tid)
                name = tweak_def.name_ru if tweak_def else tid
                
                self.tweak_started.emit(tid, name, "WAIT")
                
                if enable:
                    success = registry.apply_tweak(tid)
                else:
                    success = registry.revert_tweak(tid)
                
                if success:
                    success_count += 1
                    self.tweak_finished.emit(tid, name, "DONE")
                else:
                    error_count += 1
                    self.tweak_finished.emit(tid, name, "ERROR")
            
            self.batch_finished.emit(success_count, error_count)
                
        except Exception as e:
            # This shouldn't normally happen with the registry handlers
            self.batch_finished.emit(success_count, 1)

class TweaksPage(QWidget):
    def __init__(self, title: str, items: List[TweakDefinition]):
        super().__init__()
        self.items = items
        self.active_tweaks: Dict[str, bool] = {} 
        self.switches: Dict[str, AnimatedToggleSwitch] = {} 
        
        for t in items:
            registry.register(t)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Scroll Area for Tweaks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 8px; background: transparent; }
            QScrollBar::handle:vertical { background: #475569; border-radius: 4px; }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(20, 20, 20, 100) # Large bottom margin for absolute button

        for tweak in items:
            self.add_tweak_item(self.content_layout, tweak)

        self.content_layout.addStretch()
        scroll.setWidget(content_widget)
        self.main_layout.addWidget(scroll)
        
        # Floating-style Apply Button (at bottom right)
        self.btn_apply = AnimatedButton("Применить изменения", color_default="#4f46e5", color_hover="#4338ca")
        self.btn_apply.setFixedSize(220, 50)
        self.btn_apply.clicked.connect(self.request_apply)
        
        # We overlay it or just add to layout. Let's use a small bottom container without the bar.
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(30, 10, 30, 20)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_apply)
        self.main_layout.addLayout(bottom_layout)

    def add_tweak_item(self, layout, tweak: TweakDefinition):
        frame = QFrame()
        frame.setObjectName("tweakItem")
        frame.setStyleSheet("""
            QFrame#tweakItem {
                background-color: #1a1b26;
                border: 1px solid #292e42;
                border-radius: 6px;
            }
            QFrame#tweakItem:hover {
                border: 1px solid #3b4261;
            }
        """)
        
        main_layout = QVBoxLayout(frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header Row
        header_widget = QWidget()
        row_layout = QHBoxLayout(header_widget)
        row_layout.setContentsMargins(20, 15, 20, 15)
        
        # Toggle details button / expander
        self.btn_expand = QPushButton("▶")
        self.btn_expand.setFixedSize(24, 24)
        self.btn_expand.setCursor(Qt.PointingHandCursor)
        self.btn_expand.setStyleSheet("QPushButton { color: #565f89; border: none; font-size: 14px; background: transparent; } QPushButton:hover { color: #7aa2f7; }")
        
        lbl = QLabel(tweak.name_ru)
        
        switch = AnimatedToggleSwitch()
        
        # Hardware compatibility check
        is_supported = HardwareManager.is_supported(tweak.hardware_tags)
        
        if is_supported:
            lbl.setStyleSheet("color: #c0caf5; font-size: 14px; font-weight: 600;")
        else:
            lbl.setText(f"{tweak.name_ru} ⚠️ (Не поддерживается)")
            lbl.setStyleSheet("color: #565f89; font-size: 14px; font-weight: 600;")
            switch.setEnabled(False)

        is_active = registry.get_status(tweak.id)
        switch.setChecked(is_active)
        
        self.active_tweaks[tweak.id] = is_active
        self.switches[tweak.id] = switch
        switch.stateChanged.connect(lambda state, t=tweak: self.on_tweak_toggled(t, state == 2))

        row_layout.addWidget(self.btn_expand)
        row_layout.addWidget(lbl)
        
        # Hardware Tag Badges
        if tweak.hardware_tags:
            for tag in tweak.hardware_tags:
                tag_lbl = QLabel(tag.replace("_", " "))
                bg_color = "#73daca" if "NVIDIA" in tag else "#f7768e" if "AMD" in tag else "#7aa2f7"
                tag_lbl.setStyleSheet(f"""
                    background-color: {bg_color}; color: #15161e; font-size: 10px; font-weight: bold;
                    padding: 2px 6px; border-radius: 4px; border: none;
                """)
                row_layout.addWidget(tag_lbl)
                
        row_layout.addStretch()
        row_layout.addWidget(switch)
        
        main_layout.addWidget(header_widget)
        
        # Details container
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(50, 0, 20, 15)
        details_layout.setSpacing(5)
        
        # We fill details if available
        d_text = tweak.detailed_info or tweak.tooltip or "Описание отсутствует."
        # Enable HTML breaking
        d_text = d_text.replace('\n', '<br>')
        if tweak.registry_path:
            d_text += f'<br><br>Путь: <a href="reg:{tweak.registry_path}" style="color: #73daca; text-decoration: none;">{tweak.registry_path}</a>'
            if tweak.value_name:
                d_text += f'<br>Ключ: {tweak.value_name} (Тип: {tweak.value_type})'
            
        lbl_details = QLabel(d_text)
        lbl_details.setTextFormat(Qt.RichText)
        lbl_details.setOpenExternalLinks(False)
        lbl_details.setWordWrap(True)
        lbl_details.setStyleSheet("QLabel { color: #565f89; font-size: 12px; font-family: Consolas, monospace; }")
        
        lbl_details.linkActivated.connect(self._handle_reg_link)
        details_layout.addWidget(lbl_details)
        
        details_widget.setVisible(False)
        main_layout.addWidget(details_widget)
        
        # Connect expand
        def toggle_details(checked=False, dw=details_widget, btn=self.btn_expand):
            is_visible = dw.isVisible()
            dw.setVisible(not is_visible)
            btn.setText("▼" if not is_visible else "▶")
            
        self.btn_expand.clicked.connect(toggle_details)

        layout.addWidget(frame)

    def _handle_reg_link(self, url: str):
        if url.startswith("reg:"):
            path = url[4:].strip().replace("/", "\\")
            try:
                import winreg, subprocess
                mapping = {
                    "HKLM": "HKEY_LOCAL_MACHINE",
                    "HKCU": "HKEY_CURRENT_USER",
                    "HKCR": "HKEY_CLASSES_ROOT",
                    "HKU": "HKEY_USERS",
                    "HKCC": "HKEY_CURRENT_CONFIG"
                }
                
                parts = path.split("\\")
                if parts[0].upper() in mapping:
                    parts[0] = mapping[parts[0].upper()]
                path = "\\".join(parts)
                
                root_name = "Computer"
                try:
                    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Applets\Regedit")
                    last_key, _ = winreg.QueryValueEx(k, "LastKey")
                    winreg.CloseKey(k)
                    if last_key:
                        root_name = last_key.split("\\")[0]
                except Exception:
                    root_name = "Компьютер" # Fallback RU
                    
                if not path.startswith(root_name + "\\"):
                    path = f"{root_name}\\{path}"
                    
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Applets\Regedit")
                winreg.SetValueEx(key, "LastKey", 0, winreg.REG_SZ, path)
                winreg.CloseKey(key)
                subprocess.Popen(["regedit.exe", "-m"], creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                from core.logger import logger
                logger.error(f"Failed to open regedit: {e}")

    def on_tweak_toggled(self, tweak, checked):
        self.active_tweaks[tweak.id] = checked

    def request_apply(self):
        # Calculate changes count
        changes_count = 0
        for tid, desired in self.active_tweaks.items():
            if registry.get_status(tid) != desired:
                changes_count += 1
        
        if changes_count == 0:
            VortexMessageDialog("Инфо", "Изменений не обнаружено.", parent=self).exec()
            return

        # 1. Confirmation Dialog
        confirm_dlg = ApplyConfirmationDialog(changes_count, self)
        if confirm_dlg.exec():
            action = confirm_dlg.result_action
            if action == 'cancel': return
            
            create_point = (action == 'create_and_apply')
            self.run_apply_process(create_point)

    def run_apply_process(self, create_point):
        # 2. Progress Dialog
        self.prog_dlg = ApplyProgressDialog(self)
        
        # 3. Thread
        self.worker = TweaksApplyThread(self.active_tweaks, create_point)
        
        # Track items to update existing log entries if needed, or just append
        # For simplicity, we append
        total_items = len([tid for tid, des in self.active_tweaks.items() if registry.get_status(tid) != des])
        if create_point: total_items += 1
        
        self.current_step = 0
        self.total_steps = total_items
        
        self.worker.restore_point_status.connect(lambda tid, txt, st: self._handle_log(tid, txt, st))
        self.worker.tweak_started.connect(lambda tid, txt, st: self._handle_log(tid, txt, st))
        self.worker.tweak_finished.connect(lambda tid, txt, st: self._handle_log(tid, txt, st, update=True))
        self.worker.batch_finished.connect(self.prog_dlg.finish_process)
        
        # Handle Cancel via new signal in the dialog
        self.prog_dlg.cancelRequested.connect(self.worker.abort)
        
        # Handle Close button in progress dialog
        self.prog_dlg.btn_close.clicked.connect(self.refresh_ui_states)
        
        self.worker.start()
        self.prog_dlg.exec()

    def _handle_log(self, process_id, text, status, update=False):
        self.prog_dlg.add_log(text, status, process_id)
        if status in ["DONE", "ERROR"]:
            self.current_step += 1
            self.prog_dlg.update_progress(self.current_step, self.total_steps)

    def refresh_ui_states(self):
        # Update switches to real status in case some failed
        for tid, switch in self.switches.items():
            real_val = registry.get_status(tid)
            switch.blockSignals(True)
            switch.setChecked(real_val)
            switch.blockSignals(False)
            self.active_tweaks[tid] = real_val

    def lock_ui(self, locked: bool):
        self.btn_apply.setEnabled(not locked)
        for s in self.switches.values():
            s.setEnabled(not locked)


