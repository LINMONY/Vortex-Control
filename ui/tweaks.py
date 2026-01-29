from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QScrollArea, QCheckBox, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt

class TweaksPage(QWidget):
    def __init__(self, title, items):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header for the page (optional, user screenshot doesn't explicitly show a big header on the page itself, 
        # but it helps context)
        # header = QLabel(title)
        # header.setProperty("class", "header")
        # layout.addWidget(header)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;") # Make scroll area transparent
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)

        for item_text in items:
            self.add_tweak_item(content_layout, item_text)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def add_tweak_item(self, layout, text):
        frame = QFrame()
        frame.setObjectName("tweakItem")
        frame.setStyleSheet("""
            #tweakItem {
                background-color: rgba(30, 41, 59, 0.4);
                border-radius: 8px;
                border: 1px solid rgba(148, 163, 184, 0.05);
                min-height: 56px;
            }
            #tweakItem:hover {
                background-color: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(129, 140, 248, 0.3);
            }
        """)
        
        row_layout = QHBoxLayout(frame)
        row_layout.setContentsMargins(20, 10, 20, 10)
        
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #e2e8f0; font-size: 14px; font-weight: 500;")
        
        switch = QCheckBox()
        switch.setCursor(Qt.PointingHandCursor)
        # Styling the switch (QCheckBox) - inheriting mostly from global styles but ensuring size
        # We can rely on global QCheckBox styles in styles.qss for consistency!
        # Just ensure no overriding here unless needed.
        # But for the "knob" animation hack we might need something, but styles.qss handles standard indicator well.
        # Let's trust styles.qss for the clean consistency.

        row_layout.addWidget(lbl)
        row_layout.addStretch()
        row_layout.addWidget(switch)
        
        layout.addWidget(frame)
