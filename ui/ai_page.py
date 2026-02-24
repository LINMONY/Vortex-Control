from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                               QFrame, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

class AIPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(25)
        
        # Header Section
        header_layout = QVBoxLayout()
        title_lbl = QLabel("AI Оптимизация")
        title_lbl.setStyleSheet("color: white; font-size: 24px; font-weight: 700;")
        
        desc_lbl = QLabel("Автоматический анализ и настройка системы под ваши задачи.\n(В разработке для версии 2.0)")
        desc_lbl.setStyleSheet("color: #94a3b8; font-size: 14px;")
        
        header_layout.addWidget(title_lbl)
        header_layout.addWidget(desc_lbl)
        layout.addLayout(header_layout)
        
        # Feature placeholder list
        features_frame = QFrame()
        features_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.4);
                border-radius: 12px;
                border: 1px solid rgba(148, 163, 184, 0.1);
            }
        """)
        feat_layout = QVBoxLayout(features_frame)
        feat_layout.setContentsMargins(20, 20, 20, 20)
        feat_layout.setSpacing(15)
        
        # Features to come
        features = [
            "Глубокий анализ системных процессов",
            "Автоматическая подстройка приоритетов CPU/RAM",
            "Оптимизация сетевого стека под текущую задачу",
            "Интеллектуальное управление питанием"
        ]
        
        lbl_coming = QLabel("Будущие возможности:")
        lbl_coming.setStyleSheet("color: #7aa2f7; font-weight: bold; font-size: 15px; margin-bottom: 5px;")
        feat_layout.addWidget(lbl_coming)
        
        for feat in features:
            f_row = QHBoxLayout()
            # Fake checkmark or bullet
            bullet = QLabel("◈") 
            bullet.setStyleSheet("color: #7aa2f7; font-size: 12px;")
            
            f_lbl = QLabel(feat)
            f_lbl.setStyleSheet("color: #cbd5e1; font-size: 14px;")
            
            f_row.addWidget(bullet)
            f_row.addWidget(f_lbl)
            f_row.addStretch()
            feat_layout.addLayout(f_row)
            
        layout.addWidget(features_frame)
        
        layout.addStretch()
        
        # Action Button (Disabled/Placeholder)
        btn_scan = QPushButton("Запустить анализ системы")
        btn_scan.setFixedWidth(250)
        btn_scan.setCursor(Qt.PointingHandCursor)
        # Styled similar to dashboard button but maybe different tone or disabled look
        btn_scan.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 41, 59, 0.5);
                color: #64748b; 
                border-radius: 8px; 
                padding: 12px 24px;
                font-weight: 700;
                font-size: 14px;
                border: 1px solid #334155;
            }
            QPushButton:hover {
                 background-color: rgba(30, 41, 59, 0.7);
                 color: #94a3b8;
            }
        """)
        btn_scan.clicked.connect(self.show_coming_soon)
        
        # Center the button
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(btn_scan)
        center_layout.addStretch()
        
        layout.addLayout(center_layout)

    def show_coming_soon(self):
        QMessageBox.information(self, "AI Оптимизация", "Этот модуль находится в активной разработке.\nСледите за обновлениями Vortex Control!")

