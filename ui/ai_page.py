from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class AIPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        self.label = QLabel("AI Оптимизация — В разработке")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            color: #7aa2f7;
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        
        layout.addWidget(self.label)
