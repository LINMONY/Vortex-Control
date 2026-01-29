from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QStackedWidget, QFrame, QLabel, QButtonGroup)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from ui.frameless import FramelessWindow
from ui.components import AnimatedButton, FadingStackedWidget
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

class MainWindow(FramelessWindow):
    def resizeEvent(self, event):
        if hasattr(self, 'safety'):
            self.safety.resize(self.size())
        super().resizeEvent(event)

    def __init__(self):
        super().__init__()
        self.resize(1100, 720)
        self.setAttribute(Qt.WA_TranslucentBackground) # Important for rounded corners
        
        # Central Widget & Main Layout
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        # Style is handled in styles.qss now
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom Title Bar
        self.setup_custom_titlebar(main_layout, "VORTEX CONTROL")

        # Content Layout (Sidebar + Stack)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        
        # Sidebar
        self.create_sidebar(content_layout)
        
        # Stacked Pages
        self.content_stack = FadingStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        main_layout.addLayout(content_layout)

        # Init Pages
        self.init_pages()
        self.nav_buttons[0].setChecked(True)
        
        # Safety / Modals
        # We perform lazy import to avoid circular dependencies if any, 
        # but here we can just import at top or here.
        from ui.modal import SafetyManager
        self.safety = SafetyManager(self)

    def create_sidebar(self, parent_layout):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        # Sidebar width smaller for icon-focus or kept specific size
        self.sidebar.setFixedWidth(80) 
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(15)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = {}

        # Icons
        icons = {
            0: os.path.join(ASSETS_DIR, "icons/diamond.svg"), # Dashboard
            2: os.path.join(ASSETS_DIR, "icons/fire.svg"),    # Tweaks/System
        }

        # Dashboard (Index 0)
        self.add_nav_btn(layout, "", 0, icons.get(0), "Дашборд")
        
        # AI Page (Index 1) - Styled Text Button
        self.add_nav_btn(layout, "AI", 1, None, "AI Оптимизация")

        # System Layout (Index 2)
        self.add_nav_btn(layout, "", 2, icons.get(2), "Оптимизация")

        layout.addStretch()
        # Settings (Index 3)
        self.add_nav_btn(layout, "", 3, os.path.join(ASSETS_DIR, "icons/settings.svg"), "Настройки")

        parent_layout.addWidget(self.sidebar)

    def add_nav_btn(self, layout, text, index, icon_path, tooltip=""):
        btn = QPushButton(text)
        btn.setObjectName("sidebarButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setFixedSize(50, 50) 
        
        if icon_path and os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(28, 28))
        elif text == "AI":
            # AI Section Styling
            btn.setStyleSheet("""
                QPushButton#sidebarButton {
                    font-family: 'Montserrat', 'Gilroy', 'Segoe UI', sans-serif;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    border: 1px solid rgba(122, 162, 247, 0.4);
                    border-radius: 12px;
                    background-color: transparent;
                }
                QPushButton#sidebarButton:hover {
                    background-color: rgba(122, 162, 247, 0.1);
                    border: 1px solid #7aa2f7;
                }
                QPushButton#sidebarButton:checked {
                    background-color: rgba(122, 162, 247, 0.2);
                    border: 1px solid #7aa2f7;
                    border-left: 3px solid #7aa2f7;
                    color: #7aa2f7;
                }
            """)
            from PySide6.QtWidgets import QGraphicsDropShadowEffect
            from PySide6.QtGui import QColor
            glow = QGraphicsDropShadowEffect()
            glow.setBlurRadius(15)
            glow.setColor(QColor(122, 162, 247, 150))
            glow.setOffset(0, 0)
            btn.setGraphicsEffect(glow)
        elif icon_path:
            print(f"Icon not found: {icon_path}")
        
        btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(index))
        layout.addWidget(btn, 0, Qt.AlignCenter)
        self.nav_group.addButton(btn, index)
        self.nav_buttons[index] = btn

    def init_pages(self):
        from ui.dashboard import Dashboard
        from ui.tweaks_container import TweaksContainer
        from ui.settings_page import SettingsPage
        from ui.ai_page import AIPage

        # 0: Dashboard (Home)
        self.content_stack.addWidget(Dashboard())

        # 1: AI Page
        self.content_stack.addWidget(AIPage())

        # 2: System / Tweaks
        self.content_stack.addWidget(TweaksContainer())

        # 3: Settings
        self.settings_page = SettingsPage()
        self.content_stack.addWidget(self.settings_page)
        
        # Connect SafetyManager signal to Settings refresh
        if hasattr(self, 'safety'):
            self.safety.restore_point_created.connect(self.settings_page.refresh_logs)
