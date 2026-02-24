from PySide6.QtWidgets import QCheckBox, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRectF, Property, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPainterPath

class AnimatedToggleSwitch(QCheckBox):
    """
    Premium Animated Toggle Switch (iOS style).
    - Smooth slider animation (300ms, OutBack easing)
    - Color transitions (OFF -> ON)
    - Glow effects and shadows
    """
    
    def __init__(self, parent=None, width=50, height=26):
        super().__init__(parent)
        
        # Dimensions
        self.setFixedSize(width, height)
        self.setCursor(Qt.PointingHandCursor)
        self._circle_radius = height - 6 # e.g. 20px for 26px height
        
        # Internal State
        self._slider_pos = 3.0 # Start position (OFF)
        self._bg_color = QColor("#414868") # Default OFF
        
        # Appearance Config
        self.color_off = QColor("#414868")
        self.color_on = QColor("#7aa2f7") # Indigo accent
        self.color_circle = QColor("#ffffff")
        
        self.anim_duration = 300
        
        # Setup Animation
        self._anim = QPropertyAnimation(self, b"slider_pos", self)
        self._anim.setDuration(self.anim_duration)
        self._anim.setEasingCurve(QEasingCurve.OutBack)
        
        # Connect CheckBox signal
        self.stateChanged.connect(self._handle_state_change)
        
        # Initial draw state
        if self.isChecked():
            self._slider_pos = self.width() - self._circle_radius - 3
            self._bg_color = self.color_on
            
        # Add Glow Effect (visible when checked ideally, but constant subtle shadow is fine)
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(8)
        self._shadow.setColor(QColor(0, 0, 0, 40))
        self._shadow.setOffset(0, 2)
        self.setGraphicsEffect(self._shadow)

    # --- Property for Animation ---
    def get_slider_pos(self):
        return self._slider_pos
        
    def set_slider_pos(self, pos):
        self._slider_pos = pos
        self.update() # Trigger repaint
        
    slider_pos = Property(float, get_slider_pos, set_slider_pos)

    # --- Event Handlers ---
    def _handle_state_change(self, state):
        start = self._slider_pos
        if state == Qt.Checked or state == 2:
            end = self.width() - self._circle_radius - 3
            self._bg_color = self.color_on
            # Add stronger glow when ON
            self._shadow.setColor(QColor(122, 162, 247, 100))
        else:
            end = 3.0
            self._bg_color = self.color_off
            self._shadow.setColor(QColor(0, 0, 0, 40))
            
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # 1. Draw Track (Background)
        track_rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(track_rect), self.height() / 2, self.height() / 2)
        
        # Handle Hover lightness
        color = self._bg_color
        if self.underMouse() and not self.isChecked():
            color = color.lighter(110)
        elif self.underMouse() and self.isChecked():
             color = color.lighter(105)
             
        if not self.isEnabled():
            color = QColor("#24283b") # Disabled Dark
        
        p.fillPath(path, QBrush(color))
        
        # 2. Draw Slider (Circle)
        # Check center y
        cy = self.height() / 2
        # Slider x comes from animated property
        cx = self._slider_pos + (self._circle_radius / 2) 
        
        slider_rect = QRectF(self._slider_pos, 
                             (self.height() - self._circle_radius) / 2, 
                             self._circle_radius, 
                             self._circle_radius)
        
        p.setBrush(QBrush(self.color_circle))
        p.setPen(Qt.NoPen)
        p.drawEllipse(slider_rect)
        p.end()
