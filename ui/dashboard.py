from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QPushButton, QSizePolicy, QMessageBox, QProgressDialog)
from PySide6.QtCore import Qt, QSize, QTimer, QThread, Signal
from PySide6.QtGui import QIcon
from utils.paths import get_assets_dir
from core.tweaks_registry import registry
from core.logger import logger
from core.i18n import I18n as _

class DashboardOptimizationThread(QThread):
    finished_optimizing = Signal(int)
    error = Signal(str)

    def __init__(self, recommended_ids, parent=None):
        super().__init__(parent)
        self.recommended_ids = recommended_ids

    def run(self):
        try:
            count = registry.apply_batch(self.recommended_ids)
            self.finished_optimizing.emit(count)
        except Exception as e:
            self.error.emit(str(e))

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 40)
        main_layout.setSpacing(25)

        # -- Top Cards --
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        assets = get_assets_dir()
        
        self.add_card(cards_layout, "Производительный", "Идеальное быстродействие", assets / "icons/diamond.svg", "#7aa2f7")
        self.add_card(cards_layout, "Энергосберегающий", "Баланс быстродействия", assets / "icons/leaf.svg", "#9ece6a")
        self.add_card(cards_layout, "Рискованный", "Максимум, без гарантий", assets / "icons/fire.svg", "#f7768e")
        self.add_card(cards_layout, "Пользовательский", "Индивидуальный набор", assets / "icons/settings.svg", "#e0af68")

        main_layout.addLayout(cards_layout)

        # -- Info Panels --
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)

        # Start Panel
        start_panel = QFrame()
        start_panel.setObjectName("infoPanel")
        sp_layout = QVBoxLayout(start_panel)
        sp_layout.setContentsMargins(30, 30, 30, 30)
        
        sp_title = QLabel(_.get("start_title"))
        sp_title.setAlignment(Qt.AlignCenter)
        sp_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;")
        
        sp_desc = QLabel(_.get("start_desc"))
        sp_desc.setAlignment(Qt.AlignCenter)
        sp_desc.setStyleSheet("color: #787c99; font-size: 14px; margin-bottom: 20px;")
        
        btn_start = QPushButton(_.get("start_optimization"))
        btn_start.setCursor(Qt.PointingHandCursor)
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #818cf8);
                color: white; 
                border-radius: 8px; 
                padding: 12px 24px;
                font-weight: 700;
                font-size: 14px;
                border: 1px solid #6366f1;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #4338ca, stop:1 #6366f1);
                border: 1px solid #818cf8;
            }
            QPushButton:pressed {
                 background-color: #3730a3;
            }
        """)

        btn_start.clicked.connect(self.on_start_optimization)

        sp_layout.addWidget(sp_title)
        sp_layout.addWidget(sp_desc)
        sp_layout.addWidget(btn_start, 0, Qt.AlignCenter)
        
        # Update Panel
        update_panel = QFrame()
        update_panel.setObjectName("infoPanel")
        up_layout = QVBoxLayout(update_panel)
        up_layout.setContentsMargins(30, 30, 30, 30)
        
        up_title = QLabel(_.get("update_info"))
        up_title.setAlignment(Qt.AlignCenter)
        up_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;")
        
        up_status = QLabel(_.get("version_info"))
        up_status.setAlignment(Qt.AlignCenter)
        up_status.setStyleSheet("color: #9ece6a; font-weight: bold; margin-bottom: 10px;")

        up_text = QLabel(
            "• Добавлен новый режим 'Рискованный'\n"
            "• Исправлены ошибки интерфейса\n"
            "• Улучшена производительность анимаций"
        )
        up_text.setStyleSheet("color: #94a3b8; font-size: 13px; line-height: 1.6;")
        up_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        up_layout.addWidget(up_title)
        up_layout.addWidget(up_status)
        up_layout.addWidget(up_text)
        up_layout.addStretch()

        info_layout.addWidget(start_panel)
        info_layout.addWidget(update_panel)

        main_layout.addLayout(info_layout)
        main_layout.addStretch()

    def add_card(self, layout, title, desc, icon_path, color):
        card = QFrame()
        card.setObjectName("card")
        
        base_style = """
            #card {
                background-color: rgba(30, 41, 59, 0.4);
                border: 1px solid rgba(148, 163, 184, 0.1);
                border-radius: 16px;
            }
        """
        
        card.setStyleSheet(base_style + f"""
            #card:hover {{
                background-color: rgba(30, 41, 59, 0.6);
                border: 1px solid {color};
            }}
        """)
        
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 30, 20, 30)
        c_layout.setSpacing(15)

        # Icon as QPushButton for interactivity and effects
        btn_icon = QPushButton()
        btn_icon.setFlat(True)
        btn_icon.setStyleSheet("background: transparent; border: none;")
        btn_icon.setCursor(Qt.PointingHandCursor)
        
        # Load icon via pathlib
        if icon_path and icon_path.exists():
            btn_icon.setIcon(QIcon(str(icon_path)))
            btn_icon.setIconSize(QSize(50, 50))
            
            # Simple hover effect via property check or simply stylesheets
            btn_icon.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                }}
                QPushButton:hover {{
                    border-radius: 25px;
                    background-color: {color}22; 
                }}
            """)

        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #f1f5f9;")

        lbl_desc = QLabel(desc)
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 500;")

        c_layout.addWidget(btn_icon, 0, Qt.AlignCenter)
        c_layout.addWidget(lbl_title)
        c_layout.addWidget(lbl_desc)
        
        layout.addWidget(card)

    def on_start_optimization(self):
        mw = self.window()
        
        if hasattr(mw, 'safety'):
             # Define the actual task
            def run_optimization():
                # For demo purposes, let's pretend we have a list of 'Recommended' IDs
                # In real app, this might come from a preset
                recommended_ids = ["disable_paging_exec", "large_system_cache", "power_plan"] 
                
                # Show progress
                progress = QProgressDialog("Применение настроек...", "Отмена", 0, 0, self)
                progress.setWindowModality(Qt.WindowModal)
                progress.setMinimumDuration(0)
                
                self.opt_thread = DashboardOptimizationThread(recommended_ids, self)
                
                def on_finished(count):
                    progress.accept()
                    QMessageBox.information(
                        self, 
                        _.get("success"), 
                        f"Успешно применено твиков: {count}\nСистема оптимизирована!"
                    )
                
                def on_error(err):
                    progress.accept()
                    QMessageBox.warning(self, _.get("error"), f"Ошибка при применении: {err}")
                
                self.opt_thread.finished_optimizing.connect(on_finished)
                self.opt_thread.error.connect(on_error)
                
                progress.canceled.connect(self.opt_thread.terminate) # Optional: basic cancellation
                
                self.opt_thread.start()
                progress.exec()
            
            # Verify and run calls the safety manager (creating restore point if needed)
            mw.safety.verify_and_run(run_optimization)
        else:
             QMessageBox.warning(self, _.get("error"), "Менеджер безопасности не найден")

