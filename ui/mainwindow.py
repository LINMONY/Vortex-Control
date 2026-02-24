from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QPushButton, QStackedWidget, QFrame, QLabel, QButtonGroup,
                               QGraphicsDropShadowEffect) # Added Grid and Effect import
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor
from pathlib import Path
from ui.frameless import FramelessWindow
from ui.components import AnimatedButton, FadingStackedWidget

# Use pathlib for robust path handling
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

class MainWindow(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.resize(1100, 720)
        self.setAttribute(Qt.WA_TranslucentBackground) # Important for rounded corners
        
        # Central Widget & Main Layout
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Use QGridLayout for overlay management (SafetyManager)
        main_layout = QGridLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Content Container (Title + Body) ---
        content_container = QWidget()
        content_layout_v = QVBoxLayout(content_container)
        content_layout_v.setContentsMargins(0, 0, 0, 0)
        content_layout_v.setSpacing(0)

        # Custom Title Bar
        self.setup_custom_titlebar(content_layout_v, "VORTEX CONTROL")

        # Body Layout (Sidebar + Stack)
        body_layout = QHBoxLayout()
        body_layout.setSpacing(0)
        
        # Sidebar
        self.create_sidebar(body_layout)
        
        # Stacked Pages
        self.content_stack = FadingStackedWidget()
        body_layout.addWidget(self.content_stack)
        
        content_layout_v.addLayout(body_layout)
        
        # Add content container to grid at bottom level
        main_layout.addWidget(content_container, 0, 0)

        # Init Pages
        self.init_pages()
        self.nav_buttons[0].setChecked(True)
        
        # Safety / Modals (Overlay)
        from ui.modal import SafetyManager
        self.safety = SafetyManager(self)
        # Add safety manager to the same grid cell to overlay it
        main_layout.addWidget(self.safety, 0, 0)

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

        # Icons (using pathlib)
        icons = {
            0: ASSETS_DIR / "icons/diamond.svg", # Dashboard
            2: ASSETS_DIR / "icons/fire.svg",    # Tweaks/System
        }

        # Dashboard (Index 0)
        self.add_nav_btn(layout, "", 0, icons.get(0), "Дашборд")
        
        # AI Page (Index 1) - Styled Text Button
        self.add_nav_btn(layout, "AI", 1, None, "AI Оптимизация")

        # System Layout (Index 2)
        self.add_nav_btn(layout, "", 2, icons.get(2), "Оптимизация")

        layout.addStretch()
        # Settings (Index 3)
        self.add_nav_btn(layout, "", 3, ASSETS_DIR / "icons/settings.svg", "Настройки")

        parent_layout.addWidget(self.sidebar)

    def add_nav_btn(self, layout, text, index, icon_path, tooltip=""):
        btn = QPushButton(text)
        btn.setObjectName("sidebarButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setFixedSize(50, 50) 
        
        if icon_path:
            path_obj = Path(icon_path)
            if path_obj.exists():
                btn.setIcon(QIcon(str(path_obj)))
                btn.setIconSize(QSize(28, 28))
            else:
                print(f"Icon not found: {path_obj}")
        
        if text == "AI":
            # Set property for QSS styling
            btn.setProperty("isAI", True)
            
            # Keep Glow Effect in Python as strictly requested/necessary
            glow = QGraphicsDropShadowEffect()
            glow.setBlurRadius(15)
            glow.setColor(QColor(122, 162, 247, 150))
            glow.setOffset(0, 0)
            btn.setGraphicsEffect(glow)
        
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

