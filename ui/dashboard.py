from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QPushButton, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from ui.components import AnimatedButton
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 40)
        main_layout.setSpacing(25)

        # -- Top Cards --
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        self.add_card(cards_layout, "Производительный", "Идеальное быстродействие", os.path.join(ASSETS_DIR, "icons/diamond.svg"), "#7aa2f7")
        self.add_card(cards_layout, "Энергосберегающий", "Баланс быстродействия", os.path.join(ASSETS_DIR, "icons/leaf.svg"), "#9ece6a")
        self.add_card(cards_layout, "Рискованный", "Максимум, без гарантий", os.path.join(ASSETS_DIR, "icons/fire.svg"), "#f7768e")
        self.add_card(cards_layout, "Пользовательский", "Индивидуальный набор", os.path.join(ASSETS_DIR, "icons/settings.svg"), "#e0af68")

        main_layout.addLayout(cards_layout)

        # -- Info Panels --
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)

        # Start Panel
        start_panel = QFrame()
        start_panel.setObjectName("infoPanel")
        sp_layout = QVBoxLayout(start_panel)
        sp_layout.setContentsMargins(30, 30, 30, 30)
        
        sp_title = QLabel("Начало использования")
        sp_title.setAlignment(Qt.AlignCenter)
        sp_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;")
        
        sp_desc = QLabel("Нажмите кнопку ниже, чтобы применить\nрекомендованные настройки.")
        sp_desc.setAlignment(Qt.AlignCenter)
        sp_desc.setStyleSheet("color: #787c99; font-size: 14px; margin-bottom: 20px;")
        
        btn_start = QPushButton("Начать оптимизацию")
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
        
        up_title = QLabel("Информация обновлений")
        up_title.setAlignment(Qt.AlignCenter)
        up_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;")
        
        up_status = QLabel("У вас актуальная версия: 1.2.0")
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

        # Icon
        lbl_icon = QLabel()
        lbl_icon.setAlignment(Qt.AlignCenter)
        if icon_path:
            # Add a subtle glow/drop shadow to the icon if possible? 
            # For now just properly sized.
            lbl_icon.setPixmap(QIcon(icon_path).pixmap(52, 52))

        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #f1f5f9;")

        lbl_desc = QLabel(desc)
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 500;")

        c_layout.addWidget(lbl_icon)
        c_layout.addWidget(lbl_title)
        c_layout.addWidget(lbl_desc)
        
        layout.addWidget(card)

    def on_start_optimization(self):
        mw = self.window()
        if hasattr(mw, 'safety'):
            # Define what to do after safety check passes
            def run_optimization():
                print(">>> STARTING OPTIMIZATION PHASE... (Tweaks to be applied here)")
            
            mw.safety.verify_and_run(run_optimization)
        else:
            print("Safety manager not found")
