from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect, QStackedWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, QRect, QEasingCurve, QSize, Qt
from PySide6.QtGui import QColor, QIcon

class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None, color_default="#24283b", color_hover="#3b4261", icon_path=None):
        super().__init__(text, parent)
        self.color_default = color_default
        self.color_hover = color_hover
        
        button_style = f"""
            QPushButton {{
                background-color: {self.color_default};
                border: 1px solid rgba(148, 163, 184, 0.1);
                border-radius: 8px;
                color: #cbd5e1;
                font-weight: 600;
                padding: 10px;
                text-align: center;
            }}
        """
        self.setStyleSheet(button_style)
        
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))

        # Drop Shadow for "Glow"
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)
        self.shadow.setColor(QColor(0, 0, 0, 0))
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)

        # Animation
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)

    def enterEvent(self, event):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color_hover};
                border: 1px solid #818cf8;
                border-radius: 8px;
                color: #ffffff;
                font-weight: 700;
                padding: 10px;
            }}
        """)
        self.shadow.setColor(QColor("#818cf8"))
        self.anim.setStartValue(0)
        self.anim.setEndValue(25)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color_default};
                border: 1px solid rgba(148, 163, 184, 0.1);
                border-radius: 8px;
                color: #cbd5e1;
                font-weight: 600;
                padding: 10px;
            }}
        """)
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(event)

class FadingStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(250)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.m_next_index = 0
        self.m_active = False

    def setCurrentIndex(self, index):
        if self.currentIndex() == index:
            return
            
        self.m_next_index = index
        self.fade_out()

    def fade_out(self):
        current = self.currentWidget()
        if not current:
            super().setCurrentIndex(self.m_next_index)
            return

        self.effect_out = QGraphicsOpacityEffect(current)
        current.setGraphicsEffect(self.effect_out)
        
        self.anim_out = QPropertyAnimation(self.effect_out, b"opacity")
        self.anim_out.setDuration(150)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.OutQuad)
        self.anim_out.finished.connect(self.on_fade_out_finished)
        self.anim_out.start()

    def on_fade_out_finished(self):
        super().setCurrentIndex(self.m_next_index)
        
        new_widget = self.currentWidget()
        if new_widget:
            self.effect_in = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(self.effect_in)
            
            self.anim_in = QPropertyAnimation(self.effect_in, b"opacity")
            self.anim_in.setDuration(250)
            self.anim_in.setStartValue(0.0)
            self.anim_in.setEndValue(1.0)
            self.anim_in.setEasingCurve(QEasingCurve.InQuad)
            self.anim_in.finished.connect(self.on_fade_in_finished)
            self.anim_in.start()

    def on_fade_in_finished(self):
        if self.currentWidget():
            self.currentWidget().setGraphicsEffect(None)
