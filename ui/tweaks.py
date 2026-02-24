from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QScrollArea, QCheckBox, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal
from typing import List, Dict
from core.tweak_models import TweakDefinition
from core.tweaks_registry import registry
from core.wmi_manager import RestorePointManager
from ui.components.toggle_switch import AnimatedToggleSwitch
from ui.components import AnimatedButton
from ui.dialogs import ApplyConfirmationDialog, ApplyProgressDialog, VortexMessageDialog

class TweaksApplyThread(QThread):
    # Detailed progress signals
    tweak_started = Signal(str, str)  # name, status('WAIT')
    tweak_finished = Signal(str, str) # name, status('DONE' or 'ERROR')
    batch_finished = Signal(int, int) # success_count, error_count
    restore_point_status = Signal(str, str) # text, status

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
                self.restore_point_status.emit("Создание точки восстановления...", "WAIT")
                success, msg = RestorePointManager.create_point_wmi("Vortex Optimization Manual")
                if success:
                    self.restore_point_status.emit("Точка восстановления создана", "DONE")
                else:
                    self.restore_point_status.emit(f"Ошибка создания точки: {msg}", "ERROR")
                    # We continue anyway if user just wants the tweaks, but we logged it.
            
            # 2. Iterate and apply
            for i, (tid, enable) in enumerate(changes.items()):
                if self._is_aborted:
                    break
                    
                tweak_def = registry.get(tid)
                name = tweak_def.name_ru if tweak_def else tid
                
                self.tweak_started.emit(name, "WAIT")
                
                if enable:
                    success = registry.apply_tweak(tid, create_checkpoint=False)
                else:
                    success = registry.revert_tweak(tid)
                
                if success:
                    success_count += 1
                    self.tweak_finished.emit(name, "DONE")
                else:
                    error_count += 1
                    self.tweak_finished.emit(name, "ERROR")
            
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
            #tweakItem {
                background-color: rgba(30, 41, 59, 0.4);
                border-radius: 12px;
                border: 1px solid rgba(148, 163, 184, 0.1);
                min-height: 60px;
            }
            #tweakItem:hover {
                background-color: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(122, 162, 247, 0.3);
            }
        """)
        
        row_layout = QHBoxLayout(frame)
        row_layout.setContentsMargins(25, 12, 25, 12)
        
        lbl = QLabel(tweak.name_ru)
        lbl.setStyleSheet("color: #e2e8f0; font-size: 15px; font-weight: 500;")
        if tweak.tooltip:
            frame.setToolTip(tweak.tooltip)
        
        switch = AnimatedToggleSwitch()
        is_active = registry.get_status(tweak.id)
        switch.setChecked(is_active)
        
        self.active_tweaks[tweak.id] = is_active
        self.switches[tweak.id] = switch
        
        switch.stateChanged.connect(lambda state, t=tweak: self.on_tweak_toggled(t, state == 2))

        row_layout.addWidget(lbl)
        row_layout.addStretch()
        row_layout.addWidget(switch)
        layout.addWidget(frame)

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
        
        self.worker.restore_point_status.connect(lambda txt, st: self._handle_log(txt, st))
        self.worker.tweak_started.connect(lambda txt, st: self._handle_log(txt, st))
        self.worker.tweak_finished.connect(lambda txt, st: self._handle_log(txt, st, update=True))
        self.worker.batch_finished.connect(self.prog_dlg.finish_process)
        
        # Handle Close button in progress dialog
        self.prog_dlg.btn_close.clicked.connect(self.refresh_ui_states)
        
        self.worker.start()
        self.prog_dlg.exec()

    def _handle_log(self, text, status, update=False):
        if status == "WAIT" and not update:
            self.prog_dlg.add_log(text, status)
        else:
            # If update, ideally we find the last item and change its status
            # But add_log with DONE/ERROR works too for sequential flow
            self.prog_dlg.add_log(text, status)
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


